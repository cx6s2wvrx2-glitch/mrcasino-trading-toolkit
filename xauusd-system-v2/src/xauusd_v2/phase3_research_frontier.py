from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from .phase3_stage_comparison import BrokerStageEvidenceRecord, index_broker_evidence
from .strategy_evidence_sequence import EvidenceState, StrategyEvidenceRecord, StrategyEvidenceStage, index_evidence


_R143_ORDER = (
    StrategyEvidenceStage.HCS_ZONE_REACTION,
    StrategyEvidenceStage.TFS_CONFIRMED,
    StrategyEvidenceStage.LAOL_MET,
    StrategyEvidenceStage.TRUE_STOP_RESPECTED,
    StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED,
    StrategyEvidenceStage.TARGETS_AND_TIMING,
)


class FrontierState(StrEnum):
    COMPLETE_AT_THIS_LAYER = "complete_at_this_layer"
    SOURCE_SEMANTIC_FRONTIER = "source_semantic_frontier"
    BROKER_SEMANTIC_FRONTIER = "broker_semantic_frontier"
    SOURCE_AND_BROKER_FRONTIER = "source_and_broker_frontier"
    MISSING_EVIDENCE = "missing_evidence"


@dataclass(frozen=True, slots=True)
class ResearchFrontierResult:
    state: FrontierState
    stage: StrategyEvidenceStage | None
    source_state: EvidenceState | None
    broker_semantic_state: EvidenceState | None
    broker_path_observed: bool | None
    downstream_semantic_promotion_allowed: bool
    reason: str


def find_first_research_frontier(
    source_records: Iterable[StrategyEvidenceRecord],
    broker_records: Iterable[BrokerStageEvidenceRecord],
) -> ResearchFrontierResult:
    """Find the first R-143 stage that must be resolved before downstream promotion.

    Source semantic truth is checked first because broker geometry cannot define
    strategy truth. Broker price/path observations are preserved for diagnostics
    but never allow a blocked source semantic stage to be skipped.
    """
    source_index = index_evidence(source_records)
    broker_index = index_broker_evidence(broker_records)

    for stage in _R143_ORDER:
        source = source_index.get(stage)
        broker = broker_index.get(stage)

        if source is None or broker is None:
            return ResearchFrontierResult(
                state=FrontierState.MISSING_EVIDENCE,
                stage=stage,
                source_state=source.state if source else None,
                broker_semantic_state=broker.semantic_state if broker else None,
                broker_path_observed=broker.broker_path_observed if broker else None,
                downstream_semantic_promotion_allowed=False,
                reason="required source or broker stage record is absent",
            )

        source_ready = source.state is EvidenceState.OBSERVED
        broker_ready = broker.semantic_state is EvidenceState.OBSERVED

        if source_ready and broker_ready:
            continue
        if not source_ready and not broker_ready:
            return ResearchFrontierResult(
                FrontierState.SOURCE_AND_BROKER_FRONTIER,
                stage,
                source.state,
                broker.semantic_state,
                broker.broker_path_observed,
                False,
                "strategy-source semantics and broker semantic evidence are both unresolved at this stage",
            )
        if not source_ready:
            return ResearchFrontierResult(
                FrontierState.SOURCE_SEMANTIC_FRONTIER,
                stage,
                source.state,
                broker.semantic_state,
                broker.broker_path_observed,
                False,
                "source semantic stage is unresolved; broker evidence cannot skip or define it",
            )
        return ResearchFrontierResult(
            FrontierState.BROKER_SEMANTIC_FRONTIER,
            stage,
            source.state,
            broker.semantic_state,
            broker.broker_path_observed,
            False,
            "source stage is explicit but broker semantic certification is unresolved",
        )

    return ResearchFrontierResult(
        FrontierState.COMPLETE_AT_THIS_LAYER,
        None,
        None,
        None,
        None,
        False,
        "all six source and broker semantic stages are observed at this layer; reference alignment, certification and risk gates still remain",
    )
