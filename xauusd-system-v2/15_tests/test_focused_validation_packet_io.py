from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.focused_validation_packet import (
    FOCUSED_VERDICT_TAXONOMY,
    FocusedValidationCase,
    FocusedValidationPacket,
    focused_packet_sha256,
)
from xauusd_v2.focused_validation_packet_io import load_focused_packet, write_focused_packet


class FocusedValidationPacketIOTests(unittest.TestCase):
    def test_focused_packet_round_trips_without_answer_metadata(self) -> None:
        packet = FocusedValidationPacket(
            dataset_name="focused",
            cases=(
                FocusedValidationCase(
                    vector_id="GT-X-001",
                    source_locator="source#image:1",
                    candidate_claim="candidate_claim_one",
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "focused.json"
            write_focused_packet(packet, path)
            raw = json.loads(path.read_text(encoding="utf-8"))
            loaded = load_focused_packet(path)
        self.assertEqual(loaded, packet)
        self.assertEqual(raw["protocol"], "agent06_focused_claim_adjudication_v2")
        self.assertEqual(tuple(raw["verdict_taxonomy"]), FOCUSED_VERDICT_TAXONOMY)
        self.assertEqual(raw["cases"][0]["candidate_claim"], "candidate_claim_one")
        self.assertNotIn("expected_verdict", json.dumps(raw))
        self.assertNotIn("evidence", json.dumps(raw))

    def test_candidate_claim_changes_packet_identity(self) -> None:
        first = FocusedValidationPacket(
            dataset_name="focused",
            cases=(FocusedValidationCase("V1", "source#1", "claim_one"),),
        )
        second = FocusedValidationPacket(
            dataset_name="focused",
            cases=(FocusedValidationCase("V1", "source#1", "claim_two"),),
        )
        self.assertNotEqual(focused_packet_sha256(first), focused_packet_sha256(second))

    def test_answer_metadata_is_rejected(self) -> None:
        payload = {
            "version": 1,
            "protocol": "agent06_focused_claim_adjudication_v2",
            "dataset_name": "focused",
            "verdict_taxonomy": list(FOCUSED_VERDICT_TAXONOMY),
            "cases": [
                {
                    "vector_id": "V1",
                    "source_locator": "source#1",
                    "candidate_claim": "claim_one",
                    "expected_verdict": "SUPPORTED",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "focused.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "forbidden answer field"):
                load_focused_packet(path)


if __name__ == "__main__":
    unittest.main()
