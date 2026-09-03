from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .mt5_snapshot_load import MT5SnapshotLoadError, load_verified_persisted_mt5_snapshot
from .mtf_aggregation import (
    MTFAggregationError,
    MinuteOHLC,
    TimeframeAggregator,
    load_broker_timezone,
    parse_timeframe_codes,
)


_CSV_HEADER = (
    "timestamp_utc",
    "broker_open_time",
    "bucket_end_utc",
    "open",
    "high",
    "low",
    "close",
    "child_count",
    "expected_slots",
    "leading_missing_minutes",
    "internal_missing_minutes",
    "trailing_missing_minutes",
    "first_child_timestamp_utc",
    "last_child_timestamp_utc",
)


@dataclass(slots=True)
class _OutputState:
    code: str
    timeframe_seconds: int
    aggregator: TimeframeAggregator
    temp_path: Path
    handle: object
    writer: csv.writer
    bar_count: int = 0
    gap_affected_bar_count: int = 0
    internal_gap_bar_count: int = 0
    leading_missing_minutes: int = 0
    internal_missing_minutes: int = 0
    trailing_missing_minutes: int = 0
    first_timestamp_utc: str | None = None
    last_timestamp_utc: str | None = None


def _parse_timestamp(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MTFAggregationError("canonical M1 timestamp must be timezone-aware")
    return parsed


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_candidate(state: _OutputState, candidate) -> None:
    state.writer.writerow(
        (
            _iso(candidate.timestamp_utc),
            candidate.broker_open_time.isoformat(),
            _iso(candidate.bucket_end_utc),
            candidate.open_text,
            candidate.high_text,
            candidate.low_text,
            candidate.close_text,
            candidate.child_count,
            candidate.expected_slots,
            candidate.leading_missing_minutes,
            candidate.internal_missing_minutes,
            candidate.trailing_missing_minutes,
            _iso(candidate.first_child_timestamp_utc),
            _iso(candidate.last_child_timestamp_utc),
        )
    )
    state.bar_count += 1
    if candidate.gap_affected:
        state.gap_affected_bar_count += 1
    if candidate.internal_missing_minutes:
        state.internal_gap_bar_count += 1
    state.leading_missing_minutes += candidate.leading_missing_minutes
    state.internal_missing_minutes += candidate.internal_missing_minutes
    state.trailing_missing_minutes += candidate.trailing_missing_minutes
    timestamp = _iso(candidate.timestamp_utc)
    if state.first_timestamp_utc is None:
        state.first_timestamp_utc = timestamp
    state.last_timestamp_utc = timestamp


def _publish_idempotent(temp_path: Path, final_path: Path) -> str:
    new_sha = _sha256_file(temp_path)
    if final_path.exists():
        existing_sha = _sha256_file(final_path)
        if existing_sha != new_sha:
            raise MTFAggregationError(
                f"existing candidate differs at {final_path}; refusing to overwrite"
            )
        temp_path.unlink()
        return existing_sha
    os.replace(temp_path, final_path)
    return new_sha


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-build-mtf",
        description=(
            "Build broker-local higher-timeframe OHLC candidates from one verified "
            "immutable M1 MT5 snapshot. No native-TF certification or strategy promotion."
        ),
    )
    parser.add_argument("ingestion_manifest", type=Path)
    parser.add_argument(
        "--timeframes",
        default="M5,M10,M15,M30,H1,H4,H8,D1",
        help="Comma-separated governed target timeframes",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        help="Candidate output root; defaults to <MT5 store>/derived-candidates",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    states: list[_OutputState] = []
    try:
        verified = load_verified_persisted_mt5_snapshot(args.ingestion_manifest)
        if verified.snapshot.timeframe_seconds != 60:
            raise MTFAggregationError("multi-timeframe derivation requires a verified M1 snapshot")

        raw_manifest = json.loads(verified.manifest_path.read_text(encoding="utf-8"))
        source_timezone = str(raw_manifest["ingestion"]["source_timezone"]).strip()
        broker_timezone = load_broker_timezone(source_timezone)
        timeframe_specs = parse_timeframe_codes(args.timeframes)

        output_root = (
            args.output_root.expanduser().resolve()
            if args.output_root is not None
            else (verified.store_root / "derived-candidates").resolve()
        )
        run_root = output_root / verified.normalized_sha256
        run_root.mkdir(parents=True, exist_ok=True)

        for spec in timeframe_specs:
            temp = tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                prefix=f".{spec.code}.",
                suffix=".tmp",
                dir=run_root,
                delete=False,
            )
            writer = csv.writer(temp, lineterminator="\n")
            writer.writerow(_CSV_HEADER)
            states.append(
                _OutputState(
                    code=spec.code,
                    timeframe_seconds=spec.seconds,
                    aggregator=TimeframeAggregator(
                        timeframe=spec,
                        broker_timezone=broker_timezone,
                        source_coverage_end_utc=verified.snapshot.coverage_end,
                    ),
                    temp_path=Path(temp.name),
                    handle=temp,
                    writer=writer,
                )
            )

        with verified.canonical_snapshot_path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as source_handle:
            reader = csv.DictReader(source_handle)
            required = {"timestamp", "open", "high", "low", "close"}
            missing = sorted(required - set(reader.fieldnames or ()))
            if missing:
                raise MTFAggregationError(
                    f"canonical M1 snapshot missing fields: {', '.join(missing)}"
                )
            source_rows = 0
            for row in reader:
                minute = MinuteOHLC(
                    timestamp_utc=_parse_timestamp(row["timestamp"]),
                    open_text=row["open"].strip(),
                    high_text=row["high"].strip(),
                    low_text=row["low"].strip(),
                    close_text=row["close"].strip(),
                )
                for state in states:
                    candidate = state.aggregator.add(minute)
                    if candidate is not None:
                        _write_candidate(state, candidate)
                source_rows += 1

        if source_rows != verified.snapshot.bar_count:
            raise MTFAggregationError(
                "streamed M1 row count disagrees with verified snapshot manifest"
            )

        for state in states:
            candidate = state.aggregator.finish()
            if candidate is not None:
                _write_candidate(state, candidate)

        for state in states:
            state.handle.flush()
            state.handle.close()

        results: list[dict[str, object]] = []
        for state in states:
            final_csv = run_root / f"{state.code}.candidate.csv"
            derived_sha = _publish_idempotent(state.temp_path, final_csv)
            manifest = {
                "schema_version": "mtf_derived_candidate_v1",
                "status": "DERIVED_CANDIDATE_NOT_NATIVE_CERTIFIED",
                "canonical_symbol": "XAUUSD",
                "broker_name": verified.snapshot.source_name,
                "broker_symbol": verified.snapshot.source_symbol,
                "source_timezone": source_timezone,
                "source_snapshot_id": verified.snapshot.snapshot_id,
                "source_normalized_sha256": verified.normalized_sha256,
                "source_m1_bar_count": verified.snapshot.bar_count,
                "source_coverage_end_utc": verified.snapshot.coverage_end.isoformat(),
                "timeframe_code": state.code,
                "timeframe_seconds": state.timeframe_seconds,
                "bar_count": state.bar_count,
                "first_timestamp_utc": state.first_timestamp_utc,
                "last_timestamp_utc": state.last_timestamp_utc,
                "gap_affected_bar_count": state.gap_affected_bar_count,
                "internal_gap_bar_count": state.internal_gap_bar_count,
                "leading_missing_minutes": state.leading_missing_minutes,
                "internal_missing_minutes": state.internal_missing_minutes,
                "trailing_missing_minutes": state.trailing_missing_minutes,
                "omitted_trailing_partial_buckets": state.aggregator.omitted_trailing_partial_buckets,
                "derived_csv_sha256": derived_sha,
                "derived_csv_path": str(final_csv),
                "missing_minutes_synthetically_filled": False,
                "native_mt5_boundary_validation_passed": False,
                "strategy_truth_authority": False,
                "promotion_allowed": False,
                "live_execution_authorized": False,
            }
            manifest_path = run_root / f"{state.code}.candidate.manifest.json"
            encoded = (
                json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
            ).encode("utf-8")
            if manifest_path.exists():
                if manifest_path.read_bytes() != encoded:
                    raise MTFAggregationError(
                        f"existing candidate manifest differs at {manifest_path}"
                    )
            else:
                manifest_path.write_bytes(encoded)
            results.append(
                {
                    "timeframe": state.code,
                    "bar_count": state.bar_count,
                    "gap_affected_bar_count": state.gap_affected_bar_count,
                    "internal_gap_bar_count": state.internal_gap_bar_count,
                    "omitted_trailing_partial_buckets": state.aggregator.omitted_trailing_partial_buckets,
                    "sha256": derived_sha,
                    "csv": str(final_csv),
                    "manifest": str(manifest_path),
                }
            )

        payload = {
            "status": "MTF_DERIVED_CANDIDATES_BUILT",
            "source_snapshot_id": verified.snapshot.snapshot_id,
            "source_normalized_sha256": verified.normalized_sha256,
            "source_m1_bar_count": verified.snapshot.bar_count,
            "source_timezone": source_timezone,
            "output_root": str(run_root),
            "timeframes": results,
            "native_mt5_boundary_validation_required": True,
            "eleven_hour_synthesis_allowed": False,
            "strategy_truth_changed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
        }
        print(json.dumps(payload, sort_keys=True, ensure_ascii=False))
        return 0

    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        MT5SnapshotLoadError,
        MTFAggregationError,
    ) as exc:
        for state in states:
            try:
                state.handle.close()
            except Exception:
                pass
            try:
                if state.temp_path.exists():
                    state.temp_path.unlink()
            except OSError:
                pass
        print(
            json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False),
            file=__import__("sys").stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
