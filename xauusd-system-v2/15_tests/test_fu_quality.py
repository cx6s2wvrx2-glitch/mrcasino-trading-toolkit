from __future__ import annotations

import unittest

from xauusd_v2.fu_quality import CandleDirection, measure_fu_quality


class FUQualityMetricTests(unittest.TestCase):
    def test_bullish_close_at_high_has_zero_close_rejection(self) -> None:
        metrics = measure_fu_quality(open=100.0, high=110.0, low=95.0, close=110.0)
        self.assertEqual(metrics.direction, CandleDirection.BULLISH)
        self.assertAlmostEqual(metrics.close_side_rejection_fraction, 0.0)
        self.assertAlmostEqual(metrics.close_location, 1.0)
        self.assertAlmostEqual(metrics.manipulation_side_wick_fraction, 5.0 / 15.0)

    def test_bearish_close_at_low_has_zero_close_rejection(self) -> None:
        metrics = measure_fu_quality(open=110.0, high=115.0, low=100.0, close=100.0)
        self.assertEqual(metrics.direction, CandleDirection.BEARISH)
        self.assertAlmostEqual(metrics.close_side_rejection_fraction, 0.0)
        self.assertAlmostEqual(metrics.close_location, 0.0)
        self.assertAlmostEqual(metrics.manipulation_side_wick_fraction, 5.0 / 15.0)

    def test_body_and_wick_fractions_are_reproducible(self) -> None:
        metrics = measure_fu_quality(open=102.0, high=110.0, low=100.0, close=108.0)
        self.assertAlmostEqual(metrics.body_fraction, 0.6)
        self.assertAlmostEqual(metrics.upper_wick_fraction, 0.2)
        self.assertAlmostEqual(metrics.lower_wick_fraction, 0.2)
        self.assertAlmostEqual(metrics.close_side_rejection_fraction, 0.2)
        self.assertAlmostEqual(metrics.close_location, 0.8)

    def test_bearish_close_rejection_uses_lower_wick(self) -> None:
        metrics = measure_fu_quality(open=108.0, high=110.0, low=100.0, close=102.0)
        self.assertEqual(metrics.direction, CandleDirection.BEARISH)
        self.assertAlmostEqual(metrics.close_side_rejection_fraction, 0.2)
        self.assertAlmostEqual(metrics.manipulation_side_wick_fraction, 0.2)

    def test_doji_is_measured_without_strong_classification(self) -> None:
        metrics = measure_fu_quality(open=105.0, high=110.0, low=100.0, close=105.0)
        self.assertEqual(metrics.direction, CandleDirection.DOJI)
        self.assertAlmostEqual(metrics.body_fraction, 0.0)
        self.assertAlmostEqual(metrics.close_location, 0.5)

    def test_invalid_ohlc_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            measure_fu_quality(open=105.0, high=104.0, low=100.0, close=103.0)

    def test_flat_candle_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            measure_fu_quality(open=105.0, high=105.0, low=105.0, close=105.0)

    def test_non_finite_ohlc_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            measure_fu_quality(open=105.0, high=float("inf"), low=100.0, close=104.0)


if __name__ == "__main__":
    unittest.main()
