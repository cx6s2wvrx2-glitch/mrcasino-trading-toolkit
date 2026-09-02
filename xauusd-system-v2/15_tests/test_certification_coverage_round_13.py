from __future__ import annotations

import unittest

from xauusd_v2.certification_coverage import CoverageState
from xauusd_v2.certification_coverage_round_13 import round_13_coverage_by_id, round_13_coverage_counts


class CertificationCoverageRound13Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.coverage = round_13_coverage_by_id()

    def test_every_round_13_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), {f"GT-R13-{i:03d}" for i in range(1, 30)})

    def test_round_13_is_honestly_partial(self) -> None:
        counts = round_13_coverage_counts()
        self.assertEqual(counts[CoverageState.PARTIAL], 29)
        self.assertEqual(counts[CoverageState.EXECUTABLE], 0)

    def test_every_case_names_a_blocker(self) -> None:
        self.assertTrue(all(x.blocker for x in self.coverage.values()))

    def test_one_more_reaction_is_not_fixed_lifecycle(self) -> None:
        self.assertIn("not a certified fixed", self.coverage["GT-R13-012"].blocker or "")

    def test_70_pips_is_not_management_threshold(self) -> None:
        self.assertIn("70-pip", self.coverage["GT-R13-023"].blocker or "")

    def test_150_pips_is_not_expected_return(self) -> None:
        self.assertIn("not expected return", self.coverage["GT-R13-026"].blocker or "")


if __name__ == "__main__":
    unittest.main()
