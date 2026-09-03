from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from .replay_alignment import (
    ReplayAlignmentError,
    load_source_price_anchors,
    load_verified_replay_slice,
    probe_replay_anchors,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-replay-align",
        description=(
            "Measure source-labelled price anchors against one verified immutable historical replay slice. "
            "This is evidence alignment only; no detector certification or strategy promotion."
        ),
    )
    parser.add_argument("replay_manifest", type=Path)
    parser.add_argument("anchor_file", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        replay = load_verified_replay_slice(args.replay_manifest)
        episode_id, source_locator, anchors = load_source_price_anchors(args.anchor_file)
        if episode_id != replay.episode_id:
            raise ReplayAlignmentError("anchor episode_id does not match replay episode_id")
        if source_locator != replay.source_locator:
            raise ReplayAlignmentError("anchor source_locator does not match replay source_locator")
        results = probe_replay_anchors(replay, anchors)
        payload = {
            "schema_version": "historical_replay_source_alignment_v1",
            "status": "REPLAY_SOURCE_PRICE_ALIGNMENT_MEASURED",
            "episode_id": replay.episode_id,
            "source_locator": replay.source_locator,
            "slice_sha256": replay.slice_sha256,
            "bar_count": replay.bar_count,
            "slice_low_min": str(replay.low_min),
            "slice_high_max": str(replay.high_max),
            "anchor_count": len(results),
            "all_anchors_within_slice_price_range": all(item.within_slice_price_range for item in results),
            "all_anchors_touched": all(item.touched for item in results),
            "anchors": [asdict(item) for item in results],
            "strategy_truth_changed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
            "reference_feed_alignment_complete": False,
            "reference_feed_required": "FOREXCOM:XAUUSD",
        }
        print(json.dumps(payload, sort_keys=True, indent=2))
        return 0
    except ReplayAlignmentError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
