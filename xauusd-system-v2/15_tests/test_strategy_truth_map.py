from __future__ import annotations

import json
import unittest
from pathlib import Path


EXAMPLES = Path(__file__).resolve().parents[1] / "06_examples"


class StrategyTruthMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads((EXAMPLES / "STRATEGY_TRUTH_MAP_2026_09_04.json").read_text(encoding="utf-8"))

    def test_truth_map_never_grants_strategy_or_live_authority(self) -> None:
        self.assertFalse(self.payload["strategy_certified"])
        self.assertFalse(self.payload["performance_claim_allowed"])
        self.assertFalse(self.payload["promotion_allowed"])
        self.assertFalse(self.payload["live_execution_authorized"])
        self.assertFalse(self.payload["reference_feed_alignment_complete"])

    def test_flow_has_unique_ordered_nodes(self) -> None:
        flow = self.payload["flow"]
        self.assertEqual([item["order"] for item in flow], list(range(1, len(flow) + 1)))
        ids = [item["id"] for item in flow]
        self.assertEqual(len(ids), len(set(ids)))

    def test_fu_hcs_and_full_context_layers_are_separate(self) -> None:
        ids = [item["id"] for item in self.payload["flow"]]
        self.assertIn("fu_event_language", ids)
        self.assertIn("hcs_negation_stack", ids)
        self.assertIn("liquidity_context", ids)
        self.assertIn("tfs", ids)
        self.assertIn("laol", ids)
        self.assertIn("true_stop", ids)
        self.assertIn("ltf_execution", ids)
        self.assertIn("risk_execution_authority", ids)

    def test_r143_order_is_preserved(self) -> None:
        self.assertEqual(
            self.payload["official_r143_order"],
            [
                "zone_poi_reaction",
                "tfs",
                "laol",
                "true_stop",
                "ten_min_establishment",
                "targets_management",
            ],
        )

    def test_march_frontiers_are_not_hidden(self) -> None:
        frontiers = self.payload["current_march_frontiers"]
        self.assertEqual(frontiers["2023-03-30_buy"]["source_semantic_frontier"], "laol")
        self.assertEqual(frontiers["2023-03-31_sell"]["source_semantic_frontier"], "tfs")
        self.assertEqual(frontiers["2023-03-30_buy"]["broker_semantic_frontier"], "zone_poi_reaction")
        self.assertEqual(frontiers["2023-03-31_sell"]["broker_semantic_frontier"], "zone_poi_reaction")


if __name__ == "__main__":
    unittest.main()
