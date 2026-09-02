from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).with_name("ground_truth_round_03.json"))

    def test_round_03_contains_seven_primary_explicit_label_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 7)
        self.assertEqual({v.expected_class for v in self.dataset.vectors}, {"valid"})

    def test_round_03_is_fail_closed_for_promotion(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_round_03_uses_only_approved_batch_01_source_ids(self) -> None:
        allowed_source_ids = {
            "a338728f-1796-4665-b678-774ea9f9f031",
            "ec297fcb-5693-4aa6-857b-d27ae1dd1143",
            "2c5fc1ca-e581-4c28-83c3-2843e227af68",
            "47c7d97d-a873-43f9-b4fc-b0fabbd47ba2",
        }
        for vector in self.dataset.vectors:
            self.assertTrue(vector.source_locator.startswith("v2_sources:"))
            source_id = vector.source_locator.split(":", 1)[1].split("#", 1)[0]
            self.assertIn(source_id, allowed_source_ids)

    def test_hcs_examples_do_not_claim_component_strength_labels(self) -> None:
        hcs = [v for v in self.dataset.vectors if v.expected_label.startswith("hcs_visual_")]
        self.assertEqual(len(hcs), 2)
        for vector in hcs:
            self.assertIn("Do not label the individual circled HCS components", vector.forbidden_inference)

    def test_imbalance_examples_remain_separate_constructs(self) -> None:
        labels = {v.expected_label for v in self.dataset.vectors}
        self.assertIn("imbalanced_candle_visual_h1", labels)
        self.assertIn("classic_imbalance_visual_m5", labels)


if __name__ == "__main__":
    unittest.main()
