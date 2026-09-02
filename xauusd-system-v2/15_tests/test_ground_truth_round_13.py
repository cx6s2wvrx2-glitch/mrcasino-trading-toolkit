from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).parent / "ground_truth_round_13.json")
        cls.by_id = {v.id: v for v in cls.dataset.vectors}

    def test_round_13_contains_29_primary_june_2023_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 29)
        self.assertEqual(set(self.by_id), {f"GT-R13-{i:03d}" for i in range(1, 30)})

    def test_every_june_chart_has_one_unique_case(self) -> None:
        locators = [v.source_locator for v in self.dataset.vectors]
        self.assertEqual(len(locators), len(set(locators)))
        self.assertTrue(all("#sequence:2023-06-" in x for x in locators))

    def test_round_13_is_fail_closed(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_reaction_is_not_silently_promoted_to_confirmation(self) -> None:
        self.assertEqual(self.by_id["GT-R13-014"].expected_class, "edge_case")
        self.assertIn("not_automatically_full_confirmation", self.by_id["GT-R13-014"].expected_label)

    def test_30m_plus_closure_case_is_negative(self) -> None:
        self.assertEqual(self.by_id["GT-R13-022"].expected_class, "invalid")
        self.assertIn("30m_plus", self.by_id["GT-R13-022"].expected_label)

    def test_historic_pip_values_are_not_expected_return(self) -> None:
        self.assertIn("expected return", self.by_id["GT-R13-026"].forbidden_inference)
        self.assertIn("70 pips", self.by_id["GT-R13-023"].forbidden_inference)


if __name__ == "__main__":
    unittest.main()
