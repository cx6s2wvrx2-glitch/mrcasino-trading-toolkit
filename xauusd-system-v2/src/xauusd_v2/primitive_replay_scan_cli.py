from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Sequence

from .data_snapshot import load_xauusd_csv_snapshot_bytes
from .mt5_snapshot_load import MT5SnapshotLoadError, load_verified_persisted_mt5_snapshot
from .primitive_replay_scan import PrimitiveReplayScanError, scan_primitive_replay_window


def _parse_time(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError("timestamp must be timezone-aware")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-primitive-scan",
        description=(
            "Scan a finite window of one verified immutable MT5 snapshot for raw basic-FU candidates, "
            "swept-side wick interactions, and source-style HCS candidates. All outputs remain NOT CERTIFIED."
        ),
    )
    parser.add_argument("ingestion_manifest", type=Path)
    parser.add_argument("--start", required=True, type=_parse_time)
    parser.add_argument("--end", required=True, type=_parse_time)
    parser.add_argument("--max-window-bars", type=int, default=20_000)
    parser.add_argument(
        "--candidate-only",
        action="store_true",
        help="omit non-HCS wick interactions from JSON output; scan logic itself is unchanged",
    )
    return parser


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        verified = load_verified_persisted_mt5_snapshot(args.ingestion_manifest)
        bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
            verified.canonical_snapshot_path.read_bytes(),
            source_name=verified.snapshot.source_name,
            source_symbol=verified.snapshot.source_symbol,
            timeframe_seconds=verified.snapshot.timeframe_seconds,
            evaluation_time=verified.snapshot.coverage_end,
            source_file_name=verified.snapshot.source_file_name,
        )
        if reproduced != verified.snapshot:
            raise PrimitiveReplayScanError("verified snapshot changed when canonical bytes were reproduced")

        result = scan_primitive_replay_window(
            bars=bars,
            timeframe_seconds=verified.snapshot.timeframe_seconds,
            scan_start=args.start,
            scan_end=args.end,
            max_window_bars=args.max_window_bars,
        )
        interactions = (
            tuple(item for item in result.wick_interactions if item.source_style_hcs_candidate)
            if args.candidate_only
            else result.wick_interactions
        )
        payload = {
            "schema_version": "primitive_replay_scan_report_v1",
            "status": "PRIMITIVE_REPLAY_SCAN_COMPLETE_NOT_CERTIFIED",
            "snapshot_id": verified.snapshot.snapshot_id,
            "normalized_sha256": verified.normalized_sha256,
            "broker_name": verified.snapshot.source_name,
            "broker_symbol": verified.snapshot.source_symbol,
            "timeframe_seconds": result.timeframe_seconds,
            "scan_start": result.scan_start,
            "scan_end": result.scan_end,
            "bar_count": result.bar_count,
            "basic_fu_candidate_count": len(result.fu_candidates),
            "ambiguous_basic_fu_bar_count": result.ambiguous_basic_fu_bars,
            "adjacency_gap_pairs_skipped": result.adjacency_gap_pairs_skipped,
            "wick_interaction_count_total": len(result.wick_interactions),
            "source_style_hcs_candidate_count": result.source_style_hcs_candidates,
            "candidate_only_output": bool(args.candidate_only),
            "fu_candidates": [asdict(item) for item in result.fu_candidates],
            "wick_interactions": [asdict(item) for item in interactions],
            "certified_fu_count": 0,
            "certified_hcs_count": 0,
            "blockers_preserved": ["B-01", "B-02", "B-03", "B-05"],
            "strategy_truth_changed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
        }
        print(json.dumps(_jsonable(payload), sort_keys=True, indent=2))
        return 0
    except (PrimitiveReplayScanError, MT5SnapshotLoadError, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
