from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .mt5_snapshot_load import VerifiedPersistedMT5Snapshot


class ReplaySliceError(ValueError):
    pass


_EPISODE_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_REQUIRED_COLUMNS = {"timestamp", "open", "high", "low", "close"}


@dataclass(frozen=True, slots=True)
class ReplaySliceResult:
    episode_id: str
    source_locator: str
    start_utc: datetime
    end_utc: datetime
    bar_count: int
    first_timestamp_utc: datetime
    last_timestamp_utc: datetime
    gap_count: int
    max_gap_seconds: int
    low_min: Decimal
    high_max: Decimal
    slice_sha256: str
    csv_path: Path
    manifest_path: Path


def parse_aware_timestamp(value: str, *, field: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ReplaySliceError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ReplaySliceError(f"{field} must be timezone-aware")
    return parsed.astimezone(UTC)


def _decimal(value: str, *, field: str) -> Decimal:
    try:
        return Decimal(value.strip())
    except (InvalidOperation, AttributeError) as exc:
        raise ReplaySliceError(f"invalid decimal in {field}") from exc


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _publish_bytes_idempotent(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise ReplaySliceError(f"existing replay artifact differs: {path}")
        return
    path.write_bytes(data)


def build_replay_slice(
    verified: VerifiedPersistedMT5Snapshot,
    *,
    episode_id: str,
    source_locator: str,
    start_utc: datetime,
    end_utc: datetime,
    output_root: Path | None = None,
) -> ReplaySliceResult:
    episode = episode_id.strip()
    locator = source_locator.strip()
    if not episode or not _EPISODE_ID_RE.fullmatch(episode):
        raise ReplaySliceError("episode_id may contain only letters, numbers, dot, underscore and hyphen")
    if not locator:
        raise ReplaySliceError("source_locator is required")
    if start_utc.tzinfo is None or start_utc.utcoffset() is None:
        raise ReplaySliceError("start_utc must be timezone-aware")
    if end_utc.tzinfo is None or end_utc.utcoffset() is None:
        raise ReplaySliceError("end_utc must be timezone-aware")
    start = start_utc.astimezone(UTC)
    end = end_utc.astimezone(UTC)
    if start >= end:
        raise ReplaySliceError("replay slice requires start_utc < end_utc")
    if verified.snapshot.timeframe_seconds != 60:
        raise ReplaySliceError("historical replay market slicing requires the verified M1 snapshot")
    if not verified.snapshot.closed_only:
        raise ReplaySliceError("historical replay slicing requires a closed-only immutable source snapshot")
    if end <= verified.snapshot.first_timestamp or start >= verified.snapshot.coverage_end:
        raise ReplaySliceError("requested replay window is outside the immutable snapshot coverage")

    root = (
        output_root.expanduser().resolve()
        if output_root is not None
        else (verified.store_root / "replay-slices").resolve()
    )
    temp_dir = root / ".tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    temp = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        prefix=f".{episode}.",
        suffix=".csv.tmp",
        dir=temp_dir,
        delete=False,
    )
    temp_path = Path(temp.name)

    bar_count = 0
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None
    previous_timestamp: datetime | None = None
    gap_count = 0
    max_gap_seconds = 0
    low_min: Decimal | None = None
    high_max: Decimal | None = None

    try:
        writer = csv.writer(temp, lineterminator="\n")
        writer.writerow(("timestamp", "open", "high", "low", "close"))
        with verified.canonical_snapshot_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(_REQUIRED_COLUMNS - set(reader.fieldnames or ()))
            if missing:
                raise ReplaySliceError(
                    f"canonical M1 snapshot missing fields: {', '.join(missing)}"
                )
            for row_no, row in enumerate(reader, start=2):
                timestamp = parse_aware_timestamp(row["timestamp"], field=f"row {row_no} timestamp")
                if timestamp < start:
                    continue
                if timestamp >= end:
                    break

                open_text = row["open"].strip()
                high_text = row["high"].strip()
                low_text = row["low"].strip()
                close_text = row["close"].strip()
                high_value = _decimal(high_text, field=f"row {row_no} high")
                low_value = _decimal(low_text, field=f"row {row_no} low")

                writer.writerow((
                    timestamp.isoformat().replace("+00:00", "Z"),
                    open_text,
                    high_text,
                    low_text,
                    close_text,
                ))
                bar_count += 1
                if first_timestamp is None:
                    first_timestamp = timestamp
                last_timestamp = timestamp
                low_min = low_value if low_min is None else min(low_min, low_value)
                high_max = high_value if high_max is None else max(high_max, high_value)

                if previous_timestamp is not None:
                    delta_seconds = int((timestamp - previous_timestamp).total_seconds())
                    if delta_seconds > 60:
                        gap_count += 1
                        max_gap_seconds = max(max_gap_seconds, delta_seconds - 60)
                previous_timestamp = timestamp
        temp.flush()
        os.fsync(temp.fileno())
        temp.close()

        if bar_count == 0 or first_timestamp is None or last_timestamp is None:
            raise ReplaySliceError("requested replay window contains no M1 bars")
        if low_min is None or high_max is None:
            raise ReplaySliceError("replay slice price range could not be computed")

        slice_sha = _sha256_file(temp_path)
        final_root = root / verified.normalized_sha256 / episode / slice_sha
        final_root.mkdir(parents=True, exist_ok=True)
        csv_path = final_root / "m1.csv"
        manifest_path = final_root / "manifest.json"

        if csv_path.exists():
            if _sha256_file(csv_path) != slice_sha:
                raise ReplaySliceError("existing replay slice hash mismatch")
            temp_path.unlink(missing_ok=True)
        else:
            os.replace(temp_path, csv_path)

        manifest = {
            "schema_version": "historical_replay_slice_v1",
            "status": "REPLAY_MARKET_SLICE_BUILT",
            "episode_id": episode,
            "source_locator": locator,
            "window_semantics": "start_inclusive_end_exclusive",
            "start_utc": start.isoformat().replace("+00:00", "Z"),
            "end_utc": end.isoformat().replace("+00:00", "Z"),
            "bar_count": bar_count,
            "first_timestamp_utc": first_timestamp.isoformat().replace("+00:00", "Z"),
            "last_timestamp_utc": last_timestamp.isoformat().replace("+00:00", "Z"),
            "gap_count": gap_count,
            "max_missing_gap_seconds": max_gap_seconds,
            "low_min": str(low_min),
            "high_max": str(high_max),
            "slice_sha256": slice_sha,
            "source_snapshot_sha256": verified.normalized_sha256,
            "source_snapshot_id": verified.snapshot.snapshot_id,
            "source_snapshot_bar_count": verified.snapshot.bar_count,
            "broker_name": verified.snapshot.source_name,
            "broker_symbol": verified.snapshot.source_symbol,
            "canonical_symbol": verified.snapshot.canonical_symbol,
            "source_timeframe_seconds": verified.snapshot.timeframe_seconds,
            "source_manifest_path": str(verified.manifest_path),
            "csv_path": str(csv_path),
            "strategy_truth_changed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
        }
        _publish_bytes_idempotent(manifest_path, _json_bytes(manifest))

        return ReplaySliceResult(
            episode_id=episode,
            source_locator=locator,
            start_utc=start,
            end_utc=end,
            bar_count=bar_count,
            first_timestamp_utc=first_timestamp,
            last_timestamp_utc=last_timestamp,
            gap_count=gap_count,
            max_gap_seconds=max_gap_seconds,
            low_min=low_min,
            high_max=high_max,
            slice_sha256=slice_sha,
            csv_path=csv_path,
            manifest_path=manifest_path,
        )
    finally:
        try:
            temp.close()
        except Exception:
            pass
        temp_path.unlink(missing_ok=True)
