from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


DATASET_PATH = Path(__file__).with_name("ground_truth_round_02.json")


class GroundTruthRound02Tests(unittest.TestCase):
    def test_round_02_is_mixed_and_fail_closed(self) -> None:
        dataset = load_ground_truth(DATASET_PATH)
        classes = {v.expected_class for v in dataset.vectors}
        self.assertGreaterEqual(len(dataset.vectors), 19)
        self.assertIn("valid", classes)
        self.assertIn("invalid", classes)
        self.assertIn("edge_case", classes)
        self.assertFalse(dataset.promotion_allowed)
        self.assertTrue(all(v.source_locator for v in dataset.vectors))


if __name__ == "__main__":
    unittest.main()
