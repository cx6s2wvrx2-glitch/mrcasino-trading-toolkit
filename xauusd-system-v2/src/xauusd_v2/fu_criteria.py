from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FUCriteriaState(StrEnum):
    MET = "met"
    NOT_MET = "not_met"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class FUCriteriaResult:
    state: FUCriteriaState
    liquidity_taken: bool | None
    opposite_direction_move: bool | None
    same_candle: bool | None
    reason: str


def evaluate_fu_criteria(
    *,
    liquidity_taken: bool | None,
    opposite_direction_move: bool | None,
    same_candle: bool | None,
) -> FUCriteriaResult:
    """Evaluate the source-backed semantic FU criterion without inventing OHLC geometry.

    Approved Analysis Basics defines FU as a candle that takes liquidity and makes
    a move in the other direction, all in the same candle. This function certifies
    only that semantic conjunction. It deliberately does NOT equate 'liquidity
    taken' with a previous-candle sweep, because approved sources allow multiple
    liquidity forms and the raw mapping remains a separate detector task.
    """
    if liquidity_taken is None or opposite_direction_move is None or same_candle is None:
        return FUCriteriaResult(
            state=FUCriteriaState.NOT_CERTIFIED,
            liquidity_taken=liquidity_taken,
            opposite_direction_move=opposite_direction_move,
            same_candle=same_candle,
            reason="required FU semantic evidence is missing",
        )

    if liquidity_taken and opposite_direction_move and same_candle:
        return FUCriteriaResult(
            state=FUCriteriaState.MET,
            liquidity_taken=True,
            opposite_direction_move=True,
            same_candle=True,
            reason="liquidity taken + opposite-direction move in the same candle",
        )

    return FUCriteriaResult(
        state=FUCriteriaState.NOT_MET,
        liquidity_taken=liquidity_taken,
        opposite_direction_move=opposite_direction_move,
        same_candle=same_candle,
        reason="one or more source-required FU semantic conditions are false",
    )
