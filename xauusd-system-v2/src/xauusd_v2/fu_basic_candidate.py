from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class BasicFUCandidateState(StrEnum):
    BULLISH = "bullish_candidate"
    BEARISH = "bearish_candidate"
    NONE = "none"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class BasicFUCandidateResult:
    state: BasicFUCandidateState
    swept_previous_high: bool
    swept_previous_low: bool
    candle_bullish: bool
    candle_bearish: bool
    reason: str


def classify_basic_fu_candidate(
    *,
    open: float,
    high: float,
    low: float,
    close: float,
    previous_high: float,
    previous_low: float,
) -> BasicFUCandidateResult:
    """Map the simplest approved FU semantics to raw previous-candle OHLC.

    Approved Analysis Basics states that an FU takes liquidity and moves in the
    opposite direction in the same candle, and separately notes that the FU takes
    the previous candle's liquidity. This narrow layer therefore recognizes only:

    - previous-low sweep + bullish current candle -> bullish candidate
    - previous-high sweep + bearish current candle -> bearish candidate

    It deliberately fails closed on both-side sweeps because x3/self-negation and
    other advanced constructs can occupy that geometry. It also does not detect
    Reflection ATT Form 1, which explicitly may make no new high/low.
    """
    values = (open, high, low, close, previous_high, previous_low)
    if not all(isfinite(value) for value in values):
        raise ValueError("OHLC values must be finite")
    if high < max(open, close) or low > min(open, close) or low > high:
        raise ValueError("invalid current OHLC geometry")
    if previous_low > previous_high:
        raise ValueError("invalid previous high/low geometry")

    swept_high = high > previous_high
    swept_low = low < previous_low
    bullish = close > open
    bearish = close < open

    if swept_high and swept_low:
        return BasicFUCandidateResult(
            state=BasicFUCandidateState.AMBIGUOUS,
            swept_previous_high=True,
            swept_previous_low=True,
            candle_bullish=bullish,
            candle_bearish=bearish,
            reason="both previous extremes were swept; advanced manipulation classification required",
        )

    if swept_low and bullish:
        return BasicFUCandidateResult(
            state=BasicFUCandidateState.BULLISH,
            swept_previous_high=False,
            swept_previous_low=True,
            candle_bullish=True,
            candle_bearish=False,
            reason="previous-low liquidity swept and candle moved bullish in the same candle",
        )

    if swept_high and bearish:
        return BasicFUCandidateResult(
            state=BasicFUCandidateState.BEARISH,
            swept_previous_high=True,
            swept_previous_low=False,
            candle_bullish=False,
            candle_bearish=True,
            reason="previous-high liquidity swept and candle moved bearish in the same candle",
        )

    return BasicFUCandidateResult(
        state=BasicFUCandidateState.NONE,
        swept_previous_high=swept_high,
        swept_previous_low=swept_low,
        candle_bullish=bullish,
        candle_bearish=bearish,
        reason="basic previous-candle liquidity + opposite-move conjunction is not present",
    )
