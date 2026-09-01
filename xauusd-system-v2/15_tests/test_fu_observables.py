from __future__ import annotations

import unittest

from xauusd_v2.fu_observables import CandleDirection, extract_fu_observables


class FUObservableTests(unittest.TestCase):
    def test_bullish_low_sweep_candidate_and_close_inside_previous_body(self) -> None:
        obs = extract_fu_observables(
            open=99.0,
            high=106.0,
            low=94.0,
            close=103.0,
            previous_open=105.0,
            previous_high=108.0,
            previous_low=95.0,
            previous_close=100.0,
        )
        self.assertEqual(obs.direction, CandleDirection.BULLISH)
        self.assertTrue(obs.swept_previous_low)
        self.assertFalse(obs.swept_previous_high)
        self.assertTrue(obs.bullish_reversal_candidate)
        self.assertTrue(obs.close_within_previous_body)

    def test_bearish_high_sweep_candidate_and_close_inside_previous_body(self) -> None:
        obs = extract_fu_observables(
            open=106.0,
            high=111.0,
            low=99.0,
            close=103.0,
            previous_open=100.0,
            previous_high=110.0,
            previous_low=98.0,
            previous_close=105.0,
        )
        self.assertEqual(obs.direction, CandleDirection.BEARISH)
        self.assertTrue(obs.swept_previous_high)
        self.assertTrue(obs.bearish_reversal_candidate)
        self.assertTrue(obs.close_within_previous_body)

    def test_outside_bar_preserves_both_sweeps_instead_of_guessing_fu_side(self) -> None:
        obs = extract_fu_observables(
            open=100.0,
            high=112.0,
            low=94.0,
            close=104.0,
            previous_open=101.0,
            previous_high=110.0,
            previous_low=95.0,
            previous_close=105.0,
        )
        self.assertTrue(obs.swept_both_sides)
        self.assertTrue(obs.swept_previous_high)
        self.assertTrue(obs.swept_previous_low)

    def test_no_sweep_is_not_a_reversal_candidate(self) -> None:
        obs = extract_fu_observables(
            open=101.0,
            high=109.0,
            low=96.0,
            close=104.0,
            previous_open=100.0,
            previous_high=110.0,
            previous_low=95.0,
            previous_close=105.0,
        )
        self.assertFalse(obs.swept_previous_high)
        self.assertFalse(obs.swept_previous_low)
        self.assertFalse(obs.bullish_reversal_candidate)
        self.assertFalse(obs.bearish_reversal_candidate)

    def test_close_outside_previous_body_is_preserved(self) -> None:
        obs = extract_fu_observables(
            open=99.0,
            high=112.0,
            low=94.0,
            close=111.0,
            previous_open=100.0,
            previous_high=110.0,
            previous_low=95.0,
            previous_close=105.0,
        )
        self.assertFalse(obs.close_within_previous_body)
        self.assertTrue(obs.close_above_previous_body)
        self.assertFalse(obs.close_below_previous_body)

    def test_doji_direction_does_not_create_directional_reversal_candidate(self) -> None:
        obs = extract_fu_observables(
            open=100.0,
            high=111.0,
            low=94.0,
            close=100.0,
            previous_open=101.0,
            previous_high=110.0,
            previous_low=95.0,
            previous_close=105.0,
        )
        self.assertEqual(obs.direction, CandleDirection.DOJI)
        self.assertFalse(obs.bullish_reversal_candidate)
        self.assertFalse(obs.bearish_reversal_candidate)

    def test_invalid_current_ohlc_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            extract_fu_observables(
                open=100.0,
                high=99.0,
                low=94.0,
                close=98.0,
                previous_open=101.0,
                previous_high=110.0,
                previous_low=95.0,
                previous_close=105.0,
            )

    def test_invalid_previous_ohlc_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            extract_fu_observables(
                open=100.0,
                high=111.0,
                low=94.0,
                close=104.0,
                previous_open=101.0,
                previous_high=100.0,
                previous_low=95.0,
                previous_close=105.0,
            )


if __name__ == "__main__":
    unittest.main()
