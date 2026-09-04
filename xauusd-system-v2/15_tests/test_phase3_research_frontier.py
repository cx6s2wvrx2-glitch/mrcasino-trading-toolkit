from __future__ import annotations

import json
import unittest
from pathlib import Path

from xauusd_v2.phase3_broker_evidence import broker_records_from_payload
from xauusd_v2.phase3_research_frontier import FrontierState, find_first_research_frontier
from xauusd_v2.r143_source_evidence_adapter import records_from_r143_source_evidence
from xauusd_v2.strategy_evidence_sequence import StrategyEvidenceStage


EXAMPLES = Path(__file__).resolve().parents[1] / "06_examples"


def load_json(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def frontier(source_name: str, broker_name: str):
    return find_first_research_frontier(
        records_from_r143_source_evidence(load_json(source_name)),
        broker_records_from_payload(load_json(broker_name)),
    )


class Phase3ResearchFrontierTests(unittest.TestCase):
    def test_march_buy_first_machine_frontier_is_hcs_stage(self) -> None:
        result = frontier(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        self.assertEqual(result.stage, StrategyEvidenceStage.HCS_ZONE_REACTION)
        self.assertEqual(result.state, FrontierState.BROKER_SEMANTIC_FRONTIER)
        self.assertTrue(result.broker_path_observed)
        self.assertFalse(result.downstream_semantic_promotion_allowed)

    def test_march_sell_first_machine_frontier_is_hcs_stage(self) -> None:
        result = frontier(
            "R143_SOURCE_EVIDENCE_2023_03_31_SELL.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_31_SELL.json",
        )
        self.assertEqual(result.stage, StrategyEvidenceStage.HCS_ZONE_REACTION)
        self.assertEqual(result.state, FrontierState.BROKER_SEMANTIC_FRONTIER)
        self.assertTrue(result.broker_path_observed)

    def test_price_path_cannot_skip_blocked_broker_semantics(self) -> None:
        result = frontier(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        self.assertFalse(result.downstream_semantic_promotion_allowed)
        self.assertIn("broker semantic certification", result.reason)


if __name__ == "__main__":
    unittest.main()
