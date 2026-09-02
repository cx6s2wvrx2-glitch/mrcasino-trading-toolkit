from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.mt5_history_cli import main


RAW = (
    "<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\n"
    "2026.09.01\t10:00:00\t2500.0\t2501.0\t2499.5\t2500.5\n"
    "2026.09.01\t10:01:00\t2500.5\t2502.0\t2500.0\t2501.5\n"
)


class MT5HistoryCliTests(unittest.TestCase):
    def args(self, source: Path, store: Path) -> list[str]:
        return [
            str(source),
            "--broker-name",
            "Broker A",
            "--broker-symbol",
            "XAUUSD.a",
            "--source-timezone",
            "UTC",
            "--timeframe-seconds",
            "60",
            "--evaluation-time",
            "2026-09-01T10:03:00Z",
            "--store-root",
            str(store),
        ]

    def dry_run_args(self, source: Path) -> list[str]:
        return [
            str(source),
            "--broker-name",
            "Broker A",
            "--broker-symbol",
            "XAUUSD.a",
            "--source-timezone",
            "UTC",
            "--timeframe-seconds",
            "60",
            "--evaluation-time",
            "2026-09-01T10:03:00Z",
            "--dry-run",
        ]

    def test_cli_persists_valid_export_and_returns_audit_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "history.tsv"
            store = root / "store"
            source.write_text(RAW, encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(self.args(source, store))
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["status"], "PERSISTED")
            self.assertTrue(payload["persisted"])
            self.assertEqual(payload["canonical_symbol"], "XAUUSD")
            self.assertEqual(payload["bar_count"], 2)
            self.assertTrue(payload["closed_only"])
            self.assertTrue(Path(payload["raw_source_path"]).is_file())
            self.assertTrue(Path(payload["canonical_snapshot_path"]).is_file())
            self.assertTrue(Path(payload["ingestion_manifest_path"]).is_file())

    def test_cli_dry_run_validates_and_fingerprints_without_persisting(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "history.tsv"
            source.write_text(RAW, encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(self.dry_run_args(source))
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["status"], "VALIDATED_NOT_PERSISTED")
            self.assertFalse(payload["persisted"])
            self.assertEqual(payload["bar_count"], 2)
            self.assertEqual(payload["gap_count"], 0)
            self.assertTrue(payload["closed_only"])
            self.assertEqual(payload["first_timestamp_utc"], "2026-09-01T10:00:00+00:00")
            self.assertEqual(payload["last_timestamp_utc"], "2026-09-01T10:01:00+00:00")
            self.assertEqual(len(payload["source_sha256"]), 64)
            self.assertEqual(len(payload["normalized_sha256"]), 64)
            self.assertNotIn("raw_source_path", payload)
            self.assertNotIn("canonical_snapshot_path", payload)
            self.assertNotIn("ingestion_manifest_path", payload)
            self.assertEqual(list(root.iterdir()), [source])

    def test_cli_persist_mode_requires_store_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "history.tsv"
            source.write_text(RAW, encoding="utf-8")
            args = self.dry_run_args(source)
            args.remove("--dry-run")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(args)
            self.assertEqual(code, 2)
            payload = json.loads(stderr.getvalue())
            self.assertEqual(payload["status"], "BLOCKED")
            self.assertIn("--store-root", payload["error"])
            self.assertEqual(list(root.iterdir()), [source])

    def test_cli_missing_file_fails_closed_without_store(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = root / "store"
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(self.args(root / "missing.tsv", store))
            self.assertEqual(code, 2)
            payload = json.loads(stderr.getvalue())
            self.assertEqual(payload["status"], "BLOCKED")
            self.assertFalse(store.exists())

    def test_cli_invalid_history_fails_closed_without_persisting(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "bad.tsv"
            store = root / "store"
            source.write_text("not an MT5 export\n", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main(self.args(source, store))
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(stderr.getvalue())["status"], "BLOCKED")
            self.assertFalse(store.exists())

    def test_cli_provisional_final_bar_is_persisted_but_marked_not_closed_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "history.tsv"
            store = root / "store"
            source.write_text(RAW, encoding="utf-8")
            args = self.args(source, store)
            index = args.index("--evaluation-time") + 1
            args[index] = "2026-09-01T10:01:30Z"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(args)
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["closed_only"])


if __name__ == "__main__":
    unittest.main()
