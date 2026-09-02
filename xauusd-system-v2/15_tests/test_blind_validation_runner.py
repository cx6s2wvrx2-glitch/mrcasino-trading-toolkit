from __future__ import annotations

import unittest

from xauusd_v2.agents.validation_agent import IndependentValidationAgent
from xauusd_v2.blind_validation_packet import BlindValidationCase, BlindValidationPacket
from xauusd_v2.blind_validation_runner import run_blind_validation_batch


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def generate_json(self, *, system: str, user: str) -> dict[str, object]:
        self.calls.append(user)
        return {
            "predicted_label": None,
            "confidence": 0.0,
            "evidence": [],
            "ambiguities": ["insufficient primary evidence"],
        }


class BlindValidationRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = RecordingClient()
        self.agent = IndependentValidationAgent(self.client)
        self.packet = BlindValidationPacket(
            dataset_name="test",
            taxonomy=("label_a", "label_b"),
            cases=(
                BlindValidationCase("V1", "source#1"),
                BlindValidationCase("V2", "source#2"),
            ),
        )

    def test_batch_runs_each_case_and_preserves_abstentions(self) -> None:
        result = run_blind_validation_batch(
            packet=self.packet,
            agent=self.agent,
            source_context_resolver=lambda locator: f"PRIMARY CONTEXT FOR {locator}",
        )
        self.assertEqual(result.predictions, {"V1": None, "V2": None})
        self.assertEqual(len(self.client.calls), 2)

    def test_prompt_contains_taxonomy_but_no_expected_answer_fields(self) -> None:
        run_blind_validation_batch(
            packet=self.packet,
            agent=self.agent,
            source_context_resolver=lambda locator: f"PRIMARY CONTEXT FOR {locator}",
        )
        for prompt in self.client.calls:
            lower = prompt.lower()
            self.assertIn("allowed label taxonomy", lower)
            self.assertNotIn("expected_label", lower)
            self.assertNotIn("expected_class", lower)
            self.assertNotIn("forbidden_inference", lower)

    def test_empty_source_context_fails_closed_before_model_call(self) -> None:
        with self.assertRaises(ValueError):
            run_blind_validation_batch(
                packet=self.packet,
                agent=self.agent,
                source_context_resolver=lambda locator: "" if locator == "source#1" else "context",
            )
        self.assertEqual(self.client.calls, [])


if __name__ == "__main__":
    unittest.main()
