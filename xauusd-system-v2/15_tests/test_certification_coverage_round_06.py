from __future__ import annotations

import unittest

from xauusd_v2.certification_coverage import CoverageState
from xauusd_v2.certification_coverage_round_06 import round_06_coverage_by_id, round_06_coverage_counts


class CertificationCoverageRound06Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.coverage = round_06_coverage_by_id()

    def test_every_round_06_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), {f"GT-R06-{i:03d}" for i in range(1, 9)})

    def test_round_06_is_honestly_partial_except_unclosed_confirmation_case(self) -> None:
        counts = round_06_coverage_counts()
        self.assertEqual(counts[CoverageState.EXECUTABLE], 1)
        self.assertEqual(counts[CoverageState.PARTIAL], 7)
        self.assertEqual(counts[CoverageState.RAW_BLOCKED], 0)
        self.assertEqual(counts[CoverageState.CONTEXT_ONLY], 0)

    def test_all_partial_cases_name_their_blocker(self) -> None:
        for item in self.coverage.values():
            if item.state == CoverageState.PARTIAL:
                self.assertTrue(item.blocker)

    def test_unclosed_daily_case_maps_to_confirmed_only_gates(self) -> None:
        item = self.coverage["GT-R06-007"]
        self.assertEqual(item.state, CoverageState.EXECUTABLE)
        self.assertIn("tfs_semantic", item.components)
        self.assertIn("historical_reproducibility", item.components)

    def test_weaker_counter_hcs_is_not_falsely_claimed_executable(self) -> None:
        item = self.coverage["GT-R06-002"]
        self.assertEqual(item.state, CoverageState.PARTIAL)
        self.assertIn("cross-timeframe strength priority", item.blocker or "")


if __name__ == "__main__":
    unittest.main()
