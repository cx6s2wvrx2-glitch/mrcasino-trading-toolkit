from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from xauusd_v2.mtf_aggregation import parse_timeframe_codes
from xauusd_v2.mtf_native_validation_cli import (
    NativeMTFValidationError,
    _bars_within_source_horizon,
    _load_candidate_index,
    _parse_native_arg,
)


class NativeMTFValidationCLITests(unittest.TestCase):
    def test_parse_native_arg(self) -> None:
        code, path = _parse_native_arg("H4=/tmp/native_h4.csv")
        self.assertEqual(code, "H4")
        self.assertEqual(path, Path("/tmp/native_h4.csv"))

    def test_parse_native_arg_blocks_11h(self) -> None:
        with self.assertRaises(Exception):
            _parse_native_arg("H11=/tmp/native_h11.csv")

    def test_candidate_index_loads_exact_decimals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "H4.candidate.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(("timestamp_utc", "open", "high", "low", "close"))
                writer.writerow(("2026-01-05T10:00:00Z", "100.10", "101.25", "99.80", "100.50"))
            index = _load_candidate_index(path)
            item = index["2026-01-05T10:00:00Z"]
            self.assertEqual(str(item.open_value), "100.10")
            self.assertEqual(str(item.high_value), "101.25")

    def test_candidate_index_rejects_duplicate_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "H1.candidate.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(("timestamp_utc", "open", "high", "low", "close"))
                row = ("2026-01-05T10:00:00Z", "100", "101", "99", "100")
                writer.writerow(row)
                writer.writerow(row)
            with self.assertRaises(NativeMTFValidationError):
                _load_candidate_index(path)

    def test_native_bars_after_frozen_m1_horizon_are_ignored(self) -> None:
        spec = parse_timeframe_codes("H1")[0]
        start = datetime(2026, 9, 3, 7, 0, tzinfo=UTC)
        bars = tuple(SimpleNamespace(timestamp=start + timedelta(hours=i)) for i in range(5))
        comparable, ignored = _bars_within_source_horizon(
            bars=bars,
            spec=spec,
            source_coverage_end=datetime(2026, 9, 3, 9, 52, tzinfo=UTC),
        )
        self.assertEqual([bar.timestamp for bar in comparable], [start, start + timedelta(hours=1)])
        self.assertEqual(ignored, 3)


if __name__ == "__main__":
    unittest.main()
