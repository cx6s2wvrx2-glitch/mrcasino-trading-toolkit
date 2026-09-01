from __future__ import annotations

import unittest

from xauusd_v2.liquidity_interaction import (
    LiquidityInteractionState,
    LiquiditySide,
    MarkedLiquidityReference,
    evaluate_marked_liquidity_interaction,
)


class LiquidityInteractionTests(unittest.TestCase):
    def test_above_liquidity_is_taken_only_beyond_level(self) -> None:
        ref = MarkedLiquidityReference("liq-1", 110.0, LiquiditySide.ABOVE, "doji")
        result = evaluate_marked_liquidity_interaction(reference=ref, candle_high=111.0, candle_low=100.0)
        self.assertEqual(result.state, LiquidityInteractionState.TAKEN)

    def test_above_liquidity_exact_touch_is_not_taken(self) -> None:
        ref = MarkedLiquidityReference("liq-1", 110.0, LiquiditySide.ABOVE, "doji")
        result = evaluate_marked_liquidity_interaction(reference=ref, candle_high=110.0, candle_low=100.0)
        self.assertEqual(result.state, LiquidityInteractionState.TOUCHED)

    def test_above_liquidity_can_remain_untouched(self) -> None:
        ref = MarkedLiquidityReference("liq-1", 110.0, LiquiditySide.ABOVE, "doji")
        result = evaluate_marked_liquidity_interaction(reference=ref, candle_high=109.0, candle_low=100.0)
        self.assertEqual(result.state, LiquidityInteractionState.UNTOUCHED)

    def test_below_liquidity_is_taken_only_beyond_level(self) -> None:
        ref = MarkedLiquidityReference("liq-2", 95.0, LiquiditySide.BELOW, "double_bottom")
        result = evaluate_marked_liquidity_interaction(reference=ref, candle_high=105.0, candle_low=94.0)
        self.assertEqual(result.state, LiquidityInteractionState.TAKEN)

    def test_below_liquidity_exact_touch_is_not_taken(self) -> None:
        ref = MarkedLiquidityReference("liq-2", 95.0, LiquiditySide.BELOW, "double_bottom")
        result = evaluate_marked_liquidity_interaction(reference=ref, candle_high=105.0, candle_low=95.0)
        self.assertEqual(result.state, LiquidityInteractionState.TOUCHED)

    def test_source_type_is_provenance_not_strategy_validation(self) -> None:
        ref = MarkedLiquidityReference("liq-3", 110.0, LiquiditySide.ABOVE, "unverified_custom_level")
        result = evaluate_marked_liquidity_interaction(reference=ref, candle_high=111.0, candle_low=100.0)
        self.assertEqual(result.state, LiquidityInteractionState.TAKEN)
        self.assertEqual(result.reference_id, "liq-3")

    def test_missing_reference_id_is_rejected(self) -> None:
        ref = MarkedLiquidityReference("", 110.0, LiquiditySide.ABOVE, "doji")
        with self.assertRaises(ValueError):
            evaluate_marked_liquidity_interaction(reference=ref, candle_high=111.0, candle_low=100.0)

    def test_invalid_candle_geometry_is_rejected(self) -> None:
        ref = MarkedLiquidityReference("liq-4", 110.0, LiquiditySide.ABOVE, "doji")
        with self.assertRaises(ValueError):
            evaluate_marked_liquidity_interaction(reference=ref, candle_high=99.0, candle_low=100.0)


if __name__ == "__main__":
    unittest.main()
