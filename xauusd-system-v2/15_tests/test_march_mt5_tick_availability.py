from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from xauusd_v2.march_mt5_tick_availability import (
    MarchMT5TickAvailabilityError,
    _normalize_tick_rows,
    acquire_march_mt5_tick_availability,
    persist_march_mt5_tick_availability,
)


class _FakeProvider:
    COPY_TICKS_ALL = 7

    def __init__(self, *, rows_by_start: dict[datetime, list[dict[str, object]]], initialize_ok: bool = True):
        self.rows_by_start = rows_by_start
        self.initialize_ok = initialize_ok
        self.shutdown_called = False

    def initialize(self) -> bool:
        return self.initialize_ok

    def shutdown(self):
        self.shutdown_called = True
        return True

    def last_error(self):
        return (0, "Success")

    def symbol_info(self, symbol: str):
        return SimpleNamespace(name=symbol)

    def terminal_info(self):
        return SimpleNamespace(name="MetaTrader 5", company="Exclusive Markets")

    def account_info(self):
        return SimpleNamespace(server="ExclusiveMarkets-Demo")

    def copy_ticks_range(self, symbol: str, date_from: datetime, date_to: datetime, flags: int):
        return self.rows_by_start.get(date_from, [])


class MarchMT5TickAvailabilityTests(unittest.TestCase):
    def test_normalization_is_half_open_and_preserves_equal_millisecond_order(self):
        start = datetime(2023, 3, 30, 12, 31, tzinfo=UTC)
        end = datetime(2023, 3, 30, 12, 32, tzinfo=UTC)
        start_ms = int(start.timestamp() * 1000)
        end_ms = int(end.timestamp() * 1000)
        fields = ("time_msc", "bid", "ask", "last", "flags")
        rows = [
            {"time_msc": start_ms - 1, "bid": 1.0, "ask": 1.1, "last": 0.0, "flags": 1},
            {"time_msc": start_ms, "bid": 2.0, "ask": 2.1, "last": 0.0, "flags": 2},
            {"time_msc": start_ms, "bid": 3.0, "ask": 3.1, "last": 0.0, "flags": 3},
            {"time_msc": end_ms - 1, "bid": 4.0, "ask": 4.1, "last": 0.0, "flags": 4},
            {"time_msc": end_ms, "bid": 5.0, "ask": 5.1, "last": 0.0, "flags": 5},
        ]
        normalized = _normalize_tick_rows(rows, field_names=fields, start=start, end=end)
        self.assertEqual([item["bid"] for item in normalized], [2.0, 3.0, 4.0])
        self.assertEqual([item["sequence"] for item in normalized], [0, 1, 2])
        self.assertEqual([item["source_index"] for item in normalized], [1, 2, 3])

    def test_time_msc_is_required(self):
        start = datetime(2023, 3, 30, 12, 31, tzinfo=UTC)
        with self.assertRaises(MarchMT5TickAvailabilityError):
            _normalize_tick_rows(
                [{"time": 1, "bid": 1.0, "ask": 1.1, "last": 0.0, "flags": 1}],
                field_names=("time", "bid", "ask", "last", "flags"),
                start=start,
                end=datetime(2023, 3, 30, 12, 32, tzinfo=UTC),
            )

    @patch("xauusd_v2.march_mt5_tick_availability.load_verified_persisted_mt5_snapshot")
    def test_available_ticks_do_not_certify_fu_or_hcs(self, load_verified):
        load_verified.return_value = SimpleNamespace(
            normalized_sha256="f" * 64,
            snapshot=SimpleNamespace(
                timeframe_seconds=60,
                source_name="Exclusive Markets",
                source_symbol="XAUUSD!",
                snapshot_id="sha256:" + "f" * 64,
            ),
        )
        first = datetime(2023, 3, 30, 12, 31, tzinfo=UTC)
        second = datetime(2023, 3, 31, 12, 36, tzinfo=UTC)
        provider = _FakeProvider(
            rows_by_start={
                first: [
                    {"time_msc": int(first.timestamp() * 1000) + 100, "bid": 1974.2, "ask": 1974.4, "last": 0.0, "flags": 2}
                ],
                second: [
                    {"time_msc": int(second.timestamp() * 1000) + 200, "bid": 1986.1, "ask": 1986.3, "last": 0.0, "flags": 2}
                ],
            }
        )
        report = acquire_march_mt5_tick_availability("ignored.json", provider=provider)
        self.assertEqual(report["status"], "MARCH_MT5_TICKS_AVAILABLE_NOT_CERTIFIED")
        self.assertEqual(report["available_window_count"], 2)
        self.assertTrue(report["tick_path_evidence_available"])
        self.assertFalse(report["marked_liquidity_reference_certified"])
        self.assertFalse(report["fu_criteria_certified"])
        self.assertFalse(report["semantic_stage_certification"])
        self.assertFalse(report["performance_claim_allowed"])
        self.assertFalse(report["promotion_allowed"])
        self.assertFalse(report["live_execution_authorized"])
        self.assertTrue(provider.shutdown_called)

    def test_persistence_is_content_addressed_and_repeatable(self):
        payload = b'{"sequence":0,"time_msc":1}\n'
        import hashlib

        digest = hashlib.sha256(payload).hexdigest()
        report = {
            "status": "MARCH_MT5_TICKS_AVAILABLE_NOT_CERTIFIED",
            "tick_windows": [
                {
                    "window_id": "x",
                    "status": "MT5_TICKS_AVAILABLE",
                    "tick_count": 1,
                    "ticks_sha256": digest,
                    "ticks_bytes": payload,
                }
            ],
            "marked_liquidity_reference_certified": False,
            "fu_criteria_certified": False,
            "semantic_stage_certification": False,
            "performance_claim_allowed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
        }
        with tempfile.TemporaryDirectory() as tmp:
            first = persist_march_mt5_tick_availability(report, store_root=Path(tmp))
            second = persist_march_mt5_tick_availability(report, store_root=Path(tmp))
            self.assertEqual(first["report_sha256"], second["report_sha256"])
            self.assertTrue(Path(first["tick_windows"][0]["ticks_path"]).is_file())
            self.assertTrue(Path(first["report_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
