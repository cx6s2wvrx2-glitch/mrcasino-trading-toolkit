from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .fu_criteria import FUCriteriaResult, FUCriteriaState, evaluate_fu_criteria
from .liquidity_interaction import (
    LiquidityInteractionState,
    LiquiditySide,
    MarkedLiquidityReference,
    evaluate_marked_liquidity_interaction,
)


class FULiquidityBridgeState(StrEnum):
    NO_LIQUIDITY_TAKE = "no_liquidity_take"
    AWAITING_INTRABAR_SEQUENCE = "awaiting_intrabar_sequence"
    FU_SEMANTIC_MET = "fu_semantic_met"
    FU_SEMANTIC_NOT_MET = "fu_semantic_not_met"


@dataclass(frozen=True, slots=True)
class FULiquidityBridgeResult:
    state: FULiquidityBridgeState
    reference_id: str
    liquidity_side: LiquiditySide
    liquidity_interaction: LiquidityInteractionState
    expected_reversal_direction: str
    semantic_result: FUCriteriaResult
    reason: str


def evaluate_fu_against_marked_liquidity(
    *,
    reference: MarkedLiquidityReference,
    candle_high: float,
    candle_low: float,
    intrabar_opposite_move_after_take: bool | None,
) -> FULiquidityBridgeResult:
    """Bridge marked-liquidity evidence into the semantic FU contract.

    Approved Casino material allows an FU to take liquidity of different kinds in
    different areas. Therefore the liquidity reference is supplied explicitly by
    an upstream certified detector or labelled example rather than guessed from
    the previous candle.

    A parent OHLC candle is sufficient to prove whether the supplied level traded
    beyond its marked liquidity reference. It is *not* sufficient to prove the
    temporal phrase "takes liquidity and then reverses in the opposite direction"
    because OHLC does not preserve the intrabar path. That second fact must come
    from lower-timeframe/tick evidence or approved labelled source evidence.
    """
    interaction = evaluate_marked_liquidity_interaction(
        reference=reference,
        candle_high=candle_high,
        candle_low=candle_low,
    )
    expected_direction = "bearish" if reference.side is LiquiditySide.ABOVE else "bullish"

    if interaction.state is not LiquidityInteractionState.TAKEN:
        semantic = evaluate_fu_criteria(
            liquidity_taken=False,
            opposite_direction_move=False,
            same_candle=True,
        )
        return FULiquidityBridgeResult(
            state=FULiquidityBridgeState.NO_LIQUIDITY_TAKE,
            reference_id=reference.reference_id,
            liquidity_side=reference.side,
            liquidity_interaction=interaction.state,
            expected_reversal_direction=expected_direction,
            semantic_result=semantic,
            reason="the supplied marked liquidity was not traded beyond, so the FU liquidity prerequisite is absent",
        )

    if intrabar_opposite_move_after_take is None:
        semantic = evaluate_fu_criteria(
            liquidity_taken=True,
            opposite_direction_move=None,
            same_candle=None,
        )
        return FULiquidityBridgeResult(
            state=FULiquidityBridgeState.AWAITING_INTRABAR_SEQUENCE,
            reference_id=reference.reference_id,
            liquidity_side=reference.side,
            liquidity_interaction=interaction.state,
            expected_reversal_direction=expected_direction,
            semantic_result=semantic,
            reason="liquidity take is objective, but parent OHLC cannot certify that the opposite move occurred after the take inside the same candle",
        )

    semantic = evaluate_fu_criteria(
        liquidity_taken=True,
        opposite_direction_move=intrabar_opposite_move_after_take,
        same_candle=True,
    )
    state = (
        FULiquidityBridgeState.FU_SEMANTIC_MET
        if semantic.state is FUCriteriaState.MET
        else FULiquidityBridgeState.FU_SEMANTIC_NOT_MET
    )
    return FULiquidityBridgeResult(
        state=state,
        reference_id=reference.reference_id,
        liquidity_side=reference.side,
        liquidity_interaction=interaction.state,
        expected_reversal_direction=expected_direction,
        semantic_result=semantic,
        reason=(
            "marked liquidity take plus certified same-candle opposite move satisfies the semantic FU criterion"
            if semantic.state is FUCriteriaState.MET
            else "marked liquidity was taken, but certified intrabar evidence does not show the required opposite move after the take"
        ),
    )
