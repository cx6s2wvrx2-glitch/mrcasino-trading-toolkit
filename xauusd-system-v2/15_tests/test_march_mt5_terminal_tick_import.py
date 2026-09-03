from __future__ import annotations

import csv
import io
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.march_mt5_terminal_tick_import import (
    MarchMT5TerminalTickImportError,
    build_march_mt5_terminal_tick_import_report,
    persist_march_mt5_terminal_tick_import,
)


HEADER = (
    "schema_version",
    "record_type",
    "window_id",
    "broker_symbol",
    "start_msc",
    "end_msc_inclusive",
    "copy_result",
    "last_error",
    "source_index",
    "time_msc",
    "bid",
    "ask",
    "last",
    "volume",
    "flags",
    "volume_real",
)
SCHEMA = "xauusd_v2_mt5_terminal_tick_export_v1"
W1 = "buy_1975_hcs_candidate_2023_03_30_1231"
W2 = "sell_1986_hcs_control_2023_03_31_1236"
W1_START = 1680179460000
W1_END = 1680179519999
W2_START = 1680266160000
W2_END = 1680266219999


def _csv_bytes(rows: list[list[object]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(HEADER)
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def _status(window: str, start: int, end: int, copied: int, error: int = 0, symbol: str = "XAUUSD!"):
    return [SCHEMA, "status", window, symbol, start, end, copied, error, "", "", "", "", "", "", "", ""]


def _tick(window: str, start: int, end: int, index: int, time_msc: int, bid: str, ask: str, symbol: str = "XAUUSD!"):
    return [
        SCHEMA,
        "tick",
        window,
        symbol,
        start,
        end,
        "",
        "",
        index,
        time_msc,
        bid,
        ask,
        "0.00",
        0,
        6,
        "0.00000000",
    ]


def _build(raw: bytes):
    return build_march_mt5_terminal_tick_import_report(
        raw,
        broker_name="Exclusive Markets",
        broker_symbol="XAUUSD!",
        normalized_sha256="f" * 64,
        snapshot_id="sha256:" + "f" * 64,
    )


class MarchMT5TerminalTickImportTests(unittest.TestCase):
    def test_two_available_windows_are_imported_without_certification(self):
        raw = _csv_bytes(
            [
                _status(W1, W1_START, W1_END, 2),
                _tick(W1, W1_START, W1_END, 0, W1_START + 100, "1974.20", "1974.40"),
                _tick(W1, W1_START, W1_END, 1, W1_START + 100, "1974.21", "1974.41"),
                _status(W2, W2_START, W2_END, 1),
                _tick(W2, W2_START, W2_END, 0, W2_END, "1986.10", "1986.30"),
            ]
        )
        report = _build(raw)
        self.assertEqual(report["status"], "MARCH_MT5_TERMINAL_TICKS_IMPORTED_NOT_CERTIFIED")
        self.assertEqual(report["available_window_count"], 2)
        self.assertTrue(report["tick_path_evidence_available"])
        first = report["tick_windows"][0]
        self.assertEqual(first["tick_count"], 2)
        self.assertEqual(first["first_tick_utc"], "2023-03-30T12:31:00.100Z")
        self.assertEqual(first["last_tick_utc"], "2023-03-30T12:31:00.100Z")
        self.assertFalse(report["marked_liquidity_reference_certified"])
        self.assertFalse(report["fu_criteria_certified"])
        self.assertFalse(report["semantic_stage_certification"])
        self.assertFalse(report["performance_claim_allowed"])
        self.assertFalse(report["promotion_allowed"])
        self.assertFalse(report["live_execution_authorized"])

    def test_zero_tick_history_is_preserved_as_unavailable(self):
        raw = _csv_bytes(
            [
                _status(W1, W1_START, W1_END, 0, 0),
                _status(W2, W2_START, W2_END, 0, 0),
            ]
        )
        report = _build(raw)
        self.assertEqual(
            report["status"],
            "MARCH_MT5_TERMINAL_TICK_IMPORT_PARTIAL_OR_UNAVAILABLE_NOT_CERTIFIED",
        )
        self.assertEqual(report["available_window_count"], 0)
        self.assertFalse(report["tick_path_evidence_available"])
        self.assertEqual(
            [item["status"] for item in report["tick_windows"]],
            ["MT5_TERMINAL_TICKS_UNAVAILABLE_FOR_RANGE"] * 2,
        )

    def test_failed_terminal_request_is_not_confused_with_empty_history(self):
        raw = _csv_bytes(
            [
                _status(W1, W1_START, W1_END, -1, 4403),
                _status(W2, W2_START, W2_END, 0, 0),
            ]
        )
        report = _build(raw)
        self.assertEqual(report["tick_windows"][0]["status"], "MT5_TERMINAL_TICK_RANGE_REQUEST_FAILED")
        self.assertEqual(report["tick_windows"][0]["mt5_last_error"], 4403)

    def test_wrong_broker_symbol_is_rejected(self):
        raw = _csv_bytes(
            [
                _status(W1, W1_START, W1_END, 0, symbol="XAUUSD"),
                _status(W2, W2_START, W2_END, 0),
            ]
        )
        with self.assertRaises(MarchMT5TerminalTickImportError):
            _build(raw)

    def test_modified_window_bounds_are_rejected(self):
        raw = _csv_bytes(
            [
                _status(W1, W1_START, W1_END + 1, 0),
                _status(W2, W2_START, W2_END, 0),
            ]
        )
        with self.assertRaises(MarchMT5TerminalTickImportError):
            _build(raw)

    def test_out_of_range_tick_is_rejected(self):
        raw = _csv_bytes(
            [
                _status(W1, W1_START, W1_END, 1),
                _tick(W1, W1_START, W1_END, 0, W1_END + 1, "1974.20", "1974.40"),
                _status(W2, W2_START, W2_END, 0),
            ]
        )
        with self.assertRaises(MarchMT5TerminalTickImportError):
            _build(raw)

    def test_copy_result_must_match_tick_row_count(self):
        raw = _csv_bytes(
            [
                _status(W1, W1_START, W1_END, 2),
                _tick(W1, W1_START, W1_END, 0, W1_START, "1974.20", "1974.40"),
                _status(W2, W2_START, W2_END, 0),
            ]
        )
        with self.assertRaises(MarchMT5TerminalTickImportError):
            _build(raw)

    def test_persistence_is_content_addressed_and_repeatable(self):
        raw = _csv_bytes(
            [
                _status(W1, W1_START, W1_END, 1),
                _tick(W1, W1_START, W1_END, 0, W1_START, "1974.20", "1974.40"),
                _status(W2, W2_START, W2_END, 0),
            ]
        )
        report = _build(raw)
        with tempfile.TemporaryDirectory() as tmp:
            first = persist_march_mt5_terminal_tick_import(report, raw_export_bytes=raw, store_root=Path(tmp))
            second = persist_march_mt5_terminal_tick_import(report, raw_export_bytes=raw, store_root=Path(tmp))
            self.assertEqual(first["report_sha256"], second["report_sha256"])
            self.assertTrue(Path(first["raw_export_path"]).is_file())
            self.assertTrue(Path(first["tick_windows"][0]["ticks_path"]).is_file())
            self.assertTrue(Path(first["report_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
