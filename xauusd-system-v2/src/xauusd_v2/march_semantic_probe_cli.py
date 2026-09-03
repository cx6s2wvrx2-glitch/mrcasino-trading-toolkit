from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .march_semantic_probe import MarchSemanticProbeError, build_march_semantic_probe_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-march-semantic-probe",
        description=(
            "Probe the verified March 2023 M1 snapshot at explicitly source-labelled FU/HCS price levels. "
            "No source occurrence time is inferred, no nearest-bar substitution or price tolerance is used, "
            "and no FU/HCS, strategy, performance, promotion or live-execution certification is produced."
        ),
    )
    parser.add_argument("ingestion_manifest", type=Path, help="verified persisted broker MT5 ingestion manifest")
    parser.add_argument(
        "--probe-fixture",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "06_examples" / "MARCH_SOURCE_SEMANTIC_PROBES.json",
        help="governed source-labelled March FU/HCS probe fixture",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = build_march_semantic_probe_report(
            args.ingestion_manifest,
            probe_fixture=args.probe_fixture,
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (MarchSemanticProbeError, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
