from __future__ import annotations

import json

from ..models import AgentRunResult, KnowledgeClaim, RuleStatus, StrategyRuleDraft
from .base import AgentContractError, StructuredModelClient
from .prompts import RULES_AGENT_SYSTEM


class RulesAgent:
    name = "rules_agent_02"
    version = "0.1.0"

    def __init__(self, client: StructuredModelClient) -> None:
        self.client = client

    def formalize(self, *, claims: list[KnowledgeClaim]) -> tuple[list[StrategyRuleDraft], AgentRunResult]:
        if not claims:
            raise AgentContractError("At least one knowledge claim is required")
        source_ids = {claim.source.source_id for claim in claims}
        if len(source_ids) != 1:
            raise AgentContractError("V0.1 formalization accepts one source at a time to preserve provenance")

        serializable = [
            {
                "claim_type": c.claim_type,
                "content": c.content,
                "locator": c.source.locator,
                "confidence": c.confidence,
                "ambiguities": list(c.ambiguities),
                "evidence": list(c.evidence),
            }
            for c in claims
        ]
        raw = self.client.generate_json(system=RULES_AGENT_SYSTEM, user=json.dumps(serializable, ensure_ascii=False))
        items = raw.get("rules", [])
        if not isinstance(items, list):
            raise AgentContractError("Model output must contain a rules list")

        base_source = claims[0].source
        rules: list[StrategyRuleDraft] = []
        for item in items:
            if not isinstance(item, dict):
                raise AgentContractError("Each rule must be an object")
            status = str(item.get("status", "draft")).lower()
            if status != RuleStatus.DRAFT.value:
                raise AgentContractError("AI is not allowed to promote a rule beyond DRAFT")
            locator = str(item.get("source_locator") or base_source.locator)
            scoped_source = type(base_source)(
                source_id=base_source.source_id,
                title=base_source.title,
                source_type=base_source.source_type,
                locator=locator,
                approved_by_user=True,
            )
            rules.append(
                StrategyRuleDraft(
                    rule_code=str(item.get("rule_code", "")).strip(),
                    title=str(item.get("title", "")).strip(),
                    description=str(item.get("description", "")).strip(),
                    source=scoped_source,
                    conditions=dict(item.get("conditions") or {}),
                    action=dict(item.get("action") or {}),
                    invalidation=dict(item.get("invalidation") or {}),
                    unresolved=tuple(str(x) for x in item.get("unresolved", [])),
                    status=RuleStatus.DRAFT,
                )
            )

        result = AgentRunResult(
            agent_name=self.name,
            agent_version=self.version,
            input_refs=tuple(sorted(source_ids)),
            payload=raw,
            needs_review=True,
        )
        return rules, result
