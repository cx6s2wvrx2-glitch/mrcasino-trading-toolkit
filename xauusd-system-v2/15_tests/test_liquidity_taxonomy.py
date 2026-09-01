from __future__ import annotations

import unittest

from xauusd_v2.liquidity_taxonomy import (
    LiquidityKind,
    LiquidityMarkingRole,
    classify_r207_liquidity_role,
)


class LiquidityTaxonomyTests(unittest.TestCase):
    def test_big_wick_is_core_on_30m_plus(self) -> None:
        result = classify_r207_liquidity_role(kind=LiquidityKind.BIG_WICK_TO_FILL, timeframe_minutes=30)
        self.assertEqual(result.role, LiquidityMarkingRole.CORE)

    def test_unmanipulated_doji_is_core_on_30m_plus(self) -> None:
        result = classify_r207_liquidity_role(kind=LiquidityKind.UNMANIPULATED_DOJI, timeframe_minutes=60)
        self.assertEqual(result.role, LiquidityMarkingRole.CORE)

    def test_breakout_is_advanced_optional_not_core(self) -> None:
        result = classify_r207_liquidity_role(kind=LiquidityKind.BREAKOUT, timeframe_minutes=60)
        self.assertEqual(result.role, LiquidityMarkingRole.ADVANCED_OPTIONAL)

    def test_att_fu_is_refinement_context_not_core(self) -> None:
        result = classify_r207_liquidity_role(kind=LiquidityKind.ATT_FU, timeframe_minutes=60)
        self.assertEqual(result.role, LiquidityMarkingRole.REFINEMENT_CONTEXT)

    def test_15m_is_outside_r207_scope(self) -> None:
        result = classify_r207_liquidity_role(kind=LiquidityKind.UNMANIPULATED_DOJI, timeframe_minutes=15)
        self.assertEqual(result.role, LiquidityMarkingRole.OUTSIDE_R207_SCOPE)

    def test_invalid_timeframe_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            classify_r207_liquidity_role(kind=LiquidityKind.BIG_WICK_TO_FILL, timeframe_minutes=0)


if __name__ == "__main__":
    unittest.main()
