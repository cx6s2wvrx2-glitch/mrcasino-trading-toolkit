from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class SourceBoundaryState(StrEnum):
    OBSERVED = "observed"
    BLOCKED = "blocked"


class LAOLSourceEvent(StrEnum):
    IDENTIFIED = "identified"
    RESPECTED = "respected"
    TAKEN = "taken"
    R143_MET_EXPLICIT = "r143_met_explicit"
    OTHER_LIQUIDITY = "other_liquidity"


class TFSSourceEvidence(StrEnum):
    CONFIRMED_PREVALENT_DIRECTION = "confirmed_prevalent_direction"
    TIMEFRAME_STRENGTH_CONTEXT = "timeframe_strength_context"
    FORMING_FU_BACKING = "forming_fu_backing"
    LATER_CONFIRMED_CLOSE = "later_confirmed_close"


@dataclass(frozen=True, slots=True)
class SourceBoundaryResult:
    state: SourceBoundaryState
    reason: str


def evaluate_r143_laol_met_source(*, event: LAOLSourceEvent | None) -> SourceBoundaryResult:
    """Fail-closed source boundary for canonical R-143 `LAOL met`.

    Approved Reflection material separately uses LAOL identified/respected/taken
    and the R-143 wording `LAOL met`. Until primary authority explicitly maps
    these terms for the setup being reconstructed, the adapter must not silently
    substitute one for another.
    """
    if event is LAOLSourceEvent.R143_MET_EXPLICIT:
        return SourceBoundaryResult(
            SourceBoundaryState.OBSERVED,
            "source explicitly identifies the canonical R-143 LAOL-met stage",
        )
    if event is None:
        return SourceBoundaryResult(
            SourceBoundaryState.BLOCKED,
            "no source event was supplied for canonical R-143 LAOL met",
        )
    return SourceBoundaryResult(
        SourceBoundaryState.BLOCKED,
        f"source event {event.value!r} is not automatically equivalent to canonical R-143 LAOL met",
    )


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("source evidence timestamps must be timezone-aware")
    return parsed


def evaluate_tfs_source_at_decision_time(
    *,
    evidence: TFSSourceEvidence | None,
    evidence_available_at: str | None,
    decision_time: str | None,
) -> SourceBoundaryResult:
    """Evaluate source-side TFS authority without future leakage.

    TFS requires confirmed prevalent direction. Timeframe-strength commentary or
    a still-forming FU can support context but cannot be promoted to established
    TFS. A confirming close that occurs after the decision time cannot be used
    retroactively to validate the earlier decision.
    """
    if evidence is None or evidence_available_at is None or decision_time is None:
        return SourceBoundaryResult(
            SourceBoundaryState.BLOCKED,
            "complete TFS source evidence and decision timing are required",
        )

    available = _parse_time(evidence_available_at)
    decision = _parse_time(decision_time)
    if available > decision:
        return SourceBoundaryResult(
            SourceBoundaryState.BLOCKED,
            "TFS evidence became available after the decision time and cannot be used retroactively",
        )

    if evidence is TFSSourceEvidence.CONFIRMED_PREVALENT_DIRECTION:
        return SourceBoundaryResult(
            SourceBoundaryState.OBSERVED,
            "confirmed prevalent-direction TFS evidence was available by the decision time",
        )

    return SourceBoundaryResult(
        SourceBoundaryState.BLOCKED,
        f"source evidence {evidence.value!r} is contextual/forming evidence, not confirmed prevalent-direction TFS",
    )
