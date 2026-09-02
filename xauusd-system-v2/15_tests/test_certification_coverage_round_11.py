from __future__ import annotations

import unittest

from xauusd_v2.certification_coverage import CoverageState
from xauusd_v2.certification_coverage_round_11 import round_11_coverage_by_id, round_11_coverage_counts


class CertificationCoverageRound11Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.coverage = round_11_coverage_by_id()

    def test_every_round_11_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), {f"GT-R11-{i:03d}" for i in range(1, 31)})

    def test_round_11_is_honestly_partial(self) -> None:
        counts = round_11_coverage_counts()
        self.assertEqual(counts[CoverageState.EXECUTABLE], 0)
        self.assertEqual(counts[CoverageState.PARTIAL], 30)
        self.assertEqual(counts[CoverageState.RAW_BLOCKED], 0)
        self.assertEqual(counts[CoverageState.CONTEXT_ONLY], 0)

    def test_every_case_names_a_blocker(self) -> None:
        for item in self.coverage.values():
            self.assertEqual(item.state, CoverageState.PARTIAL)
            self.assertTrue(item.blocker)

    def test_fu_wick_retest_case_keeps_significance_unresolved(self) -> None:
        self.assertIn("significant liquidity", self.coverage["GT-R11-015"].blocker or "")

    def test_strong_3h_fu_does_not_create_numeric_threshold(self) -> None:
        self.assertIn("threshold", self.coverage["GT-R11-022"].blocker or "")

    def test_broker_specific_imbalance_case_requires_raw_data(self) -> None:
        self.assertIn("broker-specific", self.coverage["GT-R11-030"].blocker or "")


if __name__ == "__main__":
    unittest.main()
