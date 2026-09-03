from __future__ import annotations

import unittest

from xauusd_v2.fu_basic_candidate import BasicFUCandidateState
from xauusd_v2.fu_completion import FUCompletionClass
from xauusd_v2.fu_family_observability import observe_fu_family
from xauusd_v2.fu_observables import CandleDirection
from xauusd_v2.helper_fu_shadow import HelperFUClass


PREVIOUS = {
    "previous_open": 105.0,
    "previous_high": 110.0,
    "previous_low": 95.0,
    "previous_close": 100.0,
}


class FUFamilyObservabilityTests(unittest.TestCase):
    def test_reflection_att_form_1_stays_visible_when_helpers_miss_it(self) -> None:
        result = observe_fu_family(
            open=101.0,
            high=108.0,
            low=97.0,
            close=103.0,
            **PREVIOUS,
        )

        self.assertEqual(result.direction, CandleDirection.BULLISH)
        self.assertFalse(result.swept_previous_high)
        self.assertFalse(result.swept_previous_low)
        self.assertEqual(result.basic_fu_proxy, BasicFUCandidateState.NONE)
        self.assertEqual(result.reflection_observed_class, FUCompletionClass.ATTEMPTED_FU_FORM_1)
        self.assertIsNone(result.reflection_conditional_if_fu_criteria_met)
        self.assertFalse(result.reflection_conditional_is_counterfactual)
        self.assertEqual(result.casino_v7_bullish, HelperFUClass.NONE)
        self.assertEqual(result.casino_v7_bearish, HelperFUClass.NONE)
        self.assertFalse(result.beta_bullish_fu_candidate)
        self.assertFalse(result.beta_bearish_fu_candidate)
        self._assert_non_certifying(result)

    def test_complete_fu_geometry_is_only_conditional_until_fu_criteria_are_supplied(self) -> None:
        result = observe_fu_family(
            open=99.0,
            high=107.0,
            low=94.0,
            close=103.0,
            **PREVIOUS,
        )

        self.assertEqual(result.basic_fu_proxy, BasicFUCandidateState.BULLISH)
        self.assertEqual(result.reflection_observed_class, FUCompletionClass.NOT_CERTIFIED)
        self.assertEqual(result.reflection_conditional_if_fu_criteria_met, FUCompletionClass.COMPLETE_FU)
        self.assertTrue(result.reflection_conditional_is_counterfactual)
        self.assertEqual(result.casino_v7_bullish, HelperFUClass.ATT)
        self.assertEqual(result.casino_v7_bullish_branch, "bull_reversal_att_1")
        self.assertTrue(result.beta_bullish_fu_candidate)
        self.assertFalse(result.beta_bearish_fu_candidate)
        self._assert_non_certifying(result)

    def test_att_form_2_geometry_preserves_v7_and_beta_divergence(self) -> None:
        result = observe_fu_family(
            open=94.0,
            high=111.0,
            low=94.0,
            close=106.0,
            **PREVIOUS,
        )

        self.assertTrue(result.swept_both_sides)
        self.assertEqual(result.basic_fu_proxy, BasicFUCandidateState.AMBIGUOUS)
        self.assertEqual(result.reflection_observed_class, FUCompletionClass.NOT_CERTIFIED)
        self.assertEqual(result.reflection_conditional_if_fu_criteria_met, FUCompletionClass.ATTEMPTED_FU_FORM_2)
        self.assertTrue(result.reflection_conditional_is_counterfactual)
        self.assertEqual(result.casino_v7_bullish, HelperFUClass.ATT)
        self.assertEqual(result.casino_v7_bullish_branch, "bull_continuation_att")
        self.assertTrue(result.beta_bullish_fu_candidate)
        self.assertTrue(result.beta_bearish_fu_candidate)
        self.assertFalse(result.beta_is_x3)
        self._assert_non_certifying(result)

    def test_v7_continuation_fu_and_beta_x3_can_coexist_as_competing_code_evidence(self) -> None:
        result = observe_fu_family(
            open=100.0,
            high=113.0,
            low=94.0,
            close=111.0,
            **PREVIOUS,
        )

        self.assertTrue(result.swept_both_sides)
        self.assertEqual(result.basic_fu_proxy, BasicFUCandidateState.AMBIGUOUS)
        self.assertEqual(result.casino_v7_bullish, HelperFUClass.FU)
        self.assertEqual(result.casino_v7_bullish_branch, "bull_continuation_fu")
        self.assertTrue(result.beta_is_x3)
        self.assertFalse(result.beta_bullish_fu_candidate)
        self.assertFalse(result.beta_bearish_fu_candidate)
        self.assertEqual(result.reflection_conditional_if_fu_criteria_met, FUCompletionClass.ATTEMPTED_FU_FORM_2)
        self._assert_non_certifying(result)

    def test_beta_outside_bar_x3_is_preserved_in_union_layer(self) -> None:
        result = observe_fu_family(
            open=100.0,
            high=112.0,
            low=94.0,
            close=104.0,
            **PREVIOUS,
        )

        self.assertTrue(result.swept_both_sides)
        self.assertTrue(result.beta_is_x3)
        self.assertFalse(result.beta_bullish_fu_candidate)
        self.assertFalse(result.beta_bearish_fu_candidate)
        self._assert_non_certifying(result)

    def test_doji_does_not_gain_fu_certification_from_broad_helper_candidates(self) -> None:
        result = observe_fu_family(
            open=100.0,
            high=111.0,
            low=94.0,
            close=100.0,
            **PREVIOUS,
        )

        self.assertEqual(result.direction, CandleDirection.DOJI)
        self.assertTrue(result.swept_both_sides)
        self.assertEqual(result.basic_fu_proxy, BasicFUCandidateState.AMBIGUOUS)
        self.assertEqual(result.reflection_observed_class, FUCompletionClass.NOT_CERTIFIED)
        self.assertEqual(result.reflection_conditional_if_fu_criteria_met, FUCompletionClass.COMPLETE_FU)
        self.assertTrue(result.beta_bullish_fu_candidate)
        self.assertTrue(result.beta_bearish_fu_candidate)
        self._assert_non_certifying(result)

    def _assert_non_certifying(self, result) -> None:
        self.assertFalse(result.fu_semantics_certified)
        self.assertFalse(result.strong_fu_certified)
        self.assertFalse(result.strategy_truth_changed)


if __name__ == "__main__":
    unittest.main()
