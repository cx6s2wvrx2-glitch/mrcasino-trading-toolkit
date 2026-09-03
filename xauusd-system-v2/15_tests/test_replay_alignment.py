from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.replay_alignment import (
    ReplayAlignmentError,
    load_source_price_anchors,
    load_verified_replay_slice,
    probe_replay_anchors,
)


class ReplayAlignmentTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, Path]:
        csv_path = root / "m1.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(("timestamp", "open", "high", "low", "close"))
            writer.writerow(("2023-11-01T00:00:00Z", "1974.80", "1975.10", "1974.70", "1975.00"))
            writer.writerow(("2023-11-01T00:01:00Z", "1975.00", "1975.30", "1974.95", "1975.20"))
            writer.writerow(("2023-11-01T00:02:00Z", "1975.20", "1975.50", "1975.15", "1975.40"))
        sha = hashlib.sha256(csv_path.read_bytes()).hexdigest()
        manifest = {
            "schema_version": "historical_replay_slice_v1",
            "status": "REPLAY_MARKET_SLICE_BUILT",
            "episode_id": "casino-2023-11-01",
            "source_locator": "top down analysis (1).zip#sequence:2023-11-01",
            "bar_count": 3,
            "low_min": "1974.70",
            "high_max": "1975.50",
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
                    "price": "1975.00",
                    "evidence_class": "PRIMARY_SOURCE_LABEL",
                    "source_image": "image.jpg",
                    "source_claim": "claim",
                    "source_note": "note",
                    "role": "context_condition_level"
                },
                {
                    "anchor_id": "a2",
                    "price": "1976.00",
                    "evidence_class": "PRIMARY_SOURCE_LABEL",
                    "source_image": "image2.jpg",
                    "source_claim": "claim2",
                    "source_note": "note2",
                    "role": "context_condition_level"
                }
            ]
        }
        anchor_path = root / "anchors.json"
        anchor_path.write_text(json.dumps(anchors), encoding="utf-8")
        return manifest_path, anchor_path

    def test_probe_detects_touch_and_closest_distance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, anchor_path = self._fixture(Path(tmp))
            replay = load_verified_replay_slice(manifest_path)
            episode_id, source_locator, anchors = load_source_price_anchors(anchor_path)
            self.assertEqual(episode_id, replay.episode_id)
            self.assertEqual(source_locator, replay.source_locator)
            results = probe_replay_anchors(replay, anchors)
            first, second = results
            self.assertTrue(first.touched)
            self.assertEqual(first.touch_bar_count, 2)
            self.assertEqual(first.first_touch_timestamp_utc, "2023-11-01T00:00:00Z")
            self.assertEqual(first.last_touch_timestamp_utc, "2023-11-01T00:01:00Z")
            self.assertEqual(first.closest_distance, "0")
            self.assertFalse(second.touched)
            self.assertFalse(second.within_slice_price_range)
            self.assertEqual(second.closest_distance, "0.50")
            self.assertEqual(second.closest_timestamp_utc, "2023-11-01T00:02:00Z")

    def test_tampered_replay_csv_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, _ = self._fixture(Path(tmp))
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            csv_path = Path(payload["csv_path"])
            csv_path.write_text(csv_path.read_text(encoding="utf-8") + "tamper\n", encoding="utf-8")
            with self.assertRaisesRegex(ReplayAlignmentError, "SHA-256 mismatch"):
                load_verified_replay_slice(manifest_path)

    def test_anchor_episode_must_be_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _, anchor_path = self._fixture(Path(tmp))
            payload = json.loads(anchor_path.read_text(encoding="utf-8"))
            payload["anchors"][0]["source_note"] = ""
            anchor_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ReplayAlignmentError, "incomplete provenance"):
                load_source_price_anchors(anchor_path)


if __name__ == "__main__":
    unittest.main()
