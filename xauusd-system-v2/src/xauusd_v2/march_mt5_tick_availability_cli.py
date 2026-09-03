from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .march_mt5_tick_availability import (
    MarchMT5TickAvailabilityError,
    acquire_march_mt5_tick_availability,
    persist_march_mt5_tick_availability,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-march-mt5-tick-availability",
        description=(
            "Request two governed March-2023 MT5 tick windows from the broker terminal and persist "
            "available ticks immutably. This is availability/path evidence only, never FU/HCS certification."
        ),
    )
    parser.add_argument("ingestion_manifest", type=Path)
    parser.add_argument(
        "--store-root",
        required=True,
        type=Path,
        help="Existing XAUUSD MT5 immutable store root, for example $HOME/.xauusd-v2/mt5",
    )
    return parser


def _blocked_payload(*, status: str, error: str) -> dict[str, object]:
    return {
        "status": status,
        "error": error,
        "tick_path_evidence_available": False,
        "marked_liquidity_reference_certified": False,
        "fu_criteria_certified": False,
        "semantic_stage_certification": False,
        "strategy_truth_changed": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        import MetaTrader5 as mt5  # type: ignore[import-not-found]
    except (ImportError, OSError) as exc:
        print(
            json.dumps(
                _blocked_payload(
                    status="MT5_PYTHON_API_UNAVAILABLE_NOT_CERTIFIED",
                    error=f"MetaTrader5 Python integration is unavailable: {exc}",
                ),
                sort_keys=True,
                indent=2,
            )
        )
        return 3

    try:
        report = acquire_march_mt5_tick_availability(
            args.ingestion_manifest,
            provider=mt5,
        )
        persisted = persist_march_mt5_tick_availability(
            report,
            store_root=args.store_root,
        )
    except (OSError, ValueError, MarchMT5TickAvailabilityError) as exc:
        print(
            json.dumps(
                _blocked_payload(
                    status="MARCH_MT5_TICK_AVAILABILITY_BLOCKED_NOT_CERTIFIED",
                    error=str(exc),
                ),
                sort_keys=True,
                indent=2,
            )
        )
        return 2

    print(json.dumps(persisted, sort_keys=True, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
