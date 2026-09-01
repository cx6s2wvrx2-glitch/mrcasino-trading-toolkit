from __future__ import annotations

import unittest

from xauusd_v2.imbalance_observables import CandleDirection, measure_imbalanced_candle_observables


class ImbalancedCandleObservableTests(unittest.TestCase):
    def test_bullish_open_at_low_is_recorded_without_classifying_imbalance(self) -> None:
        obs = measure_imbalanced_candle_observables(open=100.0, high=110.0, low=100.0, close=108.0)
        self.assertEqual(obs.direction, CandleDirection.BULLISH)
        self.assertTrue(obs.open_equals_low_exact)
        self.assertFalse(obs.open_equals_high_exact)
        self.assertAlmostEqual(obs.open_distance_from_low_fraction, 0.0)

    def test_bearish_open_at_high_is_recorded_without_classifying_imbalance(self) -> None:
        obs = measure_imbalanced_candle_observables(open=110.0, high=110.0, low=100.0, close=102.0)
        self.assertEqual(obs.direction, CandleDirection.BEARISH)
        self.assertTrue(obs.open_equals_high_exact)
        self.assertFalse(obs.open_equals_low_exact)
        self.assertAlmostEqual(obs.high_distance_from_open_fraction, 0.0)

    def test_near_low_is_measured_but_not_rounded_to_exact(self) -> None:
        obs = measure_imbalanced_candle_observables(open=100.01, high=110.0, low=100.0, close=108.0)
        self.assertFalse(obs.open_equals_low_exact)
        self.assertGreater(obs.open_distance_from_low_fraction, 0.0)

    def test_near_high_is_measured_but_not_rounded_to_exact(self) -> None:
        obs = measure_imbalanced_candle_observables(open=109.99, high=110.0, low=100.0, close=102.0)
        self.assertFalse(obs.open_equals_high_exact)
        self.assertGreater(obs.high_distance_from_open_fraction, 0.0)

    def test_wick_and_body_fractions_are_reproducible(self) -> None:
        obs = measure_imbalanced_candle_observables(open=102.0, high=110.0, low=100.0, close=108.0)
        self.assertAlmostEqual(obs.body_fraction, 0.6)
        self.assertAlmostEqual(obs.upper_wick_fraction, 0.2)
        self.assertAlmostEqual(obs.lower_wick_fraction, 0.2)

    def test_doji_is_measured_without_directional_classification(self) -> None:
        obs = measure_imbalanced_candle_observables(open=105.0, high=110.0, low=100.0, close=105.0)
        self.assertEqual(obs.direction, CandleDirection.DOJI)
        self.assertAlmostEqual(obs.body_fraction, 0.0)

    def test_invalid_ohlc_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            measure_imbalanced_candle_observables(open=105.0, high=104.0, low=100.0, close=103.0)

    def test_flat_candle_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            measure_imbalanced_candle_observables(open=105.0, high=105.0, low=105.0, close=105.0)

    def test_non_finite_price_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            measure_imbalanced_candle_observables(open=105.0, high=float("nan"), low=100.0, close=103.0)


if __name__ == "__main__":
    unittest.main()
