from __future__ import annotations

import unittest

from xauusd_v2.certification_coverage import (
    CoverageState,
    round_04_coverage_by_id,
    round_04_coverage_counts,
)


class CertificationCoverageRound04Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.coverage = round_04_coverage_by_id()

    def test_every_round_04_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), {f"GT-R04-{i:03d}" for i in range(1, 7)})

    def test_round_04_remains_partial_until_raw_cross_version_certification(self) -> None:
        counts = round_04_coverage_counts()
        self.assertEqual(counts[CoverageState.PARTIAL], 6)
        self.assertEqual(counts[CoverageState.EXECUTABLE], 0)
        self.assertEqual(counts[CoverageState.RAW_BLOCKED], 0)
        self.assertEqual(counts[CoverageState.CONTEXT_ONLY], 0)

    def test_every_partial_case_names_its_blocker(self) -> None:
        for item in self.coverage.values():
            self.assertEqual(item.state, CoverageState.PARTIAL)
            self.assertTrue(item.blocker and item.blocker.strip())

    def test_older_zone_baseline_is_not_collapsed_into_reflection_geometry(self) -> None:
        blocker = self.coverage["GT-R04-002"].blocker or ""
        self.assertIn("distinct from later Reflection zone geometry", blocker)

    def test_fu_retest_visual_does_not_resolve_r54(self) -> None:
        blocker = self.coverage["GT-R04-001"].blocker or ""
        self.assertIn("R-54 fib orientation", blocker)

    def test_hcs_strength_is_not_numeric(self) -> None:
        blocker = self.coverage["GT-R04-004"].blocker or ""
        self.assertIn("no numeric zone-strength model", blocker)


if __name__ == "__main__":
    unittest.main()
