from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .agents.risk_agent import RiskDecisionState


class PipelineReadinessState(StrEnum):
    BLOCKED = "BLOCKED"
    RESEARCH_READY = "RESEARCH_READY"
    EXECUTION_CANDIDATE = "EXECUTION_CANDIDATE"


@dataclass(frozen=True, slots=True)
class ResearchReadinessInput:
    source_approved: bool
    strategy_version_frozen: bool
    ground_truth_ready: bool
    blind_validation_passed: bool
    historical_reproducible: bool
    market_data_validated: bool
    research_design_approved: bool


@dataclass(frozen=True, slots=True)
class ExecutionReadinessInput:
    market_data_validated: bool
    market_context_unambiguous: bool
    strategy_candidate_ready: bool
    risk_state: RiskDecisionState


@dataclass(frozen=True, slots=True)
class PipelineReadinessReport:
    state: PipelineReadinessState
    blockers: tuple[str, ...]
    live_execution_authorized: bool = False


class AgentPipelineCoordinator:
    """Deterministic coordinator for cross-agent gates.

    V0.1 intentionally has no live-execution authorization path. Even a complete
    candidate stops at EXECUTION_CANDIDATE until later paper/shadow/live gates exist.
    """

    version = "0.1.0"

    def research_readiness(self, inputs: ResearchReadinessInput) -> PipelineReadinessReport:
        blockers: list[str] = []
        checks = (
            (inputs.source_approved, "source approval missing"),
            (inputs.strategy_version_frozen, "strategy version is not frozen"),
            (inputs.ground_truth_ready, "ground-truth dataset is not ready"),
            (inputs.blind_validation_passed, "blind independent validation has not passed"),
            (inputs.historical_reproducible, "historical reproducibility has not passed"),
            (inputs.market_data_validated, "market-data validation has not passed"),
            (inputs.research_design_approved, "quant research design has not passed"),
        )
        blockers.extend(message for passed, message in checks if not passed)
        state = PipelineReadinessState.RESEARCH_READY if not blockers else PipelineReadinessState.BLOCKED
        return PipelineReadinessReport(state=state, blockers=tuple(blockers))

    def execution_readiness(self, inputs: ExecutionReadinessInput) -> PipelineReadinessReport:
        blockers: list[str] = []
        if not inputs.market_data_validated:
            blockers.append("market-data validation has not passed")
        if not inputs.market_context_unambiguous:
            blockers.append("market context is ambiguous/conflicting")
        if not inputs.strategy_candidate_ready:
            blockers.append("strategy candidate is not ready")
        if inputs.risk_state is not RiskDecisionState.APPROVE_CANDIDATE:
            blockers.append(f"risk gate state is {inputs.risk_state.value}")

        state = PipelineReadinessState.EXECUTION_CANDIDATE if not blockers else PipelineReadinessState.BLOCKED
        return PipelineReadinessReport(
            state=state,
            blockers=tuple(blockers),
            live_execution_authorized=False,
        )
