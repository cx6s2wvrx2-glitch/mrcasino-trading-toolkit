from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.blind_validation_packet import BlindValidationCase, BlindValidationPacket
from xauusd_v2.blind_validation_packet_io import load_blind_packet, write_blind_packet


class BlindValidationPacketIOTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def packet(self) -> BlindValidationPacket:
        return BlindValidationPacket(
            dataset_name="blind",
            taxonomy=("label_a", "label_b"),
            cases=(
                BlindValidationCase(vector_id="GT-A", source_locator="source#a"),
                BlindValidationCase(vector_id="GT-B", source_locator="source#b"),
            ),
        )

    def test_round_trip_preserves_only_blind_fields(self) -> None:
        path = self.root / "packet.json"
        write_blind_packet(self.packet(), path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(set(raw), {"version", "dataset_name", "taxonomy", "cases"})
        self.assertEqual(set(raw["cases"][0]), {"vector_id", "source_locator"})
        self.assertEqual(load_blind_packet(path), self.packet())

    def test_answer_field_anywhere_is_rejected(self) -> None:
        path = self.root / "bad.json"
        path.write_text(
            json.dumps({
                "version": 1,
                "dataset_name": "blind",
                "taxonomy": ["a", "b"],
                "cases": [{
                    "vector_id": "GT-A",
                    "source_locator": "source#a",
                    "expected_label": "a",
                }],
            }),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "forbidden answer field"):
            load_blind_packet(path)

    def test_extra_case_field_is_rejected(self) -> None:
        path = self.root / "bad.json"
        path.write_text(
            json.dumps({
                "version": 1,
                "dataset_name": "blind",
                "taxonomy": ["a", "b"],
                "cases": [{"vector_id": "GT-A", "source_locator": "source#a", "note": "x"}],
            }),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "case schema mismatch"):
            load_blind_packet(path)

    def test_duplicate_vector_ids_are_rejected(self) -> None:
        path = self.root / "bad.json"
        path.write_text(
            json.dumps({
                "version": 1,
                "dataset_name": "blind",
                "taxonomy": ["a", "b"],
                "cases": [
                    {"vector_id": "GT-A", "source_locator": "source#a"},
                    {"vector_id": "GT-A", "source_locator": "source#b"},
                ],
            }),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "duplicate blind packet vector id"):
            load_blind_packet(path)


if __name__ == "__main__":
    unittest.main()
