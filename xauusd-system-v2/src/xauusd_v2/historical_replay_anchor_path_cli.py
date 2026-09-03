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
)
from .replay_anchor_path import (
    ReplayAnchorPathError,
    measure_anchor_path,
    parse_aware_timestamp,
    select_anchor,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-replay-anchor-path",
        description=(
            "Measure neutral M1 path facts around one primary-source price anchor inside a "
            "verified replay slice. This does not decide respect, break, entry, TFS or strategy truth."
        ),
    )
    parser.add_argument("replay_manifest", type=Path)
    parser.add_argument("source_anchors", type=Path)
    parser.add_argument("--anchor-id", required=True)
    parser.add_argument("--start-utc", required=True)
    parser.add_argument("--end-utc", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        replay = load_verified_replay_slice(args.replay_manifest)
        episode_id, source_locator, anchors = load_source_price_anchors(args.source_anchors)
        if episode_id != replay.episode_id or source_locator != replay.source_locator:
            raise ReplayAnchorPathError("source anchor provenance does not match replay slice")
        anchor = select_anchor(anchors, args.anchor_id)
        facts = measure_anchor_path(
            replay,
            anchor,
            start_utc=parse_aware_timestamp(args.start_utc, field="start_utc"),
            end_utc=parse_aware_timestamp(args.end_utc, field="end_utc"),
        )
        payload = {
            "schema_version": "historical_replay_anchor_path_v1",
            "status": "REPLAY_ANCHOR_PATH_MEASURED",
            "episode_id": replay.episode_id,
            "source_locator": replay.source_locator,
            "slice_sha256": replay.slice_sha256,
            "window_semantics": "engineering_inspection_start_inclusive_end_exclusive",
            "source_capture_time_certified": False,
            "interpretation_authority": False,
            "strategy_truth_changed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
            "facts": asdict(facts),
        }
        print(json.dumps(payload, sort_keys=True))
        return 0
    except (ReplayAlignmentError, ReplayAnchorPathError, OSError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
