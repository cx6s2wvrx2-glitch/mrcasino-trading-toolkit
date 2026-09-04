from __future__ import annotations

import json
import unittest
from pathlib import Path

from xauusd_v2.phase3_broker_evidence import broker_records_from_payload
from xauusd_v2.phase3_research_frontier import (
    FrontierState,
    find_first_broker_semantic_frontier,
    find_first_research_frontier,
    find_first_source_semantic_frontier,
)
from xauusd_v2.r143_source_evidence_adapter import records_from_r143_source_evidence
from xauusd_v2.strategy_evidence_sequence import StrategyEvidenceStage


EXAMPLES = Path(__file__).resolve().parents[1] / "06_examples"


def load_json(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def source_records(name: str):
    return records_from_r143_source_evidence(load_json(name))


def broker_records(name: str):
    return broker_records_from_payload(load_json(name))


def frontier(source_name: str, broker_name: str):
    return find_first_research_frontier(source_records(source_name), broker_records(broker_name))


class Phase3ResearchFrontierTests(unittest.TestCase):
    def test_march_buy_source_research_frontier_is_laol(self) -> None:
        result = find_first_source_semantic_frontier(source_records("R143_SOURCE_EVIDENCE_2023_03_30_BUY.json"))
        self.assertEqual(result.stage, StrategyEvidenceStage.LAOL_MET)
        self.assertEqual(result.state, FrontierState.SOURCE_SEMANTIC_FRONTIER)
        self.assertFalse(result.downstream_semantic_promotion_allowed)

    def test_march_sell_source_research_frontier_is_tfs(self) -> None:
        result = find_first_source_semantic_frontier(source_records("R143_SOURCE_EVIDENCE_2023_03_31_SELL.json"))
        self.assertEqual(result.stage, StrategyEvidenceStage.TFS_CONFIRMED)
        self.assertEqual(result.state, FrontierState.SOURCE_SEMANTIC_FRONTIER)

    def test_march_buy_first_broker_frontier_is_hcs_stage(self) -> None:
        result = find_first_broker_semantic_frontier(
            broker_records("PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json")
        )
        self.assertEqual(result.stage, StrategyEvidenceStage.HCS_ZONE_REACTION)
        self.assertEqual(result.state, FrontierState.BROKER_SEMANTIC_FRONTIER)
        self.assertTrue(result.broker_path_observed)

    def test_march_sell_first_broker_frontier_is_hcs_stage(self) -> None:
        result = find_first_broker_semantic_frontier(
            broker_records("PHASE3_BROKER_STAGE_EVIDENCE_2023_03_31_SELL.json")
        )
        self.assertEqual(result.stage, StrategyEvidenceStage.HCS_ZONE_REACTION)
        self.assertEqual(result.state, FrontierState.BROKER_SEMANTIC_FRONTIER)
        self.assertTrue(result.broker_path_observed)

    def test_combined_frontier_stops_at_source_explicit_broker_blocked_hcs(self) -> None:
        result = frontier(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        self.assertEqual(result.stage, StrategyEvidenceStage.HCS_ZONE_REACTION)
        self.assertEqual(result.state, FrontierState.BROKER_SEMANTIC_FRONTIER)
        self.assertFalse(result.downstream_semantic_promotion_allowed)

    def test_price_path_cannot_skip_blocked_broker_semantics(self) -> None:
        result = frontier(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        self.assertFalse(result.downstream_semantic_promotion_allowed)
        self.assertIn("broker semantic certification", result.reason)


if __name__ == "__main__":
    unittest.main()
