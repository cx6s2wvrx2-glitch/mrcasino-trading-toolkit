from __future__ import annotations

import unittest
from datetime import datetime, timezone

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.primitive_replay_scan import scan_primitive_replay_window


UTC = timezone.utc


def bar(ts: str, open_: float, high: float, low: float, close: float) -> MarketBar:
    return MarketBar(
        timestamp=datetime.fromisoformat(ts.replace("Z", "+00:00")),
        open=open_,
        high=high,
        low=low,
        close=close,
        is_closed=True,
        source_name="Exclusive Markets Ltd.",
        source_symbol="XAUUSD!",
    )


class March2023PrimitiveBoundaryTests(unittest.TestCase):
    def test_1972_70_source_true_stop_bar_is_not_forced_into_basic_fu_on_exclusive(self) -> None:
        # Immutable Exclusive reconstruction around the source-labelled 1972.70
        # True Stop / strongest-1m-FU discussion. The current bar is bullish but
        # its 1972.70 low does NOT sweep the immediately previous 1972.69 low.
        # Therefore the narrow previous-candle basic-FU candidate must stay false.
        bars = (
            bar("2023-03-30T15:52:00Z", 1973.09, 1973.15, 1972.69, 1972.80),
            bar("2023-03-30T15:53:00Z", 1972.80, 1973.53, 1972.70, 1973.47),
        )
        result = scan_primitive_replay_window(
            bars=bars,
            timeframe_seconds=60,
            scan_start=datetime(2023, 3, 30, 15, 52, tzinfo=UTC),
            scan_end=datetime(2023, 3, 30, 15, 54, tzinfo=UTC),
        )
        self.assertEqual(result.fu_candidates, ())
        self.assertEqual(result.ambiguous_basic_fu_bars, 0)
        self.assertEqual(result.adjacency_gap_pairs_skipped, 0)

    def test_1987_56_source_area_bar_is_ambiguous_basic_fu_on_exclusive(self) -> None:
        # The source describes 1987.56 imbalance / 1986 HCS context. On the
        # Exclusive execution feed the 12:34 bar extends above the previous high
        # AND below the previous low, so the narrow primitive scanner must fail
        # closed as an ambiguous both-side sweep rather than inventing a side.
        bars = (
            bar("2023-03-31T12:33:00Z", 1987.51, 1987.51, 1985.46, 1986.40),
            bar("2023-03-31T12:34:00Z", 1986.50, 1987.57, 1985.30, 1986.05),
        )
        result = scan_primitive_replay_window(
            bars=bars,
            timeframe_seconds=60,
            scan_start=datetime(2023, 3, 31, 12, 33, tzinfo=UTC),
            scan_end=datetime(2023, 3, 31, 12, 35, tzinfo=UTC),
        )
        self.assertEqual(result.fu_candidates, ())
        self.assertEqual(result.ambiguous_basic_fu_bars, 1)
        self.assertEqual(result.adjacency_gap_pairs_skipped, 0)


if __name__ == "__main__":
    unittest.main()
