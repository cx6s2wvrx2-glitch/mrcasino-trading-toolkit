from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

from .helper_fu_shadow import CasinoV7ShadowResult, HelperFUClass


@dataclass(frozen=True, slots=True)
class CasinoV7DojiFilterShadowResult:
    """Faithful implementation evidence for Casino_v7's current-candle doji filter.

    `body_ratio_threshold` is an implementation parameter copied from the supplied
    helper (default 0.30 there). It is NOT a certified Casino strategy threshold.

    The original helper's final current-candle doji check clears ordinary FU flags
    but does not clear ATT-FU flags. This function reproduces only that behavior.
    """

    is_doji_by_helper_parameter: bool
    body_ratio_threshold: float
    bullish_before_filter: HelperFUClass
    bearish_before_filter: HelperFUClass
    bullish_after_filter: HelperFUClass
    bearish_after_filter: HelperFUClass
    helper_parameter_is_strategy_truth: bool
    strategy_truth_changed: bool


def apply_casino_v7_current_doji_filter(
    *,
    open: float,
    high: float,
    low: float,
    close: float,
    branch_result: CasinoV7ShadowResult,
    body_ratio_threshold: float = 0.30,
) -> CasinoV7DojiFilterShadowResult:
    values = (open, high, low, close, body_ratio_threshold)
    if not all(isfinite(value) for value in values):
        raise ValueError("values must be finite")
    if low > high or low > min(open, close) or high < max(open, close):
        raise ValueError("invalid OHLC geometry")
    if not 0.0 <= body_ratio_threshold <= 1.0:
        raise ValueError("body_ratio_threshold must be within [0, 1]")

    candle_range = high - low
    is_doji = (
        candle_range == 0.0
        or abs(open - close) <= candle_range * body_ratio_threshold
    )

    bullish_after = branch_result.bullish
    bearish_after = branch_result.bearish

    if is_doji:
        if bullish_after is HelperFUClass.FU:
            bullish_after = HelperFUClass.NONE
        if bearish_after is HelperFUClass.FU:
            bearish_after = HelperFUClass.NONE

    return CasinoV7DojiFilterShadowResult(
        is_doji_by_helper_parameter=is_doji,
        body_ratio_threshold=body_ratio_threshold,
        bullish_before_filter=branch_result.bullish,
        bearish_before_filter=branch_result.bearish,
        bullish_after_filter=bullish_after,
        bearish_after_filter=bearish_after,
        helper_parameter_is_strategy_truth=False,
        strategy_truth_changed=False,
    )


def apply_casino_v7_default_visible_filters(
    *,
    open: float,
    high: float,
    low: float,
    close: float,
    branch_result: CasinoV7ShadowResult,
    body_ratio_threshold: float = 0.30,
) -> CasinoV7DojiFilterShadowResult:
    """Replay the default visible Casino_v7 filters used after its FU branches.

    Casino_v7 defaults ``useBearBull`` to true. After the optional MA / leading-doji
    gates (both default false), the script removes a bearish ATT marker from a bullish
    candle and removes a bullish ATT marker from a bearish candle. The later current-
    candle doji gate then removes only ordinary FU markers. This helper reproduces the
    default visible output order without enabling the optional MA or leading-doji gates.

    This remains supplied-code implementation evidence only; it does not certify the
    strategy semantics or promote the helper's 0.30 doji parameter to strategy truth.
    """

    filtered = apply_casino_v7_current_doji_filter(
        open=open,
        high=high,
        low=low,
        close=close,
        branch_result=branch_result,
        body_ratio_threshold=body_ratio_threshold,
    )
    bullish_after = filtered.bullish_after_filter
    bearish_after = filtered.bearish_after_filter

    # Supplied Casino_v7 default: useBearBull = true.
    if open < close and bearish_after is HelperFUClass.ATT:
        bearish_after = HelperFUClass.NONE
    elif open > close and bullish_after is HelperFUClass.ATT:
        bullish_after = HelperFUClass.NONE

    return replace(
        filtered,
        bullish_after_filter=bullish_after,
        bearish_after_filter=bearish_after,
    )
