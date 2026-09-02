from __future__ import annotations

import unittest

from xauusd_v2.fu_retest_quality import FURetestQualityState, classify_fu_retest_quality


class FURetestQualityTests(unittest.TestCase):
    def test_half_wick_touch_is_strongest_without_full_fu_fib_anchor(self) -> None:
        result = classify_fu_retest_quality(
            fu_wick_touched=True,
            half_fu_wick_touched=True,
            past_70_full_fu_fib=None,
            full_fu_fib_anchor_certified=False,
        )
        self.assertEqual(result.state, FURetestQualityState.STRONGEST)
        self.assertTrue(result.retest_counts)
        self.assertFalse(result.numeric_full_fu_fib_used)

    def test_wick_touch_is_stronger_without_full_fu_fib_anchor(self) -> None:
        result = classify_fu_retest_quality(
            fu_wick_touched=True,
            half_fu_wick_touched=False,
            past_70_full_fu_fib=None,
            full_fu_fib_anchor_certified=False,
        )
        self.assertEqual(result.state, FURetestQualityState.STRONGER)
        self.assertTrue(result.retest_counts)
        self.assertFalse(result.numeric_full_fu_fib_used)

    def test_no_wick_touch_cannot_use_70_percent_while_anchor_unresolved(self) -> None:
        result = classify_fu_retest_quality(
            fu_wick_touched=False,
            half_fu_wick_touched=False,
            past_70_full_fu_fib=True,
            full_fu_fib_anchor_certified=False,
        )
        self.assertEqual(result.state, FURetestQualityState.NOT_CERTIFIED)
        self.assertIsNone(result.retest_counts)
        self.assertFalse(result.numeric_full_fu_fib_used)
        self.assertIn("anchor remains unresolved", result.reason)

    def test_certified_anchor_allows_weak_70_percent_branch(self) -> None:
        result = classify_fu_retest_quality(
            fu_wick_touched=False,
            half_fu_wick_touched=False,
            past_70_full_fu_fib=True,
            full_fu_fib_anchor_certified=True,
        )
        self.assertEqual(result.state, FURetestQualityState.WEAK)
        self.assertTrue(result.retest_counts)
        self.assertTrue(result.numeric_full_fu_fib_used)

    def test_certified_anchor_below_70_without_wick_is_below_minimum(self) -> None:
        result = classify_fu_retest_quality(
            fu_wick_touched=False,
            half_fu_wick_touched=False,
            past_70_full_fu_fib=False,
            full_fu_fib_anchor_certified=True,
        )
        self.assertEqual(result.state, FURetestQualityState.BELOW_MINIMUM)
        self.assertFalse(result.retest_counts)

    def test_missing_70_interaction_with_certified_anchor_fails_closed(self) -> None:
        result = classify_fu_retest_quality(
            fu_wick_touched=False,
            half_fu_wick_touched=False,
            past_70_full_fu_fib=None,
            full_fu_fib_anchor_certified=True,
        )
        self.assertEqual(result.state, FURetestQualityState.NOT_CERTIFIED)
        self.assertTrue(result.numeric_full_fu_fib_used)

    def test_inconsistent_half_wick_touch_is_rejected(self) -> None:
        result = classify_fu_retest_quality(
            fu_wick_touched=False,
            half_fu_wick_touched=True,
            past_70_full_fu_fib=None,
            full_fu_fib_anchor_certified=False,
        )
        self.assertEqual(result.state, FURetestQualityState.NOT_CERTIFIED)

    def test_missing_wick_evidence_fails_closed(self) -> None:
        result = classify_fu_retest_quality(
            fu_wick_touched=None,
            half_fu_wick_touched=False,
            past_70_full_fu_fib=None,
            full_fu_fib_anchor_certified=False,
        )
        self.assertEqual(result.state, FURetestQualityState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
