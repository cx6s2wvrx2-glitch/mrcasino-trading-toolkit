from __future__ import annotations

import unittest

from xauusd_v2.zone_geometry import (
    Candle,
    NeighborSide,
    WickSide,
    ZoneRange,
    build_1m_strong_fu_zone,
    combine_full_zone_range,
    detect_true_orderblock,
)


class ZoneGeometryTests(unittest.TestCase):
    def test_body_inside_previous_upper_wick_is_true_orderblock(self) -> None:
        previous = Candle(open=100.0, high=110.0, low=95.0, close=102.0)
        current = Candle(open=104.0, high=106.0, low=103.0, close=105.0)
        result = detect_true_orderblock(candle=current, previous_candle=previous, next_candle=None)
        self.assertTrue(result.is_true_orderblock)
        self.assertEqual(result.matches[0].neighbor, NeighborSide.PREVIOUS)
        self.assertEqual(result.matches[0].wick_side, WickSide.UPPER)

    def test_body_inside_previous_lower_wick_is_true_orderblock(self) -> None:
        previous = Candle(open=103.0, high=108.0, low=95.0, close=101.0)
        current = Candle(open=98.0, high=100.0, low=97.0, close=99.0)
        result = detect_true_orderblock(candle=current, previous_candle=previous, next_candle=None)
        self.assertTrue(result.is_true_orderblock)
        self.assertEqual(result.matches[0].wick_side, WickSide.LOWER)

    def test_body_inside_next_wick_is_also_valid(self) -> None:
        current = Candle(open=104.0, high=106.0, low=103.0, close=105.0)
        next_candle = Candle(open=102.0, high=110.0, low=99.0, close=101.0)
        result = detect_true_orderblock(candle=current, previous_candle=None, next_candle=next_candle)
        self.assertTrue(result.is_true_orderblock)
        self.assertEqual(result.matches[0].neighbor, NeighborSide.NEXT)
        self.assertEqual(result.matches[0].wick_side, WickSide.UPPER)

    def test_partial_body_overlap_is_not_enough(self) -> None:
        previous = Candle(open=100.0, high=110.0, low=95.0, close=102.0)
        current = Candle(open=101.0, high=106.0, low=100.0, close=105.0)
        result = detect_true_orderblock(candle=current, previous_candle=previous, next_candle=None)
        self.assertFalse(result.is_true_orderblock)

    def test_zero_size_neighbor_wick_does_not_match(self) -> None:
        previous = Candle(open=110.0, high=110.0, low=95.0, close=102.0)
        current = Candle(open=108.0, high=109.0, low=107.0, close=109.0)
        result = detect_true_orderblock(candle=current, previous_candle=previous, next_candle=None)
        self.assertFalse(result.is_true_orderblock)

    def test_1m_strong_fu_zone_uses_full_candle_range(self) -> None:
        candle = Candle(open=100.0, high=112.0, low=94.0, close=108.0)
        zone = build_1m_strong_fu_zone(candle=candle, timeframe_minutes=1, strong_fu_confirmed=True)
        self.assertIsNotNone(zone)
        self.assertEqual((zone.low, zone.high), (94.0, 112.0))

    def test_strong_fu_zone_is_scoped_to_1m(self) -> None:
        candle = Candle(open=100.0, high=112.0, low=94.0, close=108.0)
        self.assertIsNone(build_1m_strong_fu_zone(candle=candle, timeframe_minutes=5, strong_fu_confirmed=True))

    def test_unconfirmed_strong_fu_cannot_create_zone(self) -> None:
        candle = Candle(open=100.0, high=112.0, low=94.0, close=108.0)
        self.assertIsNone(build_1m_strong_fu_zone(candle=candle, timeframe_minutes=1, strong_fu_confirmed=None))

    def test_full_zone_range_is_union_of_fu_wick_and_ob(self) -> None:
        fu_wick = ZoneRange(100.0, 103.0, "fu_wick")
        ob = ZoneRange(102.0, 105.0, "body_in_wick_ob")
        full = combine_full_zone_range(fu_wick=fu_wick, body_in_wick_orderblock=ob)
        self.assertEqual((full.low, full.high), (100.0, 105.0))

    def test_invalid_candle_geometry_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Candle(open=100.0, high=99.0, low=95.0, close=101.0)


if __name__ == "__main__":
    unittest.main()
