from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class FUCompletionClass(StrEnum):
    NOT_CERTIFIED = "not_certified"
    ATTEMPTED_FU_FORM_1 = "attempted_fu_form_1"
    ATTEMPTED_FU_FORM_2 = "attempted_fu_form_2"
    COMPLETE_FU = "complete_fu"


@dataclass(frozen=True, slots=True)
class FUCompletionResult:
    classification: FUCompletionClass
    previous_body_low: float
    previous_body_high: float
    close_within_previous_body: bool | None
    reason: str


def classify_fu_completion(
    *,
    new_high_or_low: bool | None,
    fu_criteria_met: bool | None,
    close: float,
    previous_open: float,
    previous_close: float,
) -> FUCompletionResult:
    """Classify FU completion only after upstream FU-candidate logic is supplied.

    Primary Reflection R-120..R-122 supports this narrow classifier:
    - no new high/low -> Attempted FU form 1;
    - FU criteria met + close within previous candle open/close -> Complete FU;
    - new high/low + FU setup but no closure within previous body -> Attempted FU form 2.

    Timeframe-scope contract (explicit user clarification, 2026-09-02):
    this FU/ATT-FU primitive logic is timeframe-neutral. The same classifier is
    conceptually applicable on every timeframe. Timeframe authority and
    downstream use are evaluated elsewhere and must not change the primitive
    completion definition.

    This function deliberately does NOT decide whether the broader ``FU criteria``
    are met from raw OHLC. That predicate remains a separate certification task.
    """
    prices = (close, previous_open, previous_close)
    if not all(isfinite(value) for value in prices):
        raise ValueError("FU completion prices must be finite")

    body_low = min(previous_open, previous_close)
    body_high = max(previous_open, previous_close)

    if new_high_or_low is None:
        return FUCompletionResult(
            FUCompletionClass.NOT_CERTIFIED,
            body_low,
            body_high,
            None,
            "new-high/low evidence is missing",
        )

    if not new_high_or_low:
        return FUCompletionResult(
            FUCompletionClass.ATTEMPTED_FU_FORM_1,
            body_low,
            body_high,
            body_low <= close <= body_high,
            "no new high/low; primary Reflection classifies this as Attempted FU form 1",
        )

    if fu_criteria_met is not True:
        return FUCompletionResult(
            FUCompletionClass.NOT_CERTIFIED,
            body_low,
            body_high,
            body_low <= close <= body_high,
            "new high/low exists but upstream FU criteria are not certified as met",
        )

    close_inside = body_low <= close <= body_high
    if close_inside:
        return FUCompletionResult(
            FUCompletionClass.COMPLETE_FU,
            body_low,
            body_high,
            True,
            "FU criteria met and close is within previous candle open/close",
        )

    return FUCompletionResult(
        FUCompletionClass.ATTEMPTED_FU_FORM_2,
        body_low,
        body_high,
        False,
        "new high/low and FU setup present, but closure is not within previous candle body",
    )
