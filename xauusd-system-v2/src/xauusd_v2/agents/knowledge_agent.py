from __future__ import annotations

from typing import Any

from ..models import AgentRunResult, KnowledgeClaim, SourceRef, VerificationStatus
from .base import AgentContractError, StructuredModelClient
from .prompts import KNOWLEDGE_AGENT_SYSTEM


class KnowledgeAgent:
    name = "knowledge_agent_01"
    version = "0.1.0"

    def __init__(self, client: StructuredModelClient) -> None:
        self.client = client

    def analyze(self, *, source: SourceRef, source_text: str) -> tuple[list[KnowledgeClaim], AgentRunResult]:
        if not source.approved_by_user:
            raise AgentContractError("Source is not approved for XAUUSD V2")
        if not source_text.strip():
            raise AgentContractError("Source content is empty")

        raw = self.client.generate_json(
            system=KNOWLEDGE_AGENT_SYSTEM,
            user=f"SOURCE TITLE: {source.title}\nSOURCE LOCATOR BASE: {source.locator}\n\nCONTENT:\n{source_text}",
        )
        items = raw.get("claims", [])
        if not isinstance(items, list):
            raise AgentContractError("Model output must contain a claims list")

        claims: list[KnowledgeClaim] = []
        for item in items:
            if not isinstance(item, dict):
                raise AgentContractError("Each claim must be an object")
            locator = str(item.get("locator") or source.locator).strip()
            scoped_source = SourceRef(
                source_id=source.source_id,
                title=source.title,
                source_type=source.source_type,
                locator=locator,
                approved_by_user=True,
            )
            claims.append(
                KnowledgeClaim(
                    claim_type=str(item.get("claim_type", "unknown")),
                    content=str(item.get("content", "")).strip(),
                    source=scoped_source,
                    confidence=float(item.get("confidence", 0.0)),
                    status=VerificationStatus.UNVERIFIED,
                    ambiguities=tuple(str(x) for x in item.get("ambiguities", [])),
                    evidence=tuple(str(x) for x in item.get("evidence", [])),
                )
            )

        result = AgentRunResult(
            agent_name=self.name,
            agent_version=self.version,
            input_refs=(source.source_id,),
            payload=raw,
            needs_review=True,
        )
        return claims, result
