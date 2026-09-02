from __future__ import annotations

import dataclasses
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from xauusd_v2.mt5_history import load_mt5_xauusd_history_bytes
from xauusd_v2.mt5_snapshot_store import MT5SnapshotStoreError, persist_mt5_ingestion


RAW = (
    "<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<SPREAD>\n"
    "2026.09.01\t10:00:00\t2500.0\t2501.0\t2499.5\t2500.5\t100\t20\n"
    "2026.09.01\t10:01:00\t2500.5\t2502.0\t2500.0\t2501.5\t120\t18\n"
).encode("utf-8")


class MT5SnapshotStoreTests(unittest.TestCase):
    def result(self):
        return load_mt5_xauusd_history_bytes(
            RAW,
            broker_name="Broker A",
            broker_symbol="XAUUSD.a",
            source_timezone="UTC",
            timeframe_seconds=60,
            evaluation_time=datetime(2026, 9, 1, 10, 3, tzinfo=timezone.utc),
            source_file_name="history.tsv",
        )

    def test_persists_raw_normalized_and_manifest_by_hash(self) -> None:
        result = self.result()
        with tempfile.TemporaryDirectory() as temp:
            persisted = persist_mt5_ingestion(
                raw_source_bytes=RAW,
                result=result,
                store_root=temp,
            )
            self.assertEqual(persisted.raw_source_path.read_bytes(), RAW)
            self.assertEqual(
                persisted.canonical_snapshot_path.read_bytes(), result.canonical_csv_bytes
            )
            self.assertIn(result.ingestion.source_sha256, str(persisted.raw_source_path))
            self.assertIn(result.ingestion.normalized_sha256, str(persisted.canonical_snapshot_path))

            manifest = json.loads(persisted.ingestion_manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_sha256"], result.ingestion.source_sha256)
            self.assertEqual(manifest["normalized_sha256"], result.ingestion.normalized_sha256)
            self.assertEqual(manifest["ingestion"]["source_file_name"], "history.tsv")
            self.assertEqual(manifest["validation"]["provisional_bars"], 0)

    def test_second_identical_persist_is_idempotent(self) -> None:
        result = self.result()
        with tempfile.TemporaryDirectory() as temp:
            first = persist_mt5_ingestion(raw_source_bytes=RAW, result=result, store_root=temp)
            second = persist_mt5_ingestion(raw_source_bytes=RAW, result=result, store_root=temp)
            self.assertEqual(first.raw_source_path, second.raw_source_path)
            self.assertEqual(first.canonical_snapshot_path, second.canonical_snapshot_path)
            self.assertEqual(first.ingestion_manifest_path, second.ingestion_manifest_path)

    def test_raw_source_hash_mismatch_is_rejected_before_write(self) -> None:
        result = self.result()
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(MT5SnapshotStoreError, "raw MT5 source hash"):
                persist_mt5_ingestion(
                    raw_source_bytes=RAW + b"tampered",
                    result=result,
                    store_root=temp,
                )
            self.assertFalse((Path(temp) / "raw").exists())

    def test_canonical_snapshot_hash_mismatch_is_rejected(self) -> None:
        result = self.result()
        mutated = dataclasses.replace(result, canonical_csv_bytes=result.canonical_csv_bytes + b"tampered")
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(MT5SnapshotStoreError, "canonical snapshot hash"):
                persist_mt5_ingestion(raw_source_bytes=RAW, result=mutated, store_root=temp)

    def test_existing_tampered_content_addressed_object_is_never_overwritten(self) -> None:
        result = self.result()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            expected = root / "snapshots" / result.ingestion.normalized_sha256 / "xauusd_ohlc.csv"
            expected.parent.mkdir(parents=True)
            expected.write_bytes(b"tampered")
            with self.assertRaisesRegex(MT5SnapshotStoreError, "tampering detected"):
                persist_mt5_ingestion(raw_source_bytes=RAW, result=result, store_root=root)
            self.assertEqual(expected.read_bytes(), b"tampered")

    def test_original_filename_cannot_control_store_path(self) -> None:
        result = dataclasses.replace(
            self.result(),
            ingestion=dataclasses.replace(self.result().ingestion, source_file_name="../../escape.tsv"),
        )
        with tempfile.TemporaryDirectory() as temp:
            persisted = persist_mt5_ingestion(raw_source_bytes=RAW, result=result, store_root=temp)
            self.assertTrue(persisted.raw_source_path.is_relative_to(Path(temp)))
            self.assertFalse((Path(temp).parent / "escape.tsv").exists())


if __name__ == "__main__":
    unittest.main()
