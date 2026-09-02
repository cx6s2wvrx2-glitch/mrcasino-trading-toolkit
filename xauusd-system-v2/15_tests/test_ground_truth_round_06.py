from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound06Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).parent / "ground_truth_round_06.json")

    def test_round_06_contains_eight_primary_topdown_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 8)
        self.assertEqual({v.id for v in self.dataset.vectors}, {f"GT-R06-{i:03d}" for i in range(1, 9)})

    def test_round_06_uses_only_approved_primary_topdown_source(self) -> None:
        prefix = "v2_sources:b271d0b8-a86b-4d65-a4ae-b7e49d5803a6#sequence:2023-11-01#image:"
        self.assertTrue(all(v.source_locator.startswith(prefix) for v in self.dataset.vectors))

    def test_round_06_is_fail_closed_for_promotion(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_round_06_contains_valid_invalid_and_edge_cases(self) -> None:
        classes = {v.expected_class for v in self.dataset.vectors}
        self.assertEqual(classes, {"valid", "invalid", "edge_case"})

    def test_forming_or_unclosed_htf_evidence_is_not_promoted(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertEqual(by_id["GT-R06-003"].expected_class, "edge_case")
        self.assertEqual(by_id["GT-R06-007"].expected_class, "invalid")
        self.assertIn("forming", by_id["GT-R06-003"].expected_label)
        self.assertIn("unclosed", by_id["GT-R06-007"].expected_label)

    def test_counter_hcs_does_not_auto_reverse_prevalent_htf_bias(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertEqual(by_id["GT-R06-002"].expected_class, "invalid")
        self.assertIn("not_enough_to_negate", by_id["GT-R06-002"].expected_label)


if __name__ == "__main__":
    unittest.main()
