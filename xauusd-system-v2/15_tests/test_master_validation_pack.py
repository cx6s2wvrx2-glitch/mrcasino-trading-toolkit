from __future__ import annotations

import json
import unittest
from pathlib import Path


EXAMPLES = Path(__file__).resolve().parents[1] / "06_examples"


class MasterValidationPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(
            (EXAMPLES / "MASTER_VALIDATION_PACK_2026_09_04.json").read_text(encoding="utf-8")
        )

    def test_strategy_flow_and_r143_subset_are_ordered(self) -> None:
        flow = self.payload["strategy_flow"]
        self.assertEqual(len(flow), len(set(flow)))
        self.assertEqual(
            self.payload["official_r143_subset"],
            [
                "zone_poi_reaction",
                "tfs_prevalent_direction",
                "active_laol",
                "true_stop_main_poi_respect",
                "ten_min_true_stop_establishment",
                "targets_management",
            ],
        )
        positions = [flow.index(stage) for stage in self.payload["official_r143_subset"]]
        self.assertEqual(positions, sorted(positions))

    def test_all_truth_layers_are_explicitly_non_certified_states(self) -> None:
        allowed = {"PARTIAL", "BLOCKED_FOR_PRODUCTION"}
        layers = self.payload["truth_layers"]
        self.assertEqual([layer["id"] for layer in layers], self.payload["strategy_flow"])
        self.assertTrue(all(layer["state"] in allowed for layer in layers))
        self.assertTrue(all(layer["locked"] for layer in layers))
        self.assertTrue(all(layer["open"] for layer in layers))

    def test_march_buy_and_sell_frontiers_remain_fail_closed(self) -> None:
        buy = self.payload["march_episodes"]["2023-03-30_buy"]
        sell = self.payload["march_episodes"]["2023-03-31_sell"]
        self.assertEqual(buy["source_frontier"], "LAOL_MET")
        self.assertEqual(buy["broker_frontier"], "HCS_ZONE_REACTION")
        self.assertFalse(buy["reference_alignment"])
        self.assertEqual(sell["source_frontier"], "TFS_CONFIRMED")
        self.assertEqual(sell["broker_frontier"], "HCS_ZONE_REACTION")
        self.assertFalse(sell["reference_alignment"])

    def test_agent_reality_is_not_background_swarm(self) -> None:
        reality = self.payload["agent_reality"]
        self.assertEqual(reality["canonical_agent_count"], 8)
        self.assertTrue(reality["all_foundations_implemented"])
        self.assertFalse(reality["continuous_background_swarm_observed"])
        self.assertEqual(reality["orchestrator_version"], "0.6.0")
        self.assertEqual(reality["agent06_blind_case_count"], 173)
        self.assertFalse(reality["completed_audited_full_external_agent06_run_observed"])

    def test_user_questions_are_only_isolated_not_silently_resolved(self) -> None:
        questions = self.payload["user_only_questions_currently_isolated"]
        self.assertEqual([item["id"] for item in questions], ["UQ-01", "UQ-02"])
        self.assertEqual([item["topic"] for item in questions], ["LAOL_MET", "TFS_CONFIRMED"])
        self.assertTrue(all(item["ask_now"] is False for item in questions))

    def test_all_canonical_blocker_families_remain_visible(self) -> None:
        self.assertEqual(
            self.payload["canonical_blockers"],
            [f"B-{i:02d}" for i in range(1, 9)],
        )

    def test_pack_cannot_grant_certification_performance_or_live_authority(self) -> None:
        authority = self.payload["authority"]
        self.assertTrue(authority)
        self.assertTrue(all(value is False for value in authority.values()))


if __name__ == "__main__":
    unittest.main()
