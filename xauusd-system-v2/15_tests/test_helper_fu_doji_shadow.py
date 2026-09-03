from __future__ import annotations

import unittest

from xauusd_v2.helper_fu_doji_shadow import apply_casino_v7_current_doji_filter
from xauusd_v2.helper_fu_shadow import CasinoV7ShadowResult, HelperFUClass


class CasinoV7DojiFilterShadowTests(unittest.TestCase):
    def test_helper_doji_clears_ordinary_fu_but_keeps_att(self) -> None:
        result = apply_casino_v7_current_doji_filter(
            open=100.0,
            high=110.0,
            low=90.0,
            close=104.0,
            branch_result=CasinoV7ShadowResult(
                bullish=HelperFUClass.FU,
                bearish=HelperFUClass.ATT,
                bullish_branch="test_fu",
                bearish_branch="test_att",
            ),
        )

        self.assertTrue(result.is_doji_by_helper_parameter)
        self.assertEqual(result.bullish_before_filter, HelperFUClass.FU)
        self.assertEqual(result.bullish_after_filter, HelperFUClass.NONE)
        self.assertEqual(result.bearish_before_filter, HelperFUClass.ATT)
        self.assertEqual(result.bearish_after_filter, HelperFUClass.ATT)
        self.assertFalse(result.helper_parameter_is_strategy_truth)
        self.assertFalse(result.strategy_truth_changed)

    def test_non_doji_keeps_fu(self) -> None:
        result = apply_casino_v7_current_doji_filter(
            open=100.0,
            high=110.0,
            low=90.0,
            close=108.0,
            branch_result=CasinoV7ShadowResult(
                bullish=HelperFUClass.FU,
                bearish=HelperFUClass.NONE,
                bullish_branch="test_fu",
                bearish_branch="none",
            ),
        )

        self.assertFalse(result.is_doji_by_helper_parameter)
        self.assertEqual(result.bullish_after_filter, HelperFUClass.FU)
        self.assertFalse(result.helper_parameter_is_strategy_truth)

    def test_custom_threshold_is_recorded_as_helper_parameter_not_truth(self) -> None:
        result = apply_casino_v7_current_doji_filter(
            open=100.0,
            high=110.0,
            low=90.0,
            close=106.0,
            body_ratio_threshold=0.40,
            branch_result=CasinoV7ShadowResult(
                bullish=HelperFUClass.FU,
                bearish=HelperFUClass.ATT,
                bullish_branch="test_fu",
                bearish_branch="test_att",
            ),
        )

        self.assertTrue(result.is_doji_by_helper_parameter)
        self.assertEqual(result.body_ratio_threshold, 0.40)
        self.assertFalse(result.helper_parameter_is_strategy_truth)
        self.assertEqual(result.bearish_after_filter, HelperFUClass.ATT)

    def test_zero_range_is_handled_without_promoting_threshold(self) -> None:
        result = apply_casino_v7_current_doji_filter(
            open=100.0,
            high=100.0,
            low=100.0,
            close=100.0,
            branch_result=CasinoV7ShadowResult(
                bullish=HelperFUClass.NONE,
                bearish=HelperFUClass.NONE,
                bullish_branch="none",
                bearish_branch="none",
            ),
        )
        self.assertTrue(result.is_doji_by_helper_parameter)
        self.assertFalse(result.helper_parameter_is_strategy_truth)
        self.assertFalse(result.strategy_truth_changed)


if __name__ == "__main__":
    unittest.main()
