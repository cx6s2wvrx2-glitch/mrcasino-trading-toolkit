from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .march_reference_feed import MarchReferenceFeedError, build_march_reference_feed_comparison


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-march-reference-feed",
        description=(
            "Compare a bounded FOREXCOM:XAUUSD M1 reference export against the verified broker snapshot for "
            "the governed March 30-31 2023 source episodes. Exact timestamps only: no nearest-bar substitution, "
            "no price tolerance, no strategy certification, performance claim, promotion or live execution."
        ),
    )
    parser.add_argument("reference_csv", type=Path, help="FOREXCOM:XAUUSD M1 CSV export")
    parser.add_argument("ingestion_manifest", type=Path, help="verified persisted broker MT5 ingestion manifest")
    parser.add_argument(
        "--reference-feed-id",
        required=True,
        choices=("FOREXCOM:XAUUSD",),
        help="explicit provenance acknowledgement for the supplied reference export",
    )
    parser.add_argument(
        "--examples-root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "06_examples",
        help="directory containing the governed March source-fidelity fixtures",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.reference_feed_id != "FOREXCOM:XAUUSD":
        parser.error("reference feed must be FOREXCOM:XAUUSD")
    try:
        result = build_march_reference_feed_comparison(
            args.reference_csv,
            args.ingestion_manifest,
            examples_root=args.examples_root,
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (MarchReferenceFeedError, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
