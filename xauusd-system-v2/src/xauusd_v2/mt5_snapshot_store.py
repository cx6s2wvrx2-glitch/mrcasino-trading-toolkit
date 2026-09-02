from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .mt5_history import MT5HistoryIngestionResult


class MT5SnapshotStoreError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PersistedMT5Snapshot:
    store_root: Path
    raw_source_path: Path
    canonical_snapshot_path: Path
    ingestion_manifest_path: Path
    source_sha256: str
    normalized_sha256: str
    schema_version: str = "mt5_snapshot_store_v1"


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _immutable_write(path: Path, payload: bytes) -> None:
    """Create a file exactly once, or verify an identical existing file.

    The temporary file is linked into place instead of replaced so an existing
    content-addressed object can never be overwritten by this function.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not path.is_file():
            raise MT5SnapshotStoreError(f"immutable store target is not a file: {path}")
        if path.read_bytes() != payload:
            raise MT5SnapshotStoreError(f"immutable store collision or tampering detected: {path}")
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
                raise MT5SnapshotStoreError(
                    f"immutable store collision or tampering detected: {path}"
                )
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _store_manifest_bytes(result: MT5HistoryIngestionResult) -> bytes:
    manifest = {
        "schema_version": "mt5_snapshot_store_v1",
        "source_sha256": result.ingestion.source_sha256,
        "normalized_sha256": result.ingestion.normalized_sha256,
        "raw_source_ref": f"raw/{result.ingestion.source_sha256}/source.mt5.txt",
        "canonical_snapshot_ref": f"snapshots/{result.ingestion.normalized_sha256}/xauusd_ohlc.csv",
        "ingestion": _jsonable(asdict(result.ingestion)),
        "snapshot": _jsonable(asdict(result.snapshot)),
        "validation": _jsonable(asdict(result.validation)),
    }
    return (
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def persist_mt5_ingestion(
    *,
    raw_source_bytes: bytes,
    result: MT5HistoryIngestionResult,
    store_root: str | Path,
) -> PersistedMT5Snapshot:
    """Persist exact MT5 source bytes + normalized XAUUSD snapshot immutably.

    Paths are derived only from verified SHA-256 values. The original source
    filename is retained inside the ingestion manifest as provenance but never
    controls filesystem placement.
    """

    root = Path(store_root)
    if not raw_source_bytes:
        raise MT5SnapshotStoreError("raw MT5 source bytes are required")

    import hashlib

    observed_source_sha = hashlib.sha256(raw_source_bytes).hexdigest()
    if observed_source_sha != result.ingestion.source_sha256:
        raise MT5SnapshotStoreError("raw MT5 source hash does not match ingestion manifest")

    observed_normalized_sha = hashlib.sha256(result.canonical_csv_bytes).hexdigest()
    if observed_normalized_sha != result.ingestion.normalized_sha256:
        raise MT5SnapshotStoreError("canonical snapshot hash does not match ingestion manifest")
    if result.snapshot.sha256 != observed_normalized_sha:
        raise MT5SnapshotStoreError("snapshot manifest hash does not match canonical snapshot bytes")

    raw_path = root / "raw" / observed_source_sha / "source.mt5.txt"
    snapshot_path = root / "snapshots" / observed_normalized_sha / "xauusd_ohlc.csv"
    ingestion_path = (
        root
        / "ingestions"
        / f"{observed_source_sha}--{observed_normalized_sha}.json"
    )

    _immutable_write(raw_path, raw_source_bytes)
    _immutable_write(snapshot_path, result.canonical_csv_bytes)
    _immutable_write(ingestion_path, _store_manifest_bytes(result))

    return PersistedMT5Snapshot(
        store_root=root,
        raw_source_path=raw_path,
        canonical_snapshot_path=snapshot_path,
        ingestion_manifest_path=ingestion_path,
        source_sha256=observed_source_sha,
        normalized_sha256=observed_normalized_sha,
    )
