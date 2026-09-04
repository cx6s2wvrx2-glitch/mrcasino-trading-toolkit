from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.casino_source_negation_candidate import (
    STATUS,
    run_source_marker_fu_negation_proxy,
)
from xauusd_v2.helper_fu_shadow import HelperFUClass
from xauusd_v2.negation_semantic import NegationState


class CasinoSourceMarkerFUNegationProxyTests(unittest.TestCase):
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

    def test_attempted_fu_can_be_original_and_opposite_strong_next_bar_is_proxy(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            # Bull ATT: manipulates below previous low but closes below previous high.
            self._bar(1, open=101.0, high=107.0, low=94.0, close=104.0),
            # Bear Strong: opposite full/helper-F close on the next candle.
            self._bar(2, open=103.0, high=108.0, low=92.0, close=91.0),
        )
        run = run_source_marker_fu_negation_proxy(bars=bars)

        self.assertEqual(run.status, STATUS)
        self.assertEqual(run.candidate_count, 1)
        candidate = run.candidates[0]
        self.assertEqual(candidate.candle_offset, 1)
        self.assertEqual(candidate.original_helper_class, HelperFUClass.ATT)
        self.assertEqual(candidate.negating_helper_class, HelperFUClass.FU)
        self.assertEqual(
            candidate.semantic_state_if_helper_strong_is_complete_fu,
            NegationState.CONFIRMED,
        )
        self.assertTrue(candidate.helper_strong_used_as_complete_fu_proxy)
        self.assertFalse(candidate.raw_negation_semantics_certified)
        self.assertFalse(run.reference_feed_alignment_complete)

    def test_offset_two_is_allowed_when_intervening_bar_has_no_marker(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(1, open=101.0, high=107.0, low=94.0, close=106.0),  # bull Strong
            self._bar(2, open=104.0, high=106.0, low=96.0, close=103.0),  # no marker
            self._bar(3, open=104.0, high=107.0, low=94.0, close=95.0),   # bear Strong
        )
        run = run_source_marker_fu_negation_proxy(bars=bars)

        self.assertEqual(run.candidate_count, 1)
        self.assertEqual(run.candidates[0].candle_offset, 2)
        self.assertEqual(run.candidates[0].original_bar_time_utc, bars[1].timestamp)

    def test_same_direction_strong_is_not_negation(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(1, open=101.0, high=107.0, low=94.0, close=106.0),
            self._bar(2, open=102.0, high=109.0, low=93.0, close=108.0),
        )
        run = run_source_marker_fu_negation_proxy(bars=bars)
        self.assertEqual(run.candidate_count, 0)

    def test_opposite_attempted_current_marker_is_not_promoted_to_negation(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(1, open=101.0, high=107.0, low=94.0, close=106.0),  # bull Strong
            self._bar(2, open=105.0, high=108.0, low=95.0, close=103.0),  # bear ATT
        )
        run = run_source_marker_fu_negation_proxy(bars=bars)
        self.assertEqual(run.candidate_count, 0)
        self.assertTrue(run.negating_marker_must_be_strong_fu)

    def test_latest_marker_blocks_reaching_back_to_older_opposite_manipulation(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(1, open=101.0, high=107.0, low=94.0, close=106.0),  # bull Strong
            self._bar(2, open=105.0, high=108.0, low=95.0, close=103.0),  # bear ATT
            self._bar(3, open=104.0, high=109.0, low=93.0, close=92.0),   # bear Strong
        )
        run = run_source_marker_fu_negation_proxy(bars=bars)

        # Current bear Strong is opposite the older bull Strong at +2, but the latest
        # manipulation is the bear ATT at +1, so it is not a negation of the older node.
        self.assertEqual(run.candidate_count, 0)
        self.assertTrue(run.latest_prior_manipulation_only)

    def test_final_provisional_strong_marker_is_ignored(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(1, open=101.0, high=107.0, low=94.0, close=104.0),
            self._bar(2, open=103.0, high=108.0, low=92.0, close=91.0, closed=False),
        )
        run = run_source_marker_fu_negation_proxy(bars=bars)

        self.assertEqual(run.closed_bar_count, 2)
        self.assertEqual(run.candidate_count, 0)


if __name__ == "__main__":
    unittest.main()
