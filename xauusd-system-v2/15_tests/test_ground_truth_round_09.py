from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound09Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).parent / "ground_truth_round_09.json")

    def test_round_09_contains_four_primary_topdown_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 4)
        self.assertEqual({v.id for v in self.dataset.vectors}, {f"GT-R09-{i:03d}" for i in range(1, 5)})

    def test_round_09_uses_only_approved_primary_topdown_source(self) -> None:
        prefix = "v2_sources:b271d0b8-a86b-4d65-a4ae-b7e49d5803a6#sequence:2023-11-08#image:"
        self.assertTrue(all(v.source_locator.startswith(prefix) for v in self.dataset.vectors))

    def test_round_09_is_fail_closed_for_promotion(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_dynamic_zone_adjustment_does_not_claim_algorithm(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertEqual(by_id["GT-R09-001"].expected_class, "valid")
        self.assertIn("universal automatic zone-adjustment algorithm", by_id["GT-R09-001"].forbidden_inference)

    def test_monthly_zone_removal_preserves_unknown_reason(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertEqual(by_id["GT-R09-004"].expected_class, "edge_case")
        self.assertIn("Do not infer why", by_id["GT-R09-004"].forbidden_inference)


if __name__ == "__main__":
    unittest.main()
