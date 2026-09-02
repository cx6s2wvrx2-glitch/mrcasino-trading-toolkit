from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).with_name("ground_truth_round_04.json"))

    def test_round_04_contains_six_primary_explicit_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 6)
        self.assertEqual({v.expected_class for v in self.dataset.vectors}, {"valid"})

    def test_round_04_is_fail_closed_for_promotion(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_round_04_uses_only_approved_fu_retest_and_zone_sources(self) -> None:
        allowed = {
            "bdbc80ef-3ad9-4bbb-b711-3883ae26b824",
            "c574ae7f-7928-4ca7-9df8-5fea1c125fd7",
        }
        for vector in self.dataset.vectors:
            source_id = vector.source_locator.split(":", 1)[1].split("#", 1)[0]
            self.assertIn(source_id, allowed)

    def test_hcs_strength_case_remains_qualitative(self) -> None:
        case = next(v for v in self.dataset.vectors if v.id == "GT-R04-004")
        self.assertIn("numeric strength score", case.forbidden_inference)

    def test_fu_retest_case_does_not_claim_r54_anchor(self) -> None:
        case = next(v for v in self.dataset.vectors if v.id == "GT-R04-001")
        self.assertIn("R-54 fib anchor", case.forbidden_inference)

    def test_round_04_locators_use_real_physical_pdf_pages(self) -> None:
        expected_pages = {
            "GT-R04-001": 3,
            "GT-R04-002": 3,
            "GT-R04-003": 4,
            "GT-R04-004": 5,
            "GT-R04-005": 4,
            "GT-R04-006": 6,
        }
        for vector in self.dataset.vectors:
            marker = vector.source_locator.split("#page:", 1)[1].split("#", 1)[0]
            self.assertEqual(int(marker), expected_pages[vector.id])


if __name__ == "__main__":
    unittest.main()
