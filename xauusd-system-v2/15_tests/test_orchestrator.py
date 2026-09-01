from __future__ import annotations

import unittest

from xauusd_v2.agents.risk_agent import RiskDecisionState
from xauusd_v2.orchestrator import (
    AgentPipelineCoordinator,
    ExecutionReadinessInput,
    PipelineReadinessState,
    ResearchReadinessInput,
)


class OrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.coordinator = AgentPipelineCoordinator()

    def test_research_ready_requires_all_gates(self) -> None:
        report = self.coordinator.research_readiness(
            ResearchReadinessInput(True, True, True, True, True, True, True)
        )
        self.assertEqual(report.state, PipelineReadinessState.RESEARCH_READY)

    def test_missing_blind_validation_blocks_research(self) -> None:
        report = self.coordinator.research_readiness(
            ResearchReadinessInput(True, True, True, False, True, True, True)
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertIn("blind independent validation has not passed", report.blockers)

    def test_risk_veto_blocks_execution_candidate(self) -> None:
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(True, True, True, RiskDecisionState.VETO)
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_ambiguous_context_blocks_execution_candidate(self) -> None:
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(True, False, True, RiskDecisionState.APPROVE_CANDIDATE)
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_complete_candidate_never_authorizes_live_execution(self) -> None:
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(True, True, True, RiskDecisionState.APPROVE_CANDIDATE)
        )
        self.assertEqual(report.state, PipelineReadinessState.EXECUTION_CANDIDATE)
        self.assertFalse(report.live_execution_authorized)


if __name__ == "__main__":
    unittest.main()
