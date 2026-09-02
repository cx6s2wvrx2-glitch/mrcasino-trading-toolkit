from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.backtest_sequence import SequenceState
from xauusd_v2.component_replay_dataset import load_historical_replay_dataset, replay_dataset


class ComponentReplayDatasetTests(unittest.TestCase):
    def write_payload(self, payload: dict[str, object]) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(payload, handle)
        handle.close()
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        return Path(handle.name)

    def valid_session(self, session_id: str = "S1") -> dict[str, object]:
        return {
            "session_id": session_id,
            "source_ref": "primary:fixture",
            "evaluation_time": "2026-01-05T12:00:00+00:00",
            "confirmations": [
                {"stage": "HCS_ZONE_REACTION", "occurred_at": "2026-01-05T08:10:00+00:00", "available_at": "2026-01-05T08:10:00+00:00", "source_ref": "primary:hcs"},
                {"stage": "TFS", "occurred_at": "2026-01-05T08:20:00+00:00", "available_at": "2026-01-05T08:20:00+00:00", "source_ref": "primary:tfs"},
                {"stage": "LAOL_MET", "occurred_at": "2026-01-05T08:30:00+00:00", "available_at": "2026-01-05T08:30:00+00:00", "source_ref": "primary:laol"},
                {"stage": "TRUE_STOP_RESPECTED", "occurred_at": "2026-01-05T08:40:00+00:00", "available_at": "2026-01-05T08:40:00+00:00", "source_ref": "primary:ts"},
                {"stage": "TEN_MIN_TRUE_STOP_ESTABLISHED", "occurred_at": "2026-01-05T08:50:00+00:00", "available_at": "2026-01-05T09:00:00+00:00", "source_ref": "primary:10m-ts"},
                {"stage": "TARGETS_AND_TIMING", "occurred_at": "2026-01-05T09:10:00+00:00", "available_at": "2026-01-05T09:10:00+00:00", "source_ref": "primary:targets"}
            ],
        }

    def valid_payload(self) -> dict[str, object]:
        return {
            "dataset": "Historical Replay Fixture",
            "status": "candidate_not_verified",
            "promotion_allowed": False,
            "sessions": [self.valid_session()],
        }

    def test_valid_dataset_loads_and_replays_complete_sequence(self) -> None:
        dataset = load_historical_replay_dataset(self.write_payload(self.valid_payload()))
        self.assertEqual(len(dataset.sessions), 1)
        self.assertFalse(dataset.promotion_allowed)
        results = replay_dataset(dataset)
        self.assertEqual(results[0].sequence.state, SequenceState.COMPLETE_CANDIDATE)
        self.assertFalse(results[0].lookahead_used)

    def test_duplicate_session_id_is_rejected(self) -> None:
        payload = self.valid_payload()
        payload["sessions"] = [self.valid_session("S1"), self.valid_session("S1")]
        with self.assertRaises(ValueError):
            load_historical_replay_dataset(self.write_payload(payload))

    def test_duplicate_stage_inside_session_is_rejected(self) -> None:
        payload = self.valid_payload()
        session = payload["sessions"][0]
        assert isinstance(session, dict)
        confirmations = session["confirmations"]
        assert isinstance(confirmations, list)
        confirmations.append(dict(confirmations[0]))
        with self.assertRaises(ValueError):
            load_historical_replay_dataset(self.write_payload(payload))

    def test_unknown_stage_name_is_rejected(self) -> None:
        payload = self.valid_payload()
        session = payload["sessions"][0]
        assert isinstance(session, dict)
        confirmations = session["confirmations"]
        assert isinstance(confirmations, list)
        confirmations[0]["stage"] = "MAGIC_ENTRY"
        with self.assertRaises(ValueError):
            load_historical_replay_dataset(self.write_payload(payload))

    def test_naive_evaluation_time_is_rejected(self) -> None:
        payload = self.valid_payload()
        session = payload["sessions"][0]
        assert isinstance(session, dict)
        session["evaluation_time"] = "2026-01-05T12:00:00"
        with self.assertRaises(ValueError):
            load_historical_replay_dataset(self.write_payload(payload))

    def test_missing_event_provenance_is_rejected(self) -> None:
        payload = self.valid_payload()
        session = payload["sessions"][0]
        assert isinstance(session, dict)
        confirmations = session["confirmations"]
        assert isinstance(confirmations, list)
        confirmations[0]["source_ref"] = ""
        with self.assertRaises(ValueError):
            load_historical_replay_dataset(self.write_payload(payload))

    def test_empty_dataset_is_rejected(self) -> None:
        payload = self.valid_payload()
        payload["sessions"] = []
        with self.assertRaises(ValueError):
            load_historical_replay_dataset(self.write_payload(payload))

    def test_promotion_allowed_must_be_boolean(self) -> None:
        payload = self.valid_payload()
        payload["promotion_allowed"] = "false"
        with self.assertRaises(ValueError):
            load_historical_replay_dataset(self.write_payload(payload))

    def test_event_available_before_occurrence_is_rejected(self) -> None:
        payload = self.valid_payload()
        session = payload["sessions"][0]
        assert isinstance(session, dict)
        confirmations = session["confirmations"]
        assert isinstance(confirmations, list)
        confirmations[0]["available_at"] = "2026-01-05T08:09:00+00:00"
        with self.assertRaises(ValueError):
            load_historical_replay_dataset(self.write_payload(payload))


if __name__ == "__main__":
    unittest.main()
