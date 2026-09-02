from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .mt5_snapshot_load import MT5SnapshotLoadError, load_verified_persisted_mt5_snapshot
from .replay_candidate_readiness import evaluate_replay_candidate_readiness
from .replay_candidate_registry import replay_candidates_by_id
from .source_chart_alignment import SourceChartAlignmentRequest, align_source_chart_to_snapshot


def _aware_datetime(value: str) -> datetime:
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
        prog="xauusd-v2-replay-readiness",
        description=(
            "Verify one persisted MT5 snapshot and evaluate one registered source episode "
            "for historical component replay. No source metadata is inferred."
        ),
    )
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--manifest", required=True, type=Path, help="Persisted MT5 ingestion manifest")
    parser.add_argument("--broker-name", required=True, help="Explicit broker identity shown by source provenance")
    parser.add_argument("--source-symbol", required=True, help="Explicit broker symbol shown by source provenance")
    parser.add_argument("--timeframe-seconds", required=True, type=int, help="Explicit source-chart timeframe")
    parser.add_argument("--window-start", required=True, type=_aware_datetime)
    parser.add_argument("--window-end", required=True, type=_aware_datetime)
    parser.add_argument(
        "--stage-timestamps-certified",
        action="store_true",
        help=(
            "Assert only when each required R-143 stage has independently certified "
            "occurred_at/available_at timestamps. Omit to fail closed."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    candidate_id = args.candidate_id.strip()
    candidates = replay_candidates_by_id()
    candidate = candidates.get(candidate_id)
    if candidate is None:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "error": "unknown replay candidate id",
                    "candidate_id": candidate_id,
                    "promotion_allowed": False,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    if args.timeframe_seconds <= 0:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "error": "timeframe_seconds must be positive",
                    "candidate_id": candidate_id,
                    "promotion_allowed": False,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2

    try:
        verified = load_verified_persisted_mt5_snapshot(args.manifest)
        alignment = align_source_chart_to_snapshot(
            request=SourceChartAlignmentRequest(
                source_id=candidate.source_id,
                source_locator=candidate.locator,
                broker_name=args.broker_name,
                source_symbol=args.source_symbol,
                timeframe_seconds=args.timeframe_seconds,
                window_start=args.window_start,
                window_end=args.window_end,
            ),
            snapshot=verified.snapshot,
        )
        readiness = evaluate_replay_candidate_readiness(
            candidate=candidate,
            alignment=alignment,
            stage_timestamps_certified=True if args.stage_timestamps_certified else None,
        )
    except (MT5SnapshotLoadError, OSError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "error": str(exc),
                    "candidate_id": candidate_id,
                    "promotion_allowed": False,
                },
                sort_keys=True,
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    payload = {
        "status": "EVALUATED",
        "candidate_id": candidate.candidate_id,
        "candidate_registry_state": candidate.state.value,
        "source_id": candidate.source_id,
        "source_locator": candidate.locator,
        "snapshot_id": verified.snapshot.snapshot_id,
        "snapshot_closed_only": verified.snapshot.closed_only,
        "source_sha256": verified.source_sha256,
        "normalized_sha256": verified.normalized_sha256,
        "alignment_state": alignment.state.value,
        "aligned": alignment.aligned,
        "alignment_reason": alignment.reason,
        "stage_timestamps_certified": bool(args.stage_timestamps_certified),
        "readiness_state": readiness.state.value,
        "replay_ready": readiness.replay_ready,
        "readiness_reason": readiness.reason,
        "promotion_allowed": False,
        "strategy_verified": False,
        "performance_claim_allowed": False,
    }
    print(json.dumps(payload, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
