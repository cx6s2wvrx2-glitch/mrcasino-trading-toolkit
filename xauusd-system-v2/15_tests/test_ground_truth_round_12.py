from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).parent / "ground_truth_round_12.json")
        cls.by_id = {v.id: v for v in cls.dataset.vectors}

    def test_round_12_contains_24_primary_may_2023_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 24)
        self.assertEqual(set(self.by_id), {f"GT-R12-{i:03d}" for i in range(1, 25)})

    def test_every_may_chart_has_one_unique_dominant_case(self) -> None:
        locators = [v.source_locator for v in self.dataset.vectors]
        self.assertEqual(len(locators), len(set(locators)))
        self.assertTrue(all("#sequence:2023-05-" in x for x in locators))

    def test_round_12_is_fail_closed_for_promotion(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_unclosed_htf_confirmation_is_explicit_negative_case(self) -> None:
        item = self.by_id["GT-R12-021"]
        self.assertEqual(item.expected_class, "invalid")
        self.assertIn("not_established", item.expected_label)

    def test_weaker_2w_signal_cannot_override_monthly_strength(self) -> None:
        item = self.by_id["GT-R12-016"]
        self.assertEqual(item.expected_class, "invalid")
        self.assertIn("insufficient", item.expected_label)

    def test_broker_mismatch_liquidity_case_is_not_promoted(self) -> None:
        item = self.by_id["GT-R12-002"]
        self.assertEqual(item.expected_class, "invalid")
        self.assertIn("broker", item.expected_label)


if __name__ == "__main__":
    unittest.main()
