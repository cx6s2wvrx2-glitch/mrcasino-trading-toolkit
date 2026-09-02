from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.broker_precision import BrokerPriceSpec
from xauusd_v2.parent_child_bar_alignment import (
    ParentChildAlignmentState,
    validate_parent_child_alignment,
)


class ParentChildBarAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime(2026, 1, 5, 10, 0, tzinfo=UTC)
        self.eval = self.start + timedelta(minutes=5)
        self.spec = BrokerPriceSpec.from_strings(
            broker_name="IC Markets",
            source_symbol="XAUUSD",
            digits=2,
            tick_size="0.01",
        )

    def child(self, minute: int, o: float, h: float, l: float, c: float, *, source: str = "IC Markets", symbol: str = "XAUUSD") -> MarketBar:
        return MarketBar(
            timestamp=self.start + timedelta(minutes=minute),
            open=o,
            high=h,
            low=l,
            close=c,
            is_closed=True,
            source_name=source,
            source_symbol=symbol,
        )

    def valid_children(self) -> tuple[MarketBar, ...]:
        return (
            self.child(0, 100.00, 100.20, 99.90, 100.10),
            self.child(1, 100.10, 100.40, 100.00, 100.30),
            self.child(2, 100.30, 100.50, 100.20, 100.25),
            self.child(3, 100.25, 100.35, 99.80, 99.90),
            self.child(4, 99.90, 100.10, 99.70, 100.05),
        )

    def parent(self, *, source: str = "IC Markets", symbol: str = "XAUUSD", high: float = 100.50) -> MarketBar:
        return MarketBar(
            timestamp=self.start,
            open=100.00,
            high=high,
            low=99.70,
            close=100.05,
            is_closed=True,
            source_name=source,
            source_symbol=symbol,
        )

    def test_exact_child_reconstruction_is_aligned(self) -> None:
        result = validate_parent_child_alignment(
            parent_bar=self.parent(),
            parent_timeframe_seconds=300,
            child_bars=self.valid_children(),
            child_timeframe_seconds=60,
            evaluation_time=self.eval,
            price_spec=self.spec,
        )
        self.assertEqual(result.state, ParentChildAlignmentState.ALIGNED)
        self.assertTrue(result.aligned)
        self.assertEqual(result.high_distance_ticks, 0)

    def test_parent_high_mismatch_is_reported_in_ticks(self) -> None:
        result = validate_parent_child_alignment(
            parent_bar=self.parent(high=100.55),
            parent_timeframe_seconds=300,
            child_bars=self.valid_children(),
            child_timeframe_seconds=60,
            evaluation_time=self.eval,
            price_spec=self.spec,
        )
        self.assertEqual(result.state, ParentChildAlignmentState.OHLC_MISMATCH)
        self.assertFalse(result.aligned)
        self.assertEqual(result.high_distance_ticks, 5)

    def test_cross_broker_child_series_is_blocked(self) -> None:
        children = list(self.valid_children())
        children[2] = self.child(2, 100.30, 100.50, 100.20, 100.25, source="Pepperstone")
        result = validate_parent_child_alignment(
            parent_bar=self.parent(),
            parent_timeframe_seconds=300,
            child_bars=tuple(children),
            child_timeframe_seconds=60,
            evaluation_time=self.eval,
            price_spec=self.spec,
        )
        self.assertEqual(result.state, ParentChildAlignmentState.SOURCE_MISMATCH)

    def test_cross_symbol_child_series_is_blocked(self) -> None:
        children = list(self.valid_children())
        children[2] = self.child(2, 100.30, 100.50, 100.20, 100.25, symbol="GOLD")
        result = validate_parent_child_alignment(
            parent_bar=self.parent(),
            parent_timeframe_seconds=300,
            child_bars=tuple(children),
            child_timeframe_seconds=60,
            evaluation_time=self.eval,
            price_spec=self.spec,
        )
        self.assertEqual(result.state, ParentChildAlignmentState.SYMBOL_MISMATCH)

    def test_missing_child_interval_is_coverage_mismatch(self) -> None:
        children = self.valid_children()[:-1]
        result = validate_parent_child_alignment(
            parent_bar=self.parent(),
            parent_timeframe_seconds=300,
            child_bars=children,
            child_timeframe_seconds=60,
            evaluation_time=self.eval,
            price_spec=self.spec,
        )
        self.assertEqual(result.state, ParentChildAlignmentState.COVERAGE_MISMATCH)

    def test_parent_must_match_declared_broker_spec(self) -> None:
        result = validate_parent_child_alignment(
            parent_bar=self.parent(source="Pepperstone"),
            parent_timeframe_seconds=300,
            child_bars=self.valid_children(),
            child_timeframe_seconds=60,
            evaluation_time=self.eval,
            price_spec=self.spec,
        )
        self.assertEqual(result.state, ParentChildAlignmentState.SOURCE_MISMATCH)

    def test_non_divisible_child_timeframe_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_parent_child_alignment(
                parent_bar=self.parent(),
                parent_timeframe_seconds=300,
                child_bars=self.valid_children(),
                child_timeframe_seconds=70,
                evaluation_time=self.eval,
                price_spec=self.spec,
            )


if __name__ == "__main__":
    unittest.main()
