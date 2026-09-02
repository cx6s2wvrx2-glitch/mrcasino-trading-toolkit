from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).parent / "ground_truth_round_11.json")

    def test_round_11_contains_thirty_primary_2022_xauusd_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 30)
        self.assertEqual({v.id for v in self.dataset.vectors}, {f"GT-R11-{i:03d}" for i in range(1, 31)})

    def test_round_11_uses_only_approved_primary_topdown_source(self) -> None:
        prefix = "v2_sources:b271d0b8-a86b-4d65-a4ae-b7e49d5803a6#sequence:2022-"
        self.assertTrue(all(v.source_locator.startswith(prefix) for v in self.dataset.vectors))

    def test_round_11_is_fail_closed_for_promotion(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_every_2022_chart_has_exactly_one_dominant_case(self) -> None:
        locators = [v.source_locator for v in self.dataset.vectors]
        self.assertEqual(len(locators), len(set(locators)))
        self.assertEqual(len(locators), 30)

    def test_round_11_preserves_negative_examples(self) -> None:
        invalids = [v for v in self.dataset.vectors if v.expected_class == "invalid"]
        self.assertGreaterEqual(len(invalids), 3)
        labels = {v.expected_label for v in invalids}
        self.assertIn("topdown_chart_should_keep_only_most_relevant_zones_to_avoid_confusion", labels)
        self.assertIn("absence_of_obvious_sellside_liquidity_can_keep_buys_prevalent_and_minor_att_fu_is_not_enough_to_target", labels)

    def test_broker_specific_imbalance_case_stays_broker_specific(self) -> None:
        by_id = {v.id: v for v in self.dataset.vectors}
        self.assertIn("broker", by_id["GT-R11-030"].expected_label)
        self.assertIn("broker-specific OHLC", by_id["GT-R11-030"].forbidden_inference)


if __name__ == "__main__":
    unittest.main()
