from __future__ import annotations

import unittest
from datetime import UTC, datetime

from xauusd_v2.agents.data_agent import MarketDataValidationReport
from xauusd_v2.agents.market_state_agent import ContextState, Direction, MarketContextReport
from xauusd_v2.agents.quant_agent import ResearchDesignReport
from xauusd_v2.agents.risk_agent import RiskDecision, RiskDecisionState
from xauusd_v2.backtest_sequence import SequenceState
from xauusd_v2.blind_validation_compare import BlindValidationComparisonReport
from xauusd_v2.historical_replay_gate import HistoricalReplayGateReport, HistoricalReplayGateState
from xauusd_v2.ltf_execution import LTFExecutionState
from xauusd_v2.orchestrator import (
    AgentPipelineCoordinator,
    EvidenceGateReport,
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
        self.clean_data = MarketDataValidationReport(
            canonical_symbol="XAUUSD",
            timeframe_seconds=60,
            total_bars=10,
            closed_bars=10,
            provisional_bars=0,
            first_timestamp=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
            last_timestamp=datetime(2026, 9, 1, 10, 9, tzinfo=UTC),
            source_names=("Broker A",),
            source_symbols=("XAUUSD.a",),
            warnings=(),
        )
        self.clean_context = MarketContextReport(
            state=ContextState.ALIGNED_BULLISH,
            aligned_direction=Direction.BULLISH,
            known_direction_count=3,
            reasons=("confirmed aligned context",),
            source_refs=("HTF-1", "TFS-1", "LIQ-1"),
        )
        self.clean_risk = RiskDecision(
            state=RiskDecisionState.APPROVE_CANDIDATE,
            reasons=(),
            requested_risk_fraction=0.005,
            projected_total_open_risk_fraction=0.005,
            current_daily_drawdown_fraction=0.0,
        )
        self.clean_design = ResearchDesignReport(
            experiment_id="EXP-001",
            ready_for_research=True,
            blockers=(),
            warnings=(),
            train_window=(datetime(2022, 1, 1, tzinfo=UTC), datetime(2023, 1, 1, tzinfo=UTC)),
            validation_window=(datetime(2023, 1, 2, tzinfo=UTC), datetime(2024, 1, 1, tzinfo=UTC)),
            test_window=(datetime(2024, 1, 2, tzinfo=UTC), datetime(2025, 1, 1, tzinfo=UTC)),
        )

    def strategy_input(
        self,
        *,
        data: MarketDataValidationReport | None = None,
        context: MarketContextReport | None = None,
        sequence: SequenceState = SequenceState.COMPLETE_CANDIDATE,
        ltf: LTFExecutionState = LTFExecutionState.ENTRY_CANDIDATE,
        validation: BlindValidationComparisonReport | None = None,
        replay: HistoricalReplayGateReport | None = None,
    ) -> StrategyCandidateReadinessInput:
        return StrategyCandidateReadinessInput(
            market_data_report=self.clean_data if data is None else data,
            market_context_report=self.clean_context if context is None else context,
            r143_sequence_state=sequence,
            ltf_execution_state=ltf,
            blind_validation_report=self.clean_validation if validation is None else validation,
            historical_replay_report=self.clean_replay if replay is None else replay,
        )

    @staticmethod
    def gate(name: str) -> EvidenceGateReport:
        return EvidenceGateReport(name, True, (f"evidence:{name}",))

    def research_input(
        self,
        *,
        design: ResearchDesignReport | None = None,
        strategy: StrategyCandidateReadinessInput | None = None,
    ) -> ResearchReadinessInput:
        return ResearchReadinessInput(
            source_approval_report=self.gate("source_approval"),
            strategy_freeze_report=self.gate("strategy_freeze"),
            ground_truth_report=self.gate("ground_truth_ready"),
            research_design_report=self.clean_design if design is None else design,
            strategy=self.strategy_input() if strategy is None else strategy,
        )

    def clean_strategy_report(self):
        return self.coordinator.strategy_candidate_readiness(self.strategy_input())

    def test_strategy_candidate_requires_real_data_and_context_reports(self) -> None:
        report = self.clean_strategy_report()
        self.assertEqual(report.state, PipelineReadinessState.STRATEGY_CANDIDATE_READY)
        self.assertFalse(report.live_execution_authorized)

    def test_missing_market_data_report_blocks_strategy_candidate(self) -> None:
        inputs = StrategyCandidateReadinessInput(
            None,
            self.clean_context,
            SequenceState.COMPLETE_CANDIDATE,
            LTFExecutionState.ENTRY_CANDIDATE,
            self.clean_validation,
            self.clean_replay,
        )
        report = self.coordinator.strategy_candidate_readiness(inputs)
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertTrue(any("market-data validation report" in item for item in report.blockers))

    def test_mixed_source_data_report_blocks_strategy_candidate(self) -> None:
        mixed = MarketDataValidationReport(
            canonical_symbol="XAUUSD",
            timeframe_seconds=60,
            total_bars=10,
            closed_bars=10,
            provisional_bars=0,
            first_timestamp=self.clean_data.first_timestamp,
            last_timestamp=self.clean_data.last_timestamp,
            source_names=("Broker A", "Broker B"),
            source_symbols=("XAUUSD.a",),
            warnings=("multiple sources",),
        )
        report = self.coordinator.strategy_candidate_readiness(self.strategy_input(data=mixed))
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_context_report_without_provenance_blocks_strategy_candidate(self) -> None:
        context = MarketContextReport(
            state=ContextState.ALIGNED_BULLISH,
            aligned_direction=Direction.BULLISH,
            known_direction_count=2,
            reasons=("aligned",),
            source_refs=(),
        )
        report = self.coordinator.strategy_candidate_readiness(self.strategy_input(context=context))
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertTrue(any("lacks provenance" in item for item in report.blockers))

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
            self.clean_data,
            self.clean_context,
            SequenceState.COMPLETE_CANDIDATE,
            LTFExecutionState.ENTRY_CANDIDATE,
            None,
            self.clean_replay,
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
            self.clean_data,
            self.clean_context,
            SequenceState.COMPLETE_CANDIDATE,
            LTFExecutionState.ENTRY_CANDIDATE,
            self.clean_validation,
            None,
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

    def test_passed_generic_gate_requires_provenance(self) -> None:
        with self.assertRaisesRegex(ValueError, "provenance"):
            EvidenceGateReport("source_approval", True, ())

    def test_research_ready_requires_evidence_reports_and_full_strategy_gate(self) -> None:
        report = self.coordinator.research_readiness(self.research_input())
        self.assertEqual(report.state, PipelineReadinessState.RESEARCH_READY)
        self.assertFalse(report.live_execution_authorized)

    def test_research_missing_source_approval_report_is_blocked(self) -> None:
        inputs = self.research_input()
        report = self.coordinator.research_readiness(
            ResearchReadinessInput(
                None,
                inputs.strategy_freeze_report,
                inputs.ground_truth_report,
                inputs.research_design_report,
                inputs.strategy,
            )
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertIn("source approval evidence report has not passed", report.blockers)

    def test_research_is_blocked_when_strategy_gate_is_incomplete(self) -> None:
        report = self.coordinator.research_readiness(
            self.research_input(strategy=self.strategy_input(sequence=SequenceState.IN_PROGRESS))
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertTrue(any(reason.startswith("strategy gate:") for reason in report.blockers))

    def test_research_design_failure_blocks_even_with_clean_strategy(self) -> None:
        failed_design = ResearchDesignReport(
            experiment_id="EXP-001",
            ready_for_research=False,
            blockers=("bad design",),
            warnings=(),
            train_window=self.clean_design.train_window,
            validation_window=self.clean_design.validation_window,
            test_window=self.clean_design.test_window,
        )
        report = self.coordinator.research_readiness(self.research_input(design=failed_design))
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertIn("quant research design report has not passed", report.blockers)

    def test_risk_veto_blocks_execution_candidate(self) -> None:
        veto = RiskDecision(
            state=RiskDecisionState.VETO,
            reasons=("limit",),
            requested_risk_fraction=0.02,
            projected_total_open_risk_fraction=0.02,
            current_daily_drawdown_fraction=0.0,
        )
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(self.clean_data, self.clean_context, self.clean_strategy_report(), veto)
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_ambiguous_context_report_blocks_execution_candidate(self) -> None:
        ambiguous = MarketContextReport(
            state=ContextState.AMBIGUOUS,
            aligned_direction=Direction.UNKNOWN,
            known_direction_count=0,
            reasons=("ambiguous",),
            source_refs=("CTX-1",),
        )
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(self.clean_data, ambiguous, self.clean_strategy_report(), self.clean_risk)
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)

    def test_blocked_strategy_report_cannot_be_relabelled_ready_at_execution(self) -> None:
        blocked = self.coordinator.strategy_candidate_readiness(self.strategy_input(sequence=SequenceState.IN_PROGRESS))
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(self.clean_data, self.clean_context, blocked, self.clean_risk)
        )
        self.assertEqual(report.state, PipelineReadinessState.BLOCKED)
        self.assertIn("strategy candidate report is not ready", report.blockers)

    def test_complete_candidate_never_authorizes_live_execution(self) -> None:
        report = self.coordinator.execution_readiness(
            ExecutionReadinessInput(
                self.clean_data,
                self.clean_context,
                self.clean_strategy_report(),
                self.clean_risk,
            )
        )
        self.assertEqual(report.state, PipelineReadinessState.EXECUTION_CANDIDATE)
        self.assertFalse(report.live_execution_authorized)


if __name__ == "__main__":
    unittest.main()
