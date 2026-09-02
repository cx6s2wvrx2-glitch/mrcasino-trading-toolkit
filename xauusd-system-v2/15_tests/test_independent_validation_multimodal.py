from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xauusd_v2.agents.base import AgentContractError
from xauusd_v2.agents.validation_agent import IndependentValidationAgent
from xauusd_v2.primary_context_payload import PrimaryContextPayload, PrimaryImageEvidence


class FakeMultimodalClient:
    def __init__(self) -> None:
        self.last_system = ""
        self.last_user = ""
        self.last_images = ()

    def generate_json(self, *, system: str, user: str):
        self.last_system = system
        self.last_user = user
        return {
            "predicted_label": "label_a",
            "confidence": 0.7,
            "evidence": ["primary text"],
            "ambiguities": [],
        }

    def generate_json_multimodal(self, *, system: str, user: str, images):
        self.last_system = system
        self.last_user = user
        self.last_images = images
        return {
            "predicted_label": "label_b",
            "confidence": 0.8,
            "evidence": ["primary chart"],
            "ambiguities": [],
        }


class TextOnlyClient:
    def generate_json(self, *, system: str, user: str):
        return {
            "predicted_label": "label_a",
            "confidence": 0.5,
            "evidence": [],
            "ambiguities": [],
        }


class IndependentValidationMultimodalTests(unittest.TestCase):
    def _image_payload(self):
        temp = tempfile.TemporaryDirectory()
        path = Path(temp.name) / "chart.png"
        path.write_bytes(b"chart-primary-evidence")
        image = PrimaryImageEvidence.from_path(path, mime_type="image/png")
        return temp, PrimaryContextPayload(text="original annotation", images=(image,))

    def test_actual_primary_image_is_passed_out_of_band_without_expected_answer(self) -> None:
        temp, payload = self._image_payload()
        self.addCleanup(temp.cleanup)
        client = FakeMultimodalClient()
        agent = IndependentValidationAgent(client)
        decision, result = agent.validate_multimodal(
            vector_id="GT-X-001",
            source_locator="primary#image:chart.png",
            source_context=payload,
            allowed_labels=("label_a", "label_b"),
        )
        self.assertEqual(decision.predicted_label, "label_b")
        self.assertEqual(len(client.last_images), 1)
        self.assertIn("original annotation", client.last_user)
        self.assertNotIn("expected_label", client.last_user)
        self.assertNotIn("expected_class", client.last_user)
        self.assertEqual(result.agent_version, "0.3.0")

    def test_text_only_payload_uses_existing_text_path(self) -> None:
        client = FakeMultimodalClient()
        agent = IndependentValidationAgent(client)
        decision, _ = agent.validate_multimodal(
            vector_id="GT-X-002",
            source_locator="primary#text:one",
            source_context=PrimaryContextPayload(text="primary words"),
            allowed_labels=("label_a", "label_b"),
        )
        self.assertEqual(decision.predicted_label, "label_a")
        self.assertEqual(client.last_images, ())

    def test_image_payload_fails_closed_with_text_only_client(self) -> None:
        temp, payload = self._image_payload()
        self.addCleanup(temp.cleanup)
        agent = IndependentValidationAgent(TextOnlyClient())
        with self.assertRaisesRegex(AgentContractError, "does not support primary images"):
            agent.validate_multimodal(
                vector_id="GT-X-003",
                source_locator="primary#image:chart.png",
                source_context=payload,
                allowed_labels=("label_a", "label_b"),
            )


if __name__ == "__main__":
    unittest.main()
