from __future__ import annotations

import unittest

from xauusd_v2.certification_coverage import CoverageState, round_05_coverage_by_id, round_05_coverage_counts


class CertificationCoverageRound05Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.coverage = round_05_coverage_by_id()

    def test_every_round_05_case_has_explicit_coverage(self) -> None:
        self.assertEqual(set(self.coverage), {f"GT-R05-{i:03d}" for i in range(1, 6)})

    def test_all_round_05_cases_are_semantically_executable(self) -> None:
        counts = round_05_coverage_counts()
        self.assertEqual(counts[CoverageState.EXECUTABLE], 5)
        self.assertEqual(counts[CoverageState.PARTIAL], 0)
        self.assertEqual(counts[CoverageState.RAW_BLOCKED], 0)
        self.assertEqual(counts[CoverageState.CONTEXT_ONLY], 0)

    def test_executable_means_implementation_coverage_not_verified(self) -> None:
        for item in self.coverage.values():
            self.assertEqual(item.state, CoverageState.EXECUTABLE)
            self.assertIsNone(item.blocker)

    def test_negative_hcs_establishment_maps_to_tfs_semantics(self) -> None:
        self.assertIn("tfs_semantic", self.coverage["GT-R05-001"].components)

    def test_doji_edge_cases_map_to_doji_semantic_module(self) -> None:
        self.assertIn("doji_liquidity_semantic", self.coverage["GT-R05-003"].components)
        self.assertIn("doji_liquidity_semantic", self.coverage["GT-R05-004"].components)

    def test_secondary_hcs_confluence_maps_to_sequence_gate(self) -> None:
        self.assertEqual(self.coverage["GT-R05-005"].components, ("backtest_sequence",))


if __name__ == "__main__":
    unittest.main()
