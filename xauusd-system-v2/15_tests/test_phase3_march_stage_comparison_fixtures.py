from __future__ import annotations

import json
import unittest
from pathlib import Path

from xauusd_v2.phase3_broker_evidence import broker_records_from_payload
from xauusd_v2.phase3_stage_comparison import ComparisonState, compare_source_to_broker_stages
from xauusd_v2.r143_source_evidence_adapter import records_from_r143_source_evidence
from xauusd_v2.strategy_evidence_sequence import StrategyEvidenceStage


EXAMPLES = Path(__file__).resolve().parents[1] / "06_examples"


def load_json(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def compare(source_name: str, broker_name: str):
    source_records = records_from_r143_source_evidence(load_json(source_name))
    broker_records = broker_records_from_payload(load_json(broker_name))
    results = compare_source_to_broker_stages(source_records, broker_records)
    return {result.stage: result for result in results}


class Phase3MarchStageComparisonFixtureTests(unittest.TestCase):
    def test_march_buy_preserves_source_labels_without_broker_semantic_promotion(self) -> None:
        by_stage = compare(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )

        self.assertEqual(
            by_stage[StrategyEvidenceStage.HCS_ZONE_REACTION].comparison_state,
            ComparisonState.SOURCE_OBSERVED_BROKER_PATH_ONLY,
        )
        self.assertEqual(
            by_stage[StrategyEvidenceStage.TFS_CONFIRMED].comparison_state,
            ComparisonState.SOURCE_OBSERVED_BROKER_BLOCKED,
        )
        self.assertEqual(
            by_stage[StrategyEvidenceStage.LAOL_MET].comparison_state,
            ComparisonState.BOTH_BLOCKED,
        )
        self.assertEqual(
            by_stage[StrategyEvidenceStage.TRUE_STOP_RESPECTED].comparison_state,
            ComparisonState.SOURCE_OBSERVED_BROKER_PATH_ONLY,
        )
        self.assertEqual(
            by_stage[StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED].comparison_state,
            ComparisonState.BOTH_BLOCKED,
        )
        self.assertEqual(
            by_stage[StrategyEvidenceStage.TARGETS_AND_TIMING].comparison_state,
            ComparisonState.SOURCE_BLOCKED_BROKER_PATH_OBSERVED,
        )
        self.assertTrue(all(not result.canonical_equivalence_allowed for result in by_stage.values()))

    def test_march_sell_preserves_1986_path_without_hcs_promotion(self) -> None:
        by_stage = compare(
            "R143_SOURCE_EVIDENCE_2023_03_31_SELL.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_31_SELL.json",
        )

        self.assertEqual(
            by_stage[StrategyEvidenceStage.HCS_ZONE_REACTION].comparison_state,
            ComparisonState.SOURCE_OBSERVED_BROKER_PATH_ONLY,
        )
        self.assertEqual(
            by_stage[StrategyEvidenceStage.TFS_CONFIRMED].comparison_state,
            ComparisonState.BOTH_BLOCKED,
        )
        self.assertEqual(
            by_stage[StrategyEvidenceStage.LAOL_MET].comparison_state,
            ComparisonState.BOTH_BLOCKED,
        )
        self.assertEqual(
            by_stage[StrategyEvidenceStage.TRUE_STOP_RESPECTED].comparison_state,
            ComparisonState.BOTH_BLOCKED,
        )
        self.assertEqual(
            by_stage[StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED].comparison_state,
            ComparisonState.BOTH_BLOCKED,
        )
        self.assertEqual(
            by_stage[StrategyEvidenceStage.TARGETS_AND_TIMING].comparison_state,
            ComparisonState.SOURCE_BLOCKED_BROKER_PATH_OBSERVED,
        )
        self.assertTrue(all(not result.canonical_equivalence_allowed for result in by_stage.values()))


if __name__ == "__main__":
    unittest.main()
