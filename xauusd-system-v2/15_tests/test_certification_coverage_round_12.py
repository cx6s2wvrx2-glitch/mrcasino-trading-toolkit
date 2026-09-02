from __future__ import annotations

import unittest

from xauusd_v2.certification_coverage import CoverageState
from xauusd_v2.certification_coverage_round_12 import round_12_coverage_by_id, round_12_coverage_counts


class CertificationCoverageRound12Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.coverage = round_12_coverage_by_id()

    def test_every_round_12_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), {f"GT-R12-{i:03d}" for i in range(1, 25)})

    def test_round_12_is_honestly_partial(self) -> None:
        counts = round_12_coverage_counts()
        self.assertEqual(counts[CoverageState.EXECUTABLE], 0)
        self.assertEqual(counts[CoverageState.PARTIAL], 24)
        self.assertEqual(counts[CoverageState.RAW_BLOCKED], 0)
        self.assertEqual(counts[CoverageState.CONTEXT_ONLY], 0)

    def test_every_case_names_a_blocker(self) -> None:
        for item in self.coverage.values():
            self.assertTrue(item.blocker)

    def test_concentrated_manipulation_is_not_numericized(self) -> None:
        self.assertIn("no certified numeric detector", self.coverage["GT-R12-012"].blocker or "")

    def test_unclosed_htf_case_maps_to_reproducibility_gate(self) -> None:
        self.assertIn("historical_reproducibility", self.coverage["GT-R12-021"].components)

    def test_true_stop_cases_remain_raw_blocked_by_geometry(self) -> None:
        self.assertIn("exact TS geometry", self.coverage["GT-R12-024"].blocker or "")


if __name__ == "__main__":
    unittest.main()
