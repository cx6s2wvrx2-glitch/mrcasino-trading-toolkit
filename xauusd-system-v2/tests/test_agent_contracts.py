import unittest

from xauusd_v2.agents.base import AgentContractError
from xauusd_v2.agents.knowledge_agent import KnowledgeAgent
from xauusd_v2.agents.rules_agent import RulesAgent
from xauusd_v2.models import KnowledgeClaim, SourceRef


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def generate_json(self, *, system: str, user: str):
        return self.payload


class AgentContractTests(unittest.TestCase):
    def setUp(self):
        self.source = SourceRef("SRC-001", "Approved lesson", "text", "page 1", True)

    def test_unapproved_source_is_rejected(self):
        bad = SourceRef("SRC-X", "Legacy", "text", "unknown", False)
        with self.assertRaises(AgentContractError):
            KnowledgeAgent(FakeClient({"claims": []})).analyze(source=bad, source_text="text")

    def test_knowledge_is_always_unverified(self):
        client = FakeClient({"claims": [{"claim_type": "definition", "content": "X means Y", "locator": "p.1", "confidence": 0.9, "evidence": ["X means Y"], "ambiguities": []}]})
        claims, _ = KnowledgeAgent(client).analyze(source=self.source, source_text="X means Y")
        self.assertEqual(claims[0].status.value, "unverified")

    def test_rules_agent_rejects_model_promotion(self):
        claim = KnowledgeClaim("rule", "If A then B", self.source, 0.9)
        client = FakeClient({"rules": [{"rule_code": "XAU-001", "title": "A", "description": "B", "status": "verified"}]})
        with self.assertRaises(AgentContractError):
            RulesAgent(client).formalize(claims=[claim])


if __name__ == "__main__":
    unittest.main()
