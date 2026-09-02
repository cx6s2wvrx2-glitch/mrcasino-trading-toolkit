from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.primary_context_payload import PrimaryImageEvidence
from xauusd_v2.structured_model_clients import CommandModelClientConfig, CommandStructuredModelClient


class CommandStructuredModelClientMultimodalTests(unittest.TestCase):
    def test_multimodal_request_carries_hashed_primary_image_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.png"
            path.write_bytes(b"primary-image")
            image = PrimaryImageEvidence.from_path(path, mime_type="image/png")
            script = (
                "import json,sys; r=json.load(sys.stdin); i=r['images'][0]; "
                "print(json.dumps({'predicted_label':'label_a','confidence':0.9,"
                "'evidence':[i['mime_type'],i['sha256'],str(i['size_bytes']),i['path']],"
                "'ambiguities':[]}))"
            )
            client = CommandStructuredModelClient(
                CommandModelClientConfig.from_command((sys.executable, "-c", script))
            )
            payload = client.generate_json_multimodal(
                system="system",
                user="user",
                images=(image,),
            )
            self.assertEqual(payload["predicted_label"], "label_a")
            self.assertEqual(payload["evidence"][0], "image/png")
            self.assertEqual(payload["evidence"][1], image.sha256)
            self.assertEqual(payload["evidence"][2], str(image.size_bytes))
            self.assertEqual(payload["evidence"][3], image.path)

    def test_mutated_image_is_blocked_before_external_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.jpg"
            path.write_bytes(b"original")
            image = PrimaryImageEvidence.from_path(path, mime_type="image/jpeg")
            path.write_bytes(b"mutated")
            client = CommandStructuredModelClient(
                CommandModelClientConfig.from_command((sys.executable, "-c", "raise SystemExit(99)"))
            )
            with self.assertRaises(ValueError):
                client.generate_json_multimodal(system="system", user="user", images=(image,))


if __name__ == "__main__":
    unittest.main()
