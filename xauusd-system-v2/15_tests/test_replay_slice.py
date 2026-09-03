from __future__ import annotations

import csv
import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from xauusd_v2.replay_slice import ReplaySliceError, build_replay_slice, parse_aware_timestamp


class ReplaySliceTests(unittest.TestCase):
    def _verified(self, root: Path):
        snapshot_path = root / "xauusd_ohlc.csv"
        with snapshot_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(("timestamp", "open", "high", "low", "close"))
            writer.writerow(("2023-11-01T00:00:00Z", "1980", "1981", "1979", "1980.5"))
            writer.writerow(("2023-11-01T00:01:00Z", "1980.5", "1982", "1980", "1981.5"))
            writer.writerow(("2023-11-01T00:03:00Z", "1981.5", "1984", "1978", "1983"))
            writer.writerow(("2023-11-01T00:04:00Z", "1983", "1985", "1982", "1984"))

        snapshot = SimpleNamespace(
            timeframe_seconds=60,
            closed_only=True,
            first_timestamp=datetime(2023, 11, 1, 0, 0, tzinfo=UTC),
            coverage_end=datetime(2023, 11, 1, 0, 5, tzinfo=UTC),
            snapshot_id="sha256:" + "a" * 64,
            bar_count=4,
            source_name="Exclusive Markets Ltd.",
            source_symbol="XAUUSD!",
            canonical_symbol="XAUUSD",
        )
        return SimpleNamespace(
            snapshot=snapshot,
            canonical_snapshot_path=snapshot_path,
            store_root=root,
            normalized_sha256="a" * 64,
            manifest_path=root / "ingestion.json",
        )

    def test_slice_is_end_exclusive_content_addressed_and_gap_preserving(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            verified = self._verified(root)
            result = build_replay_slice(
                verified,
                episode_id="2023-11-01-primary",
                source_locator="top down analysis (1).zip#sequence:2023-11-01",
                start_utc=datetime(2023, 11, 1, 0, 1, tzinfo=UTC),
                end_utc=datetime(2023, 11, 1, 0, 5, tzinfo=UTC),
            )
            self.assertEqual(result.bar_count, 3)
            self.assertEqual(result.first_timestamp_utc, datetime(2023, 11, 1, 0, 1, tzinfo=UTC))
            self.assertEqual(result.last_timestamp_utc, datetime(2023, 11, 1, 0, 4, tzinfo=UTC))
            self.assertEqual(result.gap_count, 1)
            self.assertEqual(result.max_gap_seconds, 60)
            self.assertEqual(str(result.low_min), "1978")
            self.assertEqual(str(result.high_max), "1985")
            self.assertEqual(len(result.slice_sha256), 64)
            self.assertTrue(result.csv_path.is_file())
            self.assertTrue(result.manifest_path.is_file())

            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "REPLAY_MARKET_SLICE_BUILT")
            self.assertFalse(manifest["strategy_truth_changed"])
            self.assertFalse(manifest["promotion_allowed"])
            self.assertFalse(manifest["live_execution_authorized"])

            second = build_replay_slice(
                verified,
                episode_id="2023-11-01-primary",
                source_locator="top down analysis (1).zip#sequence:2023-11-01",
                start_utc=datetime(2023, 11, 1, 0, 1, tzinfo=UTC),
                end_utc=datetime(2023, 11, 1, 0, 5, tzinfo=UTC),
            )
            self.assertEqual(second.slice_sha256, result.slice_sha256)
            self.assertEqual(second.csv_path, result.csv_path)

    def test_parse_requires_timezone(self) -> None:
        with self.assertRaisesRegex(ReplaySliceError, "timezone-aware"):
            parse_aware_timestamp("2023-11-01T00:00:00", field="start_utc")

    def test_invalid_episode_id_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            verified = self._verified(root)
            with self.assertRaisesRegex(ReplaySliceError, "episode_id"):
                build_replay_slice(
                    verified,
                    episode_id="../escape",
                    source_locator="source",
                    start_utc=datetime(2023, 11, 1, 0, 0, tzinfo=UTC),
                    end_utc=datetime(2023, 11, 1, 0, 5, tzinfo=UTC),
                )


if __name__ == "__main__":
    unittest.main()
