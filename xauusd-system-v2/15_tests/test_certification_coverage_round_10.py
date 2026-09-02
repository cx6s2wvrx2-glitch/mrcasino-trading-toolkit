from __future__ import annotations

import unittest

from xauusd_v2.certification_coverage import CoverageState
from xauusd_v2.certification_coverage_round_10 import round_10_coverage_by_id, round_10_coverage_counts


class CertificationCoverageRound10Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.coverage = round_10_coverage_by_id()

    def test_every_round_10_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), {f"GT-R10-{i:03d}" for i in range(1, 21)})

    def test_round_10_is_honestly_partial(self) -> None:
        counts = round_10_coverage_counts()
        self.assertEqual(counts[CoverageState.EXECUTABLE], 0)
        self.assertEqual(counts[CoverageState.PARTIAL], 20)
        self.assertEqual(counts[CoverageState.RAW_BLOCKED], 0)
        self.assertEqual(counts[CoverageState.CONTEXT_ONLY], 0)

    def test_every_case_names_a_blocker(self) -> None:
        for item in self.coverage.values():
            self.assertEqual(item.state, CoverageState.PARTIAL)
            self.assertTrue(item.blocker)

    def test_nearby_liquidity_veto_keeps_qualitative_distance_blocker(self) -> None:
        self.assertIn("qualitative", self.coverage["GT-R10-013"].blocker or "")

    def test_broker_feed_difference_requires_raw_ohlc_fixture(self) -> None:
        item = self.coverage["GT-R10-017"]
        self.assertIn("broker_precision", item.components)
        self.assertIn("machine-readable fixtures", item.blocker or "")


if __name__ == "__main__":
    unittest.main()
