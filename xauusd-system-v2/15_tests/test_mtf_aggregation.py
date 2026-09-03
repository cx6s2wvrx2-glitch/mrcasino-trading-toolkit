from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from xauusd_v2.mtf_aggregation import (
    MTFAggregationError,
    MinuteOHLC,
    TimeframeAggregator,
    aggregate_minutes,
    broker_bucket_bounds,
    parse_timeframe_codes,
)


class MTFAggregationTests(unittest.TestCase):
    def minute(
        self,
        timestamp: datetime,
        o: str,
        h: str,
        l: str,
        c: str,
    ) -> MinuteOHLC:
        return MinuteOHLC(
            timestamp_utc=timestamp,
            open_text=o,
            high_text=h,
            low_text=l,
            close_text=c,
        )

    def test_h4_bucket_uses_eet_winter_broker_boundary(self) -> None:
        spec = parse_timeframe_codes("H4")[0]
        start, end, local = broker_bucket_bounds(
            timestamp_utc=datetime(2026, 1, 5, 10, 37, tzinfo=UTC),
            timeframe=spec,
            broker_timezone=ZoneInfo("EET"),
        )
        self.assertEqual(local.hour, 12)
        self.assertEqual(start, datetime(2026, 1, 5, 10, 0, tzinfo=UTC))
        self.assertEqual(end, datetime(2026, 1, 5, 14, 0, tzinfo=UTC))

    def test_h4_bucket_uses_eest_summer_broker_boundary(self) -> None:
        spec = parse_timeframe_codes("H4")[0]
        start, end, local = broker_bucket_bounds(
            timestamp_utc=datetime(2026, 7, 6, 9, 37, tzinfo=UTC),
            timeframe=spec,
            broker_timezone=ZoneInfo("EET"),
        )
        self.assertEqual(local.hour, 12)
        self.assertEqual(start, datetime(2026, 7, 6, 9, 0, tzinfo=UTC))
        self.assertEqual(end, datetime(2026, 7, 6, 13, 0, tzinfo=UTC))

    def test_d1_boundary_moves_in_utc_across_dst(self) -> None:
        spec = parse_timeframe_codes("D1")[0]
        winter_start, _, _ = broker_bucket_bounds(
            timestamp_utc=datetime(2026, 1, 5, 10, 0, tzinfo=UTC),
            timeframe=spec,
            broker_timezone=ZoneInfo("EET"),
        )
        summer_start, _, _ = broker_bucket_bounds(
            timestamp_utc=datetime(2026, 7, 6, 10, 0, tzinfo=UTC),
            timeframe=spec,
            broker_timezone=ZoneInfo("EET"),
        )
        self.assertEqual(winter_start, datetime(2026, 1, 4, 22, 0, tzinfo=UTC))
        self.assertEqual(summer_start, datetime(2026, 7, 5, 21, 0, tzinfo=UTC))

    def test_m5_ohlc_and_internal_gap_are_preserved_without_fill(self) -> None:
        base = datetime(2026, 1, 5, 10, 0, tzinfo=UTC)
        minutes = (
            self.minute(base, "100.0", "100.2", "99.9", "100.1"),
            self.minute(base + timedelta(minutes=1), "100.1", "100.4", "100.0", "100.3"),
            self.minute(base + timedelta(minutes=3), "100.3", "100.5", "99.8", "99.9"),
            self.minute(base + timedelta(minutes=4), "99.9", "100.1", "99.7", "100.05"),
        )
        result = aggregate_minutes(
            minutes=minutes,
            timeframe=parse_timeframe_codes("M5")[0],
            broker_timezone=ZoneInfo("UTC"),
            source_coverage_end_utc=base + timedelta(minutes=5),
        )
        self.assertEqual(len(result), 1)
        bar = result[0]
        self.assertEqual(bar.open_text, "100.0")
        self.assertEqual(bar.high_text, "100.5")
        self.assertEqual(bar.low_text, "99.7")
        self.assertEqual(bar.close_text, "100.05")
        self.assertEqual(bar.child_count, 4)
        self.assertEqual(bar.expected_slots, 5)
        self.assertEqual(bar.leading_missing_minutes, 0)
        self.assertEqual(bar.internal_missing_minutes, 1)
        self.assertEqual(bar.trailing_missing_minutes, 0)
        self.assertTrue(bar.gap_affected)

    def test_leading_session_gap_is_diagnostic_not_synthetic(self) -> None:
        base = datetime(2026, 1, 5, 10, 0, tzinfo=UTC)
        minutes = tuple(
            self.minute(
                base + timedelta(minutes=i),
                str(100 + i),
                str(101 + i),
                str(99 + i),
                str(100.5 + i),
            )
            for i in (2, 3, 4)
        )
        result = aggregate_minutes(
            minutes=minutes,
            timeframe=parse_timeframe_codes("M5")[0],
            broker_timezone=ZoneInfo("UTC"),
            source_coverage_end_utc=base + timedelta(minutes=5),
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].leading_missing_minutes, 2)
        self.assertEqual(result[0].child_count, 3)

    def test_trailing_bucket_cut_by_source_horizon_is_not_emitted(self) -> None:
        base = datetime(2026, 1, 5, 10, 0, tzinfo=UTC)
        aggregator = TimeframeAggregator(
            timeframe=parse_timeframe_codes("H1")[0],
            broker_timezone=ZoneInfo("UTC"),
            source_coverage_end_utc=base + timedelta(minutes=52),
        )
        for i in range(52):
            candidate = aggregator.add(
                self.minute(
                    base + timedelta(minutes=i),
                    "100",
                    "101",
                    "99",
                    "100",
                )
            )
            self.assertIsNone(candidate)
        self.assertIsNone(aggregator.finish())
        self.assertEqual(aggregator.omitted_trailing_partial_buckets, 1)

    def test_historical_early_session_close_can_still_emit_closed_bucket(self) -> None:
        base = datetime(2026, 1, 5, 10, 0, tzinfo=UTC)
        minutes = tuple(
            self.minute(
                base + timedelta(minutes=i),
                "100",
                "101",
                "99",
                "100",
            )
            for i in range(30)
        )
        result = aggregate_minutes(
            minutes=minutes,
            timeframe=parse_timeframe_codes("H1")[0],
            broker_timezone=ZoneInfo("UTC"),
            source_coverage_end_utc=base + timedelta(hours=2),
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].trailing_missing_minutes, 30)

    def test_eleven_hour_synthesis_is_explicitly_blocked(self) -> None:
        with self.assertRaisesRegex(MTFAggregationError, "11h synthesis is blocked"):
            parse_timeframe_codes("H11")

    def test_unknown_timeframe_is_blocked(self) -> None:
        with self.assertRaises(MTFAggregationError):
            parse_timeframe_codes("H3")


if __name__ == "__main__":
    unittest.main()
