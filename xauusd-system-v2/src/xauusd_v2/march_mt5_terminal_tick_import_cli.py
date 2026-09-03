from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .march_mt5_terminal_tick_import import (
    MarchMT5TerminalTickImportError,
    import_march_mt5_terminal_tick_export,
)
from .mt5_snapshot_load import MT5SnapshotLoadError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-march-mt5-terminal-tick-import",
        description=(
            "Validate and immutably persist the governed MT5-terminal March HCS tick export. "
            "This is research evidence only and cannot certify FU/HCS, performance, promotion, or live execution."
        ),
    )
    parser.add_argument("ingestion_manifest", type=Path)
    parser.add_argument("terminal_export", type=Path)
    parser.add_argument("--store-root", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = import_march_mt5_terminal_tick_export(
            args.ingestion_manifest,
            args.terminal_export,
            store_root=args.store_root,
        )
    except (OSError, ValueError, MarchMT5TerminalTickImportError, MT5SnapshotLoadError) as exc:
        print(
            json.dumps(
                {
                    "status": "MT5_TERMINAL_TICK_IMPORT_BLOCKED_NOT_CERTIFIED",
                    "error": str(exc),
                    "fu_criteria_certified": False,
                    "semantic_stage_certification": False,
                    "strategy_truth_changed": False,
                    "performance_claim_allowed": False,
                    "promotion_allowed": False,
                    "live_execution_authorized": False,
                },
                sort_keys=True,
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    print(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
