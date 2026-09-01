from __future__ import annotations

import unittest

from xauusd_v2.fu_basic_candidate import BasicFUCandidateState, classify_basic_fu_candidate


class BasicFUCandidateTests(unittest.TestCase):
    def test_previous_low_sweep_plus_bullish_move_is_bullish_candidate(self) -> None:
        result = classify_basic_fu_candidate(
            open=99.0,
            high=106.0,
            low=94.0,
            close=103.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertEqual(result.state, BasicFUCandidateState.BULLISH)

    def test_previous_high_sweep_plus_bearish_move_is_bearish_candidate(self) -> None:
        result = classify_basic_fu_candidate(
            open=106.0,
            high=111.0,
            low=99.0,
            close=103.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertEqual(result.state, BasicFUCandidateState.BEARISH)

    def test_low_sweep_without_bullish_move_is_not_candidate(self) -> None:
        result = classify_basic_fu_candidate(
            open=103.0,
            high=106.0,
            low=94.0,
            close=99.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertEqual(result.state, BasicFUCandidateState.NONE)

    def test_high_sweep_without_bearish_move_is_not_candidate(self) -> None:
        result = classify_basic_fu_candidate(
            open=103.0,
            high=111.0,
            low=99.0,
            close=106.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertEqual(result.state, BasicFUCandidateState.NONE)

    def test_both_side_sweep_fails_closed_as_ambiguous(self) -> None:
        result = classify_basic_fu_candidate(
            open=100.0,
            high=112.0,
            low=94.0,
            close=104.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertEqual(result.state, BasicFUCandidateState.AMBIGUOUS)

    def test_no_sweep_is_none_and_does_not_fake_att_form_1(self) -> None:
        result = classify_basic_fu_candidate(
            open=101.0,
            high=108.0,
            low=97.0,
            close=103.0,
            previous_high=110.0,
            previous_low=95.0,
        )
        self.assertEqual(result.state, BasicFUCandidateState.NONE)

    def test_invalid_ohlc_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            classify_basic_fu_candidate(
                open=100.0,
                high=99.0,
                low=94.0,
                close=103.0,
                previous_high=110.0,
                previous_low=95.0,
            )


if __name__ == "__main__":
    unittest.main()
