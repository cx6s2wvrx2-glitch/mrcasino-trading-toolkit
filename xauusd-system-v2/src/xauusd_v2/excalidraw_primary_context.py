from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from .primary_context_bundle import FileSystemPrimaryContextBundleResolver


EXCALIDRAW_SOURCE_NAME = "casinonotes.excalidraw"
_SUPPORTED_IMAGE_MIME = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}
_MAX_SOURCE_BYTES = 512 * 1024 * 1024
_MAX_IMAGE_BYTES = 25 * 1024 * 1024
_MAX_REFERENCED_BYTES = 500 * 1024 * 1024


class ExcalidrawPrimaryContextError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ExcalidrawPrimaryContextStageReport:
    source_sha256: str
    requested_locators: int
    matched_locators: int
    staged_unique_images: int
    staged_unique_texts: int
    manifest_path: Path
    bundle_root: Path


def _immutable_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not path.is_file() or path.read_bytes() != payload:
            raise ExcalidrawPrimaryContextError(f"content-addressed bundle collision: {path}")
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
                raise ExcalidrawPrimaryContextError(f"content-addressed bundle collision: {path}")
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _parse_locator(locator: str) -> tuple[str, str] | None:
    value = locator.strip()
    prefix = f"{EXCALIDRAW_SOURCE_NAME}#"
    if not value.startswith(prefix):
        return None
    fragment = value[len(prefix):]
    if fragment.startswith("embedded:"):
        target = fragment.removeprefix("embedded:").strip()
        kind = "embedded"
    elif fragment.startswith("text:"):
        target = fragment.removeprefix("text:").strip()
        kind = "text"
    else:
        raise ExcalidrawPrimaryContextError(f"unsupported Excalidraw locator: {locator}")
    if not target or "#" in target or "/" in target or "\\" in target:
        raise ExcalidrawPrimaryContextError(f"invalid Excalidraw locator target: {locator}")
    return kind, target


def _verify_image_signature(payload: bytes, mime_type: str) -> None:
    valid = False
    if mime_type == "image/png":
        valid = payload.startswith(b"\x89PNG\r\n\x1a\n")
    elif mime_type == "image/jpeg":
        valid = payload.startswith(b"\xff\xd8\xff")
    elif mime_type == "image/webp":
        valid = len(payload) >= 12 and payload[:4] == b"RIFF" and payload[8:12] == b"WEBP"
    if not valid:
        raise ExcalidrawPrimaryContextError(f"embedded payload does not match declared {mime_type}")


def _decode_embedded_file(file_id: str, file_obj: object) -> tuple[bytes, str, str]:
    if not isinstance(file_obj, dict):
        raise ExcalidrawPrimaryContextError(f"missing embedded file object: {file_id}")
    mime_type = str(file_obj.get("mimeType", "")).strip().lower()
    suffix = _SUPPORTED_IMAGE_MIME.get(mime_type)
    if suffix is None:
        raise ExcalidrawPrimaryContextError(f"unsupported embedded image mime type: {mime_type or '<empty>'}")
    if str(file_obj.get("id", "")).strip() not in ("", file_id):
        raise ExcalidrawPrimaryContextError(f"embedded file id mismatch: {file_id}")
    data_url = str(file_obj.get("dataURL", "")).strip()
    expected_prefix = f"data:{mime_type};base64,"
    if not data_url.startswith(expected_prefix):
        raise ExcalidrawPrimaryContextError(f"embedded data URL mime mismatch: {file_id}")
    encoded = data_url[len(expected_prefix):]
    try:
        payload = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ExcalidrawPrimaryContextError(f"invalid embedded base64 payload: {file_id}") from exc
    if not payload or len(payload) > _MAX_IMAGE_BYTES:
        raise ExcalidrawPrimaryContextError(f"invalid embedded image size: {file_id}")
    _verify_image_signature(payload, mime_type)
    return payload, mime_type, suffix


def stage_excalidraw_primary_context(
    *,
    excalidraw_path: str | Path,
    source_locators: Iterable[str],
    bundle_root: str | Path,
    manifest_name: str = "excalidraw_primary_context_bundle.json",
) -> ExcalidrawPrimaryContextStageReport:
    """Stage exact original Excalidraw evidence for blind Agent-06 validation.

    Only source locators are accepted. `embedded:<fileId>` resolves the original image
    bytes stored in the Excalidraw `files` map; `text:<elementId>` resolves the exact
    non-deleted text element. No expected labels, analyst evidence, or ground-truth
    fields enter this boundary.
    """

    source = Path(excalidraw_path)
    root = Path(bundle_root)
    if not source.is_file():
        raise FileNotFoundError(str(source))
    source_size = source.stat().st_size
    if source_size <= 0 or source_size > _MAX_SOURCE_BYTES:
        raise ExcalidrawPrimaryContextError("invalid Excalidraw source size")

    locators = tuple(dict.fromkeys(str(item).strip() for item in source_locators if str(item).strip()))
    parsed: list[tuple[str, str, str]] = []
    for locator in locators:
        result = _parse_locator(locator)
        if result is not None:
            parsed.append((locator, result[0], result[1]))
    if not parsed:
        raise ExcalidrawPrimaryContextError("no Excalidraw source locators were supplied")

    source_bytes = source.read_bytes()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    try:
        document = json.loads(source_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExcalidrawPrimaryContextError("invalid Excalidraw JSON") from exc
    if not isinstance(document, dict) or document.get("type") != "excalidraw":
        raise ExcalidrawPrimaryContextError("source is not an Excalidraw document")
    elements = document.get("elements")
    files = document.get("files")
    if not isinstance(elements, list) or not isinstance(files, dict):
        raise ExcalidrawPrimaryContextError("Excalidraw document requires elements and files")

    live_elements = [item for item in elements if isinstance(item, dict) and not bool(item.get("isDeleted"))]
    live_by_id: dict[str, dict] = {}
    live_image_file_ids: set[str] = set()
    for element in live_elements:
        element_id = str(element.get("id", "")).strip()
        if element_id:
            if element_id in live_by_id:
                raise ExcalidrawPrimaryContextError(f"duplicate live element id: {element_id}")
            live_by_id[element_id] = element
        if element.get("type") == "image":
            file_id = str(element.get("fileId", "")).strip()
            if file_id:
                live_image_file_ids.add(file_id)

    image_assets: dict[str, tuple[str, str]] = {}
    text_assets: dict[str, str] = {}
    total_referenced_bytes = 0
    entries: list[dict[str, object]] = []

    for locator, kind, target in parsed:
        if kind == "embedded":
            if target not in live_image_file_ids:
                raise ExcalidrawPrimaryContextError(f"embedded file has no live image element: {target}")
            asset = image_assets.get(target)
            if asset is None:
                payload, mime_type, suffix = _decode_embedded_file(target, files.get(target))
                total_referenced_bytes += len(payload)
                if total_referenced_bytes > _MAX_REFERENCED_BYTES:
                    raise ExcalidrawPrimaryContextError("referenced Excalidraw payload exceeds safety limit")
                digest = hashlib.sha256(payload).hexdigest()
                relative = f"assets/{digest}{suffix}"
                _immutable_write(root / relative, payload)
                asset = (relative, mime_type)
                image_assets[target] = asset
            entries.append({
                "source_locator": locator,
                "images": [{"path": asset[0], "mime_type": asset[1]}],
            })
            continue

        element = live_by_id.get(target)
        if element is None or element.get("type") != "text":
            raise ExcalidrawPrimaryContextError(f"missing live text element: {target}")
        text = str(element.get("text", "")).strip()
        if not text:
            raise ExcalidrawPrimaryContextError(f"empty live text element: {target}")
        relative = text_assets.get(target)
        if relative is None:
            payload = (text + "\n").encode("utf-8")
            digest = hashlib.sha256(payload).hexdigest()
            relative = f"text/{digest}.txt"
            _immutable_write(root / relative, payload)
            text_assets[target] = relative
        entries.append({"source_locator": locator, "text_path": relative})

    manifest = {
        "version": 1,
        "generator": "excalidraw_primary_context_v1",
        "source_sha256": source_sha,
        "source_name": EXCALIDRAW_SOURCE_NAME,
        "entries": entries,
    }
    manifest_bytes = (json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    manifest_path = root / manifest_name
    _immutable_write(manifest_path, manifest_bytes)

    resolver = FileSystemPrimaryContextBundleResolver(bundle_root=root, manifest_path=manifest_path)
    for locator, _, _ in parsed:
        resolver.resolve_payload(locator)

    return ExcalidrawPrimaryContextStageReport(
        source_sha256=source_sha,
        requested_locators=len(locators),
        matched_locators=len(parsed),
        staged_unique_images=len(image_assets),
        staged_unique_texts=len(text_assets),
        manifest_path=manifest_path,
        bundle_root=root,
    )
