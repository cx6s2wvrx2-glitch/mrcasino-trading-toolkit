from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class VerificationStatus(StrEnum):
    UNVERIFIED = "unverified"
    REVIEW = "review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    AMBIGUOUS = "ambiguous"


class RuleStatus(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class SourceRef:
    source_id: str
    title: str
    source_type: str
    locator: str
    approved_by_user: bool


@dataclass(frozen=True, slots=True)
class KnowledgeClaim:
    claim_type: str
    content: str
    source: SourceRef
    confidence: float
    status: VerificationStatus = VerificationStatus.UNVERIFIED
    ambiguities: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.source.approved_by_user:
            raise ValueError("V2 knowledge may only use user-approved sources")


@dataclass(frozen=True, slots=True)
class StrategyRuleDraft:
    rule_code: str
    title: str
    description: str
    source: SourceRef
    conditions: dict[str, Any] = field(default_factory=dict)
    action: dict[str, Any] = field(default_factory=dict)
    invalidation: dict[str, Any] = field(default_factory=dict)
    unresolved: tuple[str, ...] = ()
    version: int = 1
    status: RuleStatus = RuleStatus.DRAFT

    def __post_init__(self) -> None:
        if self.status is not RuleStatus.DRAFT:
            raise ValueError("AI-created rules must start as DRAFT")
        if not self.source.approved_by_user:
            raise ValueError("Rules may only originate from user-approved sources")


@dataclass(frozen=True, slots=True)
class AgentRunResult:
    agent_name: str
    agent_version: str
    input_refs: tuple[str, ...]
    payload: dict[str, Any]
    needs_review: bool = True
