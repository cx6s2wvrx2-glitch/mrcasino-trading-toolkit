from __future__ import annotations

import json
import unittest
from pathlib import Path

from xauusd_v2.phase3_broker_evidence import broker_records_from_payload
from xauusd_v2.phase3_timed_reconstruction import build_timed_stage_rows, render_timed_reconstruction_gr
from xauusd_v2.r143_source_evidence_adapter import records_from_r143_source_evidence
from xauusd_v2.strategy_evidence_sequence import StrategyEvidenceStage


EXAMPLES = Path(__file__).resolve().parents[1] / "06_examples"


def load_json(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def build(source_name: str, broker_name: str):
    source_records = records_from_r143_source_evidence(load_json(source_name))
    broker_records = broker_records_from_payload(load_json(broker_name))
    return build_timed_stage_rows(source_records, broker_records)


class Phase3TimedReconstructionTests(unittest.TestCase):
    def test_march_buy_keeps_true_stop_price_time_separate_from_semantic_truth(self) -> None:
        rows = build(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        by_stage = {row.stage: row for row in rows}

        ts = by_stage[StrategyEvidenceStage.TRUE_STOP_RESPECTED]
        self.assertEqual(ts.broker_event_time, "2023-03-30T15:53:00Z")
        self.assertEqual(ts.broker_timeframe_minutes, 1)
        self.assertTrue(ts.broker_path_observed)
        self.assertFalse(ts.canonical_equivalence_allowed)
        self.assertEqual(ts.allowed_conclusion, "BROKER_PATH_ONLY_SEMANTIC_NOT_CERTIFIED")
        self.assertIn("1972.69", ts.broker_note)

    def test_march_buy_target_path_is_timed_but_not_promoted(self) -> None:
        rows = build(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        by_stage = {row.stage: row for row in rows}
        target = by_stage[StrategyEvidenceStage.TARGETS_AND_TIMING]
        self.assertEqual(target.broker_event_time, "2023-03-30T16:49:00Z")
        self.assertTrue(target.broker_path_observed)
        self.assertEqual(target.allowed_conclusion, "BROKER_PATH_ONLY_SEMANTIC_NOT_CERTIFIED")

    def test_march_sell_1986_region_is_timed_path_only(self) -> None:
        rows = build(
            "R143_SOURCE_EVIDENCE_2023_03_31_SELL.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_31_SELL.json",
        )
        by_stage = {row.stage: row for row in rows}
        hcs = by_stage[StrategyEvidenceStage.HCS_ZONE_REACTION]
        self.assertEqual(hcs.broker_event_time, "2023-03-31T12:34:00Z")
        self.assertTrue(hcs.broker_path_observed)
        self.assertFalse(hcs.canonical_equivalence_allowed)
        self.assertIn("1987.57", hcs.broker_note)
        self.assertIn("1986", hcs.broker_note)

    def test_renderer_is_human_readable_and_explicitly_fail_closed(self) -> None:
        rows = build(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        text = render_timed_reconstruction_gr(rows, title="MARCH 30 BUY")
        self.assertIn("ΠΗΓΗ → BROKER ΧΡΟΝΟΣ/TF", text)
        self.assertIn("2023-03-30T15:53:00Z / 1m", text)
        self.assertIn("BROKER_PATH_ONLY_SEMANTIC_NOT_CERTIFIED", text)
        self.assertIn("Broker price/path observation ≠ strategy semantic certification", text)
        self.assertIn("live execution authority: false", text)

    def test_rows_follow_official_r143_order(self) -> None:
        rows = build(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        self.assertEqual(
            [row.stage for row in rows],
            [
                StrategyEvidenceStage.HCS_ZONE_REACTION,
                StrategyEvidenceStage.TFS_CONFIRMED,
                StrategyEvidenceStage.LAOL_MET,
                StrategyEvidenceStage.TRUE_STOP_RESPECTED,
                StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED,
                StrategyEvidenceStage.TARGETS_AND_TIMING,
            ],
        )


if __name__ == "__main__":
    unittest.main()
