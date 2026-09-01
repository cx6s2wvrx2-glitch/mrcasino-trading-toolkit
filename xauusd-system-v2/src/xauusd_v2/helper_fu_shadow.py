from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class HelperFUClass(StrEnum):
    NONE = "none"
    FU = "fu"
    ATT = "att_fu"


@dataclass(frozen=True, slots=True)
class CasinoV7ShadowResult:
    bullish: HelperFUClass
    bearish: HelperFUClass
    bullish_branch: str
    bearish_branch: str


@dataclass(frozen=True, slots=True)
class BetaFUShadowResult:
    bullish_fu_candidate: bool
    bearish_fu_candidate: bool
    is_x3: bool
    self_negation_together: bool


def _validate_ohlc(*values: float) -> None:
    if not all(isfinite(value) for value in values):
        raise ValueError("OHLC values must be finite")


def casino_v7_core_shadow(
    *,
    open: float,
    high: float,
    low: float,
    close: float,
    previous_open: float,
    previous_high: float,
    previous_low: float,
    previous_close: float,
) -> CasinoV7ShadowResult:
    """Faithfully reproduce the core FU/ATT decision-tree order in Casino_v7.

    This is implementation evidence only. MA/doji/visual filters are intentionally
    excluded because they are optional helper filters rather than core FU branches.
    Duplicated/subset branches are kept in the same order so unreachable behavior is
    preserved instead of silently 'fixing' the helper.
    """
    _validate_ohlc(
        open,
        high,
        low,
        close,
        previous_open,
        previous_high,
        previous_low,
        previous_close,
    )

    bull = HelperFUClass.NONE
    bull_branch = "none"

    # Bullish continuation FU
    if close > open and low < previous_low and close > previous_close and high > previous_high and close > previous_high:
        bull = HelperFUClass.FU
        bull_branch = "bull_continuation_fu"
    elif close > open and low < previous_low and close > previous_close and high > previous_high and close < previous_high:
        bull = HelperFUClass.ATT
        bull_branch = "bull_continuation_att"
    elif close > open and low < previous_low and close > previous_close and high > previous_high and close < previous_high:
        bull = HelperFUClass.FU
        bull_branch = "bull_continuation_fu_duplicate_unreachable"

    # Bullish pullback FU block
    elif close < open and low < previous_low and close < previous_close and high < previous_high and close > previous_open:
        bull_branch = "bull_pullback_no_value_1"
    elif close < open and low < previous_low and close < previous_close and high > previous_high and close > previous_open:
        bull = HelperFUClass.ATT
        bull_branch = "bull_pullback_att"
    elif close < open and low < previous_low and close < previous_close and high < previous_high and close < previous_open:
        bull_branch = "bull_pullback_no_value_2"
    elif close < open and low < previous_low and close < previous_close and high > previous_high and close < previous_open:
        bull_branch = "bull_pullback_bearish_fu_comment_no_value"

    # Bullish reversal FU block
    elif close > open and low < previous_low and close > previous_close and close < previous_open and high < previous_high:
        bull = HelperFUClass.ATT
        bull_branch = "bull_reversal_att_1"
    elif close > open and low < previous_low and close > previous_close and close < previous_open and high < previous_high:
        bull = HelperFUClass.ATT
        bull_branch = "bull_reversal_att_1_duplicate_unreachable"
    elif close > open and low < previous_low and close > previous_close and close > previous_open and high > previous_high:
        bull = HelperFUClass.ATT
        bull_branch = "bull_reversal_att_2"
    elif close > open and low < previous_low and close > previous_close and close > previous_open and high > previous_high:
        bull = HelperFUClass.ATT
        bull_branch = "bull_reversal_att_2_duplicate_unreachable"
    elif close > open and low < previous_low and close > previous_close and close > previous_open and high > previous_high and close > previous_high:
        bull = HelperFUClass.FU
        bull_branch = "bull_reversal_fu_subset_unreachable"

    bear = HelperFUClass.NONE
    bear_branch = "none"

    # Bearish continuation FU
    if close < open and high > previous_high and close < previous_close and low < previous_low and close < previous_low:
        bear = HelperFUClass.FU
        bear_branch = "bear_continuation_fu"
    elif close < open and high > previous_high and close < previous_close and low > previous_low and close > previous_low:
        bear = HelperFUClass.ATT
        bear_branch = "bear_continuation_att"
    elif close < open and high > previous_high and close < previous_close and low < previous_low and close > previous_low:
        bear = HelperFUClass.FU
        bear_branch = "bear_continuation_fu_inside_range"

    # Bearish pullback FU block
    elif close > open and high > previous_high and open < previous_open and low > previous_low and close < previous_open:
        bear_branch = "bear_pullback_no_value_1"
    elif close > open and high > previous_high and open < previous_open and low < previous_low and close < previous_open:
        bear = HelperFUClass.ATT
        bear_branch = "bear_pullback_att"
    elif close > open and high > previous_high and open < previous_open and low > previous_low and close > previous_open:
        bear_branch = "bear_pullback_no_value_2"
    elif close > open and high > previous_high and open < previous_open and low < previous_low and close > previous_open:
        bear = HelperFUClass.ATT
        bear_branch = "bear_pullback_bullish_fu_comment_att"

    # Bearish reversal FU block
    elif close < open and high > previous_high and close < previous_close and close > previous_open and low > previous_low:
        bear = HelperFUClass.ATT
        bear_branch = "bear_reversal_att_1"
    elif close < open and high > previous_high and close < previous_close and close > previous_open and low < previous_low:
        bear = HelperFUClass.ATT
        bear_branch = "bear_reversal_att_2"
    elif close < open and high > previous_high and close < previous_close and close < previous_open and low > previous_low:
        bear = HelperFUClass.ATT
        bear_branch = "bear_reversal_att_3"
    elif close < open and high > previous_high and close < previous_close and close < previous_open and low < previous_low:
        bear = HelperFUClass.ATT
        bear_branch = "bear_reversal_att_4"
    elif close < open and high > previous_high and close < previous_close and close < previous_open and low < previous_low and close < previous_low:
        bear = HelperFUClass.FU
        bear_branch = "bear_reversal_fu_subset_unreachable"

    return CasinoV7ShadowResult(
        bullish=bull,
        bearish=bear,
        bullish_branch=bull_branch,
        bearish_branch=bear_branch,
    )


def beta_fu_core_shadow(
    *,
    open: float,
    high: float,
    low: float,
    close: float,
    previous_high: float,
    previous_low: float,
) -> BetaFUShadowResult:
    """Reproduce BETA 1 + LAOL's compressed FU candidate predicates.

    The beta has no separate ATT output in this block. It produces broad bull/bear
    FU candidates after excluding its x3 and self-negation-together states.
    """
    _validate_ohlc(open, high, low, close, previous_high, previous_low)

    both_sides = max(open, close) < high and min(open, close) > low
    bear_x3 = high > previous_high and low < previous_low and both_sides and close < open
    bull_x3 = high > previous_high and low < previous_low and both_sides and close > open
    is_x3 = bear_x3 or bull_x3

    sn_bull = (
        high > previous_high
        and low < previous_low
        and max(open, close) < previous_high
        and min(open, close) > previous_low
        and open < close
    )
    sn_bear = (
        high > previous_high
        and low < previous_low
        and min(open, close) > previous_low
        and max(open, close) < previous_high
        and open > close
    )
    sn_together = (sn_bull or sn_bear) and not is_x3

    bearish = (
        high > previous_high
        and close < previous_high
        and close > previous_low
        and not is_x3
        and not sn_together
    )
    bullish = (
        low < previous_low
        and close > previous_low
        and close < previous_high
        and not is_x3
        and not sn_together
    )

    return BetaFUShadowResult(
        bullish_fu_candidate=bullish,
        bearish_fu_candidate=bearish,
        is_x3=is_x3,
        self_negation_together=sn_together,
    )
