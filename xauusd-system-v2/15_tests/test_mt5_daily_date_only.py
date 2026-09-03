from __future__ import annotations

import unittest
from datetime import datetime, timezone

from xauusd_v2.mt5_history import MT5HistoryError, load_mt5_xauusd_history_bytes


UTC = timezone.utc


class MT5DailyDateOnlyTests(unittest.TestCase):
    def test_date_only_daily_export_uses_broker_local_midnight(self) -> None:
        raw = (
            "<DATE>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\n"
            "2026.01.02\t4331.44\t4402.31\t4309.86\t4332.66\t264330\t0\t17\n"
            "2026.01.05\t4357.85\t4455.72\t4344.19\t4448.79\t323433\t0\t17\n"
        ).encode("utf-8")
        result = load_mt5_xauusd_history_bytes(
            raw,
            broker_name="Exclusive Markets Ltd.",
            broker_symbol="XAUUSD!",
            source_timezone="EET",
            timeframe_seconds=86400,
            evaluation_time=datetime(2200, 1, 1, tzinfo=UTC),
            source_file_name="XAUUSD!_Daily_sample.csv",
        )
        self.assertEqual(result.bars[0].timestamp, datetime(2026, 1, 1, 22, 0, tzinfo=UTC))
        self.assertEqual(result.bars[1].timestamp, datetime(2026, 1, 4, 22, 0, tzinfo=UTC))
        self.assertEqual(result.ingestion.gap_count, 1)
        self.assertEqual(result.ingestion.gap_durations_seconds, (172800,))
        self.assertEqual(result.ingestion.detected_headers[0], "<DATE>")

    def test_daily_calendar_spacing_survives_dst_change(self) -> None:
        raw = (
            "<DATE>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\n"
            "2026.03.27\t1\t2\t0.5\t1.5\n"
            "2026.03.30\t1.5\t2\t1\t1.8\n"
        ).encode("utf-8")
        result = load_mt5_xauusd_history_bytes(
            raw,
            broker_name="Exclusive Markets Ltd.",
            broker_symbol="XAUUSD!",
            source_timezone="EET",
            timeframe_seconds=86400,
            evaluation_time=datetime(2200, 1, 1, tzinfo=UTC),
        )
        self.assertEqual(result.bars[0].timestamp, datetime(2026, 3, 26, 22, 0, tzinfo=UTC))
        self.assertEqual(result.bars[1].timestamp, datetime(2026, 3, 29, 21, 0, tzinfo=UTC))
        self.assertEqual(result.ingestion.gap_count, 1)

    def test_intraday_export_without_time_is_still_rejected(self) -> None:
        raw = (
            "<DATE>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\n"
            "2026.01.02\t1\t2\t0.5\t1.5\n"
        ).encode("utf-8")
        with self.assertRaisesRegex(MT5HistoryError, "missing required MT5 columns: time"):
            load_mt5_xauusd_history_bytes(
                raw,
                broker_name="Exclusive Markets Ltd.",
                broker_symbol="XAUUSD!",
                source_timezone="EET",
                timeframe_seconds=3600,
                evaluation_time=datetime(2200, 1, 1, tzinfo=UTC),
            )


if __name__ == "__main__":
    unittest.main()
