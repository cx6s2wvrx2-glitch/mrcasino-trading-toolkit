from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class LiquiditySide(StrEnum):
    ABOVE = "above"
    BELOW = "below"


class LiquidityInteractionState(StrEnum):
    UNTOUCHED = "untouched"
    TOUCHED = "touched"
    TAKEN = "taken"


@dataclass(frozen=True, slots=True)
class MarkedLiquidityReference:
    reference_id: str
    level: float
    side: LiquiditySide
    source_type: str


@dataclass(frozen=True, slots=True)
class LiquidityInteractionResult:
    reference_id: str
    state: LiquidityInteractionState
    extreme_price: float
    level: float
    side: LiquiditySide
    reason: str


def evaluate_marked_liquidity_interaction(
    *,
    reference: MarkedLiquidityReference,
    candle_high: float,
    candle_low: float,
) -> LiquidityInteractionResult:
    """Evaluate interaction with an already-marked liquidity level.

    This layer does not decide whether a level is valid/major/core liquidity. That
    authority belongs to upstream certified liquidity detectors or human-labelled
    ground truth. It only answers whether the current candle left the supplied
    level untouched, touched it exactly, or traded beyond it (taken).

    Prices are expected to be broker-normalized before this function is called.
    No hidden tolerance is applied.
    """
    if not reference.reference_id.strip():
        raise ValueError("reference_id is required")
    if not reference.source_type.strip():
        raise ValueError("source_type is required")
    if not all(isfinite(v) for v in (reference.level, candle_high, candle_low)):
        raise ValueError("prices must be finite")
    if candle_low > candle_high:
        raise ValueError("candle_low cannot exceed candle_high")

    if reference.side is LiquiditySide.ABOVE:
        extreme = candle_high
        if extreme > reference.level:
            state = LiquidityInteractionState.TAKEN
            reason = "candle high traded beyond marked above-price liquidity"
        elif extreme == reference.level:
            state = LiquidityInteractionState.TOUCHED
            reason = "candle high touched marked above-price liquidity exactly"
        else:
            state = LiquidityInteractionState.UNTOUCHED
            reason = "candle high remained below marked above-price liquidity"
    else:
        extreme = candle_low
        if extreme < reference.level:
            state = LiquidityInteractionState.TAKEN
            reason = "candle low traded beyond marked below-price liquidity"
        elif extreme == reference.level:
            state = LiquidityInteractionState.TOUCHED
            reason = "candle low touched marked below-price liquidity exactly"
        else:
            state = LiquidityInteractionState.UNTOUCHED
            reason = "candle low remained above marked below-price liquidity"

    return LiquidityInteractionResult(
        reference_id=reference.reference_id,
        state=state,
        extreme_price=extreme,
        level=reference.level,
        side=reference.side,
        reason=reason,
    )
