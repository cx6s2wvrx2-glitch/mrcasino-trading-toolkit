from __future__ import annotations

import unittest

from xauusd_v2.agents.base import AgentContractError
from xauusd_v2.agents.validation_agent import IndependentValidationAgent


class FakeClient:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.last_system: str | None = None
        self.last_user: str | None = None

    def generate_json(self, *, system: str, user: str) -> dict:
        self.last_system = system
        self.last_user = user
        return self.payload


class IndependentValidationAgentTests(unittest.TestCase):
    def test_blind_contract_has_no_expected_label_input(self) -> None:
        client = FakeClient(
            {
                "predicted_label": "ts_established",
                "confidence": 0.91,
                "evidence": ["10m TS established"],
                "ambiguities": [],
            }
        )
        agent = IndependentValidationAgent(client)

        decision, run = agent.validate(
            vector_id="GT-R02-001",
            source_locator="primary chart A",
            source_context="The chart states 10m TS established after the LTF sequence.",
            allowed_labels=("ts_established", "ts_not_established", "no_trade"),
        )

        self.assertEqual(decision.predicted_label, "ts_established")
        self.assertFalse(decision.abstained)
        self.assertTrue(run.needs_review)
        self.assertNotIn("expected_label", client.last_user or "")
        self.assertNotIn("candidate_label", client.last_user or "")

    def test_abstain_is_allowed_and_fail_closed(self) -> None:
        client = FakeClient(
            {
                "predicted_label": None,
                "confidence": 0.35,
                "evidence": ["mixed evidence"],
                "ambiguities": ["The source does not establish whether the TS was confirmed."],
            }
        )
        agent = IndependentValidationAgent(client)

        decision, _ = agent.validate(
            vector_id="GT-R02-002",
            source_locator="primary chart B",
            source_context="The chart is inconclusive about establishment.",
            allowed_labels=("ts_established", "ts_not_established"),
        )

        self.assertTrue(decision.abstained)
        self.assertIsNone(decision.predicted_label)
        self.assertTrue(decision.ambiguities)

    def test_unknown_label_is_rejected(self) -> None:
        client = FakeClient(
            {
                "predicted_label": "invented_label",
                "confidence": 0.8,
                "evidence": ["x"],
                "ambiguities": [],
            }
        )
        agent = IndependentValidationAgent(client)

        with self.assertRaises(AgentContractError):
            agent.validate(
                vector_id="GT-R02-003",
                source_locator="primary chart C",
                source_context="Some source context.",
                allowed_labels=("valid", "invalid"),
            )

    def test_invalid_confidence_is_rejected(self) -> None:
        client = FakeClient(
            {
                "predicted_label": "valid",
                "confidence": 1.5,
                "evidence": ["x"],
                "ambiguities": [],
            }
        )
        agent = IndependentValidationAgent(client)

        with self.assertRaises(AgentContractError):
            agent.validate(
                vector_id="GT-R02-004",
                source_locator="primary chart D",
                source_context="Some source context.",
                allowed_labels=("valid", "invalid"),
            )

    def test_taxonomy_must_not_collapse_to_one_answer(self) -> None:
        client = FakeClient(
            {
                "predicted_label": "valid",
                "confidence": 0.9,
                "evidence": ["x"],
                "ambiguities": [],
            }
        )
        agent = IndependentValidationAgent(client)

        with self.assertRaises(AgentContractError):
            agent.validate(
                vector_id="GT-R02-005",
                source_locator="primary chart E",
                source_context="Some source context.",
                allowed_labels=("valid",),
            )


if __name__ == "__main__":
    unittest.main()
