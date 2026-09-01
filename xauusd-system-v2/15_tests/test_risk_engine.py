from __future__ import annotations

import unittest

from xauusd_v2.agents.risk_agent import (
    DeterministicRiskEngine,
    RiskDecisionState,
    RiskPolicy,
    RiskSnapshot,
)


def policy(**overrides):
    values = {
        "max_risk_fraction_per_trade": 0.01,
        "max_daily_loss_fraction": 0.03,
        "max_total_open_risk_fraction": 0.02,
        "max_concurrent_positions": 2,
    }
    values.update(overrides)
    return RiskPolicy(**values)


def snapshot(**overrides):
    values = {
        "current_equity": 10000.0,
        "day_start_equity": 10000.0,
        "existing_open_risk_amount": 50.0,
        "requested_risk_amount": 50.0,
        "open_positions": 1,
        "strategy_candidate_ready": True,
        "context_unambiguous": True,
    }
    values.update(overrides)
    return RiskSnapshot(**values)


class RiskEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = DeterministicRiskEngine()

    def test_incomplete_policy_fails_closed(self) -> None:
        decision, _ = self.engine.evaluate(
            policy=policy(max_risk_fraction_per_trade=None),
            snapshot=snapshot(),
        )
        self.assertEqual(decision.state, RiskDecisionState.NOT_CONFIGURED)

    def test_valid_candidate_passes_risk_gate(self) -> None:
        decision, run = self.engine.evaluate(policy=policy(), snapshot=snapshot())
        self.assertEqual(decision.state, RiskDecisionState.APPROVE_CANDIDATE)
        self.assertFalse(run.payload["authority"]["may_authorize_execution_directly"])

    def test_strategy_not_ready_is_vetoed(self) -> None:
        decision, _ = self.engine.evaluate(
            policy=policy(),
            snapshot=snapshot(strategy_candidate_ready=False),
        )
        self.assertEqual(decision.state, RiskDecisionState.VETO)
        self.assertIn("strategy candidate is not ready", decision.reasons)

    def test_ambiguous_context_is_vetoed(self) -> None:
        decision, _ = self.engine.evaluate(
            policy=policy(),
            snapshot=snapshot(context_unambiguous=False),
        )
        self.assertEqual(decision.state, RiskDecisionState.VETO)

    def test_per_trade_limit_is_vetoed(self) -> None:
        decision, _ = self.engine.evaluate(
            policy=policy(),
            snapshot=snapshot(requested_risk_amount=150.0),
        )
        self.assertEqual(decision.state, RiskDecisionState.VETO)
        self.assertIn("requested per-trade risk exceeds configured maximum", decision.reasons)

    def test_daily_loss_limit_is_vetoed(self) -> None:
        decision, _ = self.engine.evaluate(
            policy=policy(),
            snapshot=snapshot(current_equity=9700.0),
        )
        self.assertEqual(decision.state, RiskDecisionState.VETO)
        self.assertIn("daily loss limit reached", decision.reasons)

    def test_total_open_risk_limit_is_vetoed(self) -> None:
        decision, _ = self.engine.evaluate(
            policy=policy(),
            snapshot=snapshot(existing_open_risk_amount=180.0, requested_risk_amount=50.0),
        )
        self.assertEqual(decision.state, RiskDecisionState.VETO)
        self.assertIn("projected total open risk exceeds configured maximum", decision.reasons)

    def test_max_positions_is_vetoed(self) -> None:
        decision, _ = self.engine.evaluate(
            policy=policy(),
            snapshot=snapshot(open_positions=2),
        )
        self.assertEqual(decision.state, RiskDecisionState.VETO)

    def test_invalid_policy_fraction_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.evaluate(
                policy=policy(max_daily_loss_fraction=1.5),
                snapshot=snapshot(),
            )

    def test_negative_risk_amount_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.evaluate(
                policy=policy(),
                snapshot=snapshot(requested_risk_amount=-1.0),
            )


if __name__ == "__main__":
    unittest.main()
