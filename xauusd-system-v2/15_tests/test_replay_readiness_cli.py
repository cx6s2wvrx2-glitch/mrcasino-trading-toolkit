from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from xauusd_v2.backtest_sequence import BacktestStage
from xauusd_v2.mt5_history import load_mt5_xauusd_history_bytes
from xauusd_v2.mt5_snapshot_load import load_verified_persisted_mt5_snapshot
from xauusd_v2.mt5_snapshot_store import persist_mt5_ingestion
from xauusd_v2.replay_candidate_registry import replay_candidates_by_id
from xauusd_v2.replay_readiness_cli import main


RAW = (
    "<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\n"
    "2026.09.01\t10:00:00\t2500.0\t2501.0\t2499.5\t2500.5\n"
    "2026.09.01\t10:01:00\t2500.5\t2502.0\t2500.0\t2501.5\n"
).encode("utf-8")


class ReplayReadinessCliTests(unittest.TestCase):
    def persist(self, root: Path):
        result = load_mt5_xauusd_history_bytes(
            RAW,
            broker_name="Broker A",
            broker_symbol="XAUUSD.a",
            source_timezone="UTC",
            timeframe_seconds=60,
            evaluation_time=datetime(2026, 9, 1, 10, 3, tzinfo=timezone.utc),
            source_file_name="history.tsv",
        )
        return persist_mt5_ingestion(raw_source_bytes=RAW, result=result, store_root=root)

    def args(self, manifest: Path, **overrides: str) -> list[str]:
        values = {
            "candidate_id": "RC-003",
            "broker_name": "Broker A",
            "source_symbol": "XAUUSD.a",
            "timeframe_seconds": "60",
            "window_start": "2026-09-01T10:00:00+00:00",
            "window_end": "2026-09-01T10:02:00+00:00",
        }
        stage_certification = overrides.pop("stage_certification", None)
        values.update(overrides)
        args = [
            "--candidate-id", values["candidate_id"],
            "--manifest", str(manifest),
            "--broker-name", values["broker_name"],
            "--source-symbol", values["source_symbol"],
            "--timeframe-seconds", values["timeframe_seconds"],
            "--window-start", values["window_start"],
            "--window-end", values["window_end"],
        ]
        if stage_certification is not None:
            args.extend(["--stage-certification", stage_certification])
        return args

    def write_stage_certification(self, manifest: Path, output: Path) -> None:
        verified = load_verified_persisted_mt5_snapshot(manifest)
        candidate = replay_candidates_by_id()["RC-003"]
        bar_open = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc)
        stages = [
            {
                "stage": stage.name,
                "occurred_at": "2026-09-01T10:00:30+00:00",
                "available_at": "2026-09-01T10:01:00+00:00",
                "broker_bar_open": bar_open.isoformat(),
                "source_ref": f"{candidate.locator}#stage:{stage.name}",
                "evidence_kind": "primary_source_label_aligned_to_closed_broker_bar",
            }
            for stage in BacktestStage
        ]
        payload = {
            "schema_version": "r143_stage_timestamp_certification_v1",
            "candidate_id": candidate.candidate_id,
            "source_id": candidate.source_id,
            "source_locator": candidate.locator,
            "snapshot_id": verified.snapshot.snapshot_id,
            "normalized_sha256": verified.normalized_sha256,
            "broker_name": verified.snapshot.source_name,
            "broker_symbol": verified.snapshot.source_symbol,
            "canonical_symbol": "XAUUSD",
            "timeframe_seconds": verified.snapshot.timeframe_seconds,
            "stages": stages,
            "promotion_allowed": False,
            "strategy_verified": False,
            "performance_claim_allowed": False,
        }
        output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    def test_exact_alignment_is_reported_but_stage_certification_stays_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            persisted = self.persist(Path(temp))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(self.args(persisted.ingestion_manifest_path))
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["aligned"])
            self.assertEqual(payload["alignment_state"], "aligned_candidate")
            self.assertEqual(payload["readiness_state"], "blocked_stage_timestamps")
            self.assertFalse(payload["replay_ready"])
            self.assertFalse(payload["promotion_allowed"])
            self.assertFalse(payload["strategy_verified"])
            self.assertFalse(payload["performance_claim_allowed"])
            self.assertIsNone(payload["stage_timestamp_certification_source"])
            self.assertIsNone(payload["stage_timestamp_certification_sha256"])
            self.assertEqual(payload["stage_confirmation_count"], 0)

    def test_exact_alignment_plus_valid_stage_artifact_reaches_replay_candidate_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            persisted = self.persist(root)
            stage_path = root / "r143-stage-cert.json"
            self.write_stage_certification(persisted.ingestion_manifest_path, stage_path)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    self.args(
                        persisted.ingestion_manifest_path,
                        stage_certification=str(stage_path),
                    )
                )
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["aligned"])
            self.assertTrue(payload["stage_timestamps_certified"])
            self.assertEqual(payload["stage_confirmation_count"], 6)
            self.assertEqual(payload["readiness_state"], "ready_candidate")
            self.assertTrue(payload["replay_ready"])
            self.assertEqual(len(payload["stage_timestamp_certification_sha256"]), 64)
            self.assertFalse(payload["promotion_allowed"])
            self.assertFalse(payload["strategy_verified"])
            self.assertFalse(payload["performance_claim_allowed"])

    def test_stage_artifact_snapshot_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            persisted = self.persist(root)
            stage_path = root / "r143-stage-cert.json"
            self.write_stage_certification(persisted.ingestion_manifest_path, stage_path)
            payload = json.loads(stage_path.read_text(encoding="utf-8"))
            payload["snapshot_id"] = "sha256:" + "f" * 64
            stage_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(
                    self.args(
                        persisted.ingestion_manifest_path,
                        stage_certification=str(stage_path),
                    )
                )
            self.assertEqual(code, 2)
            blocked = json.loads(stderr.getvalue())
            self.assertEqual(blocked["status"], "BLOCKED")
            self.assertIn("snapshot_id", blocked["error"])
            self.assertFalse(blocked["promotion_allowed"])

    def test_broker_mismatch_cannot_unlock_replay(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            persisted = self.persist(Path(temp))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(self.args(persisted.ingestion_manifest_path, broker_name="Other Broker"))
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["alignment_state"], "broker_mismatch")
            self.assertFalse(payload["aligned"])
            self.assertEqual(payload["readiness_state"], "blocked_alignment")
            self.assertFalse(payload["replay_ready"])

    def test_unknown_candidate_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            persisted = self.persist(Path(temp))
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(self.args(persisted.ingestion_manifest_path, candidate_id="RC-UNKNOWN"))
            self.assertEqual(code, 2)
            payload = json.loads(stderr.getvalue())
            self.assertEqual(payload["status"], "BLOCKED")
            self.assertFalse(payload["promotion_allowed"])

    def test_tampered_snapshot_store_fails_before_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            persisted = self.persist(Path(temp))
            persisted.canonical_snapshot_path.write_bytes(
                persisted.canonical_snapshot_path.read_bytes() + b"tampered"
            )
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(self.args(persisted.ingestion_manifest_path))
            self.assertEqual(code, 2)
            payload = json.loads(stderr.getvalue())
            self.assertEqual(payload["status"], "BLOCKED")
            self.assertIn("SHA-256 mismatch", payload["error"])
            self.assertFalse(payload["promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
