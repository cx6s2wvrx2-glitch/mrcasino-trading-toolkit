from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from uuid import uuid4

from .primary_context_bundle import PrimaryContextBundleEntry, load_primary_context_bundle


class PrimaryContextBundleMergeError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PrimaryContextBundleMergeReport:
    input_manifests: int
    merged_entries: int
    output_manifest: Path


def _entry_payload(entry: PrimaryContextBundleEntry) -> dict[str, object]:
    payload: dict[str, object] = {"source_locator": entry.source_locator}
    if entry.text_path is not None:
        payload["text_path"] = entry.text_path
    if entry.images:
        payload["images"] = [asdict(image) for image in entry.images]
    return payload


def _immutable_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not path.is_file() or path.read_bytes() != payload:
            raise PrimaryContextBundleMergeError(f"bundle manifest collision: {path}")
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
                raise PrimaryContextBundleMergeError(f"bundle manifest collision: {path}")
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def merge_primary_context_manifests(
    *,
    manifest_paths: tuple[str | Path, ...],
    output_manifest: str | Path,
) -> PrimaryContextBundleMergeReport:
    """Merge already-validated v1 primary-context manifests without answer fields."""

    if not manifest_paths:
        raise PrimaryContextBundleMergeError("at least one primary context manifest is required")

    by_locator: dict[str, PrimaryContextBundleEntry] = {}
    for manifest_path in manifest_paths:
        bundle = load_primary_context_bundle(manifest_path)
        for entry in bundle.entries:
            previous = by_locator.get(entry.source_locator)
            if previous is not None and previous != entry:
                raise PrimaryContextBundleMergeError(
                    f"conflicting primary context entry for {entry.source_locator}"
                )
            by_locator[entry.source_locator] = entry

    entries = [_entry_payload(by_locator[key]) for key in sorted(by_locator)]
    payload = {
        "version": 1,
        "generator": "primary_context_bundle_merge_v1",
        "entries": entries,
    }
    encoded = (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    output = Path(output_manifest)
    _immutable_write(output, encoded)
    load_primary_context_bundle(output)

    return PrimaryContextBundleMergeReport(
        input_manifests=len(manifest_paths),
        merged_entries=len(entries),
        output_manifest=output,
    )
