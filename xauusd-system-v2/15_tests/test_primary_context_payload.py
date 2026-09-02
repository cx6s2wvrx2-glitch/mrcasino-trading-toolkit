from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xauusd_v2.primary_context_payload import PrimaryContextPayload, PrimaryImageEvidence


class PrimaryContextPayloadTests(unittest.TestCase):
    def test_image_hash_and_size_are_content_addressed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.png"
            path.write_bytes(b"primary-chart-bytes")
            image = PrimaryImageEvidence.from_path(path, mime_type="image/png")
            self.assertEqual(image.size_bytes, len(b"primary-chart-bytes"))
            self.assertEqual(len(image.sha256), 64)
            image.verify()

    def test_mutated_image_fails_hash_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.jpg"
            path.write_bytes(b"original")
            image = PrimaryImageEvidence.from_path(path, mime_type="image/jpeg")
            path.write_bytes(b"changed!")
            with self.assertRaises(ValueError):
                image.verify()

    def test_non_image_mime_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chart.bin"
            path.write_bytes(b"x")
            with self.assertRaises(ValueError):
                PrimaryImageEvidence.from_path(path, mime_type="application/octet-stream")

    def test_empty_context_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PrimaryContextPayload().normalized()

    def test_text_only_primary_context_remains_supported(self) -> None:
        payload = PrimaryContextPayload(text="  original source words  ").normalized()
        self.assertEqual(payload.text, "original source words")
        self.assertEqual(payload.images, ())


if __name__ == "__main__":
    unittest.main()
