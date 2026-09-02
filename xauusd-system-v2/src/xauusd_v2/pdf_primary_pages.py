from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .primary_context_bundle import FileSystemPrimaryContextBundleResolver


_PAGE_LOCATOR = re.compile(
    r"^v2_sources:([0-9a-fA-F-]{36})#page:([1-9][0-9]*)(?:#.+)?$"
)
_IMAGE_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
_MAX_PAGE_IMAGE_BYTES = 40 * 1024 * 1024


class PDFPrimaryPageStageError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PDFPrimaryPageStageReport:
    requested_locators: int
    matched_locators: int
    staged_unique_pages: int
    staged_unique_assets: int
    manifest_path: Path
    bundle_root: Path


def _immutable_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not path.is_file() or path.read_bytes() != payload:
            raise PDFPrimaryPageStageError(f"content-addressed bundle collision: {path}")
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
                raise PDFPrimaryPageStageError(f"content-addressed bundle collision: {path}")
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _verify_image(payload: bytes, mime_type: str) -> None:
    valid = False
    if mime_type == "image/png":
        valid = payload.startswith(b"\x89PNG\r\n\x1a\n")
    elif mime_type == "image/jpeg":
        valid = payload.startswith(b"\xff\xd8\xff")
    elif mime_type == "image/webp":
        valid = len(payload) >= 12 and payload[:4] == b"RIFF" and payload[8:12] == b"WEBP"
    if not valid:
        raise PDFPrimaryPageStageError(f"rendered page does not match declared {mime_type}")


def _parse_page_locator(locator: str) -> tuple[str, int] | None:
    match = _PAGE_LOCATOR.fullmatch(locator.strip())
    if match is None:
        return None
    return match.group(1).lower(), int(match.group(2))


def stage_pdf_primary_pages(
    *,
    rendered_pages: Mapping[str, Mapping[int, str | Path]],
    source_locators: Iterable[str],
    bundle_root: str | Path,
    manifest_name: str = "pdf_primary_pages_bundle.json",
) -> PDFPrimaryPageStageReport:
    """Stage full rendered pages for UUID-backed PDF blind locators.

    The caller supplies source UUID -> page number -> rendered original page image.
    The function accepts only source locators, never expected labels or analyst answers.
    A single canonical `v2_sources:<uuid>#page:N` bundle entry is created per page;
    fragment locators safely resolve through the page fallback in the bundle resolver.
    """

    root = Path(bundle_root)
    normalized_pages: dict[str, dict[int, Path]] = {
        str(source_uuid).strip().lower(): {int(page): Path(path) for page, path in pages.items()}
        for source_uuid, pages in rendered_pages.items()
    }
    locators = tuple(dict.fromkeys(str(item).strip() for item in source_locators if str(item).strip()))

    matched: list[tuple[str, int]] = []
    for locator in locators:
        parsed = _parse_page_locator(locator)
        if parsed is None:
            continue
        source_uuid, page = parsed
        if source_uuid not in normalized_pages:
            continue
        matched.append((source_uuid, page))
    if not matched:
        raise PDFPrimaryPageStageError("no PDF page source locators matched the supplied sources")

    needed_pages = tuple(dict.fromkeys(matched))
    entries: list[dict[str, object]] = []
    staged_assets: set[str] = set()

    for source_uuid, page in needed_pages:
        page_path = normalized_pages[source_uuid].get(page)
        if page_path is None:
            raise PDFPrimaryPageStageError(
                f"missing rendered primary page for {source_uuid} page {page}"
            )
        if not page_path.is_file():
            raise FileNotFoundError(str(page_path))
        suffix = page_path.suffix.lower()
        mime_type = _IMAGE_MIME.get(suffix)
        if mime_type is None:
            raise PDFPrimaryPageStageError(f"unsupported rendered page image type: {suffix}")
        payload = page_path.read_bytes()
        if not payload or len(payload) > _MAX_PAGE_IMAGE_BYTES:
            raise PDFPrimaryPageStageError(
                f"invalid rendered primary page size for {source_uuid} page {page}"
            )
        _verify_image(payload, mime_type)
        digest = hashlib.sha256(payload).hexdigest()
        relative = f"assets/{digest}{suffix}"
        _immutable_write(root / relative, payload)
        staged_assets.add(relative)
        entries.append(
            {
                "source_locator": f"v2_sources:{source_uuid}#page:{page}",
                "images": [{"path": relative, "mime_type": mime_type}],
            }
        )

    entries.sort(key=lambda item: str(item["source_locator"]))
    manifest = {
        "version": 1,
        "generator": "pdf_primary_pages_v1",
        "entries": entries,
    }
    manifest_bytes = (
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    manifest_path = root / manifest_name
    _immutable_write(manifest_path, manifest_bytes)

    resolver = FileSystemPrimaryContextBundleResolver(
        bundle_root=root,
        manifest_path=manifest_path,
    )
    for locator in locators:
        parsed = _parse_page_locator(locator)
        if parsed is not None and parsed[0] in normalized_pages:
            resolver.resolve_payload(locator)

    return PDFPrimaryPageStageReport(
        requested_locators=len(locators),
        matched_locators=len(matched),
        staged_unique_pages=len(needed_pages),
        staged_unique_assets=len(staged_assets),
        manifest_path=manifest_path,
        bundle_root=root,
    )
