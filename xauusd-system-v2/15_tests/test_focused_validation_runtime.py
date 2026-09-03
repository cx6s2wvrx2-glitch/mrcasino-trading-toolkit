from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xauusd_v2.agents.validation_agent import IndependentValidationAgent
from xauusd_v2.blind_validation_multimodal_runtime import ResumableBlindCase
from xauusd_v2.focused_validation_packet import FocusedValidationCase, FocusedValidationPacket
from xauusd_v2.focused_validation_runtime import execute_focused_validation_runtime
from xauusd_v2.primary_context_payload import PrimaryContextPayload, PrimaryImageEvidence


class CapturingFocusedClient:
    def __init__(self) -> None:
        self.users: list[str] = []

    def generate_json_with_allowed_labels(self, *, system: str, user: str, allowed_labels):
        self.users.append(user)
        return {
            "predicted_label": "SUPPORTED",
            "confidence": 0.9,
            "evidence": ["direct source text"],
            "ambiguities": [],
        }

    def generate_json_multimodal_with_allowed_labels(
        self, *, system: str, user: str, images, allowed_labels
    ):
        self.users.append(user)
        return {
            "predicted_label": "INSUFFICIENT",
            "confidence": 0.6,
            "evidence": ["image is not exact enough"],
            "ambiguities": ["detail unclear"],
        }


class FocusedValidationRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        image_path = Path(self.temp.name) / "chart.png"
        image_path.write_bytes(b"focused-chart")
        self.image = PrimaryImageEvidence.from_path(image_path, mime_type="image/png")
        self.packet = FocusedValidationPacket(
            dataset_name="focused",
            cases=(
                FocusedValidationCase("GT-A", "source#text:a", "claim_a"),
                FocusedValidationCase("GT-B", "source#image:b", "claim_b"),
            ),
        )

    def resolver(self, locator: str) -> PrimaryContextPayload:
        if locator.endswith("text:a"):
            return PrimaryContextPayload(text="primary words")
        return PrimaryContextPayload(images=(self.image,))

    def test_candidate_claim_is_passed_as_question_and_manifest_is_non_promoting(self) -> None:
        client = CapturingFocusedClient()
        batch, manifest = execute_focused_validation_runtime(
            run_id="focus-run-1",
            model_provider="anthropic",
            model_name="claude-sonnet-5",
            packet=self.packet,
            agent=IndependentValidationAgent(client),
            source_context_resolver=self.resolver,
        )
        self.assertEqual([item.predicted_label for item in batch.decisions], ["SUPPORTED", "INSUFFICIENT"])
        self.assertEqual(manifest.case_count, 2)
        self.assertEqual(manifest.image_case_count, 1)
        self.assertFalse(manifest.promotion_allowed)
        self.assertIn("CANDIDATE CLAIM ID: claim_a", client.users[0])
        self.assertIn("CANDIDATE CLAIM ID: claim_b", client.users[1])
        self.assertNotIn("EXPECTED VERDICT", "\n".join(client.users).upper())

    def test_resume_reuses_completed_case_without_provider_recall(self) -> None:
        first_client = CapturingFocusedClient()
        first_batch, first_manifest = execute_focused_validation_runtime(
            run_id="focus-run-2",
            model_provider="anthropic",
            model_name="claude-sonnet-5",
            packet=self.packet,
            agent=IndependentValidationAgent(first_client),
            source_context_resolver=self.resolver,
        )
        resume = {
            "GT-A": ResumableBlindCase(
                decision=first_batch.decisions[0],
                audit=first_manifest.cases[0],
            )
        }
        second_client = CapturingFocusedClient()
        second_batch, _ = execute_focused_validation_runtime(
            run_id="focus-run-2",
            model_provider="anthropic",
            model_name="claude-sonnet-5",
            packet=self.packet,
            agent=IndependentValidationAgent(second_client),
            source_context_resolver=self.resolver,
            resume_cases=resume,
        )
        self.assertEqual(len(second_client.users), 1)
        self.assertIn("CANDIDATE CLAIM ID: claim_b", second_client.users[0])
        self.assertEqual(second_batch.decisions[0], first_batch.decisions[0])


if __name__ == "__main__":
    unittest.main()
