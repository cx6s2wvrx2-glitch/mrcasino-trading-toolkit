from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Direction(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"


class ManipulationType(StrEnum):
    FU = "fu"
    X3 = "x3"


class NegationState(StrEnum):
    CONFIRMED = "confirmed"
    NOT_NEGATION = "not_negation"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class NegationResult:
    state: NegationState
    candle_offset: int
    original_direction: Direction
    candidate_direction: Direction | None
    reason: str


def evaluate_negation(
    *,
    original_direction: Direction,
    original_type: ManipulationType,
    candle_offset: int,
    candidate_direction: Direction | None,
    candidate_complete_fu: bool | None,
) -> NegationResult:
    """Evaluate Reflection R-123/R-124/R-126 negation semantics.

    - Negation must oppose the latest manipulation.
    - The valid window is candle +1 or +2.
    - Normally the negating candle must complete as FU.
    - X3 is the explicit exception: its negation need not close as full FU.

    Raw FU/x3 recognition remains upstream and separately certified.
    """
    if candle_offset not in (1, 2):
        return NegationResult(
            NegationState.NOT_NEGATION,
            candle_offset,
            original_direction,
            candidate_direction,
            "negation window is limited to the next two candles",
        )
    if candidate_direction is None:
        return NegationResult(
            NegationState.NOT_CERTIFIED,
            candle_offset,
            original_direction,
            None,
            "candidate direction is missing",
        )
    if candidate_direction is original_direction:
        return NegationResult(
            NegationState.NOT_NEGATION,
            candle_offset,
            original_direction,
            candidate_direction,
            "candidate manipulation is not opposite to the original direction",
        )

    if original_type is ManipulationType.X3:
        return NegationResult(
            NegationState.CONFIRMED,
            candle_offset,
            original_direction,
            candidate_direction,
            "opposite manipulation is within the two-candle window; x3 exception does not require full-FU close",
        )

    if candidate_complete_fu is None:
        return NegationResult(
            NegationState.NOT_CERTIFIED,
            candle_offset,
            original_direction,
            candidate_direction,
            "full-FU completion evidence is required for ordinary FU negation",
        )
    if not candidate_complete_fu:
        return NegationResult(
            NegationState.NOT_NEGATION,
            candle_offset,
            original_direction,
            candidate_direction,
            "ordinary FU negation requires the opposite candle to complete as FU",
        )

    return NegationResult(
        NegationState.CONFIRMED,
        candle_offset,
        original_direction,
        candidate_direction,
        "opposite complete FU occurred within the certified two-candle negation window",
    )
