from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Sequence

from .data_snapshot import load_xauusd_csv_snapshot_bytes
from .mt5_snapshot_load import MT5SnapshotLoadError, load_verified_persisted_mt5_snapshot
from .source_fidelity_replay import (
    SourceFidelityReplayError,
    evaluate_source_fidelity_fixture,
    load_source_fidelity_fixture,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-source-fidelity-replay",
        description=(
            "Replay source-labelled ordered price anchors and optional contiguous expansion evidence "
            "against one verified immutable MT5 snapshot. This proves source-to-data fidelity only; "
            "it does not certify strategy semantics or performance."
        ),
    )
    parser.add_argument("ingestion_manifest", type=Path)
    parser.add_argument("fixture", type=Path)
    return parser


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
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
        fixture = load_source_fidelity_fixture(args.fixture)
        if fixture.timeframe_seconds != verified.snapshot.timeframe_seconds:
            raise SourceFidelityReplayError(
                "fixture timeframe does not match the verified persisted MT5 snapshot"
            )

        bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
            verified.canonical_snapshot_path.read_bytes(),
            source_name=verified.snapshot.source_name,
            source_symbol=verified.snapshot.source_symbol,
            timeframe_seconds=verified.snapshot.timeframe_seconds,
            evaluation_time=verified.snapshot.coverage_end,
            source_file_name=verified.snapshot.source_file_name,
        )
        if reproduced != verified.snapshot:
            raise SourceFidelityReplayError(
                "verified snapshot metadata changed when canonical bytes were reproduced"
            )

        result = evaluate_source_fidelity_fixture(
            bars=bars,
            fixture=fixture,
            timeframe_seconds=verified.snapshot.timeframe_seconds,
        )
        passed = result.all_anchors_matched and result.expansion_probe_matched
        payload = {
            "schema_version": "source_fidelity_replay_report_v1",
            "status": "SOURCE_FIDELITY_REPLAY_PASS" if passed else "SOURCE_FIDELITY_REPLAY_INCOMPLETE",
            "episode_id": result.episode_id,
            "source_locator": result.source_locator,
            "snapshot_id": verified.snapshot.snapshot_id,
            "normalized_sha256": verified.normalized_sha256,
            "broker_name": verified.snapshot.source_name,
            "broker_symbol": verified.snapshot.source_symbol,
            "timeframe_seconds": result.timeframe_seconds,
            "window_start": result.window_start,
            "window_end": result.window_end,
            "anchor_count": len(result.anchor_matches),
            "matched_anchor_count": sum(1 for item in result.anchor_matches if item.matched),
            "all_anchors_matched": result.all_anchors_matched,
            "anchors": [asdict(item) for item in result.anchor_matches],
            "expansion_probe": asdict(result.expansion_match) if result.expansion_match is not None else None,
            "expansion_probe_matched": result.expansion_probe_matched,
            "expansion_finishes_before_first_anchor": result.expansion_finishes_before_first_anchor,
            "semantic_stage_certification": False,
            "performance_claim_allowed": False,
            "promotion_allowed": False,
            "strategy_truth_changed": False,
            "live_execution_authorized": False,
            "reference_feed_alignment_complete": False,
            "reference_feed_required": "FOREXCOM:XAUUSD",
        }
        print(json.dumps(_jsonable(payload), sort_keys=True, indent=2))
        return 0 if passed else 1
    except (SourceFidelityReplayError, MT5SnapshotLoadError, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
