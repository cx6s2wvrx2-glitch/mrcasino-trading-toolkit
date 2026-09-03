from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .march_hcs_second_node_probe import MarchHCSSecondNodeProbeError, build_march_hcs_second_node_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-march-hcs-second-node",
        description=(
            "Inspect source-labelled March HCS level touches for second-node evidence beyond the narrow basic-FU proxy. "
            "The report is diagnostic only and never certifies FU, HCS, strategy truth, performance, promotion or live execution."
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
        result = build_march_hcs_second_node_report(
            args.ingestion_manifest,
            probe_fixture=args.probe_fixture,
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (MarchHCSSecondNodeProbeError, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
