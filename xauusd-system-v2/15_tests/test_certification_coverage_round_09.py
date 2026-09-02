from __future__ import annotations

import unittest

from xauusd_v2.certification_coverage import CoverageState
from xauusd_v2.certification_coverage_round_09 import round_09_coverage_by_id, round_09_coverage_counts


class CertificationCoverageRound09Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.coverage = round_09_coverage_by_id()

    def test_every_round_09_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), {f"GT-R09-{i:03d}" for i in range(1, 5)})

    def test_round_09_is_honestly_partial(self) -> None:
        counts = round_09_coverage_counts()
        self.assertEqual(counts[CoverageState.EXECUTABLE], 0)
        self.assertEqual(counts[CoverageState.PARTIAL], 4)
        self.assertEqual(counts[CoverageState.RAW_BLOCKED], 0)
        self.assertEqual(counts[CoverageState.CONTEXT_ONLY], 0)

    def test_every_case_names_a_blocker(self) -> None:
        for item in self.coverage.values():
            self.assertEqual(item.state, CoverageState.PARTIAL)
            self.assertTrue(item.blocker)

    def test_zone_removal_case_does_not_invent_removal_rule(self) -> None:
        item = self.coverage["GT-R09-004"]
        self.assertIn("does not state the removal decision rule", item.blocker or "")


if __name__ == "__main__":
    unittest.main()
