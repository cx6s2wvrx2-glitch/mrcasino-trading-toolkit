from __future__ import annotations

import unittest

from xauusd_v2.fu_break_evidence import (
    FUCandidateDirection,
    PreviousCandleBreakState,
    assess_previous_candle_break,
)


class FUPreviousCandleBreakEvidenceTests(unittest.TestCase):
    def test_bullish_close_through_previous_high_is_separate_from_liquidity_semantics(self) -> None:
        result = assess_previous_candle_break(
            direction=FUCandidateDirection.BULLISH,
            high=113.0,
            low=94.0,
            close=111.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertTrue(result.manipulation_side_previous_extreme_swept)
        self.assertTrue(result.opposite_side_previous_extreme_broken)
        self.assertTrue(result.close_through_opposite_extreme)
        self.assertFalse(result.close_back_within_previous_range)
        self.assertEqual(result.break_state, PreviousCandleBreakState.CLOSE_THROUGH_OPPOSITE_EXTREME)
        self._assert_non_certifying(result)

    def test_bullish_wick_break_can_close_back_inside_previous_range(self) -> None:
        result = assess_previous_candle_break(
            direction=FUCandidateDirection.BULLISH,
            high=111.0,
            low=94.0,
            close=103.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertTrue(result.manipulation_side_previous_extreme_swept)
        self.assertTrue(result.opposite_side_previous_extreme_broken)
        self.assertFalse(result.close_through_opposite_extreme)
        self.assertTrue(result.close_back_within_previous_range)
        self.assertEqual(result.break_state, PreviousCandleBreakState.WICK_BREAK_WITHOUT_CLOSE_THROUGH)
        self._assert_non_certifying(result)

    def test_bearish_close_through_previous_low_is_explicit(self) -> None:
        result = assess_previous_candle_break(
            direction=FUCandidateDirection.BEARISH,
            high=112.0,
            low=93.0,
            close=94.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertTrue(result.manipulation_side_previous_extreme_swept)
        self.assertTrue(result.opposite_side_previous_extreme_broken)
        self.assertTrue(result.close_through_opposite_extreme)
        self.assertEqual(result.break_state, PreviousCandleBreakState.CLOSE_THROUGH_OPPOSITE_EXTREME)
        self._assert_non_certifying(result)

    def test_bearish_wick_break_without_close_through_is_distinct(self) -> None:
        result = assess_previous_candle_break(
            direction=FUCandidateDirection.BEARISH,
            high=112.0,
            low=94.0,
            close=97.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertTrue(result.manipulation_side_previous_extreme_swept)
        self.assertTrue(result.opposite_side_previous_extreme_broken)
        self.assertFalse(result.close_through_opposite_extreme)
        self.assertTrue(result.close_back_within_previous_range)
        self.assertEqual(result.break_state, PreviousCandleBreakState.WICK_BREAK_WITHOUT_CLOSE_THROUGH)
        self._assert_non_certifying(result)

    def test_no_opposite_extreme_break_is_not_automatically_invalid_att_form_1(self) -> None:
        result = assess_previous_candle_break(
            direction=FUCandidateDirection.BULLISH,
            high=108.0,
            low=97.0,
            close=103.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertFalse(result.manipulation_side_previous_extreme_swept)
        self.assertFalse(result.opposite_side_previous_extreme_broken)
        self.assertEqual(result.break_state, PreviousCandleBreakState.NO_OPPOSITE_EXTREME_BREAK)
        self._assert_non_certifying(result)

    def test_touching_opposite_extreme_is_not_recorded_as_break(self) -> None:
        result = assess_previous_candle_break(
            direction=FUCandidateDirection.BULLISH,
            high=110.0,
            low=94.0,
            close=105.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertTrue(result.manipulation_side_previous_extreme_swept)
        self.assertFalse(result.opposite_side_previous_extreme_broken)
        self.assertEqual(result.break_state, PreviousCandleBreakState.NO_OPPOSITE_EXTREME_BREAK)
        self._assert_non_certifying(result)

    def _assert_non_certifying(self, result) -> None:
        self.assertFalse(result.fu_semantics_certified)
        self.assertFalse(result.sequence_after_liquidity_take_certified)
        self.assertFalse(result.strategy_truth_changed)


if __name__ == "__main__":
    unittest.main()
