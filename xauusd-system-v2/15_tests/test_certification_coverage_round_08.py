from __future__ import annotations

import unittest

from xauusd_v2.certification_coverage import CoverageState
from xauusd_v2.certification_coverage_round_08 import round_08_coverage_by_id, round_08_coverage_counts


class CertificationCoverageRound08Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.coverage = round_08_coverage_by_id()

    def test_every_round_08_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), {f"GT-R08-{i:03d}" for i in range(1, 11)})

    def test_round_08_is_honestly_partial(self) -> None:
        counts = round_08_coverage_counts()
        self.assertEqual(counts[CoverageState.EXECUTABLE], 0)
        self.assertEqual(counts[CoverageState.PARTIAL], 10)
        self.assertEqual(counts[CoverageState.RAW_BLOCKED], 0)
        self.assertEqual(counts[CoverageState.CONTEXT_ONLY], 0)

    def test_every_case_names_a_blocker(self) -> None:
        for item in self.coverage.values():
            self.assertEqual(item.state, CoverageState.PARTIAL)
            self.assertTrue(item.blocker)

    def test_multi_horizon_direction_case_stays_partial_until_horizon_model_exists(self) -> None:
        item = self.coverage["GT-R08-002"]
        self.assertIn("market_state_agent", item.components)
        self.assertIn("separate horizons", item.blocker or "")

    def test_many_fu_retests_phrase_is_not_numericized(self) -> None:
        item = self.coverage["GT-R08-009"]
        self.assertIn("no certified numeric threshold", item.blocker or "")


if __name__ == "__main__":
    unittest.main()
