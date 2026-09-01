from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isclose, isfinite


class CandleDirection(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    DOJI = "doji"


@dataclass(frozen=True, slots=True)
class ImbalancedCandleObservables:
    """Objective single-candle geometry for later IMB certification.

    Primary Casino material supports an ``imbalanced candle`` as a liquidity
    construct, but the exact raw equality/tolerance is not yet certified.
    Casino_v7's open==low/open==high logic is therefore retained only as an
    observable hypothesis, never as a strategy classification in this module.
    """

    direction: CandleDirection
    range_size: float
    body_fraction: float
    upper_wick_fraction: float
    lower_wick_fraction: float
    open_distance_from_low_fraction: float
    high_distance_from_open_fraction: float
    close_distance_from_low_fraction: float
    high_distance_from_close_fraction: float
    open_equals_low_exact: bool
    open_equals_high_exact: bool


def measure_imbalanced_candle_observables(
    *,
    open: float,
    high: float,
    low: float,
    close: float,
) -> ImbalancedCandleObservables:
    """Measure candidate imbalanced-candle geometry without classifying IMB.

    No tolerance, pip threshold, tick threshold, or broker-specific epsilon is
    embedded. Exact equality flags are reported as raw facts only. A future
    certified detector must explicitly define broker precision/tolerance and be
    validated against primary labelled examples.
    """
    prices = (open, high, low, close)
    if not all(isfinite(value) for value in prices):
        raise ValueError("OHLC values must be finite")
    if high < max(open, close) or low > min(open, close) or low > high:
        raise ValueError("invalid OHLC geometry")

    range_size = high - low
    if range_size <= 0:
        raise ValueError("candle range must be positive")

    body_size = abs(close - open)
    upper_wick = high - max(open, close)
    lower_wick = min(open, close) - low

    if close > open:
        direction = CandleDirection.BULLISH
    elif close < open:
        direction = CandleDirection.BEARISH
    else:
        direction = CandleDirection.DOJI

    return ImbalancedCandleObservables(
        direction=direction,
        range_size=range_size,
        body_fraction=body_size / range_size,
        upper_wick_fraction=upper_wick / range_size,
        lower_wick_fraction=lower_wick / range_size,
        open_distance_from_low_fraction=(open - low) / range_size,
        high_distance_from_open_fraction=(high - open) / range_size,
        close_distance_from_low_fraction=(close - low) / range_size,
        high_distance_from_close_fraction=(high - close) / range_size,
        open_equals_low_exact=isclose(open, low, rel_tol=0.0, abs_tol=0.0),
        open_equals_high_exact=isclose(open, high, rel_tol=0.0, abs_tol=0.0),
    )
