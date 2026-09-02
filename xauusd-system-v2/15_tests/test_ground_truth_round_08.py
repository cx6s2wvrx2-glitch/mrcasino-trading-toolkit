from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound08Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).parent / "ground_truth_round_08.json")

    def test_round_08_contains_ten_primary_topdown_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 10)
        self.assertEqual({v.id for v in self.dataset.vectors}, {f"GT-R08-{i:03d}" for i in range(1, 11)})

    def test_round_08_uses_only_approved_primary_topdown_source(self) -> None:
        prefix = "v2_sources:b271d0b8-a86b-4d65-a4ae-b7e49d5803a6#sequence:2023-11-20#image:"
        self.assertTrue(all(v.source_locator.startswith(prefix) for v in self.dataset.vectors))

    def test_round_08_is_fail_closed_for_promotion(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_round_08_preserves_valid_and_edge_cases_without_forcing_invalids(self) -> None:
        classes = {v.expected_class for v in self.dataset.vectors}
        self.assertEqual(classes, {"valid", "edge_case"})

    def test_overall_and_intraday_direction_are_kept_separate(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertEqual(by_id["GT-R08-002"].expected_class, "valid")
        self.assertIn("coexist", by_id["GT-R08-002"].expected_label)

    def test_forming_or_conditional_states_are_not_promoted(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertEqual(by_id["GT-R08-001"].expected_class, "edge_case")
        self.assertEqual(by_id["GT-R08-004"].expected_class, "edge_case")
        self.assertEqual(by_id["GT-R08-009"].expected_class, "edge_case")


if __name__ == "__main__":
    unittest.main()
