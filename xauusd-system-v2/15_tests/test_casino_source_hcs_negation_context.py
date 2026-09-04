from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.casino_source_hcs_negation_context import (
    STATUS,
    run_source_hcs_plus_negation_proxy,
)
from xauusd_v2.casino_source_hcs_candidate import SourceHCSMarkerProxyForm


class CasinoSourceHCSPlusNegationProxyTests(unittest.TestCase):
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

    def test_hcs_second_node_negated_next_candle_is_composite_proxy(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            # Strong bull.
            self._bar(1, open=101.0, high=107.0, low=94.0, close=106.0),
            # Bear ATT retests strong-bull wick -> source-style HCS.
            self._bar(2, open=108.0, high=109.0, low=95.0, close=103.0),
            # Bull Strong negates the HCS second node at +1.
            self._bar(3, open=102.0, high=111.0, low=94.0, close=110.0),
        )
        run = run_source_hcs_plus_negation_proxy(bars=bars)

        self.assertEqual(run.status, STATUS)
        self.assertEqual(run.composite_candidate_count, 1)
        candidate = run.candidates[0]
        self.assertEqual(candidate.hcs_bar_time_utc, bars[2].timestamp)
        self.assertEqual(candidate.negating_bar_time_utc, bars[3].timestamp)
        self.assertEqual(candidate.negation_candle_offset, 1)
        self.assertEqual(candidate.hcs_form, SourceHCSMarkerProxyForm.STRONG_ATTEMPTED)
        self.assertEqual(candidate.hcs_second_semantic_role, "attempted_fu")
        self.assertTrue(candidate.negation_opposes_hcs_second_node)
        self.assertFalse(candidate.hcs_plus_negation_semantics_certified)
        self.assertTrue(run.excludes_negation_of_negation_x3)

    def test_negation_not_of_hcs_second_node_is_not_composite(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(1, open=101.0, high=107.0, low=94.0, close=106.0),  # strong bull
            self._bar(2, open=104.0, high=106.0, low=96.0, close=103.0),  # no marker
            self._bar(3, open=104.0, high=107.0, low=94.0, close=95.0),   # bear strong negates bar1 at +2
        )
        run = run_source_hcs_plus_negation_proxy(bars=bars)
        self.assertEqual(run.composite_candidate_count, 0)

    def test_negation_of_negation_hcs_node_is_excluded_as_x3_boundary(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            # Bull ATT.
            self._bar(1, open=101.0, high=107.0, low=94.0, close=104.0),
            # Bear Strong: FU-negation of bar1 and ATT+negation HCS physical second node.
            self._bar(2, open=103.0, high=108.0, low=91.0, close=92.0),
            # Bull Strong would negate the negation, which is x3 territory.
            self._bar(3, open=93.0, high=109.0, low=90.0, close=108.0),
        )
        run = run_source_hcs_plus_negation_proxy(bars=bars)

        self.assertEqual(run.composite_candidate_count, 0)
        self.assertTrue(run.excludes_negation_of_negation_x3)


if __name__ == "__main__":
    unittest.main()
