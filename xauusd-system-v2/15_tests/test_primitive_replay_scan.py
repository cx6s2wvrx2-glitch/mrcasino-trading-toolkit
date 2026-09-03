from __future__ import annotations

import unittest
from datetime import datetime, timezone

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.primitive_replay_scan import (
    CandidateDirection,
    HCSCandidateForm,
    PrimitiveReplayScanError,
    scan_primitive_replay_window,
)


UTC = timezone.utc


class PrimitiveReplayScanTests(unittest.TestCase):
    def bar(self, minute: int, open_: float, high: float, low: float, close: float, *, closed: bool = True) -> MarketBar:
        return MarketBar(
            timestamp=datetime(2023, 3, 30, 12, minute, tzinfo=UTC),
            open=open_,
            high=high,
            low=low,
            close=close,
            is_closed=closed,
            source_name="fixture",
            source_symbol="XAUUSD!",
        )

    def scan(self, bars: tuple[MarketBar, ...]):
        return scan_primitive_replay_window(
            bars=bars,
            timeframe_seconds=60,
            scan_start=datetime(2023, 3, 30, 12, 0, tzinfo=UTC),
            scan_end=datetime(2023, 3, 30, 12, 10, tzinfo=UTC),
        )

    def test_bullish_basic_fu_candidate_records_lower_wick_interval(self) -> None:
        bars = (
            self.bar(0, 100.0, 101.0, 99.0, 100.5),
            self.bar(1, 100.2, 100.9, 98.5, 100.8),
        )
        result = self.scan(bars)
        self.assertEqual(len(result.fu_candidates), 1)
        event = result.fu_candidates[0]
        self.assertEqual(event.direction, CandidateDirection.BULLISH)
        self.assertEqual(event.candidate_wick_low, 98.5)
        self.assertEqual(event.candidate_wick_high, 100.2)
        self.assertTrue(event.candidate_wick_has_extent)
        self.assertFalse(event.certified_fu)

    def test_bearish_basic_fu_candidate_records_upper_wick_interval(self) -> None:
        bars = (
            self.bar(0, 100.0, 101.0, 99.0, 99.5),
            self.bar(1, 99.8, 101.5, 99.0, 99.2),
        )
        result = self.scan(bars)
        self.assertEqual(len(result.fu_candidates), 1)
        event = result.fu_candidates[0]
        self.assertEqual(event.direction, CandidateDirection.BEARISH)
        self.assertEqual(event.candidate_wick_low, 99.8)
        self.assertEqual(event.candidate_wick_high, 101.5)

    def test_same_direction_fu_candidate_on_wick_interaction_is_continuation_hcs_candidate(self) -> None:
        bars = (
            self.bar(0, 100.0, 101.0, 99.0, 100.5),
            self.bar(1, 100.2, 100.9, 98.5, 100.8),
            self.bar(2, 101.0, 102.0, 100.5, 101.8),
            self.bar(3, 100.1, 101.9, 98.4, 101.5),
        )
        result = self.scan(bars)
        observations = [
            item
            for item in result.wick_interactions
            if item.first_bar_open.minute == 1 and item.interaction_bar_open.minute == 3
        ]
        self.assertEqual(len(observations), 1)
        item = observations[0]
        self.assertTrue(item.source_style_hcs_candidate)
        self.assertEqual(item.second_direction, CandidateDirection.BULLISH)
        self.assertEqual(item.hcs_candidate_form, HCSCandidateForm.CONTINUATION)
        self.assertFalse(item.certified_hcs)

    def test_opposite_direction_fu_candidate_on_wick_interaction_is_negation_hcs_candidate(self) -> None:
        bars = (
            self.bar(0, 100.0, 101.0, 99.0, 100.5),
            self.bar(1, 100.2, 100.9, 98.5, 100.8),
            self.bar(2, 101.0, 102.0, 99.5, 101.8),
            self.bar(3, 101.0, 102.1, 99.7, 100.0),
        )
        result = self.scan(bars)
        observations = [
            item
            for item in result.wick_interactions
            if item.first_bar_open.minute == 1 and item.interaction_bar_open.minute == 3
        ]
        self.assertEqual(len(observations), 1)
        item = observations[0]
        self.assertTrue(item.source_style_hcs_candidate)
        self.assertEqual(item.second_direction, CandidateDirection.BEARISH)
        self.assertEqual(item.hcs_candidate_form, HCSCandidateForm.NEGATION)

    def test_plain_wick_interaction_is_observable_not_hcs_candidate(self) -> None:
        bars = (
            self.bar(0, 100.0, 101.0, 99.0, 100.5),
            self.bar(1, 100.2, 100.9, 98.5, 100.8),
            self.bar(2, 100.4, 100.8, 99.9, 100.3),
        )
        result = self.scan(bars)
        item = next(
            obs
            for obs in result.wick_interactions
            if obs.first_bar_open.minute == 1 and obs.interaction_bar_open.minute == 2
        )
        self.assertFalse(item.basic_fu_candidate_on_interaction_bar)
        self.assertFalse(item.source_style_hcs_candidate)
        self.assertIsNone(item.hcs_candidate_form)

    def test_both_side_sweep_is_counted_ambiguous_not_fu_candidate(self) -> None:
        bars = (
            self.bar(0, 100.0, 101.0, 99.0, 100.5),
            self.bar(1, 100.0, 102.0, 98.0, 101.0),
        )
        result = self.scan(bars)
        self.assertEqual(result.ambiguous_basic_fu_bars, 1)
        self.assertEqual(result.fu_candidates, ())

    def test_provisional_bar_removal_creates_gap_and_pair_is_not_classified(self) -> None:
        bars = (
            self.bar(0, 100.0, 101.0, 99.0, 100.5),
            self.bar(1, 100.2, 100.9, 98.5, 100.8, closed=False),
            self.bar(2, 100.2, 100.9, 98.5, 100.8),
        )
        result = self.scan(bars)
        self.assertEqual(result.bar_count, 2)
        self.assertEqual(result.fu_candidates, ())
        self.assertEqual(result.adjacency_gap_pairs_skipped, 1)

    def test_explicit_research_window_safety_limit_fails_closed(self) -> None:
        bars = tuple(
            self.bar(minute, 100.0, 101.0, 99.0, 100.5)
            for minute in range(5)
        )
        with self.assertRaisesRegex(PrimitiveReplayScanError, "safety limit"):
            scan_primitive_replay_window(
                bars=bars,
                timeframe_seconds=60,
                scan_start=datetime(2023, 3, 30, 12, 0, tzinfo=UTC),
                scan_end=datetime(2023, 3, 30, 12, 10, tzinfo=UTC),
                max_window_bars=4,
            )

    def test_naive_scan_time_is_rejected(self) -> None:
        bars = (
            self.bar(0, 100.0, 101.0, 99.0, 100.5),
            self.bar(1, 100.2, 100.9, 98.5, 100.8),
        )
        with self.assertRaisesRegex(PrimitiveReplayScanError, "timezone-aware"):
            scan_primitive_replay_window(
                bars=bars,
                timeframe_seconds=60,
                scan_start=datetime(2023, 3, 30, 12, 0),
                scan_end=datetime(2023, 3, 30, 12, 10, tzinfo=UTC),
            )


if __name__ == "__main__":
    unittest.main()
