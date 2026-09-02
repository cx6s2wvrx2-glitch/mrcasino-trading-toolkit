from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.fu_intrabar_evidence import (
    FUIntrabarEvidenceState,
    extract_fu_intrabar_evidence,
)
from xauusd_v2.liquidity_interaction import LiquiditySide, MarkedLiquidityReference


class FUIntrabarEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parent_start = datetime(2026, 1, 5, 10, 0, tzinfo=UTC)
        self.evaluation_time = self.parent_start + timedelta(minutes=5)
        self.above = MarkedLiquidityReference(
            reference_id="liq-above",
            level=100.0,
            side=LiquiditySide.ABOVE,
            source_type="approved_marked_liquidity",
        )

    def bar(self, minute: int, o: float, h: float, l: float, c: float, *, source: str = "IC Markets") -> MarketBar:
        return MarketBar(
            timestamp=self.parent_start + timedelta(minutes=minute),
            open=o,
            high=h,
            low=l,
            close=c,
            is_closed=True,
            source_name=source,
            source_symbol="XAUUSD",
        )

    def test_records_first_take_and_later_return_without_calling_it_fu(self) -> None:
        bars = (
            self.bar(0, 99.0, 99.5, 98.8, 99.4),
            self.bar(1, 99.4, 100.3, 99.2, 100.1),
            self.bar(2, 100.0, 100.1, 99.3, 99.5),
            self.bar(3, 99.5, 99.8, 98.9, 99.0),
            self.bar(4, 99.0, 99.4, 98.7, 99.2),
        )
        result = extract_fu_intrabar_evidence(
            parent_start=self.parent_start,
            parent_timeframe_seconds=300,
            child_timeframe_seconds=60,
            child_bars=bars,
            reference=self.above,
            evaluation_time=self.evaluation_time,
        )
        self.assertEqual(result.state, FUIntrabarEvidenceState.POST_TAKE_PATH_AVAILABLE)
        self.assertEqual(result.first_take_child_index, 1)
        self.assertEqual(result.first_take_timestamp, self.parent_start + timedelta(minutes=1))
        self.assertEqual(result.post_take_bar_count, 3)
        self.assertTrue(result.returned_through_reference_after_take)
        self.assertAlmostEqual(result.farthest_post_take_price_in_expected_direction or 0.0, 98.7)
        self.assertAlmostEqual(result.post_take_excursion_from_reference or 0.0, 1.3)
        self.assertNotIn("fu confirmed", result.reason.lower())

    def test_take_without_later_return_is_preserved_as_objective_path(self) -> None:
        bars = (
            self.bar(0, 99.0, 99.5, 98.8, 99.4),
            self.bar(1, 99.4, 100.3, 99.2, 100.1),
            self.bar(2, 100.1, 100.8, 100.0, 100.5),
            self.bar(3, 100.5, 101.0, 100.2, 100.8),
            self.bar(4, 100.8, 101.2, 100.4, 101.0),
        )
        result = extract_fu_intrabar_evidence(
            parent_start=self.parent_start,
            parent_timeframe_seconds=300,
            child_timeframe_seconds=60,
            child_bars=bars,
            reference=self.above,
            evaluation_time=self.evaluation_time,
        )
        self.assertEqual(result.state, FUIntrabarEvidenceState.POST_TAKE_PATH_AVAILABLE)
        self.assertFalse(result.returned_through_reference_after_take)
        self.assertEqual(result.post_take_excursion_from_reference, 0.0)

    def test_no_take_is_explicit(self) -> None:
        bars = tuple(self.bar(i, 99.0, 99.8, 98.8, 99.4) for i in range(5))
        result = extract_fu_intrabar_evidence(
            parent_start=self.parent_start,
            parent_timeframe_seconds=300,
            child_timeframe_seconds=60,
            child_bars=bars,
            reference=self.above,
            evaluation_time=self.evaluation_time,
        )
        self.assertEqual(result.state, FUIntrabarEvidenceState.NO_LIQUIDITY_TAKE)
        self.assertIsNone(result.first_take_timestamp)

    def test_take_on_final_child_bar_cannot_claim_later_path(self) -> None:
        bars = (
            self.bar(0, 99.0, 99.5, 98.8, 99.4),
            self.bar(1, 99.4, 99.7, 99.0, 99.2),
            self.bar(2, 99.2, 99.6, 98.9, 99.5),
            self.bar(3, 99.5, 99.9, 99.1, 99.6),
            self.bar(4, 99.6, 100.4, 99.4, 100.2),
        )
        result = extract_fu_intrabar_evidence(
            parent_start=self.parent_start,
            parent_timeframe_seconds=300,
            child_timeframe_seconds=60,
            child_bars=bars,
            reference=self.above,
            evaluation_time=self.evaluation_time,
        )
        self.assertEqual(result.state, FUIntrabarEvidenceState.TAKE_ON_FINAL_CHILD_BAR)
        self.assertIsNone(result.returned_through_reference_after_take)

    def test_child_bars_must_exactly_tile_parent(self) -> None:
        bars = (
            self.bar(0, 99.0, 99.5, 98.8, 99.4),
            self.bar(1, 99.4, 99.7, 99.0, 99.2),
            self.bar(3, 99.2, 99.6, 98.9, 99.5),
            self.bar(4, 99.5, 99.9, 99.1, 99.6),
        )
        with self.assertRaises(ValueError):
            extract_fu_intrabar_evidence(
                parent_start=self.parent_start,
                parent_timeframe_seconds=300,
                child_timeframe_seconds=60,
                child_bars=bars,
                reference=self.above,
                evaluation_time=self.evaluation_time,
            )

    def test_mixed_broker_sources_are_rejected(self) -> None:
        bars = (
            self.bar(0, 99.0, 99.5, 98.8, 99.4),
            self.bar(1, 99.4, 99.7, 99.0, 99.2),
            self.bar(2, 99.2, 99.6, 98.9, 99.5, source="Pepperstone"),
            self.bar(3, 99.5, 99.9, 99.1, 99.6),
            self.bar(4, 99.6, 100.4, 99.4, 100.2),
        )
        with self.assertRaises(ValueError):
            extract_fu_intrabar_evidence(
                parent_start=self.parent_start,
                parent_timeframe_seconds=300,
                child_timeframe_seconds=60,
                child_bars=bars,
                reference=self.above,
                evaluation_time=self.evaluation_time,
            )

    def test_child_timeframe_must_divide_parent(self) -> None:
        bars = tuple(self.bar(i, 99.0, 99.8, 98.8, 99.4) for i in range(5))
        with self.assertRaises(ValueError):
            extract_fu_intrabar_evidence(
                parent_start=self.parent_start,
                parent_timeframe_seconds=300,
                child_timeframe_seconds=70,
                child_bars=bars,
                reference=self.above,
                evaluation_time=self.evaluation_time,
            )


if __name__ == "__main__":
    unittest.main()
