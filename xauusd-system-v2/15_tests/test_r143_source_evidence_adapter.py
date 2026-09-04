from __future__ import annotations

import unittest

from xauusd_v2.backtest_sequence import BacktestStage, SequenceState
from xauusd_v2.r143_source_evidence_adapter import records_from_r143_source_evidence
from xauusd_v2.strategy_evidence_sequence import EvidenceState, StrategyEvidenceStage, evaluate_r143_evidence


def source_payload(*, laol_status: str = "unresolved") -> dict:
    return {
        "schema_version": "r143_source_evidence_map_v1",
        "episode_id": "episode-fixture",
        "stages": [
            {
                "stage": "HCS_ZONE_REACTION",
                "status": "explicit",
                "source_refs": ["source#hcs"],
                "note": "explicit HCS zone reaction",
                "machine_stage_certified": False,
            },
            {
                "stage": "TFS",
                "status": "explicit",
                "source_refs": ["source#tfs"],
                "note": "explicit source TFS context",
                "machine_stage_certified": False,
            },
            {
                "stage": "LAOL_MET",
                "status": laol_status,
                "source_refs": ["source#laol"],
                "note": "LAOL completeness unresolved",
                "machine_stage_certified": False,
            },
            {
                "stage": "TRUE_STOP_RESPECTED",
                "status": "explicit",
                "source_refs": ["source#ts"],
                "note": "explicit respected TS label",
                "machine_stage_certified": False,
            },
            {
                "stage": "TEN_MIN_TRUE_STOP_ESTABLISHED",
                "status": "unresolved",
                "source_refs": [],
                "note": "no certified 10m event",
                "machine_stage_certified": False,
            },
            {
                "stage": "TARGETS_AND_TIMING",
                "status": "partial",
                "source_refs": ["source#target"],
                "note": "target exists but package incomplete",
                "machine_stage_certified": False,
            },
        ],
        "complete_source_sequence_claim": False,
        "promotion_allowed": False,
        "performance_claim_allowed": False,
        "live_execution_authorized": False,
    }


class R143SourceEvidenceAdapterTests(unittest.TestCase):
    def test_explicit_source_stage_becomes_observed_not_certified(self) -> None:
        records = records_from_r143_source_evidence(source_payload())
        by_stage = {record.stage: record for record in records}
        hcs = by_stage[StrategyEvidenceStage.HCS_ZONE_REACTION]
        self.assertEqual(hcs.state, EvidenceState.OBSERVED)
        self.assertIn("machine_stage_certified=false", hcs.note)
        self.assertEqual(hcs.source_ref, "source#hcs")

    def test_partial_and_unresolved_stages_remain_blocked(self) -> None:
        records = records_from_r143_source_evidence(source_payload())
        by_stage = {record.stage: record for record in records}
        self.assertEqual(by_stage[StrategyEvidenceStage.LAOL_MET].state, EvidenceState.BLOCKED)
        self.assertEqual(by_stage[StrategyEvidenceStage.TARGETS_AND_TIMING].state, EvidenceState.BLOCKED)

    def test_source_packet_stays_not_certified_when_laol_is_unresolved(self) -> None:
        result = evaluate_r143_evidence(records_from_r143_source_evidence(source_payload()))
        self.assertEqual(result.state, SequenceState.NOT_CERTIFIED)
        self.assertEqual(result.next_required_stage, BacktestStage.LAOL_MET)

    def test_adapter_rejects_machine_certified_input(self) -> None:
        payload = source_payload()
        payload["stages"][0]["machine_stage_certified"] = True
        with self.assertRaises(ValueError):
            records_from_r143_source_evidence(payload)

    def test_adapter_requires_all_six_r143_stages(self) -> None:
        payload = source_payload()
        payload["stages"] = payload["stages"][:-1]
        with self.assertRaises(ValueError):
            records_from_r143_source_evidence(payload)

    def test_unknown_source_status_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            records_from_r143_source_evidence(source_payload(laol_status="maybe"))


if __name__ == "__main__":
    unittest.main()
