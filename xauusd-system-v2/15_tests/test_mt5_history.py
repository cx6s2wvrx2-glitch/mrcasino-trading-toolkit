from __future__ import annotations

import unittest
from datetime import datetime, timezone

from xauusd_v2.mt5_history import MT5HistoryError, load_mt5_xauusd_history_bytes


UTC = timezone.utc


def _tab_export() -> bytes:
    return (
        "<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\n"
        "2024.01.02\t10:00:00\t2060.00\t2061.00\t2059.50\t2060.50\t100\t0\t25\n"
        "2024.01.02\t10:05:00\t2060.50\t2062.00\t2060.00\t2061.50\t120\t0\t24\n"
        "2024.01.02\t10:10:00\t2061.50\t2063.00\t2061.00\t2062.50\t130\t0\t26\n"
    ).encode("utf-8")


class MT5HistoryTests(unittest.TestCase):
    def _load(self, raw: bytes = _tab_export(), **overrides):
        kwargs = {
            "broker_name": "IC Markets MT5",
            "broker_symbol": "XAUUSD.a",
            "source_timezone": "UTC+02:00",
            "timeframe_seconds": 300,
            "evaluation_time": datetime(2024, 1, 2, 9, 0, tzinfo=UTC),
            "source_file_name": "XAUUSD_M5.csv",
        }
        kwargs.update(overrides)
        return load_mt5_xauusd_history_bytes(raw, **kwargs)

    def test_tab_mt5_export_normalizes_to_utc_and_existing_snapshot_contract(self) -> None:
        result = self._load()
        self.assertEqual(len(result.bars), 3)
        self.assertEqual(result.bars[0].timestamp, datetime(2024, 1, 2, 8, 0, tzinfo=UTC))
        self.assertEqual(result.bars[0].source_name, "IC Markets MT5")
        self.assertEqual(result.bars[0].source_symbol, "XAUUSD.a")
        self.assertEqual(result.ingestion.detected_delimiter, "TAB")
        self.assertEqual(result.ingestion.optional_columns, ("tick_volume", "real_volume", "spread"))
        self.assertEqual(result.supplemental[0].tick_volume, 100)
        self.assertEqual(result.supplemental[0].real_volume, 0)
        self.assertEqual(result.supplemental[0].spread_points, 25)
        self.assertTrue(result.snapshot.closed_only)
        self.assertEqual(result.ingestion.normalized_snapshot_id, result.snapshot.snapshot_id)

    def test_optional_mt5_fields_do_not_enter_canonical_snapshot_csv(self) -> None:
        result = self._load()
        text = result.canonical_csv_bytes.decode("utf-8")
        self.assertEqual(text.splitlines()[0], "timestamp,open,high,low,close")
        self.assertNotIn("spread", text.lower())
        self.assertNotIn("tickvol", text.lower())

    def test_equivalent_tab_and_csv_exports_produce_same_normalized_snapshot(self) -> None:
        tab = self._load()
        csv_raw = (
            "date,time,open,high,low,close,tick_volume,volume,spread\n"
            "2024.01.02,10:00,2060,2061,2059.5,2060.5,100,0,25\n"
            "2024.01.02,10:05,2060.5,2062,2060,2061.5,120,0,24\n"
            "2024.01.02,10:10,2061.5,2063,2061,2062.5,130,0,26\n"
        ).encode("utf-8")
        comma = self._load(csv_raw)
        self.assertNotEqual(tab.ingestion.source_sha256, comma.ingestion.source_sha256)
        self.assertEqual(tab.snapshot.snapshot_id, comma.snapshot.snapshot_id)

    def test_source_timezone_is_never_inferred(self) -> None:
        with self.assertRaisesRegex(MT5HistoryError, "source_timezone is required"):
            self._load(source_timezone="")

    def test_iana_timezone_is_supported_explicitly(self) -> None:
        result = self._load(source_timezone="Europe/Athens")
        self.assertEqual(result.bars[0].timestamp, datetime(2024, 1, 2, 8, 0, tzinfo=UTC))
        self.assertEqual(result.ingestion.source_timezone, "Europe/Athens")

    def test_duplicate_or_out_of_order_bars_are_rejected(self) -> None:
        raw = (
            "<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\n"
            "2024.01.02\t10:00\t1\t2\t0.5\t1.5\n"
            "2024.01.02\t10:00\t1.5\t2\t1\t1.8\n"
        ).encode()
        with self.assertRaisesRegex(MT5HistoryError, "strictly increasing"):
            self._load(raw)

    def test_declared_timeframe_overlap_or_off_spacing_is_rejected(self) -> None:
        raw = (
            "date,time,open,high,low,close\n"
            "2024.01.02,10:00,1,2,0.5,1.5\n"
            "2024.01.02,10:03,1.5,2,1,1.8\n"
        ).encode()
        with self.assertRaisesRegex(MT5HistoryError, "overlap or are off"):
            self._load(raw)

    def test_long_gap_is_reported_not_silently_removed_or_filled(self) -> None:
        raw = (
            "date,time,open,high,low,close\n"
            "2024.01.05,23:55,1,2,0.5,1.5\n"
            "2024.01.08,00:00,1.5,2,1,1.8\n"
        ).encode()
        result = self._load(raw, evaluation_time=datetime(2024, 1, 8, 2, 0, tzinfo=UTC))
        self.assertEqual(result.ingestion.gap_count, 1)
        self.assertGreater(result.ingestion.gap_durations_seconds[0], 0)
        self.assertEqual(len(result.bars), 2)

    def test_invalid_ohlc_is_rejected_before_snapshot(self) -> None:
        raw = (
            "date,time,open,high,low,close\n"
            "2024.01.02,10:00,10,9,8,9.5\n"
        ).encode()
        with self.assertRaisesRegex(MT5HistoryError, "invalid OHLC"):
            self._load(raw)

    def test_negative_spread_or_volume_is_rejected(self) -> None:
        raw = (
            "date,time,open,high,low,close,spread\n"
            "2024.01.02,10:00,1,2,0.5,1.5,-1\n"
        ).encode()
        with self.assertRaisesRegex(MT5HistoryError, "spread cannot be negative"):
            self._load(raw)

    def test_raw_source_and_normalized_snapshot_hashes_are_both_preserved(self) -> None:
        result = self._load()
        self.assertEqual(len(result.ingestion.source_sha256), 64)
        self.assertEqual(len(result.ingestion.normalized_sha256), 64)
        self.assertEqual(result.ingestion.normalized_sha256, result.snapshot.sha256)
        self.assertEqual(result.ingestion.source_size_bytes, len(_tab_export()))

    def test_provisional_final_bar_remains_provisional_and_not_research_safe(self) -> None:
        result = self._load(evaluation_time=datetime(2024, 1, 2, 8, 12, tzinfo=UTC))
        self.assertFalse(result.snapshot.closed_only)
        self.assertEqual(result.validation.provisional_bars, 1)


if __name__ == "__main__":
    unittest.main()
