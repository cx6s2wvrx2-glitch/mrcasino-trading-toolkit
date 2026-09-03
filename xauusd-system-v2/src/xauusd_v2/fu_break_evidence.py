from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class FUCandidateDirection(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"


class PreviousCandleBreakState(StrEnum):
    NO_OPPOSITE_EXTREME_BREAK = "no_opposite_extreme_break"
    WICK_BREAK_WITHOUT_CLOSE_THROUGH = "wick_break_without_close_through"
    CLOSE_THROUGH_OPPOSITE_EXTREME = "close_through_opposite_extreme"


@dataclass(frozen=True, slots=True)
class FUPreviousCandleBreakEvidence:
    """Objective previous-candle break facts for one hypothesized FU direction.

    This is not an FU classifier. The candidate direction only determines which
    previous-candle side is the manipulation side and which side is the opposite
    structural extreme:

    - bullish hypothesis: manipulation side = previous low, opposite side = previous high;
    - bearish hypothesis: manipulation side = previous high, opposite side = previous low.

    Whether the manipulation-side excursion actually took source-valid liquidity,
    whether the opposite break happened after that take, and whether the overall FU
    criteria are met remain external semantic questions.
    """

    direction: FUCandidateDirection
    manipulation_side_previous_extreme_swept: bool
    opposite_side_previous_extreme_broken: bool
    close_through_opposite_extreme: bool
    close_back_within_previous_range: bool
    break_state: PreviousCandleBreakState

    fu_semantics_certified: bool
    sequence_after_liquidity_take_certified: bool
    strategy_truth_changed: bool


def assess_previous_candle_break(
    *,
    direction: FUCandidateDirection,
    high: float,
    low: float,
    close: float,
    previous_high: float,
    previous_low: float,
) -> FUPreviousCandleBreakEvidence:
    """Separate structural excursion from final close position.

    Strict inequalities mirror the user-supplied implementation comparisons:
    merely touching an old extreme is not recorded as breaking it.
    """

    values = (high, low, close, previous_high, previous_low)
    if not all(isfinite(value) for value in values):
        raise ValueError("price values must be finite")
    if low > high:
        raise ValueError("current low cannot exceed current high")
    if previous_low > previous_high:
        raise ValueError("previous low cannot exceed previous high")
    if close < low or close > high:
        raise ValueError("close must lie within current high/low")

    if direction is FUCandidateDirection.BULLISH:
        manipulation_swept = low < previous_low
        opposite_broken = high > previous_high
        close_through = close > previous_high
    elif direction is FUCandidateDirection.BEARISH:
        manipulation_swept = high > previous_high
        opposite_broken = low < previous_low
        close_through = close < previous_low
    else:  # defensive for non-enum callers
        raise ValueError(f"unsupported FU candidate direction: {direction!r}")

    if close_through:
        state = PreviousCandleBreakState.CLOSE_THROUGH_OPPOSITE_EXTREME
    elif opposite_broken:
        state = PreviousCandleBreakState.WICK_BREAK_WITHOUT_CLOSE_THROUGH
    else:
        state = PreviousCandleBreakState.NO_OPPOSITE_EXTREME_BREAK

    return FUPreviousCandleBreakEvidence(
        direction=direction,
        manipulation_side_previous_extreme_swept=manipulation_swept,
        opposite_side_previous_extreme_broken=opposite_broken,
        close_through_opposite_extreme=close_through,
        close_back_within_previous_range=previous_low <= close <= previous_high,
        break_state=state,
        fu_semantics_certified=False,
        sequence_after_liquidity_take_certified=False,
        strategy_truth_changed=False,
    )
