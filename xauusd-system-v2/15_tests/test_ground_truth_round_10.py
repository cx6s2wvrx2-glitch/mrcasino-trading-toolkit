from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).parent / "ground_truth_round_10.json")

    def test_round_10_contains_twenty_primary_2021_xauusd_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 20)
        self.assertEqual({v.id for v in self.dataset.vectors}, {f"GT-R10-{i:03d}" for i in range(1, 21)})

    def test_round_10_uses_only_approved_primary_topdown_source(self) -> None:
        prefix = "v2_sources:b271d0b8-a86b-4d65-a4ae-b7e49d5803a6#sequence:2021-"
        self.assertTrue(all(v.source_locator.startswith(prefix) for v in self.dataset.vectors))

    def test_round_10_excludes_non_xauusd_2021_11_30_sequence(self) -> None:
        self.assertTrue(all("sequence:2021-11-30" not in v.source_locator for v in self.dataset.vectors))

    def test_round_10_is_fail_closed_for_promotion(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_round_10_contains_direct_negative_examples(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertEqual(by_id["GT-R10-005"].expected_class, "invalid")
        self.assertEqual(by_id["GT-R10-013"].expected_class, "invalid")

    def test_nearby_liquidity_veto_is_preserved(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertIn("nearby_liquidity_can_veto", by_id["GT-R10-013"].expected_label)

    def test_broker_feed_difference_is_first_class_ground_truth_context(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertEqual(by_id["GT-R10-017"].expected_class, "valid")
        self.assertIn("broker_feed_difference", by_id["GT-R10-017"].expected_label)


if __name__ == "__main__":
    unittest.main()
