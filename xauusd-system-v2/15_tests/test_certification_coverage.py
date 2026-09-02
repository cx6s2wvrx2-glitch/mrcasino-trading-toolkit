from __future__ import annotations

import json
import unittest
from pathlib import Path

from xauusd_v2.certification_coverage import CoverageState, coverage_by_id, coverage_counts


class CertificationCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = Path(__file__).with_name("ground_truth_round_02.json")
        cls.dataset = json.loads(path.read_text(encoding="utf-8"))
        cls.ids = {item["id"] for item in cls.dataset["test_vectors"]}
        cls.coverage = coverage_by_id()

    def test_every_round_02_ground_truth_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), self.ids)

    def test_coverage_registry_has_no_unknown_extra_cases(self) -> None:
        self.assertFalse(set(self.coverage) - self.ids)

    def test_partial_and_blocked_states_must_name_a_blocker(self) -> None:
        for item in self.coverage.values():
            if item.state in {CoverageState.PARTIAL, CoverageState.RAW_BLOCKED, CoverageState.CONTEXT_ONLY}:
                self.assertTrue(item.blocker)

    def test_executable_states_do_not_claim_verified(self) -> None:
        for item in self.coverage.values():
            text = " ".join((item.state.value, *item.components, item.blocker or "")).lower()
            self.assertNotIn("verified", text)

    def test_round_02_has_mixed_coverage_not_fake_full_automation(self) -> None:
        counts = coverage_counts()
        self.assertGreater(counts[CoverageState.EXECUTABLE], 0)
        self.assertGreater(counts[CoverageState.PARTIAL], 0)
        self.assertGreater(counts[CoverageState.CONTEXT_ONLY], 0)
        self.assertEqual(sum(counts.values()), 20)


if __name__ == "__main__":
    unittest.main()
