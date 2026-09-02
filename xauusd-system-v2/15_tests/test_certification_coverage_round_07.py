from __future__ import annotations

import unittest

from xauusd_v2.certification_coverage import CoverageState
from xauusd_v2.certification_coverage_round_07 import round_07_coverage_by_id, round_07_coverage_counts


class CertificationCoverageRound07Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.coverage = round_07_coverage_by_id()

    def test_every_round_07_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), {f"GT-R07-{i:03d}" for i in range(1, 11)})

    def test_round_07_is_honestly_partial(self) -> None:
        counts = round_07_coverage_counts()
        self.assertEqual(counts[CoverageState.EXECUTABLE], 0)
        self.assertEqual(counts[CoverageState.PARTIAL], 10)
        self.assertEqual(counts[CoverageState.RAW_BLOCKED], 0)
        self.assertEqual(counts[CoverageState.CONTEXT_ONLY], 0)

    def test_every_case_names_a_blocker(self) -> None:
        for item in self.coverage.values():
            self.assertEqual(item.state, CoverageState.PARTIAL)
            self.assertTrue(item.blocker)

    def test_2w_confirmation_case_maps_to_cross_timeframe_context(self) -> None:
        item = self.coverage["GT-R07-002"]
        self.assertIn("market_state_agent", item.components)
        self.assertIn("cross-timeframe strength", item.blocker or "")

    def test_ltf_zone_case_is_not_promoted_to_htf_authority(self) -> None:
        item = self.coverage["GT-R07-010"]
        self.assertIn("ltf_execution", item.components)
        self.assertIn("LTF context", item.blocker or "")


if __name__ == "__main__":
    unittest.main()
