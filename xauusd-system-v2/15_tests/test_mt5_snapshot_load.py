from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from xauusd_v2.mt5_history import load_mt5_xauusd_history_bytes
from xauusd_v2.mt5_snapshot_load import (
    MT5SnapshotLoadError,
    load_verified_persisted_mt5_snapshot,
)
from xauusd_v2.mt5_snapshot_store import persist_mt5_ingestion


RAW = (
    "<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<SPREAD>\n"
    "2026.09.01\t10:00:00\t2500.0\t2501.0\t2499.5\t2500.5\t100\t20\n"
    "2026.09.01\t10:01:00\t2500.5\t2502.0\t2500.0\t2501.5\t120\t18\n"
).encode("utf-8")


class MT5SnapshotLoadTests(unittest.TestCase):
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
        persisted = persist_mt5_ingestion(
            raw_source_bytes=RAW,
            result=result,
            store_root=root,
        )
        return result, persisted

    def test_round_trip_rehashes_and_reloads_persisted_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result, persisted = self.persist(Path(temp))
            verified = load_verified_persisted_mt5_snapshot(persisted.ingestion_manifest_path)
            self.assertEqual(verified.snapshot, result.snapshot)
            self.assertEqual(verified.validation, result.validation)
            self.assertEqual(verified.raw_source_path.read_bytes(), RAW)
            self.assertEqual(
                verified.canonical_snapshot_path.read_bytes(),
                result.canonical_csv_bytes,
            )

    def test_tampered_raw_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            _, persisted = self.persist(Path(temp))
            persisted.raw_source_path.write_bytes(RAW + b"tampered")
            with self.assertRaisesRegex(MT5SnapshotLoadError, "raw MT5 source SHA-256"):
                load_verified_persisted_mt5_snapshot(persisted.ingestion_manifest_path)

    def test_tampered_canonical_snapshot_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            _, persisted = self.persist(Path(temp))
            persisted.canonical_snapshot_path.write_bytes(
                persisted.canonical_snapshot_path.read_bytes() + b"tampered"
            )
            with self.assertRaisesRegex(MT5SnapshotLoadError, "canonical snapshot SHA-256"):
                load_verified_persisted_mt5_snapshot(persisted.ingestion_manifest_path)

    def test_noncanonical_reference_is_rejected_before_path_use(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            _, persisted = self.persist(Path(temp))
            manifest = json.loads(persisted.ingestion_manifest_path.read_text(encoding="utf-8"))
            manifest["raw_source_ref"] = "../../escape.txt"
            persisted.ingestion_manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(MT5SnapshotLoadError, "raw_source_ref"):
                load_verified_persisted_mt5_snapshot(persisted.ingestion_manifest_path)

    def test_snapshot_metadata_tampering_is_rejected_even_when_bytes_are_intact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            _, persisted = self.persist(Path(temp))
            manifest = json.loads(persisted.ingestion_manifest_path.read_text(encoding="utf-8"))
            manifest["snapshot"]["source_name"] = "Other Broker"
            persisted.ingestion_manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(MT5SnapshotLoadError, "broker_name disagrees"):
                load_verified_persisted_mt5_snapshot(persisted.ingestion_manifest_path)

    def test_extra_manifest_field_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            _, persisted = self.persist(Path(temp))
            manifest = json.loads(persisted.ingestion_manifest_path.read_text(encoding="utf-8"))
            manifest["unexpected"] = True
            persisted.ingestion_manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(MT5SnapshotLoadError, "schema mismatch"):
                load_verified_persisted_mt5_snapshot(persisted.ingestion_manifest_path)


if __name__ == "__main__":
    unittest.main()
