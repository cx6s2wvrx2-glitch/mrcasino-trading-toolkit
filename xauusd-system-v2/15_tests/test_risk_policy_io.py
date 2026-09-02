from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.risk_policy_io import (
    RiskPolicyIOError,
    load_production_risk_policy,
    parse_production_risk_policy,
)


def valid_policy(**overrides):
    value = {
        "version": 1,
        "policy_id": "risk-policy-001",
        "policy_scope": "production_risk_safety_only",
        "approval_reference": "user-approval:pending-example",
        "max_risk_fraction_per_trade": 0.01,
        "max_daily_loss_fraction": 0.03,
        "max_total_open_risk_fraction": 0.02,
        "max_concurrent_positions": 2,
        "strategy_truth_authority": False,
        "live_execution_authorized": False,
        "promotion_allowed": False,
    }
    value.update(overrides)
    return value


class ProductionRiskPolicyIOTests(unittest.TestCase):
    def test_complete_explicit_policy_maps_to_engine_without_defaults(self) -> None:
        document = parse_production_risk_policy(valid_policy())
        engine_policy = document.to_engine_policy()
        self.assertEqual(engine_policy.max_risk_fraction_per_trade, 0.01)
        self.assertEqual(engine_policy.max_daily_loss_fraction, 0.03)
        self.assertEqual(engine_policy.max_total_open_risk_fraction, 0.02)
        self.assertEqual(engine_policy.max_concurrent_positions, 2)
        self.assertFalse(document.strategy_truth_authority)
        self.assertFalse(document.live_execution_authorized)
        self.assertFalse(document.promotion_allowed)

    def test_missing_limit_is_rejected_instead_of_defaulted(self) -> None:
        value = valid_policy()
        del value["max_daily_loss_fraction"]
        with self.assertRaisesRegex(RiskPolicyIOError, "missing=max_daily_loss_fraction"):
            parse_production_risk_policy(value)

    def test_extra_hidden_field_is_rejected(self) -> None:
        with self.assertRaisesRegex(RiskPolicyIOError, "extra=legacy_three_percent"):
            parse_production_risk_policy(valid_policy(legacy_three_percent=True))

    def test_policy_cannot_claim_strategy_truth(self) -> None:
        with self.assertRaisesRegex(RiskPolicyIOError, "strategy_truth_authority must be false"):
            parse_production_risk_policy(valid_policy(strategy_truth_authority=True))

    def test_policy_cannot_authorize_live_execution(self) -> None:
        with self.assertRaisesRegex(RiskPolicyIOError, "live_execution_authorized must be false"):
            parse_production_risk_policy(valid_policy(live_execution_authorized=True))

    def test_policy_cannot_allow_promotion(self) -> None:
        with self.assertRaisesRegex(RiskPolicyIOError, "promotion_allowed must be false"):
            parse_production_risk_policy(valid_policy(promotion_allowed=True))

    def test_invalid_fraction_is_rejected(self) -> None:
        with self.assertRaisesRegex(RiskPolicyIOError, "strictly between 0 and 1"):
            parse_production_risk_policy(valid_policy(max_risk_fraction_per_trade=1.0))

    def test_boolean_is_not_accepted_as_numeric_fraction(self) -> None:
        with self.assertRaisesRegex(RiskPolicyIOError, "numeric fraction"):
            parse_production_risk_policy(valid_policy(max_daily_loss_fraction=True))

    def test_concurrent_positions_must_be_positive_integer(self) -> None:
        with self.assertRaisesRegex(RiskPolicyIOError, "positive integer"):
            parse_production_risk_policy(valid_policy(max_concurrent_positions=0))

    def test_approval_reference_is_required_and_nonempty(self) -> None:
        with self.assertRaisesRegex(RiskPolicyIOError, "approval_reference"):
            parse_production_risk_policy(valid_policy(approval_reference=" "))

    def test_loader_reads_exact_json_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "risk-policy.json"
            path.write_text(json.dumps(valid_policy()), encoding="utf-8")
            document = load_production_risk_policy(path)
            self.assertEqual(document.policy_id, "risk-policy-001")


if __name__ == "__main__":
    unittest.main()
