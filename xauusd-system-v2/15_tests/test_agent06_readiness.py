from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.agent06_readiness import assess_agent06_readiness, locator_requires_primary_image
from xauusd_v2.blind_validation_packet import BlindValidationCase, BlindValidationPacket
from xauusd_v2.primary_context_bundle import FileSystemPrimaryContextBundleResolver


class MultimodalClient:
    def generate_json(self, *, system: str, user: str):
        return {}

    def generate_json_multimodal(self, *, system: str, user: str, images):
        return {}


class TextClient:
    def generate_json(self, *, system: str, user: str):
        return {}


class Agent06ReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "text").mkdir()
        (self.root / "images").mkdir()
        (self.root / "text" / "a.txt").write_text("primary words", encoding="utf-8")
        (self.root / "images" / "b.png").write_bytes(b"chart")
        self.packet = BlindValidationPacket(
            dataset_name="blind",
            taxonomy=("a", "b"),
            cases=(
                BlindValidationCase("GT-A", "source#text:a"),
                BlindValidationCase("GT-B", "source#image:b.png"),
            ),
        )

    def resolver(self, entries) -> FileSystemPrimaryContextBundleResolver:
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps({"version": 1, "entries": entries}), encoding="utf-8")
        return FileSystemPrimaryContextBundleResolver(bundle_root=self.root, manifest_path=manifest)

    def test_image_locator_detection_is_explicit(self) -> None:
        self.assertTrue(locator_requires_primary_image("source#image:x.png"))
        self.assertTrue(locator_requires_primary_image("source#visual:h1"))
        self.assertTrue(locator_requires_primary_image("notes.excalidraw#embedded:abc"))
        self.assertFalse(locator_requires_primary_image("source#text:abc"))

    def test_complete_bundle_and_multimodal_client_is_ready(self) -> None:
        resolver = self.resolver([
            {"source_locator": "source#text:a", "text_path": "text/a.txt"},
            {"source_locator": "source#image:b.png", "images": [{"path": "images/b.png", "mime_type": "image/png"}]},
        ])
        report = assess_agent06_readiness(
            packet=self.packet,
            resolver=resolver,
            model_client=MultimodalClient(),
            model_provider="provider-x",
            model_name="model-y",
        )
        self.assertTrue(report.ready_to_run)
        self.assertEqual(report.total_cases, 2)
        self.assertEqual(report.resolved_cases, 2)
        self.assertEqual(report.image_required_cases, 1)
        self.assertEqual(report.blockers, ())

    def test_missing_locator_is_reported_not_silently_skipped(self) -> None:
        resolver = self.resolver([
            {"source_locator": "source#text:a", "text_path": "text/a.txt"},
        ])
        report = assess_agent06_readiness(
            packet=self.packet,
            resolver=resolver,
            model_client=MultimodalClient(),
            model_provider="provider",
            model_name="model",
        )
        self.assertFalse(report.ready_to_run)
        self.assertEqual(report.missing_locators, ("source#image:b.png",))
        self.assertIn("missing primary bundle locators: 1", report.blockers)

    def test_chart_locator_with_text_only_evidence_is_blocked(self) -> None:
        resolver = self.resolver([
            {"source_locator": "source#text:a", "text_path": "text/a.txt"},
            {"source_locator": "source#image:b.png", "text_path": "text/a.txt"},
        ])
        report = assess_agent06_readiness(
            packet=self.packet,
            resolver=resolver,
            model_client=MultimodalClient(),
            model_provider="provider",
            model_name="model",
        )
        self.assertFalse(report.ready_to_run)
        self.assertEqual(report.image_missing_locators, ("source#image:b.png",))

    def test_text_only_client_cannot_run_image_corpus(self) -> None:
        resolver = self.resolver([
            {"source_locator": "source#text:a", "text_path": "text/a.txt"},
            {"source_locator": "source#image:b.png", "images": [{"path": "images/b.png", "mime_type": "image/png"}]},
        ])
        report = assess_agent06_readiness(
            packet=self.packet,
            resolver=resolver,
            model_client=TextClient(),
            model_provider="provider",
            model_name="model",
        )
        self.assertFalse(report.ready_to_run)
        self.assertIn("configured model client is not multimodal-capable", report.blockers)

    def test_missing_provider_or_model_metadata_blocks_run(self) -> None:
        resolver = self.resolver([
            {"source_locator": "source#text:a", "text_path": "text/a.txt"},
            {"source_locator": "source#image:b.png", "images": [{"path": "images/b.png", "mime_type": "image/png"}]},
        ])
        report = assess_agent06_readiness(
            packet=self.packet,
            resolver=resolver,
            model_client=MultimodalClient(),
            model_provider="",
            model_name="",
        )
        self.assertFalse(report.ready_to_run)
        self.assertIn("model provider metadata is missing", report.blockers)
        self.assertIn("model name metadata is missing", report.blockers)


if __name__ == "__main__":
    unittest.main()
