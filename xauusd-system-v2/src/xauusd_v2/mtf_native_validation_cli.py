from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence

from .mt5_history import MT5HistoryError, load_mt5_xauusd_history
from .mt5_snapshot_load import MT5SnapshotLoadError, load_verified_persisted_mt5_snapshot
from .mtf_aggregation import MTFAggregationError, TimeframeSpec, parse_timeframe_codes


class NativeMTFValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CandidateOHLC:
    timestamp_utc: str
    open_value: Decimal
    high_value: Decimal
    low_value: Decimal
    close_value: Decimal


def _decimal(value: object, *, field: str) -> Decimal:
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise NativeMTFValidationError(f"invalid decimal field {field}") from exc
    if not parsed.is_finite():
        raise NativeMTFValidationError(f"non-finite decimal field {field}")
    return parsed


def _iso_utc(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_native_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("native sample must use TIMEFRAME=/path/to/export.csv")
    code, raw_path = value.split("=", 1)
    code = code.strip().upper()
    try:
        spec = parse_timeframe_codes(code)[0]
    except MTFAggregationError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    path = Path(raw_path.strip()).expanduser()
    if not raw_path.strip():
        raise argparse.ArgumentTypeError("native sample path cannot be empty")
    return spec.code, path


def _candidate_path(verified, spec: TimeframeSpec) -> Path:
    return (
        verified.store_root
        / "derived-candidates"
        / verified.normalized_sha256
        / f"{spec.code}.candidate.csv"
    ).resolve()


def _load_candidate_index(path: Path) -> dict[str, CandidateOHLC]:
    if not path.is_file():
        raise NativeMTFValidationError(f"derived candidate file is unavailable: {path}")
    index: dict[str, CandidateOHLC] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"timestamp_utc", "open", "high", "low", "close"}
        missing = sorted(required - set(reader.fieldnames or ()))
        if missing:
            raise NativeMTFValidationError(
                f"derived candidate file missing fields: {', '.join(missing)}"
            )
        for row_no, row in enumerate(reader, start=2):
            timestamp = str(row["timestamp_utc"]).strip()
            if not timestamp:
                raise NativeMTFValidationError(f"candidate row {row_no}: timestamp is required")
            if timestamp in index:
                raise NativeMTFValidationError(f"duplicate candidate timestamp: {timestamp}")
            index[timestamp] = CandidateOHLC(
                timestamp_utc=timestamp,
                open_value=_decimal(row["open"], field="candidate.open"),
                high_value=_decimal(row["high"], field="candidate.high"),
                low_value=_decimal(row["low"], field="candidate.low"),
                close_value=_decimal(row["close"], field="candidate.close"),
            )
    if not index:
        raise NativeMTFValidationError("derived candidate file contains no rows")
    return index


def _bars_within_source_horizon(*, bars, spec: TimeframeSpec, source_coverage_end: datetime):
    """Return native parent bars fully covered by the frozen M1 source snapshot."""
    interval = timedelta(seconds=spec.seconds)
    comparable = tuple(bar for bar in bars if bar.timestamp + interval <= source_coverage_end)
    ignored = len(bars) - len(comparable)
    return comparable, ignored


def _validate_one(*, verified, source_timezone: str, spec: TimeframeSpec, native_path: Path) -> dict[str, object]:
    candidate_path = _candidate_path(verified, spec)
    candidates = _load_candidate_index(candidate_path)

    # A native export may extend beyond the exact time at which the immutable M1
    # source snapshot was frozen and may include a currently-forming parent bar.
    # Parse the observation file in full, then let the M1 snapshot coverage horizon
    # decide which parent bars are actually comparable.
    native = load_mt5_xauusd_history(
        native_path,
        broker_name=verified.snapshot.source_name,
        broker_symbol=verified.snapshot.source_symbol,
        source_timezone=source_timezone,
        timeframe_seconds=spec.seconds,
        evaluation_time=datetime(2200, 1, 1, tzinfo=UTC),
    )

    comparable_bars, ignored_outside_horizon = _bars_within_source_horizon(
        bars=native.bars,
        spec=spec,
        source_coverage_end=verified.snapshot.coverage_end,
    )
    if not comparable_bars:
        raise NativeMTFValidationError(
            f"native {spec.code} export has no fully closed bars inside the frozen M1 source horizon"
        )

    exact_matches = 0
    missing_candidate: list[str] = []
    mismatches: list[dict[str, object]] = []

    for bar in comparable_bars:
        timestamp = _iso_utc(bar.timestamp)
        candidate = candidates.get(timestamp)
        if candidate is None:
            missing_candidate.append(timestamp)
            continue

        native_values = (
            _decimal(bar.open, field="native.open"),
            _decimal(bar.high, field="native.high"),
            _decimal(bar.low, field="native.low"),
            _decimal(bar.close, field="native.close"),
        )
        candidate_values = (
            candidate.open_value,
            candidate.high_value,
            candidate.low_value,
            candidate.close_value,
        )
        if native_values == candidate_values:
            exact_matches += 1
            continue

        if len(mismatches) < 20:
            mismatches.append(
                {
                    "timestamp_utc": timestamp,
                    "native": {
                        "open": str(native_values[0]),
                        "high": str(native_values[1]),
                        "low": str(native_values[2]),
                        "close": str(native_values[3]),
                    },
                    "derived": {
                        "open": str(candidate_values[0]),
                        "high": str(candidate_values[1]),
                        "low": str(candidate_values[2]),
                        "close": str(candidate_values[3]),
                    },
                }
            )

    comparable_count = len(comparable_bars)
    missing_count = len(missing_candidate)
    mismatch_count = comparable_count - exact_matches - missing_count
    passed = comparable_count > 0 and missing_count == 0 and mismatch_count == 0

    return {
        "timeframe": spec.code,
        "timeframe_seconds": spec.seconds,
        "native_file": str(native_path.resolve()),
        "native_source_sha256": native.ingestion.source_sha256,
        "native_export_bar_count": len(native.bars),
        "native_comparable_bar_count": comparable_count,
        "native_outside_source_horizon_ignored_count": ignored_outside_horizon,
        "native_first_timestamp_utc": native.ingestion.first_timestamp_utc.isoformat(),
        "native_last_timestamp_utc": native.ingestion.last_timestamp_utc.isoformat(),
        "native_gap_count": native.ingestion.gap_count,
        "candidate_file": str(candidate_path),
        "candidate_bar_count": len(candidates),
        "exact_ohlc_match_count": exact_matches,
        "missing_candidate_timestamp_count": missing_count,
        "ohlc_mismatch_count": mismatch_count,
        "missing_candidate_timestamps_sample": missing_candidate[:20],
        "ohlc_mismatches_sample": mismatches,
        "comparison_horizon_utc": verified.snapshot.coverage_end.isoformat(),
        "representative_native_sample_passed": passed,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-validate-native-mtf",
        description=(
            "Compare native MT5 higher-timeframe exports against deterministic M1-derived "
            "candidate candles from one verified immutable snapshot."
        ),
    )
    parser.add_argument("ingestion_manifest", type=Path)
    parser.add_argument(
        "--native",
        action="append",
        required=True,
        type=_parse_native_arg,
        metavar="TF=PATH",
        help="Native MT5 sample, e.g. H4=/path/XAUUSD_H4.csv; repeat for multiple TFs",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        verified = load_verified_persisted_mt5_snapshot(args.ingestion_manifest)
        if verified.snapshot.timeframe_seconds != 60:
            raise NativeMTFValidationError("native MTF validation requires a verified M1 source snapshot")

        raw_manifest = json.loads(verified.manifest_path.read_text(encoding="utf-8"))
        source_timezone = str(raw_manifest["ingestion"]["source_timezone"]).strip()
        if not source_timezone:
            raise NativeMTFValidationError("source timezone is missing from ingestion provenance")

        seen: set[str] = set()
        results: list[dict[str, object]] = []
        for code, native_path in args.native:
            if code in seen:
                raise NativeMTFValidationError(f"duplicate native timeframe argument: {code}")
            seen.add(code)
            spec = parse_timeframe_codes(code)[0]
            results.append(
                _validate_one(
                    verified=verified,
                    source_timezone=source_timezone,
                    spec=spec,
                    native_path=native_path,
                )
            )

        all_passed = all(bool(item["representative_native_sample_passed"]) for item in results)
        payload = {
            "status": "NATIVE_MTF_SAMPLE_VALIDATION_PASS" if all_passed else "NATIVE_MTF_SAMPLE_VALIDATION_FAIL",
            "source_snapshot_id": verified.snapshot.snapshot_id,
            "source_normalized_sha256": verified.normalized_sha256,
            "broker_name": verified.snapshot.source_name,
            "broker_symbol": verified.snapshot.source_symbol,
            "source_timezone": source_timezone,
            "comparison_horizon_utc": verified.snapshot.coverage_end.isoformat(),
            "validated_timeframes": [item["timeframe"] for item in results],
            "all_representative_samples_passed": all_passed,
            "results": results,
            "strategy_truth_changed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
            "eleven_hour_synthesis_allowed": False,
        }
        print(json.dumps(payload, sort_keys=True, ensure_ascii=False))
        return 0 if all_passed else 3

    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        MT5HistoryError,
        MT5SnapshotLoadError,
        MTFAggregationError,
        NativeMTFValidationError,
    ) as exc:
        print(
            json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False),
            file=__import__("sys").stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
