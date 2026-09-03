from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.replay_alignment import load_source_price_anchors


class NarratedMarch2023EpisodeTests(unittest.TestCase):
    def test_primary_narrated_anchor_set_is_machine_readable_and_non_promoting(self) -> None:
        fixture = (
            Path(__file__).resolve().parents[1]
            / "06_examples"
            / "PRIMARY_REPLAY_EPISODE_2023_03_30_31_ANCHORS.json"
        )
        episode_id, source_locator, anchors = load_source_price_anchors(fixture)
        self.assertEqual(episode_id, "casino-2023-03-30-31")
        self.assertIn("2023-03-30_to_2023-03-31", source_locator)
        self.assertEqual(len(anchors), 8)
        by_price = {str(anchor.price): anchor for anchor in anchors}
        self.assertEqual(by_price["1972.70"].role, "true_stop_level")
        self.assertEqual(by_price["1975.00"].role, "hcs_reentry_context")
        self.assertEqual(by_price["1984.19"].role, "major_target_context")
        self.assertEqual(by_price["1987.56"].role, "imbalance_fingerprint")


if __name__ == "__main__":
    unittest.main()
