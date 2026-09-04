from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.casino_directional_marker_semantics import (
    CasinoMarkerDirection,
    CasinoMarkerVisualCue,
)
from xauusd_v2.casino_historical_event_runner import (
    STATUS,
    run_supplied_indicator_history,
)
from xauusd_v2.casino_indicator_events import CasinoIndicatorEventKind


class CasinoHistoricalEventRunnerTests(unittest.TestCase):
    def _bar(
        self,
        minute: int,
        *,
        open: float,
        high: float,
        low: float,
        close: float,
        closed: bool = True,
    ) -> MarketBar:
        return MarketBar(
            timestamp=datetime(2026, 9, 4, 0, 0, tzinfo=UTC) + timedelta(minutes=minute),
            open=open,
            high=high,
            low=low,
            close=close,
            is_closed=closed,
            source_name="test_feed",
            source_symbol="XAUUSD!",
        )

    def test_historical_casino_v7_strong_bull_marker_is_emitted(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(15, open=99.0, high=107.0, low=94.0, close=106.0),
        )
        run = run_supplied_indicator_history(bars=bars, timeframe_seconds=900)

        self.assertEqual(run.status, STATUS)
        self.assertEqual(run.evaluated_bar_count, 1)
        self.assertEqual(run.event_frame_count, 1)
        event = run.frames[0].events[0]
        self.assertEqual(event.kind, CasinoIndicatorEventKind.STRONG_FU)
        self.assertEqual(event.direction, CasinoMarkerDirection.BULLISH)
        self.assertEqual(event.visual_cue, CasinoMarkerVisualCue.BRIGHT_GREEN)
        self.assertFalse(event.strategy_semantics_certified)
        self.assertFalse(run.strategy_semantics_certified)
        self.assertFalse(run.live_execution_authorized)

    def test_historical_casino_v7_attempted_bull_marker_is_emitted(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(15, open=99.0, high=106.0, low=94.0, close=104.0),
        )
        run = run_supplied_indicator_history(bars=bars, timeframe_seconds=900)

        event = run.frames[0].events[0]
        self.assertEqual(event.kind, CasinoIndicatorEventKind.ATTEMPTED_FU)
        self.assertEqual(event.direction, CasinoMarkerDirection.BULLISH)
        self.assertEqual(event.visual_cue, CasinoMarkerVisualCue.FADED_GREEN)

    def test_supplied_current_doji_filter_removes_strong_fu_marker(self) -> None:
        bars = (
            self._bar(0, open=99.8, high=100.0, low=99.5, close=99.8),
            self._bar(15, open=99.9, high=100.2, low=99.4, close=100.1),
        )
        run = run_supplied_indicator_history(bars=bars, timeframe_seconds=900)

        self.assertEqual(run.event_frame_count, 0)
        self.assertEqual(run.diagnostics[0].casino_bullish_branch, "bull_continuation_fu")
        self.assertTrue(run.diagnostics[0].casino_helper_doji)

    def test_beta_hcs_counter_replays_x1_then_x2_on_same_tracked_box(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            # BETA bull FU creates a tracked bull box [94, 100].
            self._bar(15, open=100.0, high=104.0, low=94.0, close=100.0),
            # No new BETA FU; the original box survives and is retested.
            self._bar(30, open=101.0, high=103.0, low=96.0, close=102.0),
            # New bull FU enters the original box -> HCS X1.
            self._bar(45, open=99.0, high=102.0, low=95.0, close=100.0),
            # Newest box is broken, but the original survives -> HCS X2.
            self._bar(60, open=98.0, high=101.0, low=94.5, close=99.0),
        )
        run = run_supplied_indicator_history(bars=bars, timeframe_seconds=900)

        hcs_events = [
            event
            for frame in run.frames
            for event in frame.events
            if event.kind is CasinoIndicatorEventKind.HCS
        ]
        self.assertEqual([event.hcs_count for event in hcs_events], [1, 2])
        self.assertEqual(
            [event.marker_text for event in hcs_events],
            ["HCS X1", "HCS X2"],
        )
        self.assertTrue(all(event.direction is CasinoMarkerDirection.BULLISH for event in hcs_events))
        self.assertEqual(
            [diag.emitted_hcs_counts for diag in run.diagnostics[-2:]],
            [(('bullish', 1),), (('bullish', 2),)],
        )

    def test_final_provisional_bar_is_not_allowed_to_emit_confirmed_events(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(15, open=100.0, high=104.0, low=96.0, close=101.0),
            self._bar(30, open=99.0, high=107.0, low=94.0, close=106.0, closed=False),
        )
        run = run_supplied_indicator_history(bars=bars, timeframe_seconds=900)

        self.assertEqual(run.input_bar_count, 3)
        self.assertEqual(run.closed_bar_count, 2)
        self.assertEqual(run.evaluated_bar_count, 1)
        self.assertEqual(len(run.diagnostics), 1)
        self.assertNotEqual(run.diagnostics[0].bar_time_utc, bars[-1].timestamp)

    def test_non_monotonic_history_is_rejected(self) -> None:
        bar = self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0)
        with self.assertRaises(ValueError):
            run_supplied_indicator_history(bars=(bar, bar), timeframe_seconds=900)


if __name__ == "__main__":
    unittest.main()
