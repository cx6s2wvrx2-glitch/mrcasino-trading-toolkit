from __future__ import annotations

import json
import unittest
from pathlib import Path

from xauusd_v2.certification_coverage import (
    CoverageState,
    round_03_coverage_by_id,
    round_03_coverage_counts,
)


class CertificationCoverageRound03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        payload = json.loads(Path(__file__).with_name("ground_truth_round_03.json").read_text(encoding="utf-8"))
        cls.ids = {item["id"] for item in payload["test_vectors"]}
        cls.coverage = round_03_coverage_by_id()

    def test_every_round_03_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), self.ids)

    def test_all_round_03_cases_preserve_a_blocker_until_raw_fixture_certification(self) -> None:
        for item in self.coverage.values():
            self.assertIn(item.state, {CoverageState.PARTIAL, CoverageState.RAW_BLOCKED})
            self.assertTrue(item.blocker)

    def test_imbalance_h1_is_explicitly_raw_blocked_not_fake_executable(self) -> None:
        item = self.coverage["GT-R03-006"]
        self.assertEqual(item.state, CoverageState.RAW_BLOCKED)
        self.assertIn("broker-quality", item.blocker)

    def test_round_03_counts_are_seven_without_verified_proxy(self) -> None:
        counts = round_03_coverage_counts()
        self.assertEqual(sum(counts.values()), 7)
        self.assertEqual(counts[CoverageState.EXECUTABLE], 0)
        self.assertEqual(counts[CoverageState.PARTIAL], 6)
        self.assertEqual(counts[CoverageState.RAW_BLOCKED], 1)


if __name__ == "__main__":
    unittest.main()
