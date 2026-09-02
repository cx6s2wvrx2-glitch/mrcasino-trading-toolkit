from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import load_ground_truth


class GroundTruthRound05Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = load_ground_truth(Path(__file__).with_name("ground_truth_round_05.json"))

    def test_round_05_contains_five_negative_or_edge_cases(self) -> None:
        self.assertEqual(len(self.dataset.vectors), 5)
        classes = {v.expected_class for v in self.dataset.vectors}
        self.assertEqual(classes, {"invalid", "edge_case"})

    def test_round_05_is_fail_closed_for_promotion(self) -> None:
        self.assertFalse(self.dataset.promotion_allowed)
        self.assertEqual(self.dataset.status, "candidate_not_verified")

    def test_round_05_uses_only_approved_sources(self) -> None:
        allowed = {
            "f88aa3b8-2900-4829-a565-3d12580d591e",
            "c574ae7f-7928-4ca7-9df8-5fea1c125fd7",
            "8a73b7d8-923c-4222-bc95-f5597a90edde",
        }
        for vector in self.dataset.vectors:
            source_id = vector.source_locator.split(":", 1)[1].split("#", 1)[0]
            self.assertIn(source_id, allowed)

    def test_hcs_not_established_case_is_scoped_to_establishment(self) -> None:
        case = next(v for v in self.dataset.vectors if v.id == "GT-R05-001")
        self.assertEqual(case.expected_class, "invalid")
        self.assertIn("establishment", case.forbidden_inference)

    def test_zone_first_reaction_case_points_to_real_pdf_page_three(self) -> None:
        case = next(v for v in self.dataset.vectors if v.id == "GT-R05-002")
        self.assertEqual(
            case.source_locator,
            "v2_sources:c574ae7f-7928-4ca7-9df8-5fea1c125fd7#page:3#text:potential-zone-before-first-reaction",
        )

    def test_doji_outside_last_wick_is_preserved_as_edge_case(self) -> None:
        case = next(v for v in self.dataset.vectors if v.id == "GT-R05-004")
        self.assertEqual(case.expected_class, "edge_case")
        self.assertIn("Attempted FU", case.forbidden_inference)

    def test_hcs_zone_reaction_alone_is_not_complete_setup(self) -> None:
        case = next(v for v in self.dataset.vectors if v.id == "GT-R05-005")
        self.assertEqual(case.expected_class, "invalid")
        self.assertIn("alone", case.forbidden_inference)


if __name__ == "__main__":
    unittest.main()
