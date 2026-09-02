from __future__ import annotations

import unittest

from xauusd_v2.agents.risk_agent import RiskDecisionState
from xauusd_v2.backtest_sequence import SequenceState
from xauusd_v2.ltf_execution import LTFExecutionState
from xauusd_v2.orchestrator import (
    AgentPipelineCoordinator,
    ExecutionReadinessInput,
    PipelineReadinessState,
    ResearchReadinessInput,
    StrategyCandidateReadinessInput,
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

    def test_strategy_candidate_requires_r143_and_r145(self) -> None:
        report = self.coordinator.strategy_candidate_readiness(
            StrategyCandidateReadinessInput(
                True,
                True,
                SequenceState.COMPLETE_CANDIDATE,
                LTFExecutionState.ENTRY_CANDIDATE,
                True,
                True,
            )
        )
        self.assertEqual(report.state, PipelineReadinessState.STRATEGY_CANDIDATE_READY)
        self.assertFalse(report.live_execution_authorized)

    def test_incomplete_r143_blocks_strategy_candidate(self) -> None:
        report = self.coordinator.strategy_candidate_readiness(
            StrategyCandidateReadinessInput(
                True,
                True,
                SequenceState.IN_PROGRESS,
                LTFExecutionState.ENTRY_CANDIDATE,
                True,
                True,
            )
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertIn("R-143 sequence state is in_progress", report.blockers)

    def test_ltf_wait_blocks_strategy_candidate(self) -> None:
        report = self.coordinator.strategy_candidate_readiness(
            StrategyCandidateReadinessInput(
                True,
                True,
                SequenceState.COMPLETE_CANDIDATE,
                LTFExecutionState.WAIT,
                True,
                True,
            )
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertIn("R-145 LTF execution state is wait", report.blockers)

    def test_blind_validation_blocks_strategy_candidate(self) -> None:
        report = self.coordinator.strategy_candidate_readiness(
            StrategyCandidateReadinessInput(
                True,
                True,
                SequenceState.COMPLETE_CANDIDATE,
                LTFExecutionState.ENTRY_CANDIDATE,
                False,
                True,
            )
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_historical_reproducibility_blocks_strategy_candidate(self) -> None:
        report = self.coordinator.strategy_candidate_readiness(
            StrategyCandidateReadinessInput(
                True,
                True,
                SequenceState.COMPLETE_CANDIDATE,
                LTFExecutionState.ENTRY_CANDIDATE,
                True,
                False,
            )
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

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
