from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .march_hcs_last_wick_probe import MarchHCSLastWickProbeError, build_march_hcs_last_wick_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-march-hcs-last-wick",
        description=(
            "Audit the March source-labelled HCS levels against a strict latest-prior-basic-FU-wick proxy. "
            "This is diagnostic only: no source occurrence timestamp is inferred, no near-enough tolerance is invented, "
            "and no HCS, strategy, performance, promotion or live-execution certification is produced."
        ),
    )
    parser.add_argument("ingestion_manifest", type=Path, help="verified persisted broker MT5 ingestion manifest")
    parser.add_argument(
        "--probe-fixture",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "06_examples" / "MARCH_SOURCE_SEMANTIC_PROBES.json",
        help="governed March source-labelled FU/HCS probe fixture",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = build_march_hcs_last_wick_report(
            args.ingestion_manifest,
            probe_fixture=args.probe_fixture,
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (MarchHCSLastWickProbeError, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
