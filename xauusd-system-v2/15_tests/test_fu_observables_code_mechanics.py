from __future__ import annotations

import unittest

from xauusd_v2.fu_observables import CandleDirection, extract_fu_observables


PREVIOUS = {
    "previous_open": 105.0,
    "previous_high": 110.0,
    "previous_low": 95.0,
    "previous_close": 100.0,
}


class FUObservablesCodeMechanicsTests(unittest.TestCase):
    def test_bullish_continuation_close_through_previous_high_is_explicit(self) -> None:
        result = extract_fu_observables(
            open=100.0,
            high=113.0,
            low=94.0,
            close=111.0,
            **PREVIOUS,
        )

        self.assertEqual(result.direction, CandleDirection.BULLISH)
        self.assertTrue(result.swept_previous_low)
        self.assertTrue(result.swept_previous_high)
        self.assertTrue(result.close_above_previous_high)
        self.assertFalse(result.close_within_previous_range)
        self.assertTrue(result.close_above_previous_open)
        self.assertTrue(result.close_above_previous_close)

    def test_bearish_continuation_close_through_previous_low_is_explicit(self) -> None:
        result = extract_fu_observables(
            open=104.0,
            high=112.0,
            low=93.0,
            close=94.0,
            **PREVIOUS,
        )

        self.assertEqual(result.direction, CandleDirection.BEARISH)
        self.assertTrue(result.swept_previous_high)
        self.assertTrue(result.swept_previous_low)
        self.assertTrue(result.close_below_previous_low)
        self.assertFalse(result.close_within_previous_range)
        self.assertTrue(result.close_below_previous_open)
        self.assertTrue(result.close_below_previous_close)

    def test_beta_style_one_side_take_and_close_back_inside_previous_range_is_explicit(self) -> None:
        result = extract_fu_observables(
            open=101.0,
            high=108.0,
            low=94.0,
            close=103.0,
            **PREVIOUS,
        )

        self.assertEqual(result.direction, CandleDirection.BULLISH)
        self.assertTrue(result.swept_previous_low)
        self.assertFalse(result.swept_previous_high)
        self.assertTrue(result.close_within_previous_range)
        self.assertFalse(result.close_above_previous_high)
        self.assertFalse(result.close_below_previous_low)
        self.assertTrue(result.close_above_previous_close)
        self.assertTrue(result.close_below_previous_open)

    def test_v7_bearish_inside_range_fu_evidence_does_not_imply_close_through_low(self) -> None:
        result = extract_fu_observables(
            open=106.0,
            high=112.0,
            low=94.0,
            close=97.0,
            **PREVIOUS,
        )

        self.assertEqual(result.direction, CandleDirection.BEARISH)
        self.assertTrue(result.swept_previous_high)
        self.assertTrue(result.swept_previous_low)
        self.assertTrue(result.close_within_previous_range)
        self.assertFalse(result.close_below_previous_low)
        self.assertTrue(result.close_below_previous_close)
        self.assertTrue(result.close_below_previous_open)

    def test_pullback_reversal_relationships_to_previous_open_and_close_are_preserved(self) -> None:
        result = extract_fu_observables(
            open=99.0,
            high=107.0,
            low=94.0,
            close=103.0,
            **PREVIOUS,
        )

        self.assertTrue(result.open_below_previous_open)
        self.assertTrue(result.open_below_previous_close)
        self.assertTrue(result.close_above_previous_close)
        self.assertTrue(result.close_below_previous_open)
        self.assertTrue(result.close_within_previous_body)


if __name__ == "__main__":
    unittest.main()
