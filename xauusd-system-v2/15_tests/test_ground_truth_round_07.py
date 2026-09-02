from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound07Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).parent / "ground_truth_round_07.json")

    def test_round_07_contains_ten_primary_topdown_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 10)
        self.assertEqual({v.id for v in self.dataset.vectors}, {f"GT-R07-{i:03d}" for i in range(1, 11)})

    def test_round_07_uses_only_approved_primary_topdown_source(self) -> None:
        prefix = "v2_sources:b271d0b8-a86b-4d65-a4ae-b7e49d5803a6#sequence:2023-11-06#image:"
        self.assertTrue(all(v.source_locator.startswith(prefix) for v in self.dataset.vectors))

    def test_round_07_is_fail_closed_for_promotion(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_round_07_preserves_valid_invalid_and_edge_cases(self) -> None:
        classes = {v.expected_class for v in self.dataset.vectors}
        self.assertEqual(classes, {"valid", "invalid", "edge_case"})

    def test_weaker_2w_confirmation_case_is_invalid_for_full_confirmation(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertEqual(by_id["GT-R07-002"].expected_class, "invalid")
        self.assertIn("not_enough_for_confirmation", by_id["GT-R07-002"].expected_label)

    def test_ltf_relevance_is_not_promoted_to_htf_authority(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertEqual(by_id["GT-R07-010"].expected_class, "edge_case")
        self.assertIn("without_becoming_strong_htf_zone", by_id["GT-R07-010"].expected_label)


if __name__ == "__main__":
    unittest.main()
