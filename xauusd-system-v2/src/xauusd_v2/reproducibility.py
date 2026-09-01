from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ObservationState(StrEnum):
    PROVISIONAL = "provisional"
    CONFIRMED = "confirmed"


@dataclass(frozen=True, slots=True)
class HistoricalEvidence:
    evidence_id: str
    observed_at: datetime
    known_at: datetime
    state: ObservationState
    source_timeframe: str

    def __post_init__(self) -> None:
        if self.known_at < self.observed_at:
            raise ValueError("known_at cannot precede observed_at")


@dataclass(frozen=True, slots=True)
class HistoricalDecisionContext:
    decision_at: datetime
    evidence: tuple[HistoricalEvidence, ...]


def future_information_ids(context: HistoricalDecisionContext) -> tuple[str, ...]:
    """Return evidence that was not knowable at the historical decision timestamp."""
    return tuple(
        item.evidence_id
        for item in context.evidence
        if item.known_at > context.decision_at
    )


def assert_no_future_information(context: HistoricalDecisionContext) -> None:
    future_ids = future_information_ids(context)
    if future_ids:
        joined = ", ".join(future_ids)
        raise ValueError(f"future information detected: {joined}")


def confirmed_evidence_available(
    evidence: HistoricalEvidence,
    *,
    decision_at: datetime,
) -> bool:
    """Confirmed evidence is usable only after its confirmation became knowable."""
    return (
        evidence.state is ObservationState.CONFIRMED
        and evidence.known_at <= decision_at
    )


def provisional_evidence_available(
    evidence: HistoricalEvidence,
    *,
    decision_at: datetime,
) -> bool:
    """Provisional evidence may be visible live but must remain explicitly provisional."""
    return (
        evidence.state is ObservationState.PROVISIONAL
        and evidence.known_at <= decision_at
    )


def historical_label_is_reproducible(
    context: HistoricalDecisionContext,
    *,
    required_confirmed_ids: tuple[str, ...] = (),
) -> bool:
    """Fail closed if any required evidence is future, missing, or only provisional."""
    if future_information_ids(context):
        return False

    by_id = {item.evidence_id: item for item in context.evidence}
    for required_id in required_confirmed_ids:
        item = by_id.get(required_id)
        if item is None:
            return False
        if not confirmed_evidence_available(item, decision_at=context.decision_at):
            return False

    return True
