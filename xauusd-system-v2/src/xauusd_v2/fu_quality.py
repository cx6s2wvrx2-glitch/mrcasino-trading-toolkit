from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class CandleDirection(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    DOJI = "doji"


@dataclass(frozen=True, slots=True)
class FUQualityMetrics:
    """Objective candle-shape measurements only.

    The approved source describes a desirable/Strong FU qualitatively as a
    strong close with little or no rejection and explicitly warns against being
    too rigid. Explicit user clarification on 2026-09-02 confirms that Strong-FU
    primitive logic is the same on every timeframe; timeframe changes authority
    and downstream context, not this quality concept.

    Therefore this object intentionally contains NO Strong-FU threshold, makes NO
    strong/attempted classification, and has no timeframe-specific branch.
    """

    direction: CandleDirection
    range_size: float
    body_size: float
    body_fraction: float
    upper_wick_fraction: float
    lower_wick_fraction: float
    close_side_rejection_fraction: float
    manipulation_side_wick_fraction: float
    close_location: float


def measure_fu_quality(*, open: float, high: float, low: float, close: float) -> FUQualityMetrics:
    """Measure reproducible FU candle quality without inventing a Strong threshold.

    ``close_location`` is normalized to [0,1], where 0=low and 1=high.
    For bullish candles, close-side rejection is the upper wick; for bearish
    candles, it is the lower wick. The opposite wick is reported as the
    manipulation-side wick. Doji candles are measured but are not classified as
    Strong/Attempted FU here.

    The measurements are timeframe-neutral by contract. Any timeframe weighting
    belongs to the higher-level authority/context layer.
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
    body_fraction = body_size / range_size
    upper_wick = high - max(open, close)
    lower_wick = min(open, close) - low
    upper_wick_fraction = upper_wick / range_size
    lower_wick_fraction = lower_wick / range_size
    close_location = (close - low) / range_size

    if close > open:
        direction = CandleDirection.BULLISH
        close_rejection = upper_wick_fraction
        manipulation_wick = lower_wick_fraction
    elif close < open:
        direction = CandleDirection.BEARISH
        close_rejection = lower_wick_fraction
        manipulation_wick = upper_wick_fraction
    else:
        direction = CandleDirection.DOJI
        # No directional Strong-FU assertion is possible for a doji. These two
        # fields remain measurable summaries rather than a classification.
        close_rejection = min(upper_wick_fraction, lower_wick_fraction)
        manipulation_wick = max(upper_wick_fraction, lower_wick_fraction)

    return FUQualityMetrics(
        direction=direction,
        range_size=range_size,
        body_size=body_size,
        body_fraction=body_fraction,
        upper_wick_fraction=upper_wick_fraction,
        lower_wick_fraction=lower_wick_fraction,
        close_side_rejection_fraction=close_rejection,
        manipulation_side_wick_fraction=manipulation_wick,
        close_location=close_location,
    )
