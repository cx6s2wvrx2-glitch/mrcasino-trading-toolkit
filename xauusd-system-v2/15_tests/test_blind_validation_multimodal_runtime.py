from __future__ import annotations

import dataclasses
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.agents.validation_agent import IndependentValidationAgent
from xauusd_v2.blind_validation_multimodal_runtime import execute_multimodal_blind_validation_runtime
from xauusd_v2.blind_validation_packet import BlindValidationCase, BlindValidationPacket
from xauusd_v2.primary_context_payload import PrimaryContextPayload, PrimaryImageEvidence


class FakeClient:
    def generate_json(self, *, system: str, user: str):
        return {"predicted_label": "a", "confidence": 0.7, "evidence": [], "ambiguities": []}

    def generate_json_multimodal(self, *, system: str, user: str, images):
        return {"predicted_label": "b", "confidence": 0.8, "evidence": [], "ambiguities": []}


class MultimodalBlindValidationRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = Path(self.temp.name) / "chart.png"
        path.write_bytes(b"primary-chart")
        self.image = PrimaryImageEvidence.from_path(path, mime_type="image/png")
        self.packet = BlindValidationPacket(
            dataset_name="blind",
            taxonomy=("a", "b"),
            cases=(
                BlindValidationCase("GT-A", "source#text:a"),
                BlindValidationCase("GT-B", "source#image:b"),
            ),
        )
        self.agent = IndependentValidationAgent(FakeClient())

    def resolver(self, locator: str) -> PrimaryContextPayload:
        if locator.endswith("text:a"):
            return PrimaryContextPayload(text="primary words")
        return PrimaryContextPayload(images=(self.image,))

    def test_manifest_audits_text_and_image_hashes_without_file_paths(self) -> None:
        batch, manifest = execute_multimodal_blind_validation_runtime(
            run_id="run-1",
            model_provider="independent-provider",
            model_name="model-x",
            packet=self.packet,
            agent=self.agent,
            source_context_resolver=self.resolver,
        )
        self.assertEqual(len(batch.decisions), 2)
        self.assertEqual(manifest.case_count, 2)
        self.assertEqual(manifest.completed_count, 2)
        self.assertEqual(manifest.image_case_count, 1)
        self.assertFalse(manifest.promotion_allowed)
        image_audit = manifest.cases[1].images[0]
        self.assertEqual(image_audit.sha256, self.image.sha256)
        self.assertEqual(image_audit.size_bytes, self.image.size_bytes)
        self.assertNotIn("path", {field.name for field in dataclasses.fields(image_audit)})

    def test_empty_runtime_metadata_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            execute_multimodal_blind_validation_runtime(
                run_id="",
                model_provider="provider",
                model_name="model",
                packet=self.packet,
                agent=self.agent,
                source_context_resolver=self.resolver,
            )

    def test_mutated_primary_image_fails_before_model_call(self) -> None:
        Path(self.image.path).write_bytes(b"changed-chart")
        with self.assertRaises(ValueError):
            execute_multimodal_blind_validation_runtime(
                run_id="run-2",
                model_provider="provider",
                model_name="model",
                packet=self.packet,
                agent=self.agent,
                source_context_resolver=self.resolver,
            )


if __name__ == "__main__":
    unittest.main()
