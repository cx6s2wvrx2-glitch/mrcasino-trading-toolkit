from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .mt5_history import MT5HistoryError, load_mt5_xauusd_history_bytes
from .mt5_snapshot_store import MT5SnapshotStoreError, persist_mt5_ingestion


def _aware_datetime(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("evaluation time must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError("evaluation time must be timezone-aware")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-ingest-mt5",
        description=(
            "Validate one MT5 XAUUSD history export and optionally persist an immutable snapshot."
        ),
    )
    parser.add_argument("source", type=Path, help="MT5 UTF-8 CSV/TSV export")
    parser.add_argument("--broker-name", required=True)
    parser.add_argument("--broker-symbol", required=True)
    parser.add_argument(
        "--source-timezone",
        required=True,
        help="Explicit MT5 export timezone; never inferred (UTC, offset, or IANA zone)",
    )
    parser.add_argument("--timeframe-seconds", required=True, type=int)
    parser.add_argument("--evaluation-time", required=True, type=_aware_datetime)
    parser.add_argument(
        "--store-root",
        type=Path,
        help="Immutable snapshot store root. Required unless --dry-run is used.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and fingerprint the export without persisting any files.",
    )
    return parser


def _base_payload(result) -> dict[str, object]:
    return {
        "canonical_symbol": "XAUUSD",
        "broker_name": result.ingestion.broker_name,
        "broker_symbol": result.ingestion.broker_symbol,
        "timeframe_seconds": result.ingestion.timeframe_seconds,
        "source_timezone": result.ingestion.source_timezone,
        "source_sha256": result.ingestion.source_sha256,
        "source_size_bytes": result.ingestion.source_size_bytes,
        "snapshot_id": result.snapshot.snapshot_id,
        "normalized_sha256": result.ingestion.normalized_sha256,
        "bar_count": result.ingestion.bar_count,
        "first_timestamp_utc": result.ingestion.first_timestamp_utc.isoformat(),
        "last_timestamp_utc": result.ingestion.last_timestamp_utc.isoformat(),
        "closed_only": result.snapshot.closed_only,
        "gap_count": result.ingestion.gap_count,
        "gap_durations_seconds": list(result.ingestion.gap_durations_seconds),
        "detected_delimiter": result.ingestion.detected_delimiter,
        "optional_columns": list(result.ingestion.optional_columns),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.dry_run and args.store_root is None:
        print(
            json.dumps(
                {"status": "BLOCKED", "error": "--store-root is required unless --dry-run is used"},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    try:
        raw = args.source.read_bytes()
        result = load_mt5_xauusd_history_bytes(
            raw,
            broker_name=args.broker_name,
            broker_symbol=args.broker_symbol,
            source_timezone=args.source_timezone,
            timeframe_seconds=args.timeframe_seconds,
            evaluation_time=args.evaluation_time,
            source_file_name=args.source.name,
        )
        if args.dry_run:
            persisted = None
        else:
            persisted = persist_mt5_ingestion(
                raw_source_bytes=raw,
                result=result,
                store_root=args.store_root,
            )
    except (OSError, MT5HistoryError, MT5SnapshotStoreError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    payload = _base_payload(result)
    if args.dry_run:
        payload["status"] = "VALIDATED_NOT_PERSISTED"
        payload["persisted"] = False
    else:
        assert persisted is not None
        payload.update(
            {
                "status": "PERSISTED",
                "persisted": True,
                "source_sha256": persisted.source_sha256,
                "normalized_sha256": persisted.normalized_sha256,
                "raw_source_path": str(persisted.raw_source_path),
                "canonical_snapshot_path": str(persisted.canonical_snapshot_path),
                "ingestion_manifest_path": str(persisted.ingestion_manifest_path),
            }
        )
    print(json.dumps(payload, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
