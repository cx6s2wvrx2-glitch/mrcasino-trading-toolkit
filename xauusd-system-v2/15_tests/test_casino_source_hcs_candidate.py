from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.casino_source_hcs_candidate import (
    STATUS,
    SourceHCSMarkerProxyForm,
    run_source_hcs_marker_proxy,
)


class CasinoSourceHCSMarkerProxyTests(unittest.TestCase):
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

    def test_strong_strong_exact_latest_marker_wick_retest_is_l3_proxy(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(15, open=101.0, high=107.0, low=94.0, close=106.0),
            self._bar(30, open=102.0, high=109.0, low=93.0, close=108.0),
        )
        run = run_source_hcs_marker_proxy(bars=bars)

        self.assertEqual(run.status, STATUS)
        self.assertEqual(run.marker_node_count, 2)
        self.assertEqual(run.candidate_count, 1)
        candidate = run.candidates[0]
        self.assertEqual(candidate.form, SourceHCSMarkerProxyForm.STRONG_STRONG)
        self.assertEqual(candidate.source_strength_label_proxy, "L3_PROXY")
        self.assertTrue(candidate.exact_last_marker_wick_retest)
        self.assertTrue(candidate.same_direction)
        self.assertEqual(candidate.latest_prior_marker_node_count, 1)
        self.assertFalse(candidate.source_hcs_semantics_certified)
        self.assertFalse(run.reference_feed_alignment_complete)
        self.assertFalse(run.live_execution_authorized)

    def test_strong_attempted_opposite_direction_is_observed_not_filtered(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(15, open=101.0, high=107.0, low=94.0, close=106.0),
            self._bar(30, open=108.0, high=109.0, low=95.0, close=103.0),
        )
        run = run_source_hcs_marker_proxy(bars=bars)

        self.assertEqual(run.candidate_count, 1)
        candidate = run.candidates[0]
        self.assertEqual(candidate.form, SourceHCSMarkerProxyForm.STRONG_ATTEMPTED)
        self.assertEqual(candidate.source_strength_label_proxy, "L2_PROXY")
        self.assertFalse(candidate.same_direction)
        self.assertFalse(run.same_direction_required)

    def test_latest_prior_marker_rule_does_not_reach_back_to_older_marker_wick(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            # Strong bull, wick [94, 101].
            self._bar(15, open=101.0, high=107.0, low=94.0, close=106.0),
            # Bear ATT, wick [108, 109]; this itself retests the strong-bull wick.
            self._bar(30, open=108.0, high=109.0, low=95.0, close=103.0),
            # Bull ATT range [93, 106] retests the older strong-bull wick but does
            # not touch the latest bear-ATT wick [108, 109].
            self._bar(45, open=102.0, high=106.0, low=93.0, close=104.0),
        )
        run = run_source_hcs_marker_proxy(bars=bars)

        self.assertEqual(run.candidate_count, 1)
        self.assertEqual(run.candidates[0].second_bar_time_utc, bars[2].timestamp)
        self.assertNotIn(bars[3].timestamp, [item.second_bar_time_utc for item in run.candidates])
        self.assertTrue(run.latest_marker_only)

    def test_final_provisional_marker_is_not_evaluated(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(15, open=101.0, high=107.0, low=94.0, close=106.0),
            self._bar(30, open=102.0, high=109.0, low=93.0, close=108.0, closed=False),
        )
        run = run_source_hcs_marker_proxy(bars=bars)

        self.assertEqual(run.closed_bar_count, 2)
        self.assertEqual(run.marker_node_count, 1)
        self.assertEqual(run.candidate_count, 0)


if __name__ == "__main__":
    unittest.main()
