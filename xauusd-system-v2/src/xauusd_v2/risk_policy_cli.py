from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .risk_policy_io import RiskPolicyIOError, load_production_risk_policy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-risk-policy-check",
        description=(
            "Validate an explicit XAUUSD V2 production risk-safety policy document. "
            "This command never authorizes live execution or strategy promotion."
        ),
    )
    parser.add_argument("policy", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        document = load_production_risk_policy(args.policy)
    except RiskPolicyIOError as exc:
        print(
            json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2

    payload = {
        "status": "VALIDATED_POLICY_CONTRACT",
        "policy_id": document.policy_id,
        "policy_scope": document.policy_scope,
        "approval_reference": document.approval_reference,
        "max_risk_fraction_per_trade": document.max_risk_fraction_per_trade,
        "max_daily_loss_fraction": document.max_daily_loss_fraction,
        "max_total_open_risk_fraction": document.max_total_open_risk_fraction,
        "max_concurrent_positions": document.max_concurrent_positions,
        "strategy_truth_authority": document.strategy_truth_authority,
        "live_execution_authorized": document.live_execution_authorized,
        "promotion_allowed": document.promotion_allowed,
    }
    print(json.dumps(payload, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
