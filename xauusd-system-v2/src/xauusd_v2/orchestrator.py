from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .agents.data_agent import MarketDataValidationReport
from .agents.market_state_agent import ContextState, Direction, MarketContextReport
from .agents.quant_agent import ResearchDesignReport
from .agents.risk_agent import RiskDecision, RiskDecisionState
from .backtest_sequence import SequenceState
from .blind_validation_compare import BlindValidationComparisonReport
from .evidence_gate import EvidenceGateReport
from .historical_replay_gate import HistoricalReplayGateReport
from .ltf_execution import LTFExecutionState


class PipelineReadinessState(StrEnum):
    BLOCKED = "BLOCKED"
    STRATEGY_CANDIDATE_READY = "STRATEGY_CANDIDATE_READY"
    RESEARCH_READY = "RESEARCH_READY"
    EXECUTION_CANDIDATE = "EXECUTION_CANDIDATE"


@dataclass(frozen=True, slots=True)
class PipelineReadinessReport:
    state: PipelineReadinessState
    blockers: tuple[str, ...]
    live_execution_authorized: bool = False


@dataclass(frozen=True, slots=True)
class StrategyCandidateReadinessInput:
    market_data_report: MarketDataValidationReport | None
    market_context_report: MarketContextReport | None
    r143_sequence_state: SequenceState
    ltf_execution_state: LTFExecutionState
    blind_validation_report: BlindValidationComparisonReport | None
    historical_replay_report: HistoricalReplayGateReport | None


@dataclass(frozen=True, slots=True)
class ResearchReadinessInput:
    source_approval_report: EvidenceGateReport | None
    strategy_freeze_report: EvidenceGateReport | None
    ground_truth_report: EvidenceGateReport | None
    research_design_report: ResearchDesignReport | None
    strategy: StrategyCandidateReadinessInput


@dataclass(frozen=True, slots=True)
class ExecutionReadinessInput:
    market_data_report: MarketDataValidationReport | None
    market_context_report: MarketContextReport | None
    strategy_report: PipelineReadinessReport | None
    risk_decision: RiskDecision | None


def _market_data_ready(report: MarketDataValidationReport | None) -> bool:
    return bool(
        report
        and report.canonical_symbol == "XAUUSD"
        and report.timeframe_seconds > 0
        and report.total_bars > 0
        and report.closed_bars >= 0
        and report.provisional_bars >= 0
        and report.closed_bars + report.provisional_bars == report.total_bars
        and len(report.source_names) == 1
        and len(report.source_symbols) == 1
        and all(value.strip() for value in report.source_names)
        and all(value.strip() for value in report.source_symbols)
    )


def _market_context_ready(report: MarketContextReport | None) -> bool:
    return bool(
        report
        and report.state in {ContextState.ALIGNED_BULLISH, ContextState.ALIGNED_BEARISH}
        and report.aligned_direction in {Direction.BULLISH, Direction.BEARISH}
        and report.known_direction_count > 0
        and report.source_refs
        and all(ref.strip() for ref in report.source_refs)
    )


def _evidence_gate_passed(report: EvidenceGateReport | None, *, expected_name: str) -> bool:
    return bool(
        report
        and report.gate_name == expected_name
        and report.passed
        and report.evidence_refs
        and all(ref.strip() for ref in report.evidence_refs)
    )


class AgentPipelineCoordinator:
    """Deterministic cross-agent coordinator with no live-execution authority.

    Readiness consumes provenance-bearing upstream reports rather than caller-supplied
    success booleans. Missing, malformed, ambiguous or conflicting evidence blocks.
    """

    version = "0.6.0"

    def strategy_candidate_readiness(
        self,
        inputs: StrategyCandidateReadinessInput,
    ) -> PipelineReadinessReport:
        blockers: list[str] = []
        if not _market_data_ready(inputs.market_data_report):
            blockers.append("market-data validation report has not passed the evidence gate")
        if not _market_context_ready(inputs.market_context_report):
            blockers.append("market context report is absent, ambiguous, conflicting, or lacks provenance")
        if inputs.r143_sequence_state is not SequenceState.COMPLETE_CANDIDATE:
            blockers.append(f"R-143 sequence state is {inputs.r143_sequence_state.value}")
        if inputs.ltf_execution_state is not LTFExecutionState.ENTRY_CANDIDATE:
            blockers.append(f"R-145 LTF execution state is {inputs.ltf_execution_state.value}")

        validation = inputs.blind_validation_report
        validation_passed = bool(
            validation
            and validation.total > 0
            and validation.all_agree
            and validation.agree == validation.total
            and validation.disagree == 0
            and validation.ambiguous == 0
            and validation.promotion_allowed is False
        )
        if not validation_passed:
            blockers.append("blind independent validation report has not passed cleanly")

        replay = inputs.historical_replay_report
        if replay is None or not replay.historical_reproducible:
            blockers.append("historical replay report has not passed reproducibility gate")

        state = (
            PipelineReadinessState.STRATEGY_CANDIDATE_READY
            if not blockers
            else PipelineReadinessState.BLOCKED
        )
        return PipelineReadinessReport(
            state=state,
            blockers=tuple(blockers),
            live_execution_authorized=False,
        )

    def research_readiness(self, inputs: ResearchReadinessInput) -> PipelineReadinessReport:
        blockers: list[str] = []

        evidence_checks = (
            (
                _evidence_gate_passed(inputs.source_approval_report, expected_name="source_approval"),
                "source approval evidence report has not passed",
            ),
            (
                _evidence_gate_passed(inputs.strategy_freeze_report, expected_name="strategy_freeze"),
                "strategy freeze evidence report has not passed",
            ),
            (
                _evidence_gate_passed(inputs.ground_truth_report, expected_name="ground_truth_ready"),
                "ground-truth evidence report has not passed",
            ),
        )
        blockers.extend(message for passed, message in evidence_checks if not passed)

        design = inputs.research_design_report
        if design is None or not design.ready_for_research or design.blockers:
            blockers.append("quant research design report has not passed")

        strategy_report = self.strategy_candidate_readiness(inputs.strategy)
        if strategy_report.state is not PipelineReadinessState.STRATEGY_CANDIDATE_READY:
            blockers.extend(f"strategy gate: {reason}" for reason in strategy_report.blockers)

        state = PipelineReadinessState.RESEARCH_READY if not blockers else PipelineReadinessState.BLOCKED
        return PipelineReadinessReport(
            state=state,
            blockers=tuple(blockers),
            live_execution_authorized=False,
        )

    def execution_readiness(self, inputs: ExecutionReadinessInput) -> PipelineReadinessReport:
        blockers: list[str] = []
        if not _market_data_ready(inputs.market_data_report):
            blockers.append("market-data validation report has not passed the evidence gate")
        if not _market_context_ready(inputs.market_context_report):
            blockers.append("market context report is absent, ambiguous, conflicting, or lacks provenance")

        strategy = inputs.strategy_report
        if (
            strategy is None
            or strategy.state is not PipelineReadinessState.STRATEGY_CANDIDATE_READY
            or strategy.blockers
            or strategy.live_execution_authorized
        ):
            blockers.append("strategy candidate report is not ready")

        risk = inputs.risk_decision
        if risk is None or risk.state is not RiskDecisionState.APPROVE_CANDIDATE or risk.reasons:
            risk_state = "missing" if risk is None else risk.state.value
            blockers.append(f"risk decision has not passed cleanly: {risk_state}")

        state = PipelineReadinessState.EXECUTION_CANDIDATE if not blockers else PipelineReadinessState.BLOCKED
        return PipelineReadinessReport(
            state=state,
            blockers=tuple(blockers),
            live_execution_authorized=False,
        )


__all__ = [
    "AgentPipelineCoordinator",
    "EvidenceGateReport",
    "ExecutionReadinessInput",
    "PipelineReadinessReport",
    "PipelineReadinessState",
    "ResearchReadinessInput",
    "StrategyCandidateReadinessInput",
]
