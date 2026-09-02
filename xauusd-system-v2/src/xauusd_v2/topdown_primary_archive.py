from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable
from uuid import uuid4
from zipfile import BadZipFile, ZipFile, ZipInfo

from .primary_context_bundle import FileSystemPrimaryContextBundleResolver


TOPDOWN_SOURCE_UUID = "b271d0b8-a86b-4d65-a4ae-b7e49d5803a6"
TOPDOWN_ARCHIVE_NAME = "top down analysis (1).zip"
_IMAGE_EXTENSIONS = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
_IMAGE_DATE = re.compile(r"^IMG_(\d{8})_")
_MAX_IMAGE_BYTES = 25 * 1024 * 1024
_MAX_REFERENCED_BYTES = 500 * 1024 * 1024


class TopDownPrimaryArchiveError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class TopDownPrimaryArchiveStageReport:
    archive_sha256: str
    requested_locators: int
    matched_locators: int
    staged_unique_images: int
    manifest_path: Path
    bundle_root: Path


def _immutable_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not path.is_file() or path.read_bytes() != payload:
            raise TopDownPrimaryArchiveError(f"content-addressed bundle collision: {path}")
        return
    temp = path.parent / f".{path.name}.{uuid4().hex}.tmp"
    try:
        with temp.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp, path)
        except FileExistsError:
            if not path.is_file() or path.read_bytes() != payload:
                raise TopDownPrimaryArchiveError(f"content-addressed bundle collision: {path}")
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _safe_image_member(info: ZipInfo) -> bool:
    name = info.filename
    path = PurePosixPath(name)
    if info.is_dir() or name.startswith("__MACOSX/") or path.name.startswith("._"):
        return False
    return path.suffix.lower() in _IMAGE_EXTENSIONS


def _image_date(filename: str) -> str | None:
    match = _IMAGE_DATE.match(filename)
    if not match:
        return None
    raw = match.group(1)
    return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"


def _parse_topdown_locator(locator: str) -> tuple[str, str | None] | None:
    value = locator.strip()
    primary_prefix = f"v2_sources:{TOPDOWN_SOURCE_UUID}#"
    legacy_prefix = f"{TOPDOWN_ARCHIVE_NAME}#"
    if value.startswith(primary_prefix):
        fragment = value[len(primary_prefix):]
    elif value.startswith(legacy_prefix):
        fragment = value[len(legacy_prefix):]
    else:
        return None

    parts = fragment.split("#")
    sequence: str | None = None
    image: str | None = None
    for part in parts:
        if part.startswith("sequence:"):
            sequence = part.removeprefix("sequence:").strip()
        elif part.startswith("image:"):
            image = PurePosixPath(part.removeprefix("image:").strip()).name
    if not sequence:
        raise TopDownPrimaryArchiveError(f"top-down locator requires sequence date: {locator}")
    if image is not None and not image:
        raise TopDownPrimaryArchiveError(f"top-down locator contains empty image name: {locator}")
    return sequence, image


def _verify_image_signature(payload: bytes, mime_type: str) -> None:
    valid = False
    if mime_type == "image/jpeg":
        valid = payload.startswith(b"\xff\xd8\xff")
    elif mime_type == "image/png":
        valid = payload.startswith(b"\x89PNG\r\n\x1a\n")
    elif mime_type == "image/webp":
        valid = len(payload) >= 12 and payload[:4] == b"RIFF" and payload[8:12] == b"WEBP"
    if not valid:
        raise TopDownPrimaryArchiveError(f"archive member does not match declared {mime_type}")


def stage_topdown_primary_archive(
    *,
    archive_path: str | Path,
    source_locators: Iterable[str],
    bundle_root: str | Path,
    manifest_name: str = "topdown_primary_context_bundle.json",
) -> TopDownPrimaryArchiveStageReport:
    """Build a label-blind Agent-06 bundle from the original top-down ZIP.

    Inputs are source locators only. No expected labels, analyst evidence, candidate
    rules, or ground-truth fields are accepted. Image matching is exact by original
    filename and sequence date. Sequence-only locators receive all original images
    whose filename date matches that sequence.
    """

    archive = Path(archive_path)
    root = Path(bundle_root)
    if not archive.is_file():
        raise FileNotFoundError(str(archive))
    locators = tuple(dict.fromkeys(str(item).strip() for item in source_locators if str(item).strip()))
    parsed: list[tuple[str, str, str | None]] = []
    for locator in locators:
        result = _parse_topdown_locator(locator)
        if result is not None:
            parsed.append((locator, result[0], result[1]))
    if not parsed:
        raise TopDownPrimaryArchiveError("no top-down source locators were supplied")

    archive_bytes = archive.read_bytes()
    archive_sha = hashlib.sha256(archive_bytes).hexdigest()

    try:
        with ZipFile(archive) as zipped:
            members: dict[str, ZipInfo] = {}
            by_sequence: dict[str, list[ZipInfo]] = {}
            for info in zipped.infolist():
                if not _safe_image_member(info):
                    continue
                basename = PurePosixPath(info.filename).name
                if basename in members:
                    raise TopDownPrimaryArchiveError(f"duplicate original image basename: {basename}")
                if info.file_size <= 0 or info.file_size > _MAX_IMAGE_BYTES:
                    raise TopDownPrimaryArchiveError(f"invalid primary image size for {basename}")
                members[basename] = info
                sequence = _image_date(basename)
                if sequence is not None:
                    by_sequence.setdefault(sequence, []).append(info)

            locator_members: list[tuple[str, tuple[ZipInfo, ...]]] = []
            referenced: dict[str, ZipInfo] = {}
            for locator, sequence, image in parsed:
                if image is not None:
                    info = members.get(image)
                    if info is None:
                        raise TopDownPrimaryArchiveError(f"primary archive is missing {image}")
                    if _image_date(image) != sequence:
                        raise TopDownPrimaryArchiveError(
                            f"source locator sequence/image date mismatch: {locator}"
                        )
                    selected = (info,)
                else:
                    selected = tuple(sorted(by_sequence.get(sequence, ()), key=lambda item: item.filename))
                    if not selected:
                        raise TopDownPrimaryArchiveError(
                            f"primary archive has no images for sequence {sequence}"
                        )
                locator_members.append((locator, selected))
                for info in selected:
                    referenced[PurePosixPath(info.filename).name] = info

            total_size = sum(info.file_size for info in referenced.values())
            if total_size > _MAX_REFERENCED_BYTES:
                raise TopDownPrimaryArchiveError("referenced primary image payload exceeds safety limit")

            asset_refs: dict[str, tuple[str, str]] = {}
            for basename, info in sorted(referenced.items()):
                payload = zipped.read(info)
                suffix = PurePosixPath(basename).suffix.lower()
                mime = _IMAGE_EXTENSIONS[suffix]
                _verify_image_signature(payload, mime)
                digest = hashlib.sha256(payload).hexdigest()
                asset_path = root / "assets" / f"{digest}{suffix}"
                _immutable_write(asset_path, payload)
                asset_refs[basename] = (f"assets/{digest}{suffix}", mime)
    except BadZipFile as exc:
        raise TopDownPrimaryArchiveError("invalid top-down source ZIP") from exc

    entries = []
    for locator, selected in locator_members:
        images = []
        for info in selected:
            basename = PurePosixPath(info.filename).name
            relative_path, mime = asset_refs[basename]
            images.append({"path": relative_path, "mime_type": mime})
        entries.append({"source_locator": locator, "images": images})

    manifest = {
        "version": 1,
        "generator": "topdown_primary_archive_v1",
        "archive_sha256": archive_sha,
        "source_uuid": TOPDOWN_SOURCE_UUID,
        "entries": entries,
    }
    manifest_bytes = (
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    manifest_path = root / manifest_name
    _immutable_write(manifest_path, manifest_bytes)

    # Validate the exact output with the runtime resolver contract before returning.
    resolver = FileSystemPrimaryContextBundleResolver(
        bundle_root=root,
        manifest_path=manifest_path,
    )
    for locator, _, _ in parsed:
        resolver.resolve_payload(locator)

    return TopDownPrimaryArchiveStageReport(
        archive_sha256=archive_sha,
        requested_locators=len(locators),
        matched_locators=len(parsed),
        staged_unique_images=len(asset_refs),
        manifest_path=manifest_path,
        bundle_root=root,
    )
