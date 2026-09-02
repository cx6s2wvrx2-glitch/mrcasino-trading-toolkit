from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from ..evidence_gate import EvidenceGateReport
from ..models import AgentRunResult
from .base import AgentContractError


class RiskDecisionState(StrEnum):
    NOT_CONFIGURED = "NOT_CONFIGURED"
    VETO = "VETO"
    APPROVE_CANDIDATE = "APPROVE_CANDIDATE"


@dataclass(frozen=True, slots=True)
class RiskPolicy:
    max_risk_fraction_per_trade: float | None
    max_daily_loss_fraction: float | None
    max_total_open_risk_fraction: float | None
    max_concurrent_positions: int | None

    def configured(self) -> bool:
        return all(
            value is not None
            for value in (
                self.max_risk_fraction_per_trade,
                self.max_daily_loss_fraction,
                self.max_total_open_risk_fraction,
                self.max_concurrent_positions,
            )
        )


@dataclass(frozen=True, slots=True)
class RiskSnapshot:
    current_equity: float
    day_start_equity: float
    existing_open_risk_amount: float
    requested_risk_amount: float
    open_positions: int
    strategy_candidate_gate: EvidenceGateReport
    market_context_gate: EvidenceGateReport


@dataclass(frozen=True, slots=True)
class RiskDecision:
    state: RiskDecisionState
    reasons: tuple[str, ...]
    requested_risk_fraction: float | None
    projected_total_open_risk_fraction: float | None
    current_daily_drawdown_fraction: float | None


def _upstream_gate_passed(gate: EvidenceGateReport, *, expected_name: str) -> bool:
    return bool(
        gate.gate_name == expected_name
        and gate.passed
        and gate.evidence_refs
        and all(ref.strip() for ref in gate.evidence_refs)
    )


class DeterministicRiskEngine:
    """Hard-veto risk gate.

    No default risk percentages are embedded. Production limits must be supplied
    explicitly by approved policy configuration. Upstream strategy/context eligibility
    must arrive as provenance-bearing gates rather than caller-supplied booleans.
    This engine can veto but never create a strategy signal or authorize execution.
    """

    name = "deterministic_risk_engine_07"
    version = "0.2.0"

    def evaluate(
        self,
        *,
        policy: RiskPolicy,
        snapshot: RiskSnapshot,
    ) -> tuple[RiskDecision, AgentRunResult]:
        self._validate_snapshot(snapshot)

        if not policy.configured():
            decision = RiskDecision(
                state=RiskDecisionState.NOT_CONFIGURED,
                reasons=("Production risk policy is incomplete; no trade authorization is possible.",),
                requested_risk_fraction=None,
                projected_total_open_risk_fraction=None,
                current_daily_drawdown_fraction=None,
            )
            return decision, self._run(decision, snapshot)

        self._validate_policy(policy)

        assert policy.max_risk_fraction_per_trade is not None
        assert policy.max_daily_loss_fraction is not None
        assert policy.max_total_open_risk_fraction is not None
        assert policy.max_concurrent_positions is not None

        requested_fraction = snapshot.requested_risk_amount / snapshot.current_equity
        projected_open_fraction = (
            snapshot.existing_open_risk_amount + snapshot.requested_risk_amount
        ) / snapshot.current_equity
        daily_drawdown_fraction = max(
            0.0,
            (snapshot.day_start_equity - snapshot.current_equity) / snapshot.day_start_equity,
        )

        reasons: list[str] = []
        if not _upstream_gate_passed(
            snapshot.strategy_candidate_gate, expected_name="strategy_candidate"
        ):
            reasons.append("strategy candidate evidence gate is not ready")
        if not _upstream_gate_passed(snapshot.market_context_gate, expected_name="market_context"):
            reasons.append("market context evidence gate is ambiguous, blocked, or missing provenance")
        if requested_fraction > policy.max_risk_fraction_per_trade:
            reasons.append("requested per-trade risk exceeds configured maximum")
        if daily_drawdown_fraction >= policy.max_daily_loss_fraction:
            reasons.append("daily loss limit reached")
        if projected_open_fraction > policy.max_total_open_risk_fraction:
            reasons.append("projected total open risk exceeds configured maximum")
        if snapshot.open_positions >= policy.max_concurrent_positions:
            reasons.append("maximum concurrent positions reached")

        state = RiskDecisionState.VETO if reasons else RiskDecisionState.APPROVE_CANDIDATE
        decision = RiskDecision(
            state=state,
            reasons=tuple(reasons),
            requested_risk_fraction=requested_fraction,
            projected_total_open_risk_fraction=projected_open_fraction,
            current_daily_drawdown_fraction=daily_drawdown_fraction,
        )
        return decision, self._run(decision, snapshot)

    @staticmethod
    def _validate_policy(policy: RiskPolicy) -> None:
        fractions = (
            policy.max_risk_fraction_per_trade,
            policy.max_daily_loss_fraction,
            policy.max_total_open_risk_fraction,
        )
        if any(value is None for value in fractions) or policy.max_concurrent_positions is None:
            raise AgentContractError("risk policy must be fully configured before validation")
        for value in fractions:
            assert value is not None
            if not isfinite(value) or not 0 < value < 1:
                raise AgentContractError("risk fractions must be finite and between 0 and 1")
        if policy.max_concurrent_positions <= 0:
            raise AgentContractError("max_concurrent_positions must be positive")

    @staticmethod
    def _validate_snapshot(snapshot: RiskSnapshot) -> None:
        numeric = (
            snapshot.current_equity,
            snapshot.day_start_equity,
            snapshot.existing_open_risk_amount,
            snapshot.requested_risk_amount,
        )
        if not all(isfinite(value) for value in numeric):
            raise AgentContractError("risk snapshot contains non-finite values")
        if snapshot.current_equity <= 0 or snapshot.day_start_equity <= 0:
            raise AgentContractError("equity values must be positive")
        if snapshot.existing_open_risk_amount < 0 or snapshot.requested_risk_amount < 0:
            raise AgentContractError("risk amounts cannot be negative")
        if snapshot.open_positions < 0:
            raise AgentContractError("open_positions cannot be negative")
        if not isinstance(snapshot.strategy_candidate_gate, EvidenceGateReport):
            raise AgentContractError("strategy candidate gate must be an EvidenceGateReport")
        if not isinstance(snapshot.market_context_gate, EvidenceGateReport):
            raise AgentContractError("market context gate must be an EvidenceGateReport")

    def _run(self, decision: RiskDecision, snapshot: RiskSnapshot) -> AgentRunResult:
        refs = tuple(
            dict.fromkeys(
                snapshot.strategy_candidate_gate.evidence_refs
                + snapshot.market_context_gate.evidence_refs
            )
        )
        return AgentRunResult(
            agent_name=self.name,
            agent_version=self.version,
            input_refs=refs,
            payload={
                "decision": decision.state.value,
                "reasons": list(decision.reasons),
                "requested_risk_fraction": decision.requested_risk_fraction,
                "projected_total_open_risk_fraction": decision.projected_total_open_risk_fraction,
                "current_daily_drawdown_fraction": decision.current_daily_drawdown_fraction,
                "strategy_candidate_gate": snapshot.strategy_candidate_gate.gate_name,
                "market_context_gate": snapshot.market_context_gate.gate_name,
                "authority": {
                    "may_create_strategy_signal": False,
                    "may_override_veto": False,
                    "may_authorize_execution_directly": False,
                },
            },
            needs_review=decision.state is not RiskDecisionState.APPROVE_CANDIDATE,
        )
