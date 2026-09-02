from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from xauusd_v2.mt5_history import load_mt5_xauusd_history_bytes
from xauusd_v2.mt5_snapshot_store import persist_mt5_ingestion
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
        values.update(overrides)
        return [
            "--candidate-id", values["candidate_id"],
            "--manifest", str(manifest),
            "--broker-name", values["broker_name"],
            "--source-symbol", values["source_symbol"],
            "--timeframe-seconds", values["timeframe_seconds"],
            "--window-start", values["window_start"],
            "--window-end", values["window_end"],
        ]

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
