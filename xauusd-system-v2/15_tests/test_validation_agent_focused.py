from __future__ import annotations

import unittest

from xauusd_v2.agents.base import AgentContractError
from xauusd_v2.agents.validation_agent import IndependentValidationAgent


class _CapturingClient:
    def __init__(self) -> None:
        self.system = ""
        self.user = ""
        self.allowed_labels: tuple[str, ...] = ()

    def generate_json_with_allowed_labels(
        self, *, system: str, user: str, allowed_labels: tuple[str, ...]
    ) -> dict[str, object]:
        self.system = system
        self.user = user
        self.allowed_labels = allowed_labels
        return {
            "predicted_label": "SUPPORTED",
            "confidence": 0.91,
            "evidence": ["direct source annotation"],
            "ambiguities": [],
        }


class FocusedValidationAgentTests(unittest.TestCase):
    def test_focused_mode_exposes_question_but_not_expected_verdict(self) -> None:
        client = _CapturingClient()
        agent = IndependentValidationAgent(client)  # type: ignore[arg-type]
        decision, _ = agent.validate(
            vector_id="GT-R02-001",
            source_locator="source#1",
            source_context="Primary source text.",
            allowed_labels=("SUPPORTED", "CONTRADICTED", "INSUFFICIENT"),
            focus="no_entry_without_1m_ts_sequence",
        )
        self.assertEqual(decision.predicted_label, "SUPPORTED")
        self.assertEqual(
            client.allowed_labels,
            ("SUPPORTED", "CONTRADICTED", "INSUFFICIENT"),
        )
        self.assertIn("FOCUSED CLAIM ADJUDICATION", client.system)
        self.assertIn("ordinary evidentiary uncertainty belongs under INSUFFICIENT", client.system)
        self.assertNotIn("set predicted_label to null and explain the ambiguity", client.system)
        self.assertIn("CANDIDATE CLAIM ID: no_entry_without_1m_ts_sequence", client.user)
        self.assertIn("CANDIDATE CLAIM TEXT: no entry without 1m ts sequence", client.user)
        self.assertIn("SUPPORTED: the supplied primary source directly", client.user)
        self.assertIn("CONTRADICTED: the supplied primary source directly conflicts", client.user)
        self.assertIn("INSUFFICIENT: the source does not clearly establish", client.user)
        self.assertNotIn("EXPECTED VERDICT", client.user.upper())

    def test_focus_rejects_legacy_label_taxonomy(self) -> None:
        client = _CapturingClient()
        agent = IndependentValidationAgent(client)  # type: ignore[arg-type]
        with self.assertRaisesRegex(AgentContractError, "requires taxonomy"):
            agent.validate(
                vector_id="GT-R02-001",
                source_locator="source#1",
                source_context="Primary source text.",
                allowed_labels=("label_a", "label_b"),
                focus="candidate_claim",
            )


if __name__ == "__main__":
    unittest.main()
