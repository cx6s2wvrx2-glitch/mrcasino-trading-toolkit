from __future__ import annotations

import json
import unittest
from pathlib import Path


EXAMPLES = Path(__file__).resolve().parents[1] / "06_examples"


class AgentRealityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(
            (EXAMPLES / "AGENT_REALITY_AUDIT_2026_09_04.json").read_text(encoding="utf-8")
        )

    def test_exactly_eight_canonical_agents_are_recorded(self) -> None:
        agents = self.payload["agents"]
        self.assertEqual([agent["id"] for agent in agents], [f"{i:02d}" for i in range(1, 9)])
        self.assertEqual(len({agent["class"] for agent in agents}), 8)

    def test_all_agent_foundations_exist_but_no_background_swarm_is_claimed(self) -> None:
        for agent in self.payload["agents"]:
            self.assertTrue(agent["code_implemented"], agent["id"])
            self.assertFalse(agent["background_runtime_observed"], agent["id"])
            self.assertFalse(agent["may_authorize_live_execution"], agent["id"])
        self.assertTrue(self.payload["system_truth"]["eight_agent_foundation_exists"])
        self.assertFalse(self.payload["system_truth"]["eight_agents_continuously_running_in_background"])

    def test_agent06_corpus_and_external_validation_boundary_are_explicit(self) -> None:
        agent06 = next(agent for agent in self.payload["agents"] if agent["id"] == "06")
        self.assertEqual(agent06["blind_corpus_case_count"], 173)
        self.assertTrue(agent06["checkpoint_resume_audit_infrastructure"])
        self.assertFalse(agent06["completed_audited_full_external_173_case_run_observed"])
        self.assertFalse(agent06["may_promote_strategy_truth"])

    def test_orchestrator_is_current_and_never_grants_live_execution(self) -> None:
        orchestrator = self.payload["orchestrator"]
        self.assertEqual(orchestrator["version"], "0.6.0")
        self.assertTrue(orchestrator["code_implemented"])
        self.assertFalse(orchestrator["background_runtime_observed"])
        self.assertFalse(orchestrator["live_execution_authorized"])

    def test_data_agent_preserves_broker_vs_reference_boundary(self) -> None:
        agent03 = next(agent for agent in self.payload["agents"] if agent["id"] == "03")
        self.assertTrue(agent03["broader_mt5_and_replay_infrastructure_available"])
        self.assertTrue(agent03["real_exclusive_markets_march_broker_evidence_available"])
        self.assertEqual(agent03["canonical_reference_feed"], "FOREXCOM:XAUUSD")
        self.assertFalse(agent03["reference_feed_alignment_complete"])

    def test_live_database_snapshot_does_not_fake_verification(self) -> None:
        snapshot = self.payload["supabase_snapshot"]
        self.assertEqual(snapshot["user_approved_sources"], 29)
        self.assertEqual(snapshot["examples"], 215)
        self.assertEqual(snapshot["knowledge_claims"], 195)
        self.assertEqual(snapshot["rules"], 23)
        self.assertEqual(snapshot["open_disagreements"], 14)
        self.assertEqual(snapshot["agent_runs"], 32)
        self.assertEqual(snapshot["verified_knowledge_claims"], 0)
        self.assertEqual(snapshot["verified_rules"], 0)

    def test_march_frontiers_and_system_authority_remain_fail_closed(self) -> None:
        frontiers = self.payload["current_strategy_frontiers"]
        self.assertEqual(frontiers["2023-03-30_buy"]["source_semantic_frontier"], "LAOL")
        self.assertEqual(frontiers["2023-03-31_sell"]["source_semantic_frontier"], "TFS")
        self.assertEqual(
            frontiers["2023-03-30_buy"]["broker_semantic_frontier"], "zone_poi_reaction"
        )
        self.assertEqual(
            frontiers["2023-03-31_sell"]["broker_semantic_frontier"], "zone_poi_reaction"
        )

        truth = self.payload["system_truth"]
        self.assertFalse(truth["strategy_certified"])
        self.assertFalse(truth["performance_claim_allowed"])
        self.assertFalse(truth["production_risk_ready"])
        self.assertFalse(truth["promotion_allowed"])
        self.assertFalse(truth["live_execution_authorized"])
        self.assertFalse(truth["reference_feed_alignment_complete"])


if __name__ == "__main__":
    unittest.main()
