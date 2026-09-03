from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.mtf_native_validation_cli import (
    NativeMTFValidationError,
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


if __name__ == "__main__":
    unittest.main()
