from __future__ import annotations

import unittest

from xauusd_v2.doji_liquidity_semantic import DojiLiquidityState, classify_doji_liquidity


class DojiLiquiditySemanticTests(unittest.TestCase):
    def test_true_unmanipulated_doji_is_core(self) -> None:
        result = classify_doji_liquidity(
            is_doji=True,
            inside_previous_wick=True,
            manipulates_last_high_or_low=False,
        )
        self.assertEqual(result.state, DojiLiquidityState.CORE_UNMANIPULATED)
        self.assertTrue(result.core_liquidity_eligible)
        self.assertFalse(result.attempted_fu_context)

    def test_manipulated_doji_is_not_core(self) -> None:
        result = classify_doji_liquidity(
            is_doji=True,
            inside_previous_wick=True,
            manipulates_last_high_or_low=True,
        )
        self.assertEqual(result.state, DojiLiquidityState.MANIPULATED_NOT_CORE)
        self.assertFalse(result.core_liquidity_eligible)

    def test_doji_outside_previous_wick_is_attempted_fu_edge(self) -> None:
        result = classify_doji_liquidity(
            is_doji=True,
            inside_previous_wick=False,
            manipulates_last_high_or_low=False,
        )
        self.assertEqual(result.state, DojiLiquidityState.OUTSIDE_PREVIOUS_WICK_ATTEMPTED_FU)
        self.assertFalse(result.core_liquidity_eligible)
        self.assertTrue(result.attempted_fu_context)

    def test_outside_previous_wick_precedes_core_doji_marking_even_if_extreme_flag_is_true(self) -> None:
        result = classify_doji_liquidity(
            is_doji=True,
            inside_previous_wick=False,
            manipulates_last_high_or_low=True,
        )
        self.assertEqual(result.state, DojiLiquidityState.OUTSIDE_PREVIOUS_WICK_ATTEMPTED_FU)
        self.assertTrue(result.attempted_fu_context)

    def test_non_doji_is_not_promoted_into_liquidity_class(self) -> None:
        result = classify_doji_liquidity(
            is_doji=False,
            inside_previous_wick=True,
            manipulates_last_high_or_low=False,
        )
        self.assertEqual(result.state, DojiLiquidityState.NOT_DOJI)
        self.assertFalse(result.core_liquidity_eligible)

    def test_missing_upstream_doji_evidence_fails_closed(self) -> None:
        result = classify_doji_liquidity(
            is_doji=None,
            inside_previous_wick=True,
            manipulates_last_high_or_low=False,
        )
        self.assertEqual(result.state, DojiLiquidityState.NOT_CERTIFIED)
        self.assertFalse(result.core_liquidity_eligible)

    def test_missing_wick_relation_fails_closed(self) -> None:
        result = classify_doji_liquidity(
            is_doji=True,
            inside_previous_wick=None,
            manipulates_last_high_or_low=False,
        )
        self.assertEqual(result.state, DojiLiquidityState.NOT_CERTIFIED)

    def test_missing_manipulation_evidence_fails_closed(self) -> None:
        result = classify_doji_liquidity(
            is_doji=True,
            inside_previous_wick=True,
            manipulates_last_high_or_low=None,
        )
        self.assertEqual(result.state, DojiLiquidityState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
