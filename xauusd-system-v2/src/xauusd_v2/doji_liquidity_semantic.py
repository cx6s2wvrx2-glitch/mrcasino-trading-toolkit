from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DojiLiquidityState(StrEnum):
    CORE_UNMANIPULATED = "core_unmanipulated"
    MANIPULATED_NOT_CORE = "manipulated_not_core"
    OUTSIDE_PREVIOUS_WICK_ATTEMPTED_FU = "outside_previous_wick_attempted_fu"
    NOT_DOJI = "not_doji"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class DojiLiquidityResult:
    state: DojiLiquidityState
    core_liquidity_eligible: bool
    attempted_fu_context: bool
    reason: str


def classify_doji_liquidity(
    *,
    is_doji: bool | None,
    inside_previous_wick: bool | None,
    manipulates_last_high_or_low: bool | None,
) -> DojiLiquidityResult:
    """Classify source-backed doji liquidity semantics without inventing doji geometry.

    Source-grounded boundaries used here:
    - core/true doji: inside a previous wick AND does not manipulate last high/low;
    - manipulated doji: breaks/manipulates the last high/low -> not core liquidity;
    - doji outside the previous wick -> Attempted-FU context, not core major doji.

    `is_doji` must come from a separately certified detector or human-labelled source.
    This function deliberately contains no body-ratio/doji threshold.
    """
    if is_doji is None or inside_previous_wick is None or manipulates_last_high_or_low is None:
        return DojiLiquidityResult(
            DojiLiquidityState.NOT_CERTIFIED,
            False,
            False,
            "required doji/liquidity evidence is missing",
        )

    if not is_doji:
        return DojiLiquidityResult(
            DojiLiquidityState.NOT_DOJI,
            False,
            False,
            "upstream evidence does not classify the candle as a doji",
        )

    if not inside_previous_wick:
        return DojiLiquidityResult(
            DojiLiquidityState.OUTSIDE_PREVIOUS_WICK_ATTEMPTED_FU,
            False,
            True,
            "source classifies a doji outside the last wick as Attempted-FU context, not core major doji liquidity",
        )

    if manipulates_last_high_or_low:
        return DojiLiquidityResult(
            DojiLiquidityState.MANIPULATED_NOT_CORE,
            False,
            False,
            "doji manipulates the last high/low and is not marked as core doji liquidity",
        )

    return DojiLiquidityResult(
        DojiLiquidityState.CORE_UNMANIPULATED,
        True,
        False,
        "doji is inside the previous wick and does not manipulate the last high/low",
    )
