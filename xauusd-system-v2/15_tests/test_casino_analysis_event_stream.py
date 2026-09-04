from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.casino_analysis_event_stream import (
    CasinoAnalysisEventKind,
    build_casino_analysis_event_stream,
)
from xauusd_v2.casino_historical_event_runner import run_supplied_indicator_history
from xauusd_v2.casino_source_hcs_candidate import run_source_hcs_marker_proxy
from xauusd_v2.casino_source_hcs_negation_context import run_source_hcs_plus_negation_proxy
from xauusd_v2.casino_source_negation_candidate import run_source_marker_fu_negation_proxy


class CasinoAnalysisEventStreamTests(unittest.TestCase):
    def _bar(
        self,
        minute: int,
        *,
        open: float,
        high: float,
        low: float,
        close: float,
    ) -> MarketBar:
        return MarketBar(
            timestamp=datetime(2026, 9, 4, 0, 0, tzinfo=UTC) + timedelta(minutes=minute),
            open=open,
            high=high,
            low=low,
            close=close,
            is_closed=True,
            source_name="test_feed",
            source_symbol="XAUUSD!",
        )

    def _stream(self, bars: tuple[MarketBar, ...]):
        supplied = run_supplied_indicator_history(
            bars=bars,
            timeframe_seconds=60,
            symbol="XAUUSD",
            timeframe="M1",
        )
        hcs = run_source_hcs_marker_proxy(bars=bars)
        negation = run_source_marker_fu_negation_proxy(bars=bars)
        hcs_negation = run_source_hcs_plus_negation_proxy(
            bars=bars,
            hcs_run=hcs,
            negation_run=negation,
        )
        return build_casino_analysis_event_stream(
            supplied_run=supplied,
            source_hcs_run=hcs,
            source_negation_run=negation,
            source_hcs_negation_run=hcs_negation,
        )

    def test_one_frame_can_surface_strong_fu_hcs_fu_negation_and_hcs_plus_negation(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(1, open=101.0, high=107.0, low=94.0, close=106.0),  # Strong bull
            self._bar(2, open=108.0, high=109.0, low=95.0, close=103.0),  # ATT bear + HCS
            self._bar(3, open=102.0, high=111.0, low=94.0, close=110.0),  # Strong bull + negation
        )
        stream = self._stream(bars)

        self.assertFalse(stream.strategy_semantics_certified)
        frame = next(item for item in stream.frames if item.bar_time_utc == bars[3].timestamp)
        kinds = {event.kind for event in frame.events}
        self.assertIn(CasinoAnalysisEventKind.STRONG_FU, kinds)
        self.assertIn(CasinoAnalysisEventKind.FU_NEGATION, kinds)
        self.assertIn(CasinoAnalysisEventKind.HCS_PLUS_NEGATION, kinds)
        self.assertTrue(
            any(event.candidate_only for event in frame.events if event.kind is CasinoAnalysisEventKind.FU_NEGATION)
        )
        self.assertTrue(
            any(event.candidate_only for event in frame.events if event.kind is CasinoAnalysisEventKind.HCS_PLUS_NEGATION)
        )

    def test_attempted_to_attempted_hcs_is_not_promoted_to_fu_negation(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(1, open=101.0, high=107.0, low=94.0, close=104.0),  # ATT bull
            self._bar(2, open=105.0, high=108.0, low=95.0, close=103.0),  # ATT bear + HCS
        )
        stream = self._stream(bars)

        frame = next(item for item in stream.frames if item.bar_time_utc == bars[2].timestamp)
        kinds = {event.kind for event in frame.events}
        self.assertIn(CasinoAnalysisEventKind.ATTEMPTED_FU, kinds)
        self.assertIn(CasinoAnalysisEventKind.SOURCE_HCS, kinds)
        self.assertNotIn(CasinoAnalysisEventKind.FU_NEGATION, kinds)
        self.assertNotIn(CasinoAnalysisEventKind.HCS_PLUS_NEGATION, kinds)

    def test_source_and_beta_hcs_keep_separate_provenance_instead_of_false_dedup(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(1, open=101.0, high=107.0, low=94.0, close=104.0),
            self._bar(2, open=105.0, high=108.0, low=95.0, close=103.0),
        )
        stream = self._stream(bars)

        counts = dict(stream.counts_by_kind)
        self.assertGreaterEqual(counts.get(CasinoAnalysisEventKind.SOURCE_HCS.value, 0), 1)
        self.assertFalse(stream.reference_feed_alignment_complete)
        self.assertFalse(stream.performance_claim_allowed)
        self.assertFalse(stream.live_execution_authorized)


if __name__ == "__main__":
    unittest.main()
