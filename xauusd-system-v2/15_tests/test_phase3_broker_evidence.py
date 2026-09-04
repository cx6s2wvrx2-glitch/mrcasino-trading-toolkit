from __future__ import annotations

import unittest

from xauusd_v2.phase3_broker_evidence import broker_records_from_payload
from xauusd_v2.strategy_evidence_sequence import EvidenceState, StrategyEvidenceStage


class Phase3BrokerEvidenceTests(unittest.TestCase):
    def test_path_observation_stays_separate_from_semantic_state(self) -> None:
        payload = {
            "schema_version": "phase3_broker_stage_evidence_v1",
            "broker_symbol": "XAUUSD!",
            "records": [
                {
                    "stage": "true_stop_respected",
                    "semantic_state": "blocked",
                    "broker_path_observed": True,
                    "evidence_ref": "fixture:1972.70",
                    "event_time": "2023-03-30T15:53:00Z",
                    "timeframe_minutes": 1,
                    "machine_stage_certified": False,
                    "reference_feed_aligned": False,
                    "note": "price anchor observed; semantic stage blocked",
                }
            ],
        }
        record = broker_records_from_payload(payload)[0]
        self.assertEqual(record.stage, StrategyEvidenceStage.TRUE_STOP_RESPECTED)
        self.assertEqual(record.semantic_state, EvidenceState.BLOCKED)
        self.assertTrue(record.broker_path_observed)
        self.assertFalse(record.machine_stage_certified)
        self.assertFalse(record.reference_feed_aligned)

    def test_parser_rejects_observed_semantic_without_machine_certification(self) -> None:
        payload = {
            "schema_version": "phase3_broker_stage_evidence_v1",
            "broker_symbol": "XAUUSD!",
            "records": [
                {
                    "stage": "tfs_confirmed",
                    "semantic_state": "observed",
                    "broker_path_observed": True,
                    "evidence_ref": "fixture:tfs",
                    "machine_stage_certified": False,
                    "reference_feed_aligned": False,
                }
            ],
        }
        with self.assertRaises(ValueError):
            broker_records_from_payload(payload)

    def test_parser_rejects_unknown_stage(self) -> None:
        payload = {
            "schema_version": "phase3_broker_stage_evidence_v1",
            "broker_symbol": "XAUUSD!",
            "records": [
                {
                    "stage": "invented_stage",
                    "semantic_state": "blocked",
                    "broker_path_observed": None,
                }
            ],
        }
        with self.assertRaises(ValueError):
            broker_records_from_payload(payload)


if __name__ == "__main__":
    unittest.main()
