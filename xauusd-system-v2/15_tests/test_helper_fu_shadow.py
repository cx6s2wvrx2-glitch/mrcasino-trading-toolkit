from __future__ import annotations

import unittest

from xauusd_v2.fu_completion import FUCompletionClass, classify_fu_completion
from xauusd_v2.helper_fu_shadow import (
    HelperFUClass,
    beta_fu_core_shadow,
    casino_v7_core_shadow,
)


class HelperFUShadowTests(unittest.TestCase):
    def test_casino_v7_bull_continuation_close_through_high_is_fu(self) -> None:
        result = casino_v7_core_shadow(
            open=100.0,
            high=113.0,
            low=94.0,
            close=111.0,
            previous_open=105.0,
            previous_high=110.0,
            previous_low=95.0,
            previous_close=100.0,
        )
        self.assertEqual(result.bullish, HelperFUClass.FU)
        self.assertEqual(result.bullish_branch, "bull_continuation_fu")

    def test_casino_v7_duplicate_bull_continuation_fu_branch_is_shadowed_by_att(self) -> None:
        result = casino_v7_core_shadow(
            open=99.0,
            high=111.0,
            low=94.0,
            close=106.0,
            previous_open=105.0,
            previous_high=110.0,
            previous_low=95.0,
            previous_close=100.0,
        )
        self.assertEqual(result.bullish, HelperFUClass.ATT)
        self.assertEqual(result.bullish_branch, "bull_continuation_att")

    def test_casino_v7_bull_reversal_fu_subset_is_unreachable(self) -> None:
        result = casino_v7_core_shadow(
            open=99.0,
            high=113.0,
            low=94.0,
            close=112.0,
            previous_open=105.0,
            previous_high=110.0,
            previous_low=95.0,
            previous_close=100.0,
        )
        self.assertEqual(result.bullish, HelperFUClass.FU)
        self.assertEqual(result.bullish_branch, "bull_continuation_fu")
        self.assertNotEqual(result.bullish_branch, "bull_reversal_fu_subset_unreachable")

    def test_reflection_att_form_1_has_no_sweep_and_both_helpers_miss_it(self) -> None:
        reflection = classify_fu_completion(
            new_high_or_low=False,
            fu_criteria_met=None,
            close=103.0,
            previous_open=105.0,
            previous_close=100.0,
        )
        v7 = casino_v7_core_shadow(
            open=101.0,
            high=108.0,
            low=97.0,
            close=103.0,
            previous_open=105.0,
            previous_high=110.0,
            previous_low=95.0,
            previous_close=100.0,
        )
        beta = beta_fu_core_shadow(
            open=101.0,
            high=108.0,
            low=97.0,
            close=103.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertEqual(reflection.classification, FUCompletionClass.ATTEMPTED_FU_FORM_1)
        self.assertEqual(v7.bullish, HelperFUClass.NONE)
        self.assertEqual(v7.bearish, HelperFUClass.NONE)
        self.assertFalse(beta.bullish_fu_candidate)
        self.assertFalse(beta.bearish_fu_candidate)

    def test_reflection_complete_fu_can_map_to_v7_att_and_beta_fu_candidate(self) -> None:
        reflection = classify_fu_completion(
            new_high_or_low=True,
            fu_criteria_met=True,
            close=103.0,
            previous_open=105.0,
            previous_close=100.0,
        )
        v7 = casino_v7_core_shadow(
            open=99.0,
            high=107.0,
            low=94.0,
            close=103.0,
            previous_open=105.0,
            previous_high=110.0,
            previous_low=95.0,
            previous_close=100.0,
        )
        beta = beta_fu_core_shadow(
            open=99.0,
            high=107.0,
            low=94.0,
            close=103.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertEqual(reflection.classification, FUCompletionClass.COMPLETE_FU)
        self.assertEqual(v7.bullish, HelperFUClass.ATT)
        self.assertEqual(v7.bullish_branch, "bull_reversal_att_1")
        self.assertTrue(beta.bullish_fu_candidate)
        self.assertFalse(beta.bearish_fu_candidate)

    def test_reflection_att_form_2_v7_att_but_beta_collapses_to_broad_fu_candidates(self) -> None:
        reflection = classify_fu_completion(
            new_high_or_low=True,
            fu_criteria_met=True,
            close=106.0,
            previous_open=105.0,
            previous_close=100.0,
        )
        v7 = casino_v7_core_shadow(
            open=94.0,
            high=111.0,
            low=94.0,
            close=106.0,
            previous_open=105.0,
            previous_high=110.0,
            previous_low=95.0,
            previous_close=100.0,
        )
        beta = beta_fu_core_shadow(
            open=94.0,
            high=111.0,
            low=94.0,
            close=106.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertEqual(reflection.classification, FUCompletionClass.ATTEMPTED_FU_FORM_2)
        self.assertEqual(v7.bullish, HelperFUClass.ATT)
        self.assertTrue(beta.bullish_fu_candidate)
        self.assertTrue(beta.bearish_fu_candidate)
        self.assertFalse(beta.is_x3)

    def test_beta_outside_bar_with_both_wicks_is_x3_not_fu(self) -> None:
        beta = beta_fu_core_shadow(
            open=100.0,
            high=112.0,
            low=94.0,
            close=104.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertTrue(beta.is_x3)
        self.assertFalse(beta.bullish_fu_candidate)
        self.assertFalse(beta.bearish_fu_candidate)

    def test_non_finite_values_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            beta_fu_core_shadow(
                open=float("nan"),
                high=112.0,
                low=94.0,
                close=104.0,
                previous_high=110.0,
                previous_low=95.0,
            )


if __name__ == "__main__":
    unittest.main()
