from __future__ import annotations

import unittest

from xauusd_v2.agents.risk_agent import (
    DeterministicRiskEngine,
    RiskDecisionState,
    RiskPolicy,
    RiskSnapshot,
)
from xauusd_v2.evidence_gate import EvidenceGateReport


def policy(**overrides):
    values = {
        "max_risk_fraction_per_trade": 0.01,
        "max_daily_loss_fraction": 0.03,
        "max_total_open_risk_fraction": 0.02,
        "max_concurrent_positions": 2,
    }
    values.update(overrides)
    return RiskPolicy(**values)


def passed_gate(name: str) -> EvidenceGateReport:
    return EvidenceGateReport(name, True, (f"evidence:{name}",))


def blocked_gate(name: str) -> EvidenceGateReport:
    return EvidenceGateReport(name, False, (f"evidence:{name}:blocked",))


def snapshot(**overrides):
    values = {
        "current_equity": 10000.0,
        "day_start_equity": 10000.0,
        "existing_open_risk_amount": 50.0,
        "requested_risk_amount": 50.0,
        "open_positions": 1,
        "strategy_candidate_gate": passed_gate("strategy_candidate"),
        "market_context_gate": passed_gate("market_context"),
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

    def test_valid_candidate_passes_risk_gate_with_provenance(self) -> None:
        decision, run = self.engine.evaluate(policy=policy(), snapshot=snapshot())
        self.assertEqual(decision.state, RiskDecisionState.APPROVE_CANDIDATE)
        self.assertIn("evidence:strategy_candidate", run.input_refs)
        self.assertIn("evidence:market_context", run.input_refs)
        self.assertFalse(run.payload["authority"]["may_authorize_execution_directly"])

    def test_strategy_gate_not_ready_is_vetoed(self) -> None:
        decision, _ = self.engine.evaluate(
            policy=policy(),
            snapshot=snapshot(strategy_candidate_gate=blocked_gate("strategy_candidate")),
        )
        self.assertEqual(decision.state, RiskDecisionState.VETO)
        self.assertIn("strategy candidate evidence gate is not ready", decision.reasons)

    def test_wrong_strategy_gate_name_is_vetoed(self) -> None:
        decision, _ = self.engine.evaluate(
            policy=policy(),
            snapshot=snapshot(strategy_candidate_gate=passed_gate("something_else")),
        )
        self.assertEqual(decision.state, RiskDecisionState.VETO)

    def test_ambiguous_context_gate_is_vetoed(self) -> None:
        decision, _ = self.engine.evaluate(
            policy=policy(),
            snapshot=snapshot(market_context_gate=blocked_gate("market_context")),
        )
        self.assertEqual(decision.state, RiskDecisionState.VETO)
        self.assertIn(
            "market context evidence gate is ambiguous, blocked, or missing provenance",
            decision.reasons,
        )

    def test_passed_risk_upstream_gate_cannot_be_bare_boolean(self) -> None:
        with self.assertRaisesRegex(ValueError, "provenance"):
            EvidenceGateReport("strategy_candidate", True, ())

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
