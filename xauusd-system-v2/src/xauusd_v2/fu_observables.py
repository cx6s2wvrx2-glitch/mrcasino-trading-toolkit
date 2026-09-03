from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class CandleDirection(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    DOJI = "doji"


@dataclass(frozen=True, slots=True)
class FUObservables:
    """Raw source/code-relevant candle facts, not a FU-validity decision.

    The extra previous-OHLC relationships are deliberately explicit because the
    user-supplied Casino_v7 implementation distinguishes continuation, pullback
    and reversal branches using different combinations of previous open/high/low/
    close. Keeping those facts here lets later research compare source semantics
    with code behavior without turning any helper branch into strategy truth.
    """

    direction: CandleDirection

    swept_previous_high: bool
    swept_previous_low: bool
    swept_both_sides: bool

    close_within_previous_range: bool
    close_above_previous_high: bool
    close_below_previous_low: bool

    close_within_previous_body: bool
    close_above_previous_body: bool
    close_below_previous_body: bool

    close_above_previous_open: bool
    close_below_previous_open: bool
    close_equal_previous_open: bool
    close_above_previous_close: bool
    close_below_previous_close: bool
    close_equal_previous_close: bool

    open_above_previous_open: bool
    open_below_previous_open: bool
    open_equal_previous_open: bool
    open_above_previous_close: bool
    open_below_previous_close: bool
    open_equal_previous_close: bool

    bullish_reversal_candidate: bool
    bearish_reversal_candidate: bool


def extract_fu_observables(
    *,
    open: float,
    high: float,
    low: float,
    close: float,
    previous_open: float,
    previous_high: float,
    previous_low: float,
    previous_close: float,
) -> FUObservables:
    """Extract objective FU-related observables from two consecutive candles.

    This deliberately does NOT return ``valid_fu``. Approved sources evolve from
    an early liquidity+structure description to a later qualitative
    liquidity+opposite-direction description and finally Reflection's
    Complete/Attempted FU closure classes. The supplied Casino_v7/BETA code adds
    useful implementation evidence about previous-OHLC relationships, but does
    not by itself resolve the semantic boundary.

    Until the upstream phrase ``FU criteria met`` is fully certified, these facts
    remain separate and threshold-free.
    """
    values = (
        open,
        high,
        low,
        close,
        previous_open,
        previous_high,
        previous_low,
        previous_close,
    )
    if not all(isfinite(value) for value in values):
        raise ValueError("OHLC values must be finite")
    if high < max(open, close) or low > min(open, close) or low > high:
        raise ValueError("invalid current OHLC geometry")
    if (
        previous_high < max(previous_open, previous_close)
        or previous_low > min(previous_open, previous_close)
        or previous_low > previous_high
    ):
        raise ValueError("invalid previous OHLC geometry")

    if close > open:
        direction = CandleDirection.BULLISH
    elif close < open:
        direction = CandleDirection.BEARISH
    else:
        direction = CandleDirection.DOJI

    swept_high = high > previous_high
    swept_low = low < previous_low

    prev_body_low = min(previous_open, previous_close)
    prev_body_high = max(previous_open, previous_close)

    return FUObservables(
        direction=direction,
        swept_previous_high=swept_high,
        swept_previous_low=swept_low,
        swept_both_sides=swept_high and swept_low,
        close_within_previous_range=previous_low <= close <= previous_high,
        close_above_previous_high=close > previous_high,
        close_below_previous_low=close < previous_low,
        close_within_previous_body=prev_body_low <= close <= prev_body_high,
        close_above_previous_body=close > prev_body_high,
        close_below_previous_body=close < prev_body_low,
        close_above_previous_open=close > previous_open,
        close_below_previous_open=close < previous_open,
        close_equal_previous_open=close == previous_open,
        close_above_previous_close=close > previous_close,
        close_below_previous_close=close < previous_close,
        close_equal_previous_close=close == previous_close,
        open_above_previous_open=open > previous_open,
        open_below_previous_open=open < previous_open,
        open_equal_previous_open=open == previous_open,
        open_above_previous_close=open > previous_close,
        open_below_previous_close=open < previous_close,
        open_equal_previous_close=open == previous_close,
        bullish_reversal_candidate=swept_low and direction is CandleDirection.BULLISH,
        bearish_reversal_candidate=swept_high and direction is CandleDirection.BEARISH,
    )
