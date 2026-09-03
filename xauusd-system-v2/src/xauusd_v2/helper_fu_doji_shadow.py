from __future__ import annotations

from dataclasses import dataclass
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
