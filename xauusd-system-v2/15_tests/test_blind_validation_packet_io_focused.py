from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.blind_validation_packet import BlindValidationCase, BlindValidationPacket
from xauusd_v2.blind_validation_packet_io import (
    blind_packet_payload,
    load_blind_packet,
    write_blind_packet,
)


class BlindValidationPacketIoFocusedTests(unittest.TestCase):
    def test_legacy_packet_serialization_stays_version_one_without_focus_key(self) -> None:
        packet = BlindValidationPacket(
            dataset_name="legacy",
            taxonomy=("A", "B"),
            cases=(BlindValidationCase(vector_id="V1", source_locator="source#1"),),
        )
        payload = blind_packet_payload(packet)
        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["cases"], [{"vector_id": "V1", "source_locator": "source#1"}])

    def test_focused_packet_round_trips_as_version_two(self) -> None:
        packet = BlindValidationPacket(
            dataset_name="focused",
            taxonomy=("SUPPORTED", "CONTRADICTED", "INSUFFICIENT"),
            cases=(
                BlindValidationCase(
                    vector_id="V1",
                    source_locator="source#1",
                    focus="candidate_claim_one",
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "packet.json"
            write_blind_packet(packet, path)
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(raw["version"], 2)
            self.assertEqual(raw["cases"][0]["focus"], "candidate_claim_one")
            loaded = load_blind_packet(path)
        self.assertEqual(loaded, packet)

    def test_mixed_focused_and_unfocused_cases_fail_closed(self) -> None:
        packet = BlindValidationPacket(
            dataset_name="mixed",
            taxonomy=("A", "B"),
            cases=(
                BlindValidationCase(vector_id="V1", source_locator="source#1", focus="claim"),
                BlindValidationCase(vector_id="V2", source_locator="source#2"),
            ),
        )
        with self.assertRaisesRegex(ValueError, "cannot mix focused and unfocused"):
            blind_packet_payload(packet)


if __name__ == "__main__":
    unittest.main()
