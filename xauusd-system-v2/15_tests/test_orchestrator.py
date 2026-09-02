from __future__ import annotations

import unittest

from xauusd_v2.agents.risk_agent import RiskDecisionState
from xauusd_v2.backtest_sequence import SequenceState
from xauusd_v2.blind_validation_compare import BlindValidationComparisonReport
from xauusd_v2.historical_replay_gate import HistoricalReplayGateReport, HistoricalReplayGateState
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
        self.clean_validation = BlindValidationComparisonReport(
            outcomes=(), agree=1, disagree=0, ambiguous=0, total=1, all_agree=True, promotion_allowed=False
        )
        self.clean_replay = HistoricalReplayGateReport(
            state=HistoricalReplayGateState.PASS,
            total_sessions=1,
            complete_candidates=1,
            valid_in_progress=0,
            invalid_order=0,
            not_certified=0,
            lookahead_violations=0,
            blockers=(),
        )

    def strategy_input(
        self,
        *,
        sequence: SequenceState = SequenceState.COMPLETE_CANDIDATE,
        ltf: LTFExecutionState = LTFExecutionState.ENTRY_CANDIDATE,
        validation: BlindValidationComparisonReport | None = None,
        replay: HistoricalReplayGateReport | None = None,
    ) -> StrategyCandidateReadinessInput:
        return StrategyCandidateReadinessInput(
            market_data_validated=True,
            market_context_unambiguous=True,
            r143_sequence_state=sequence,
            ltf_execution_state=ltf,
            blind_validation_report=self.clean_validation if validation is None else validation,
            historical_replay_report=self.clean_replay if replay is None else replay,
        )

    def clean_strategy_report(self):
        return self.coordinator.strategy_candidate_readiness(self.strategy_input())

    def test_strategy_candidate_requires_r143_r145_and_reports(self) -> None:
        report = self.clean_strategy_report()
        self.assertEqual(report.state, PipelineReadinessState.STRATEGY_CANDIDATE_READY)
        self.assertFalse(report.live_execution_authorized)

    def test_incomplete_r143_blocks_strategy_candidate(self) -> None:
        report = self.coordinator.strategy_candidate_readiness(self.strategy_input(sequence=SequenceState.IN_PROGRESS))
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertIn("R-143 sequence state is in_progress", report.blockers)

    def test_ltf_wait_blocks_strategy_candidate(self) -> None:
        report = self.coordinator.strategy_candidate_readiness(self.strategy_input(ltf=LTFExecutionState.WAIT))
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertIn("R-145 LTF execution state is wait", report.blockers)

    def test_missing_blind_validation_report_blocks_strategy_candidate(self) -> None:
        inputs = StrategyCandidateReadinessInput(
            True, True, SequenceState.COMPLETE_CANDIDATE, LTFExecutionState.ENTRY_CANDIDATE, None, self.clean_replay
        )
        report = self.coordinator.strategy_candidate_readiness(inputs)
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_ambiguous_blind_validation_report_blocks_strategy_candidate(self) -> None:
        ambiguous = BlindValidationComparisonReport(
            outcomes=(), agree=0, disagree=0, ambiguous=1, total=1, all_agree=False, promotion_allowed=False
        )
        report = self.coordinator.strategy_candidate_readiness(self.strategy_input(validation=ambiguous))
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_missing_historical_replay_report_blocks_strategy_candidate(self) -> None:
        inputs = StrategyCandidateReadinessInput(
            True, True, SequenceState.COMPLETE_CANDIDATE, LTFExecutionState.ENTRY_CANDIDATE, self.clean_validation, None
        )
        report = self.coordinator.strategy_candidate_readiness(inputs)
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_failed_historical_replay_report_blocks_strategy_candidate(self) -> None:
        failed = HistoricalReplayGateReport(
            state=HistoricalReplayGateState.FAIL,
            total_sessions=1,
            complete_candidates=0,
            valid_in_progress=0,
            invalid_order=1,
            not_certified=0,
            lookahead_violations=0,
            blockers=("invalid",),
        )
        report = self.coordinator.strategy_candidate_readiness(self.strategy_input(replay=failed))
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_research_ready_requires_full_strategy_gate(self) -> None:
        report = self.coordinator.research_readiness(
            ResearchReadinessInput(True, True, True, True, self.strategy_input())
        )
        self.assertEqual(report.state, PipelineReadinessState.RESEARCH_READY)

    def test_research_is_blocked_when_strategy_gate_is_incomplete(self) -> None:
        report = self.coordinator.research_readiness(
            ResearchReadinessInput(True, True, True, True, self.strategy_input(sequence=SequenceState.IN_PROGRESS))
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertTrue(any(reason.startswith("strategy gate:") for reason in report.blockers))

    def test_research_design_failure_blocks_even_with_clean_strategy(self) -> None:
        report = self.coordinator.research_readiness(
            ResearchReadinessInput(True, True, True, False, self.strategy_input())
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertIn("quant research design has not passed", report.blockers)

    def test_risk_veto_blocks_execution_candidate(self) -> None:
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(True, True, self.clean_strategy_report(), RiskDecisionState.VETO)
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_ambiguous_context_blocks_execution_candidate(self) -> None:
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(True, False, self.clean_strategy_report(), RiskDecisionState.APPROVE_CANDIDATE)
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_blocked_strategy_report_cannot_be_relabelled_ready_at_execution(self) -> None:
        blocked = self.coordinator.strategy_candidate_readiness(self.strategy_input(sequence=SequenceState.IN_PROGRESS))
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(True, True, blocked, RiskDecisionState.APPROVE_CANDIDATE)
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertIn("strategy candidate report is not ready", report.blockers)

    def test_complete_candidate_never_authorizes_live_execution(self) -> None:
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(True, True, self.clean_strategy_report(), RiskDecisionState.APPROVE_CANDIDATE)
        )
        self.assertEqual(report.state, PipelineReadinessState.EXECUTION_CANDIDATE)
        self.assertFalse(report.live_execution_authorized)


if __name__ == "__main__":
    unittest.main()
