from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

from xauusd_v2.backtest_sequence import BacktestStage
from xauusd_v2.data_snapshot import load_xauusd_csv_snapshot_bytes
from xauusd_v2.mt5_snapshot_load import VerifiedPersistedMT5Snapshot
from xauusd_v2.replay_candidate_registry import ReplayCandidate, ReplayCandidateState
from xauusd_v2.replay_stage_certification import (
    ReplayStageCertificationError,
    load_verified_replay_stage_certification,
)
from xauusd_v2.source_chart_alignment import SourceChartAlignmentResult, SourceChartAlignmentState


class ReplayStageCertificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.timeframe = 600
        self.start = datetime(2023, 11, 1, 0, 0, tzinfo=UTC)
        rows = ["timestamp,open,high,low,close"]
        for index in range(8):
            timestamp = self.start + timedelta(seconds=self.timeframe * index)
            rows.append(f"{timestamp.isoformat()},2000,2002,1998,2001")
        self.csv_bytes = ("\n".join(rows) + "\n").encode("utf-8")
        evaluation_time = self.start + timedelta(seconds=self.timeframe * 8)
        _, manifest, validation = load_xauusd_csv_snapshot_bytes(
            self.csv_bytes,
            source_name="Broker A",
            source_symbol="XAUUSD.a",
            timeframe_seconds=self.timeframe,
            evaluation_time=evaluation_time,
            source_file_name="fixture.csv",
        )
        self.canonical_path = self.root / "fixture.csv"
        self.canonical_path.write_bytes(self.csv_bytes)
        self.verified = VerifiedPersistedMT5Snapshot(
            manifest_path=self.root / "manifest.json",
            store_root=self.root,
            raw_source_path=self.root / "source.mt5.txt",
            canonical_snapshot_path=self.canonical_path,
            source_sha256="a" * 64,
            normalized_sha256=manifest.sha256,
            snapshot=manifest,
            validation=validation,
        )
        self.candidate = ReplayCandidate(
            candidate_id="RC-TEST",
            source_id="source-uuid",
            locator="primary-source#sequence:test",
            state=ReplayCandidateState.RAW_DATA_BLOCKED,
            sequence_evidence="explicit source sequence",
            blocker="needs immutable alignment and stage times",
        )
        self.alignment = SourceChartAlignmentResult(
            state=SourceChartAlignmentState.ALIGNED_CANDIDATE,
            source_id=self.candidate.source_id,
            source_locator=self.candidate.locator,
            snapshot_id=manifest.snapshot_id,
            aligned=True,
            reason="fixture alignment",
        )
        self.artifact_path = self.root / "stage-certification.json"

    def _valid_payload(self) -> dict[str, object]:
        stages = []
        for index, stage in enumerate(BacktestStage):
            bar_open = self.start + timedelta(seconds=self.timeframe * index)
            stages.append(
                {
                    "stage": stage.name,
                    "occurred_at": (bar_open + timedelta(minutes=5)).isoformat(),
                    "available_at": (bar_open + timedelta(seconds=self.timeframe)).isoformat(),
                    "broker_bar_open": bar_open.isoformat(),
                    "source_ref": f"{self.candidate.locator}#stage:{stage.name}",
                    "evidence_kind": "primary_source_label_aligned_to_closed_broker_bar",
                }
            )
        return {
            "schema_version": "r143_stage_timestamp_certification_v1",
            "candidate_id": self.candidate.candidate_id,
            "source_id": self.candidate.source_id,
            "source_locator": self.candidate.locator,
            "snapshot_id": self.verified.snapshot.snapshot_id,
            "normalized_sha256": self.verified.normalized_sha256,
            "broker_name": self.verified.snapshot.source_name,
            "broker_symbol": self.verified.snapshot.source_symbol,
            "canonical_symbol": "XAUUSD",
            "timeframe_seconds": self.timeframe,
            "stages": stages,
            "promotion_allowed": False,
            "strategy_verified": False,
            "performance_claim_allowed": False,
        }

    def _write(self, payload: dict[str, object]) -> None:
        self.artifact_path.write_text(
            json.dumps(payload, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )

    def _load(self):
        return load_verified_replay_stage_certification(
            self.artifact_path,
            candidate=self.candidate,
            snapshot=self.verified,
            alignment=self.alignment,
        )

    def test_exact_six_stage_closed_bar_mapping_is_admissible(self) -> None:
        self._write(self._valid_payload())
        result = self._load()
        self.assertTrue(result.stage_timestamps_certified)
        self.assertEqual(len(result.confirmations), 6)
        self.assertEqual(tuple(item.stage for item in result.confirmations), tuple(BacktestStage))
        self.assertFalse(result.promotion_allowed)
        self.assertFalse(result.strategy_verified)
        self.assertFalse(result.performance_claim_allowed)
        self.assertEqual(len(result.artifact_sha256), 64)

    def test_missing_stage_is_rejected(self) -> None:
        payload = self._valid_payload()
        payload["stages"] = list(payload["stages"])[:-1]
        self._write(payload)
        with self.assertRaisesRegex(ReplayStageCertificationError, "exactly all six"):
            self._load()

    def test_duplicate_or_wrong_stage_order_is_rejected(self) -> None:
        payload = self._valid_payload()
        stages = list(payload["stages"])
        stages[2] = dict(stages[1])
        payload["stages"] = stages
        self._write(payload)
        with self.assertRaisesRegex(ReplayStageCertificationError, "canonical R-143 order"):
            self._load()

    def test_naive_timestamp_is_rejected(self) -> None:
        payload = self._valid_payload()
        stages = list(payload["stages"])
        stages[0] = dict(stages[0])
        stages[0]["occurred_at"] = "2023-11-01T00:05:00"
        payload["stages"] = stages
        self._write(payload)
        with self.assertRaisesRegex(ReplayStageCertificationError, "timezone-aware"):
            self._load()

    def test_evidence_cannot_be_available_before_referenced_bar_close(self) -> None:
        payload = self._valid_payload()
        stages = list(payload["stages"])
        stages[0] = dict(stages[0])
        stages[0]["available_at"] = (self.start + timedelta(minutes=6)).isoformat()
        payload["stages"] = stages
        self._write(payload)
        with self.assertRaisesRegex(ReplayStageCertificationError, "precedes the referenced broker bar close"):
            self._load()

    def test_snapshot_identity_mismatch_is_rejected(self) -> None:
        payload = self._valid_payload()
        payload["snapshot_id"] = "sha256:" + "f" * 64
        self._write(payload)
        with self.assertRaisesRegex(ReplayStageCertificationError, "snapshot_id"):
            self._load()

    def test_stage_time_order_cannot_run_backwards(self) -> None:
        payload = self._valid_payload()
        stages = list(payload["stages"])
        stages[4] = dict(stages[4])
        # Keep the evidence on a real closed broker bar but move stage 5 behind
        # stage 4 in time. The loader must reject this source-order regression.
        old_bar = self.start + timedelta(seconds=self.timeframe * 2)
        stages[4]["broker_bar_open"] = old_bar.isoformat()
        stages[4]["occurred_at"] = (old_bar + timedelta(minutes=5)).isoformat()
        stages[4]["available_at"] = (old_bar + timedelta(seconds=self.timeframe)).isoformat()
        payload["stages"] = stages
        self._write(payload)
        with self.assertRaisesRegex(ReplayStageCertificationError, "out of canonical stage order"):
            self._load()

    def test_context_only_candidate_can_never_be_unlocked(self) -> None:
        self._write(self._valid_payload())
        context_only = replace(self.candidate, state=ReplayCandidateState.CONTEXT_ONLY)
        with self.assertRaisesRegex(ReplayStageCertificationError, "context-only"):
            load_verified_replay_stage_certification(
                self.artifact_path,
                candidate=context_only,
                snapshot=self.verified,
                alignment=self.alignment,
            )

    def test_claim_flags_cannot_be_set_true(self) -> None:
        payload = self._valid_payload()
        payload["strategy_verified"] = True
        self._write(payload)
        with self.assertRaisesRegex(ReplayStageCertificationError, "cannot claim strategy verification"):
            self._load()


if __name__ == "__main__":
    unittest.main()
