from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .march_replay_bundle import MarchReplayBundleError, build_march_replay_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-march-replay-bundle",
        description=(
            "Build the governed March 30-31 2023 source-fidelity research bundle from the already-verified "
            "immutable MT5 snapshot. The bundle measures raw correspondence only and never certifies strategy "
            "semantics, performance, promotion or live execution."
        ),
    )
    parser.add_argument("ingestion_manifest", type=Path)
    parser.add_argument(
        "--examples-root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "06_examples",
        help="directory containing the governed March source-fidelity and R-143 evidence fixtures",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = build_march_replay_bundle(
            args.ingestion_manifest,
            examples_root=args.examples_root,
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (MarchReplayBundleError, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
