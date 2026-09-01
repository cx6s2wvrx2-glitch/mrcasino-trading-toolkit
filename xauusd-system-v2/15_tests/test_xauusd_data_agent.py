from __future__ import annotations

import unittest
from datetime import datetime, timezone

from xauusd_v2.agents.base import AgentContractError
from xauusd_v2.agents.data_agent import MarketBar, XAUUSDDataAgent


UTC = timezone.utc


def bar(ts: str, *, closed: bool = True, o: float = 2000.0, h: float = 2002.0, l: float = 1999.0, c: float = 2001.0) -> MarketBar:
    return MarketBar(
        timestamp=datetime.fromisoformat(ts).replace(tzinfo=UTC),
        open=o,
        high=h,
        low=l,
        close=c,
        is_closed=closed,
        source_name="IC Markets MT5",
        source_symbol="XAUUSD.a",
    )


class XAUUSDDataAgentTests(unittest.TestCase):
    def test_valid_closed_batch(self) -> None:
        agent = XAUUSDDataAgent()
        report, run = agent.validate_batch(
            bars=(bar("2026-09-01T12:00:00"), bar("2026-09-01T12:05:00")),
            timeframe_seconds=300,
            evaluation_time=datetime(2026, 9, 1, 12, 10, tzinfo=UTC),
        )
        self.assertEqual(report.closed_bars, 2)
        self.assertEqual(report.provisional_bars, 0)
        self.assertFalse(run.needs_review)

    def test_final_provisional_bar_is_preserved_not_confirmed(self) -> None:
        agent = XAUUSDDataAgent()
        report, run = agent.validate_batch(
            bars=(bar("2026-09-01T12:00:00"), bar("2026-09-01T12:05:00"), bar("2026-09-01T12:10:00", closed=False)),
            timeframe_seconds=300,
            evaluation_time=datetime(2026, 9, 1, 12, 12, tzinfo=UTC),
        )
        self.assertEqual(report.closed_bars, 2)
        self.assertEqual(report.provisional_bars, 1)
        self.assertTrue(run.needs_review)
        self.assertTrue(report.warnings)

    def test_duplicate_timestamp_is_rejected(self) -> None:
        agent = XAUUSDDataAgent()
        with self.assertRaises(AgentContractError):
            agent.validate_batch(
                bars=(bar("2026-09-01T12:00:00"), bar("2026-09-01T12:00:00")),
                timeframe_seconds=300,
                evaluation_time=datetime(2026, 9, 1, 12, 10, tzinfo=UTC),
            )

    def test_impossible_ohlc_is_rejected(self) -> None:
        agent = XAUUSDDataAgent()
        with self.assertRaises(AgentContractError):
            agent.validate_batch(
                bars=(bar("2026-09-01T12:00:00", o=2000, h=2000.5, l=1999, c=2001),),
                timeframe_seconds=300,
                evaluation_time=datetime(2026, 9, 1, 12, 10, tzinfo=UTC),
            )

    def test_bar_cannot_be_marked_closed_before_close_time(self) -> None:
        agent = XAUUSDDataAgent()
        with self.assertRaises(AgentContractError):
            agent.validate_batch(
                bars=(bar("2026-09-01T12:10:00", closed=True),),
                timeframe_seconds=300,
                evaluation_time=datetime(2026, 9, 1, 12, 12, tzinfo=UTC),
            )

    def test_provisional_bar_must_be_last(self) -> None:
        agent = XAUUSDDataAgent()
        with self.assertRaises(AgentContractError):
            agent.validate_batch(
                bars=(bar("2026-09-01T12:00:00", closed=False), bar("2026-09-01T12:05:00", closed=True)),
                timeframe_seconds=300,
                evaluation_time=datetime(2026, 9, 1, 12, 10, tzinfo=UTC),
            )

    def test_non_xauusd_canonical_symbol_is_rejected(self) -> None:
        agent = XAUUSDDataAgent()
        with self.assertRaises(AgentContractError):
            agent.validate_batch(
                bars=(bar("2026-09-01T12:00:00"),),
                timeframe_seconds=300,
                evaluation_time=datetime(2026, 9, 1, 12, 10, tzinfo=UTC),
                canonical_symbol="EURUSD",
            )


if __name__ == "__main__":
    unittest.main()
