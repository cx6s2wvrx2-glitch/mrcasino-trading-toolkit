from __future__ import annotations

import unittest

from xauusd_v2.fu_criteria import FUCriteriaState, evaluate_fu_criteria


class FUCriteriaTests(unittest.TestCase):
    def test_all_source_conditions_met(self) -> None:
        result = evaluate_fu_criteria(
            liquidity_taken=True,
            opposite_direction_move=True,
            same_candle=True,
        )
        self.assertEqual(result.state, FUCriteriaState.MET)

    def test_no_liquidity_taken_is_not_fu(self) -> None:
        result = evaluate_fu_criteria(
            liquidity_taken=False,
            opposite_direction_move=True,
            same_candle=True,
        )
        self.assertEqual(result.state, FUCriteriaState.NOT_MET)

    def test_no_opposite_direction_move_is_not_fu(self) -> None:
        result = evaluate_fu_criteria(
            liquidity_taken=True,
            opposite_direction_move=False,
            same_candle=True,
        )
        self.assertEqual(result.state, FUCriteriaState.NOT_MET)

    def test_conditions_split_across_candles_are_not_fu(self) -> None:
        result = evaluate_fu_criteria(
            liquidity_taken=True,
            opposite_direction_move=True,
            same_candle=False,
        )
        self.assertEqual(result.state, FUCriteriaState.NOT_MET)

    def test_missing_liquidity_evidence_fails_closed(self) -> None:
        result = evaluate_fu_criteria(
            liquidity_taken=None,
            opposite_direction_move=True,
            same_candle=True,
        )
        self.assertEqual(result.state, FUCriteriaState.NOT_CERTIFIED)

    def test_missing_direction_evidence_fails_closed(self) -> None:
        result = evaluate_fu_criteria(
            liquidity_taken=True,
            opposite_direction_move=None,
            same_candle=True,
        )
        self.assertEqual(result.state, FUCriteriaState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
