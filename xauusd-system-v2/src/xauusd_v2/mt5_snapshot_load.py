from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .agents.data_agent import MarketDataValidationReport
from .data_snapshot import DataSnapshotManifest, load_xauusd_csv_snapshot_bytes


class MT5SnapshotLoadError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class VerifiedPersistedMT5Snapshot:
    manifest_path: Path
    store_root: Path
    raw_source_path: Path
    canonical_snapshot_path: Path
    source_sha256: str
    normalized_sha256: str
    snapshot: DataSnapshotManifest
    validation: MarketDataValidationReport
    schema_version: str = "verified_mt5_snapshot_v1"


_TOP_LEVEL_KEYS = {
    "schema_version",
    "source_sha256",
    "normalized_sha256",
    "raw_source_ref",
    "canonical_snapshot_ref",
    "ingestion",
    "snapshot",
    "validation",
}
_SNAPSHOT_KEYS = {
    "snapshot_id",
    "sha256",
    "canonical_symbol",
    "timeframe_seconds",
    "source_name",
    "source_symbol",
    "source_file_name",
    "bar_count",
    "first_timestamp",
    "last_timestamp",
    "coverage_end",
    "closed_only",
    "schema_version",
}
_INGESTION_KEYS = {
    "broker_name",
    "broker_symbol",
    "canonical_symbol",
    "timeframe_seconds",
    "source_timezone",
    "source_file_name",
    "source_sha256",
    "source_size_bytes",
    "normalized_snapshot_id",
    "normalized_sha256",
    "bar_count",
    "first_timestamp_utc",
    "last_timestamp_utc",
    "detected_delimiter",
    "detected_headers",
    "gap_count",
    "gap_durations_seconds",
    "optional_columns",
    "schema_version",
}
_VALIDATION_KEYS = {
    "canonical_symbol",
    "timeframe_seconds",
    "total_bars",
    "closed_bars",
    "provisional_bars",
    "first_timestamp",
    "last_timestamp",
    "source_names",
    "source_symbols",
    "warnings",
}


def _require_exact_keys(value: object, expected: set[str], *, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MT5SnapshotLoadError(f"{field} must be an object")
    observed = set(value)
    if observed != expected:
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        raise MT5SnapshotLoadError(
            f"{field} schema mismatch; missing={missing}, extra={extra}"
        )
    return value


def _sha256_hex(value: object, *, field: str) -> str:
    text = str(value).strip().lower()
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise MT5SnapshotLoadError(f"{field} must be a SHA-256 hex digest")
    return text


def _aware_datetime(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise MT5SnapshotLoadError(f"{field} must be an ISO-8601 timestamp")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise MT5SnapshotLoadError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MT5SnapshotLoadError(f"{field} must be timezone-aware")
    return parsed


def _positive_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise MT5SnapshotLoadError(f"{field} must be a positive integer")
    return value


def _nonnegative_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise MT5SnapshotLoadError(f"{field} must be a non-negative integer")
    return value


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


def _snapshot_from_json(value: object) -> DataSnapshotManifest:
    item = _require_exact_keys(value, _SNAPSHOT_KEYS, field="snapshot")
    canonical_symbol = str(item["canonical_symbol"]).strip().upper()
    if canonical_symbol != "XAUUSD":
        raise MT5SnapshotLoadError("persisted snapshot is not canonical XAUUSD")
    source_name = str(item["source_name"]).strip()
    source_symbol = str(item["source_symbol"]).strip()
    if not source_name or not source_symbol:
        raise MT5SnapshotLoadError("persisted snapshot source provenance is incomplete")
    source_file_name_raw = item["source_file_name"]
    if source_file_name_raw is not None and not isinstance(source_file_name_raw, str):
        raise MT5SnapshotLoadError("snapshot.source_file_name must be string or null")
    closed_only = item["closed_only"]
    if not isinstance(closed_only, bool):
        raise MT5SnapshotLoadError("snapshot.closed_only must be boolean")
    schema_version = str(item["schema_version"]).strip()
    if schema_version != "xauusd_ohlc_v1":
        raise MT5SnapshotLoadError("unsupported canonical snapshot schema_version")
    return DataSnapshotManifest(
        snapshot_id=str(item["snapshot_id"]).strip(),
        sha256=_sha256_hex(item["sha256"], field="snapshot.sha256"),
        canonical_symbol=canonical_symbol,
        timeframe_seconds=_positive_int(item["timeframe_seconds"], field="snapshot.timeframe_seconds"),
        source_name=source_name,
        source_symbol=source_symbol,
        source_file_name=source_file_name_raw,
        bar_count=_positive_int(item["bar_count"], field="snapshot.bar_count"),
        first_timestamp=_aware_datetime(item["first_timestamp"], field="snapshot.first_timestamp"),
        last_timestamp=_aware_datetime(item["last_timestamp"], field="snapshot.last_timestamp"),
        coverage_end=_aware_datetime(item["coverage_end"], field="snapshot.coverage_end"),
        closed_only=closed_only,
        schema_version=schema_version,
    )


def load_verified_persisted_mt5_snapshot(
    manifest_path: str | Path,
) -> VerifiedPersistedMT5Snapshot:
    """Load a persisted MT5 snapshot only after re-verifying bytes and provenance.

    The ingestion manifest is treated as untrusted input. No broker, symbol, timeframe,
    timestamp or path is inferred. Content-addressed references must match the exact
    store layout emitted by ``persist_mt5_ingestion`` and all source/snapshot bytes are
    hashed again before the snapshot can be used by historical-replay alignment.
    """

    path = Path(manifest_path).expanduser().resolve()
    if not path.is_file():
        raise MT5SnapshotLoadError("MT5 ingestion manifest file is unavailable")
    try:
        raw_manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MT5SnapshotLoadError("MT5 ingestion manifest is not valid UTF-8 JSON") from exc

    manifest = _require_exact_keys(raw_manifest, _TOP_LEVEL_KEYS, field="manifest")
    if manifest["schema_version"] != "mt5_snapshot_store_v1":
        raise MT5SnapshotLoadError("unsupported MT5 snapshot store schema_version")

    source_sha = _sha256_hex(manifest["source_sha256"], field="source_sha256")
    normalized_sha = _sha256_hex(manifest["normalized_sha256"], field="normalized_sha256")
    expected_raw_ref = f"raw/{source_sha}/source.mt5.txt"
    expected_snapshot_ref = f"snapshots/{normalized_sha}/xauusd_ohlc.csv"
    if manifest["raw_source_ref"] != expected_raw_ref:
        raise MT5SnapshotLoadError("raw_source_ref is not the canonical content-addressed path")
    if manifest["canonical_snapshot_ref"] != expected_snapshot_ref:
        raise MT5SnapshotLoadError("canonical_snapshot_ref is not the canonical content-addressed path")

    if path.parent.name != "ingestions":
        raise MT5SnapshotLoadError("manifest must live inside the MT5 store ingestions directory")
    store_root = path.parent.parent.resolve()
    expected_manifest_name = f"{source_sha}--{normalized_sha}.json"
    if path.name != expected_manifest_name:
        raise MT5SnapshotLoadError("ingestion manifest filename does not match content hashes")

    raw_source_path = (store_root / expected_raw_ref).resolve()
    canonical_snapshot_path = (store_root / expected_snapshot_ref).resolve()
    if not raw_source_path.is_relative_to(store_root) or not canonical_snapshot_path.is_relative_to(store_root):
        raise MT5SnapshotLoadError("persisted MT5 object path escapes store root")
    if not raw_source_path.is_file() or not canonical_snapshot_path.is_file():
        raise MT5SnapshotLoadError("persisted MT5 source or canonical snapshot file is unavailable")

    raw_source_bytes = raw_source_path.read_bytes()
    canonical_bytes = canonical_snapshot_path.read_bytes()
    if hashlib.sha256(raw_source_bytes).hexdigest() != source_sha:
        raise MT5SnapshotLoadError("persisted raw MT5 source SHA-256 mismatch")
    if hashlib.sha256(canonical_bytes).hexdigest() != normalized_sha:
        raise MT5SnapshotLoadError("persisted canonical snapshot SHA-256 mismatch")

    ingestion = _require_exact_keys(manifest["ingestion"], _INGESTION_KEYS, field="ingestion")
    validation_json = _require_exact_keys(manifest["validation"], _VALIDATION_KEYS, field="validation")
    snapshot = _snapshot_from_json(manifest["snapshot"])

    if _sha256_hex(ingestion["source_sha256"], field="ingestion.source_sha256") != source_sha:
        raise MT5SnapshotLoadError("ingestion source hash disagrees with store manifest")
    if _sha256_hex(ingestion["normalized_sha256"], field="ingestion.normalized_sha256") != normalized_sha:
        raise MT5SnapshotLoadError("ingestion normalized hash disagrees with store manifest")
    if snapshot.sha256 != normalized_sha or snapshot.snapshot_id != f"sha256:{normalized_sha}":
        raise MT5SnapshotLoadError("snapshot identity disagrees with canonical snapshot hash")
    if ingestion["normalized_snapshot_id"] != snapshot.snapshot_id:
        raise MT5SnapshotLoadError("ingestion normalized_snapshot_id disagrees with snapshot")
    if str(ingestion["canonical_symbol"]).strip().upper() != "XAUUSD":
        raise MT5SnapshotLoadError("ingestion is not canonical XAUUSD")
    if str(ingestion["broker_name"]).strip() != snapshot.source_name:
        raise MT5SnapshotLoadError("ingestion broker_name disagrees with snapshot source_name")
    if str(ingestion["broker_symbol"]).strip() != snapshot.source_symbol:
        raise MT5SnapshotLoadError("ingestion broker_symbol disagrees with snapshot source_symbol")
    if _positive_int(ingestion["timeframe_seconds"], field="ingestion.timeframe_seconds") != snapshot.timeframe_seconds:
        raise MT5SnapshotLoadError("ingestion timeframe disagrees with snapshot timeframe")
    if _positive_int(ingestion["bar_count"], field="ingestion.bar_count") != snapshot.bar_count:
        raise MT5SnapshotLoadError("ingestion bar_count disagrees with snapshot")
    if _positive_int(ingestion["source_size_bytes"], field="ingestion.source_size_bytes") != len(raw_source_bytes):
        raise MT5SnapshotLoadError("persisted raw source byte size disagrees with ingestion manifest")
    if _aware_datetime(ingestion["first_timestamp_utc"], field="ingestion.first_timestamp_utc") != snapshot.first_timestamp:
        raise MT5SnapshotLoadError("ingestion first timestamp disagrees with snapshot")
    if _aware_datetime(ingestion["last_timestamp_utc"], field="ingestion.last_timestamp_utc") != snapshot.last_timestamp:
        raise MT5SnapshotLoadError("ingestion last timestamp disagrees with snapshot")
    if str(ingestion["schema_version"]).strip() != "mt5_history_adapter_v1":
        raise MT5SnapshotLoadError("unsupported MT5 history adapter schema_version")

    _nonnegative_int(ingestion["gap_count"], field="ingestion.gap_count")
    if not isinstance(ingestion["detected_headers"], list):
        raise MT5SnapshotLoadError("ingestion.detected_headers must be an array")
    if not isinstance(ingestion["gap_durations_seconds"], list):
        raise MT5SnapshotLoadError("ingestion.gap_durations_seconds must be an array")
    if not isinstance(ingestion["optional_columns"], list):
        raise MT5SnapshotLoadError("ingestion.optional_columns must be an array")
    if len(ingestion["gap_durations_seconds"]) != ingestion["gap_count"]:
        raise MT5SnapshotLoadError("ingestion gap_count disagrees with gap durations")
    for index, duration in enumerate(ingestion["gap_durations_seconds"]):
        _positive_int(duration, field=f"ingestion.gap_durations_seconds[{index}]")

    try:
        _, reloaded_snapshot, reloaded_validation = load_xauusd_csv_snapshot_bytes(
            canonical_bytes,
            source_name=snapshot.source_name,
            source_symbol=snapshot.source_symbol,
            timeframe_seconds=snapshot.timeframe_seconds,
            evaluation_time=snapshot.coverage_end,
            source_file_name=snapshot.source_file_name,
        )
    except (OSError, ValueError) as exc:
        raise MT5SnapshotLoadError("canonical persisted snapshot failed deterministic reload") from exc

    if reloaded_snapshot != snapshot:
        raise MT5SnapshotLoadError("canonical snapshot bytes do not reproduce persisted snapshot metadata")
    if _jsonable(asdict(reloaded_validation)) != validation_json:
        raise MT5SnapshotLoadError("canonical snapshot bytes do not reproduce persisted validation report")

    return VerifiedPersistedMT5Snapshot(
        manifest_path=path,
        store_root=store_root,
        raw_source_path=raw_source_path,
        canonical_snapshot_path=canonical_snapshot_path,
        source_sha256=source_sha,
        normalized_sha256=normalized_sha,
        snapshot=snapshot,
        validation=reloaded_validation,
    )
