from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..models import AgentRunResult
from .base import AgentContractError


class Direction(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    UNKNOWN = "unknown"


class ContextState(StrEnum):
    ALIGNED_BULLISH = "aligned_bullish"
    ALIGNED_BEARISH = "aligned_bearish"
    CONFLICTING = "conflicting"
    AMBIGUOUS = "ambiguous"
    NO_CONTEXT = "no_context"


@dataclass(frozen=True, slots=True)
class MarketContextInput:
    prevalent_htf_direction: Direction = Direction.UNKNOWN
    established_tfs_direction: Direction = Direction.UNKNOWN
    major_liquidity_target_direction: Direction = Direction.UNKNOWN
    active_zone_direction: Direction = Direction.UNKNOWN
    has_provisional_required_input: bool = False
    has_unresolved_required_input: bool = False
    source_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MarketContextReport:
    state: ContextState
    aligned_direction: Direction
    known_direction_count: int
    reasons: tuple[str, ...]
    source_refs: tuple[str, ...]


class MarketStateAgent:
    """Consistency/context foundation. It does not create strategy primitives."""

    name = "market_state_agent_04"
    version = "0.1.0"

    def evaluate(self, context: MarketContextInput) -> tuple[MarketContextReport, AgentRunResult]:
        if not all(ref.strip() for ref in context.source_refs):
            raise AgentContractError("source_refs cannot contain empty provenance references")

        if context.has_provisional_required_input:
            report = MarketContextReport(
                state=ContextState.AMBIGUOUS,
                aligned_direction=Direction.UNKNOWN,
                known_direction_count=0,
                reasons=("At least one required context input is provisional/unconfirmed.",),
                source_refs=context.source_refs,
            )
            return report, self._run(report)

        if context.has_unresolved_required_input:
            report = MarketContextReport(
                state=ContextState.AMBIGUOUS,
                aligned_direction=Direction.UNKNOWN,
                known_direction_count=0,
                reasons=("At least one required context input is unresolved.",),
                source_refs=context.source_refs,
            )
            return report, self._run(report)

        directional_values = (
            context.prevalent_htf_direction,
            context.established_tfs_direction,
            context.major_liquidity_target_direction,
            context.active_zone_direction,
        )
        known = tuple(value for value in directional_values if value is not Direction.UNKNOWN)

        if not known:
            report = MarketContextReport(
                state=ContextState.NO_CONTEXT,
                aligned_direction=Direction.UNKNOWN,
                known_direction_count=0,
                reasons=("No confirmed directional context inputs are available.",),
                source_refs=context.source_refs,
            )
            return report, self._run(report)

        unique = set(known)
        if len(unique) > 1:
            report = MarketContextReport(
                state=ContextState.CONFLICTING,
                aligned_direction=Direction.UNKNOWN,
                known_direction_count=len(known),
                reasons=("Confirmed directional inputs disagree; context cannot be treated as aligned.",),
                source_refs=context.source_refs,
            )
            return report, self._run(report)

        direction = known[0]
        state = ContextState.ALIGNED_BULLISH if direction is Direction.BULLISH else ContextState.ALIGNED_BEARISH
        report = MarketContextReport(
            state=state,
            aligned_direction=direction,
            known_direction_count=len(known),
            reasons=("All currently known confirmed directional inputs agree.",),
            source_refs=context.source_refs,
        )
        return report, self._run(report)

    def _run(self, report: MarketContextReport) -> AgentRunResult:
        return AgentRunResult(
            agent_name=self.name,
            agent_version=self.version,
            input_refs=report.source_refs,
            payload={
                "state": report.state.value,
                "aligned_direction": report.aligned_direction.value,
                "known_direction_count": report.known_direction_count,
                "reasons": list(report.reasons),
            },
            needs_review=report.state not in {ContextState.ALIGNED_BULLISH, ContextState.ALIGNED_BEARISH},
        )
