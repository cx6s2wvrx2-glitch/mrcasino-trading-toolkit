from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from xauusd_v2.replay_alignment import load_source_price_anchors, load_verified_replay_slice
from xauusd_v2.replay_anchor_path import ReplayAnchorPathError, measure_anchor_path, select_anchor


class ReplayAnchorPathTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, Path]:
        csv_path = root / "m1.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(("timestamp", "open", "high", "low", "close"))
            writer.writerow(("2023-11-01T00:00:00Z", "1976.0", "1976.2", "1975.5", "1975.8"))
            writer.writerow(("2023-11-01T00:01:00Z", "1975.8", "1975.9", "1974.9", "1975.1"))
            writer.writerow(("2023-11-01T00:02:00Z", "1975.1", "1975.3", "1974.8", "1974.9"))
            writer.writerow(("2023-11-01T00:03:00Z", "1974.9", "1974.95", "1974.5", "1974.7"))
            writer.writerow(("2023-11-01T00:04:00Z", "1974.7", "1975.1", "1974.6", "1975.0"))
            writer.writerow(("2023-11-01T00:05:00Z", "1975.0", "1975.4", "1974.95", "1975.3"))
        sha = hashlib.sha256(csv_path.read_bytes()).hexdigest()
        manifest = {
            "schema_version": "historical_replay_slice_v1",
            "status": "REPLAY_MARKET_SLICE_BUILT",
            "episode_id": "casino-2023-11-01",
            "source_locator": "top down analysis (1).zip#sequence:2023-11-01",
            "bar_count": 6,
            "low_min": "1974.5",
            "high_max": "1976.2",
            "slice_sha256": sha,
            "csv_path": str(csv_path),
            "promotion_allowed": False,
            "live_execution_authorized": False,
        }
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        anchors = {
            "schema_version": "source_price_anchor_set_v1",
            "episode_id": "casino-2023-11-01",
            "source_locator": "top down analysis (1).zip#sequence:2023-11-01",
            "promotion_allowed": False,
            "live_execution_authorized": False,
            "anchors": [
                {
                    "anchor_id": "a1",
                    "price": "1975.0",
                    "evidence_class": "PRIMARY_SOURCE_LABEL",
                    "source_image": "image.jpg",
                    "source_claim": "claim",
                    "source_note": "note",
                    "role": "context_condition_level"
                }
            ]
        }
        anchor_path = root / "anchors.json"
        anchor_path.write_text(json.dumps(anchors), encoding="utf-8")
        return manifest_path, anchor_path

    def test_measures_two_touch_clusters_without_interpretation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, anchor_path = self._fixture(Path(tmp))
            replay = load_verified_replay_slice(manifest_path)
            _, _, anchors = load_source_price_anchors(anchor_path)
            anchor = select_anchor(anchors, "a1")
            facts = measure_anchor_path(
                replay,
                anchor,
                start_utc=datetime(2023, 11, 1, 0, 0, tzinfo=UTC),
                end_utc=datetime(2023, 11, 1, 0, 6, tzinfo=UTC),
            )
            self.assertEqual(facts.bar_count, 6)
            self.assertEqual(facts.touch_bar_count, 4)
            self.assertEqual(facts.touch_cluster_count, 2)
            self.assertEqual(facts.touch_clusters[0].start_timestamp_utc, "2023-11-01T00:01:00Z")
            self.assertEqual(facts.touch_clusters[0].end_timestamp_utc, "2023-11-01T00:02:00Z")
            self.assertEqual(facts.touch_clusters[0].previous_bar_close, "1975.8")
            self.assertEqual(facts.touch_clusters[0].next_bar_close, "1974.7")
            self.assertEqual(facts.touch_clusters[1].start_timestamp_utc, "2023-11-01T00:04:00Z")
            self.assertEqual(facts.touch_clusters[1].end_timestamp_utc, "2023-11-01T00:05:00Z")
            self.assertEqual(facts.strict_low_below_bar_count, 5)
            self.assertEqual(facts.close_below_bar_count, 2)
            self.assertEqual(facts.first_close_below_timestamp_utc, "2023-11-01T00:02:00Z")

    def test_unknown_anchor_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _, anchor_path = self._fixture(Path(tmp))
            _, _, anchors = load_source_price_anchors(anchor_path)
            with self.assertRaisesRegex(ReplayAnchorPathError, "exactly one"):
                select_anchor(anchors, "missing")

    def test_empty_window_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, anchor_path = self._fixture(Path(tmp))
            replay = load_verified_replay_slice(manifest_path)
            _, _, anchors = load_source_price_anchors(anchor_path)
            with self.assertRaisesRegex(ReplayAnchorPathError, "contains no replay bars"):
                measure_anchor_path(
                    replay,
                    anchors[0],
                    start_utc=datetime(2023, 11, 2, 0, 0, tzinfo=UTC),
                    end_utc=datetime(2023, 11, 2, 1, 0, tzinfo=UTC),
                )


if __name__ == "__main__":
    unittest.main()
