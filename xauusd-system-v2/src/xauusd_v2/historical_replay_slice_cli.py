from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .mt5_snapshot_load import MT5SnapshotLoadError, load_verified_persisted_mt5_snapshot
from .replay_slice import ReplaySliceError, build_replay_slice, parse_aware_timestamp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-replay-slice",
        description=(
            "Build a content-addressed closed-M1 market slice for one historical source episode. "
            "This is replay evidence preparation only; it does not certify strategy rules."
        ),
    )
    parser.add_argument("ingestion_manifest", type=Path)
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--source-locator", required=True)
    parser.add_argument("--start-utc", required=True)
    parser.add_argument("--end-utc", required=True)
    parser.add_argument("--output-root", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        verified = load_verified_persisted_mt5_snapshot(args.ingestion_manifest)
        start = parse_aware_timestamp(args.start_utc, field="start_utc")
        end = parse_aware_timestamp(args.end_utc, field="end_utc")
        result = build_replay_slice(
            verified,
            episode_id=args.episode_id,
            source_locator=args.source_locator,
            start_utc=start,
            end_utc=end,
            output_root=args.output_root,
        )
        payload = {
            "status": "REPLAY_MARKET_SLICE_BUILT",
            "episode_id": result.episode_id,
            "source_locator": result.source_locator,
            "start_utc": result.start_utc.isoformat().replace("+00:00", "Z"),
            "end_utc": result.end_utc.isoformat().replace("+00:00", "Z"),
            "bar_count": result.bar_count,
            "first_timestamp_utc": result.first_timestamp_utc.isoformat().replace("+00:00", "Z"),
            "last_timestamp_utc": result.last_timestamp_utc.isoformat().replace("+00:00", "Z"),
            "gap_count": result.gap_count,
            "max_missing_gap_seconds": result.max_gap_seconds,
            "low_min": str(result.low_min),
            "high_max": str(result.high_max),
            "slice_sha256": result.slice_sha256,
            "csv_path": str(result.csv_path),
            "manifest_path": str(result.manifest_path),
            "strategy_truth_changed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
        }
        print(json.dumps(payload, sort_keys=True))
        return 0
    except (MT5SnapshotLoadError, ReplaySliceError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
