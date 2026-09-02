from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .primary_context_payload import PrimaryContextPayload, PrimaryImageEvidence


_FORBIDDEN_KEYS = {
    "expected_label",
    "expected_class",
    "forbidden_inference",
    "ground_truth_answer",
    "promotion_allowed",
}


@dataclass(frozen=True, slots=True)
class BundleImageRef:
    path: str
    mime_type: str


@dataclass(frozen=True, slots=True)
class PrimaryContextBundleEntry:
    source_locator: str
    text_path: str | None = None
    images: tuple[BundleImageRef, ...] = ()


@dataclass(frozen=True, slots=True)
class PrimaryContextBundle:
    version: int
    entries: tuple[PrimaryContextBundleEntry, ...]

    @property
    def by_locator(self) -> dict[str, PrimaryContextBundleEntry]:
        return {entry.source_locator: entry for entry in self.entries}


def _reject_answer_fields(value: Any, *, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in _FORBIDDEN_KEYS:
                raise ValueError(f"primary context bundle contains forbidden answer field at {path}.{key}")
            _reject_answer_fields(item, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_answer_fields(item, path=f"{path}[{index}]")


def load_primary_context_bundle(path: str | Path) -> PrimaryContextBundle:
    manifest_path = Path(path)
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("primary context bundle manifest must be a JSON object")
    _reject_answer_fields(raw)

    version = raw.get("version")
    if version != 1:
        raise ValueError("unsupported primary context bundle version")
    raw_entries = raw.get("entries")
    if not isinstance(raw_entries, list) or not raw_entries:
        raise ValueError("primary context bundle requires non-empty entries")

    entries: list[PrimaryContextBundleEntry] = []
    seen: set[str] = set()
    for item in raw_entries:
        if not isinstance(item, dict):
            raise ValueError("primary context bundle entry must be an object")
        locator = str(item.get("source_locator", "")).strip()
        if not locator:
            raise ValueError("primary context bundle entry requires source_locator")
        if locator in seen:
            raise ValueError(f"duplicate primary context locator: {locator}")
        seen.add(locator)

        text_path_raw = item.get("text_path")
        text_path = None if text_path_raw is None else str(text_path_raw).strip() or None
        images_raw = item.get("images", [])
        if not isinstance(images_raw, list):
            raise ValueError("primary context bundle images must be an array")
        images: list[BundleImageRef] = []
        for image in images_raw:
            if not isinstance(image, dict):
                raise ValueError("primary context image entry must be an object")
            image_path = str(image.get("path", "")).strip()
            mime_type = str(image.get("mime_type", "")).strip().lower()
            if not image_path or not mime_type:
                raise ValueError("primary context image requires path and mime_type")
            images.append(BundleImageRef(path=image_path, mime_type=mime_type))
        if text_path is None and not images:
            raise ValueError("primary context entry requires text_path or images")
        entries.append(
            PrimaryContextBundleEntry(
                source_locator=locator,
                text_path=text_path,
                images=tuple(images),
            )
        )
    return PrimaryContextBundle(version=version, entries=tuple(entries))


class FileSystemPrimaryContextBundleResolver:
    """Resolve primary source payloads from a local immutable-ish evidence bundle.

    Paths in the manifest are always relative to `bundle_root`. Absolute paths and
    traversal outside that root are rejected. Image bytes are hashed each time they are
    resolved, then re-verified by the validation runtime before the external model call.
    """

    def __init__(self, *, bundle_root: str | Path, manifest_path: str | Path) -> None:
        self.bundle_root = Path(bundle_root).resolve()
        if not self.bundle_root.is_dir():
            raise FileNotFoundError(str(self.bundle_root))
        self.bundle = load_primary_context_bundle(manifest_path)
        self.entries = self.bundle.by_locator

    def _resolve_relative(self, relative: str) -> Path:
        candidate = (self.bundle_root / relative).resolve()
        try:
            candidate.relative_to(self.bundle_root)
        except ValueError as exc:
            raise ValueError("primary context bundle path escapes bundle root") from exc
        return candidate

    def resolve_payload(self, source_locator: str) -> PrimaryContextPayload:
        locator = source_locator.strip()
        entry = self.entries.get(locator)
        if entry is None:
            raise LookupError(f"primary context bundle has no entry for {locator}")

        text = ""
        if entry.text_path is not None:
            text_path = self._resolve_relative(entry.text_path)
            if not text_path.is_file():
                raise FileNotFoundError(str(text_path))
            text = text_path.read_text(encoding="utf-8").strip()

        images = tuple(
            PrimaryImageEvidence.from_path(
                self._resolve_relative(image.path),
                mime_type=image.mime_type,
            )
            for image in entry.images
        )
        return PrimaryContextPayload(text=text, images=images).normalized()
