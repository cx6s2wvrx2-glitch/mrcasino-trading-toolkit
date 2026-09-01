from __future__ import annotations

import unittest

from xauusd_v2.fu_completion import FUCompletionClass, classify_fu_completion


class FUCompletionTests(unittest.TestCase):
    def test_no_new_extreme_is_attempted_form_1(self) -> None:
        result = classify_fu_completion(
            new_high_or_low=False,
            fu_criteria_met=None,
            close=2345.0,
            previous_open=2340.0,
            previous_close=2350.0,
        )
        self.assertEqual(result.classification, FUCompletionClass.ATTEMPTED_FU_FORM_1)

    def test_complete_fu_requires_close_inside_previous_body(self) -> None:
        result = classify_fu_completion(
            new_high_or_low=True,
            fu_criteria_met=True,
            close=2345.0,
            previous_open=2340.0,
            previous_close=2350.0,
        )
        self.assertEqual(result.classification, FUCompletionClass.COMPLETE_FU)
        self.assertTrue(result.close_within_previous_body)

    def test_body_boundary_counts_as_inside(self) -> None:
        result = classify_fu_completion(
            new_high_or_low=True,
            fu_criteria_met=True,
            close=2350.0,
            previous_open=2340.0,
            previous_close=2350.0,
        )
        self.assertEqual(result.classification, FUCompletionClass.COMPLETE_FU)

    def test_new_extreme_without_body_closure_is_attempted_form_2(self) -> None:
        result = classify_fu_completion(
            new_high_or_low=True,
            fu_criteria_met=True,
            close=2355.0,
            previous_open=2340.0,
            previous_close=2350.0,
        )
        self.assertEqual(result.classification, FUCompletionClass.ATTEMPTED_FU_FORM_2)
        self.assertFalse(result.close_within_previous_body)

    def test_missing_upstream_fu_criteria_fails_closed(self) -> None:
        result = classify_fu_completion(
            new_high_or_low=True,
            fu_criteria_met=None,
            close=2345.0,
            previous_open=2340.0,
            previous_close=2350.0,
        )
        self.assertEqual(result.classification, FUCompletionClass.NOT_CERTIFIED)

    def test_false_upstream_fu_criteria_fails_closed(self) -> None:
        result = classify_fu_completion(
            new_high_or_low=True,
            fu_criteria_met=False,
            close=2345.0,
            previous_open=2340.0,
            previous_close=2350.0,
        )
        self.assertEqual(result.classification, FUCompletionClass.NOT_CERTIFIED)

    def test_missing_new_extreme_evidence_fails_closed(self) -> None:
        result = classify_fu_completion(
            new_high_or_low=None,
            fu_criteria_met=True,
            close=2345.0,
            previous_open=2340.0,
            previous_close=2350.0,
        )
        self.assertEqual(result.classification, FUCompletionClass.NOT_CERTIFIED)

    def test_non_finite_price_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            classify_fu_completion(
                new_high_or_low=True,
                fu_criteria_met=True,
                close=float("nan"),
                previous_open=2340.0,
                previous_close=2350.0,
            )


if __name__ == "__main__":
    unittest.main()
