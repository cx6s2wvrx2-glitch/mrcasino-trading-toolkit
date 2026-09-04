from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from .phase3_research_frontier import (
    ResearchFrontierResult,
    find_first_broker_semantic_frontier,
    find_first_source_semantic_frontier,
)
from .phase3_stage_comparison import BrokerStageEvidenceRecord
from .strategy_evidence_sequence import StrategyEvidenceRecord


class EpisodeReadinessState(StrEnum):
    BLOCKED_SOURCE_SEMANTICS = "blocked_source_semantics"
    BLOCKED_BROKER_SEMANTICS = "blocked_broker_semantics"
    BLOCKED_REFERENCE_ALIGNMENT = "blocked_reference_alignment"
    READY_FOR_SEPARATE_CERTIFICATION_REVIEW = "ready_for_separate_certification_review"


@dataclass(frozen=True, slots=True)
class EpisodeReadinessResult:
    state: EpisodeReadinessState
    source_frontier: ResearchFrontierResult
    broker_frontier: ResearchFrontierResult
    reference_feed_aligned: bool
    canonical_sequence_ready: bool
    strategy_certified: bool
    performance_claim_allowed: bool
    promotion_allowed: bool
    live_execution_authorized: bool
    reason: str


def evaluate_phase3_episode_readiness(
    source_records: Iterable[StrategyEvidenceRecord],
    broker_records: Iterable[BrokerStageEvidenceRecord],
    *,
    reference_feed_aligned: bool,
) -> EpisodeReadinessResult:
    """Summarize one source episode without promoting any downstream authority.

    Source semantics, broker machine semantics and canonical reference alignment
    are independent gates. Completing this function's upstream gates would only
    make an episode ready for a separate certification review, never certify the
    strategy, performance, risk policy or live execution automatically.
    """
    source_records = tuple(source_records)
    broker_records = tuple(broker_records)
    source_frontier = find_first_source_semantic_frontier(source_records)
    broker_frontier = find_first_broker_semantic_frontier(broker_records)

    if source_frontier.stage is not None:
        state = EpisodeReadinessState.BLOCKED_SOURCE_SEMANTICS
        reason = f"first unresolved source stage: {source_frontier.stage.value}"
    elif broker_frontier.stage is not None:
        state = EpisodeReadinessState.BLOCKED_BROKER_SEMANTICS
        reason = f"first unresolved broker semantic stage: {broker_frontier.stage.value}"
    elif not reference_feed_aligned:
        state = EpisodeReadinessState.BLOCKED_REFERENCE_ALIGNMENT
        reason = "source and broker semantic layers are complete at this layer but FOREXCOM reference alignment is not complete"
    else:
        state = EpisodeReadinessState.READY_FOR_SEPARATE_CERTIFICATION_REVIEW
        reason = "upstream episode reconstruction gates are complete; separate certification review is still mandatory"

    canonical_ready = state is EpisodeReadinessState.READY_FOR_SEPARATE_CERTIFICATION_REVIEW
    return EpisodeReadinessResult(
        state=state,
        source_frontier=source_frontier,
        broker_frontier=broker_frontier,
        reference_feed_aligned=reference_feed_aligned,
        canonical_sequence_ready=canonical_ready,
        strategy_certified=False,
        performance_claim_allowed=False,
        promotion_allowed=False,
        live_execution_authorized=False,
        reason=reason,
    )


def render_episode_readiness_gr(result: EpisodeReadinessResult, *, title: str) -> str:
    source = result.source_frontier.stage.value if result.source_frontier.stage else "κανένα σε αυτό το layer"
    broker = result.broker_frontier.stage.value if result.broker_frontier.stage else "κανένα σε αυτό το layer"
    return "\n".join(
        [
            title,
            f"Κατάσταση: {result.state.value}",
            f"Πρώτο κενό πηγής: {source}",
            f"Πρώτο κενό broker semantics: {broker}",
            f"FOREXCOM alignment: {'ΝΑΙ' if result.reference_feed_aligned else 'ΟΧΙ'}",
            f"Canonical sequence ready: {'ΝΑΙ' if result.canonical_sequence_ready else 'ΟΧΙ'}",
            "Strategy certified: ΟΧΙ",
            "Performance claim allowed: ΟΧΙ",
            "Promotion allowed: ΟΧΙ",
            "Live execution: ΟΧΙ",
            f"Γιατί: {result.reason}",
        ]
    )
