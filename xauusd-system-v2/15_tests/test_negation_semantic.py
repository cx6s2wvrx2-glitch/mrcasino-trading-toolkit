from __future__ import annotations

import unittest

from xauusd_v2.negation_semantic import (
    Direction,
    ManipulationType,
    NegationState,
    evaluate_negation,
)


class NegationSemanticTests(unittest.TestCase):
    def test_opposite_complete_fu_on_next_candle_is_negation(self) -> None:
        result = evaluate_negation(
            original_direction=Direction.BULLISH,
            original_type=ManipulationType.FU,
            candle_offset=1,
            candidate_direction=Direction.BEARISH,
            candidate_complete_fu=True,
        )
        self.assertEqual(result.state, NegationState.CONFIRMED)

    def test_second_candle_is_still_inside_window(self) -> None:
        result = evaluate_negation(
            original_direction=Direction.BEARISH,
            original_type=ManipulationType.FU,
            candle_offset=2,
            candidate_direction=Direction.BULLISH,
            candidate_complete_fu=True,
        )
        self.assertEqual(result.state, NegationState.CONFIRMED)

    def test_third_candle_is_outside_window(self) -> None:
        result = evaluate_negation(
            original_direction=Direction.BEARISH,
            original_type=ManipulationType.FU,
            candle_offset=3,
            candidate_direction=Direction.BULLISH,
            candidate_complete_fu=True,
        )
        self.assertEqual(result.state, NegationState.NOT_NEGATION)

    def test_same_direction_is_not_negation(self) -> None:
        result = evaluate_negation(
            original_direction=Direction.BULLISH,
            original_type=ManipulationType.FU,
            candle_offset=1,
            candidate_direction=Direction.BULLISH,
            candidate_complete_fu=True,
        )
        self.assertEqual(result.state, NegationState.NOT_NEGATION)

    def test_ordinary_fu_requires_complete_fu_close(self) -> None:
        result = evaluate_negation(
            original_direction=Direction.BULLISH,
            original_type=ManipulationType.FU,
            candle_offset=1,
            candidate_direction=Direction.BEARISH,
            candidate_complete_fu=False,
        )
        self.assertEqual(result.state, NegationState.NOT_NEGATION)

    def test_missing_completion_evidence_fails_closed(self) -> None:
        result = evaluate_negation(
            original_direction=Direction.BULLISH,
            original_type=ManipulationType.FU,
            candle_offset=1,
            candidate_direction=Direction.BEARISH,
            candidate_complete_fu=None,
        )
        self.assertEqual(result.state, NegationState.NOT_CERTIFIED)

    def test_x3_exception_does_not_require_complete_fu_close(self) -> None:
        result = evaluate_negation(
            original_direction=Direction.BULLISH,
            original_type=ManipulationType.X3,
            candle_offset=1,
            candidate_direction=Direction.BEARISH,
            candidate_complete_fu=False,
        )
        self.assertEqual(result.state, NegationState.CONFIRMED)

    def test_missing_candidate_direction_fails_closed(self) -> None:
        result = evaluate_negation(
            original_direction=Direction.BULLISH,
            original_type=ManipulationType.FU,
            candle_offset=1,
            candidate_direction=None,
            candidate_complete_fu=True,
        )
        self.assertEqual(result.state, NegationState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
