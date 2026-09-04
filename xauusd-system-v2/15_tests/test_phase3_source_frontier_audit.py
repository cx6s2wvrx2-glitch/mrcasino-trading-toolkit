from __future__ import annotations

import json
import unittest
from pathlib import Path


EXAMPLES = Path(__file__).resolve().parents[1] / "06_examples"


class Phase3SourceFrontierAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(
            (EXAMPLES / "PHASE3_SOURCE_FRONTIER_AUDIT_2026_09_04.json").read_text(encoding="utf-8")
        )

    def test_two_source_passes_are_recorded_without_promotion(self) -> None:
        self.assertTrue(self.payload["source_exhaustion_completed"])
        self.assertTrue(self.payload["second_independent_source_pass_completed"])
        self.assertFalse(self.payload["strategy_truth_changed"])
        self.assertFalse(self.payload["promotion_allowed"])
        self.assertFalse(self.payload["performance_claim_allowed"])
        self.assertFalse(self.payload["live_execution_authorized"])

    def test_only_two_current_user_clarification_frontiers_are_recorded(self) -> None:
        frontiers = self.payload["frontiers"]
        self.assertEqual(len(frontiers), 2)
        by_episode = {item["episode_id"]: item for item in frontiers}
        self.assertEqual(by_episode["mr-casino-2023-03-30-buy-sequence"]["stage"], "LAOL_MET")
        self.assertEqual(by_episode["mr-casino-2023-03-31-sell-sequence"]["stage"], "TFS_CONFIRMED")
        self.assertTrue(
            all(
                item["status"] == "USER_CLARIFICATION_REQUIRED_AFTER_TWO_SOURCE_PASSES"
                for item in frontiers
            )
        )

    def test_second_pass_strengthens_definitions_without_closing_frontiers(self) -> None:
        findings = {item["locator"]: item for item in self.payload["second_pass_source_locators"]}
        for locator in (
            "Reflection Master p.97 · R-180 occurrence 2",
            "Reflection Master p.97 · R-182",
            "Reflection Master p.113 · R-208",
            "Reflection Master p.118 · R-214",
            "Reflection Master p.118 · R-217",
            "Reflection Master p.39 · R-143",
        ):
            self.assertIn(locator, findings)
        self.assertIn("does not identify", findings["Reflection Master p.97 · R-180 occurrence 2"]["effect_on_frontier"])
        self.assertIn("not the operational meaning", findings["Reflection Master p.113 · R-208"]["effect_on_frontier"])

    def test_laol_frontier_forbids_silent_equivalence(self) -> None:
        buy = next(item for item in self.payload["frontiers"] if item["episode_id"].endswith("buy-sequence"))
        assumptions = "\n".join(buy["must_not_assume"])
        self.assertIn("LAOL respected equals LAOL met", assumptions)
        self.assertIn("LAOL taken equals LAOL met", assumptions)
        self.assertIn("1972.19 liquidity left behind equals LAOL met", assumptions)
        self.assertIn("R-208/R-214", buy["why_blocked"])

    def test_sell_frontier_forbids_lookahead_tfs(self) -> None:
        sell = next(item for item in self.payload["frontiers"] if item["episode_id"].endswith("sell-sequence"))
        assumptions = "\n".join(sell["must_not_assume"])
        self.assertIn("forming daily FU equals established TFS", assumptions)
        self.assertIn("later 4h close can validate the earlier 1986 decision retroactively", assumptions)
        self.assertIn("R-217", sell["why_blocked"])
        self.assertIn("R-182", sell["why_blocked"])
        self.assertIn("R-180", sell["why_blocked"])

    def test_assistant_side_prerequisites_are_complete_before_user_question(self) -> None:
        prerequisites = self.payload["assistant_side_prerequisites_completed"]
        self.assertTrue(prerequisites["agent_reality_audit"])
        self.assertTrue(prerequisites["master_validation_pack"])
        self.assertTrue(prerequisites["continuation_handoff_refresh"])
        self.assertTrue(self.payload["next_strategy_semantic_gate"].startswith("ask UQ-01 LAOL_MET first"))


if __name__ == "__main__":
    unittest.main()
