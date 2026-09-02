from __future__ import annotations

import unittest

from xauusd_v2.fu_criteria import FUCriteriaState
from xauusd_v2.fu_liquidity_bridge import (
    FULiquidityBridgeState,
    evaluate_fu_against_marked_liquidity,
)
from xauusd_v2.liquidity_interaction import LiquiditySide, MarkedLiquidityReference


class FULiquidityBridgeTests(unittest.TestCase):
    def above_reference(self) -> MarkedLiquidityReference:
        return MarkedLiquidityReference(
            reference_id="liq-above-1",
            level=2000.0,
            side=LiquiditySide.ABOVE,
            source_type="approved_marked_liquidity",
        )

    def below_reference(self) -> MarkedLiquidityReference:
        return MarkedLiquidityReference(
            reference_id="liq-below-1",
            level=1990.0,
            side=LiquiditySide.BELOW,
            source_type="approved_marked_liquidity",
        )

    def test_above_liquidity_take_waits_for_intrabar_sequence(self) -> None:
        result = evaluate_fu_against_marked_liquidity(
            reference=self.above_reference(),
            candle_high=2001.0,
            candle_low=1998.0,
            intrabar_opposite_move_after_take=None,
        )
        self.assertEqual(result.state, FULiquidityBridgeState.AWAITING_INTRABAR_SEQUENCE)
        self.assertEqual(result.expected_reversal_direction, "bearish")
        self.assertEqual(result.semantic_result.state, FUCriteriaState.NOT_CERTIFIED)

    def test_below_liquidity_take_waits_for_intrabar_sequence(self) -> None:
        result = evaluate_fu_against_marked_liquidity(
            reference=self.below_reference(),
            candle_high=1993.0,
            candle_low=1989.0,
            intrabar_opposite_move_after_take=None,
        )
        self.assertEqual(result.state, FULiquidityBridgeState.AWAITING_INTRABAR_SEQUENCE)
        self.assertEqual(result.expected_reversal_direction, "bullish")

    def test_certified_opposite_move_after_take_meets_semantic_fu(self) -> None:
        result = evaluate_fu_against_marked_liquidity(
            reference=self.above_reference(),
            candle_high=2001.0,
            candle_low=1998.0,
            intrabar_opposite_move_after_take=True,
        )
        self.assertEqual(result.state, FULiquidityBridgeState.FU_SEMANTIC_MET)
        self.assertEqual(result.semantic_result.state, FUCriteriaState.MET)

    def test_certified_no_opposite_move_after_take_is_not_fu(self) -> None:
        result = evaluate_fu_against_marked_liquidity(
            reference=self.above_reference(),
            candle_high=2001.0,
            candle_low=1998.0,
            intrabar_opposite_move_after_take=False,
        )
        self.assertEqual(result.state, FULiquidityBridgeState.FU_SEMANTIC_NOT_MET)
        self.assertEqual(result.semantic_result.state, FUCriteriaState.NOT_MET)

    def test_exact_touch_does_not_fake_liquidity_take(self) -> None:
        result = evaluate_fu_against_marked_liquidity(
            reference=self.above_reference(),
            candle_high=2000.0,
            candle_low=1998.0,
            intrabar_opposite_move_after_take=True,
        )
        self.assertEqual(result.state, FULiquidityBridgeState.NO_LIQUIDITY_TAKE)
        self.assertEqual(result.semantic_result.state, FUCriteriaState.NOT_MET)

    def test_previous_candle_high_is_not_required_when_reference_is_explicit(self) -> None:
        result = evaluate_fu_against_marked_liquidity(
            reference=MarkedLiquidityReference(
                reference_id="doji-liquidity-older-than-prev-candle",
                level=2010.0,
                side=LiquiditySide.ABOVE,
                source_type="unmanipulated_doji",
            ),
            candle_high=2011.0,
            candle_low=2004.0,
            intrabar_opposite_move_after_take=True,
        )
        self.assertEqual(result.state, FULiquidityBridgeState.FU_SEMANTIC_MET)


if __name__ == "__main__":
    unittest.main()
