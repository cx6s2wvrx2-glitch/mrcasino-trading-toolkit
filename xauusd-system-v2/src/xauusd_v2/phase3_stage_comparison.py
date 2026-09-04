from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from .strategy_evidence_sequence import EvidenceState, StrategyEvidenceRecord, StrategyEvidenceStage, index_evidence


class ComparisonState(StrEnum):
    BOTH_OBSERVED_REFERENCE_ALIGNED = "both_observed_reference_aligned"
    BOTH_OBSERVED_REFERENCE_UNALIGNED = "both_observed_reference_unaligned"
    SOURCE_OBSERVED_BROKER_BLOCKED = "source_observed_broker_blocked"
    SOURCE_BLOCKED_BROKER_OBSERVED = "source_blocked_broker_observed"
    BOTH_BLOCKED = "both_blocked"
    SOURCE_BLOCKED_BROKER_PATH_OBSERVED = "source_blocked_broker_path_observed"
    SOURCE_OBSERVED_BROKER_PATH_ONLY = "source_observed_broker_path_only"
    MISSING_OR_INCOMPLETE = "missing_or_incomplete"


@dataclass(frozen=True, slots=True)
class BrokerStageEvidenceRecord:
    stage: StrategyEvidenceStage
    semantic_state: EvidenceState
    broker_path_observed: bool | None
    evidence_ref: str | None = None
    event_time: str | None = None
    timeframe_minutes: int | None = None
    machine_stage_certified: bool = False
    reference_feed_aligned: bool = False
    note: str = ""

    def __post_init__(self) -> None:
        if self.timeframe_minutes is not None and self.timeframe_minutes <= 0:
            raise ValueError("timeframe_minutes must be positive when supplied")
        if self.semantic_state is EvidenceState.OBSERVED and not self.machine_stage_certified:
            raise ValueError("broker semantic OBSERVED requires machine_stage_certified=true")
        if self.machine_stage_certified and not self.evidence_ref:
            raise ValueError("machine-certified broker stage requires evidence_ref")
        if self.broker_path_observed is True and not self.evidence_ref:
            raise ValueError("observed broker path requires evidence_ref")


@dataclass(frozen=True, slots=True)
class StageComparisonResult:
    stage: StrategyEvidenceStage
    source_state: EvidenceState | None
    broker_semantic_state: EvidenceState | None
    broker_path_observed: bool | None
    reference_feed_aligned: bool
    comparison_state: ComparisonState
    canonical_equivalence_allowed: bool
    reason: str


def index_broker_evidence(
    records: Iterable[BrokerStageEvidenceRecord],
) -> dict[StrategyEvidenceStage, BrokerStageEvidenceRecord]:
    indexed: dict[StrategyEvidenceStage, BrokerStageEvidenceRecord] = {}
    for record in records:
        if record.stage in indexed:
            raise ValueError(f"duplicate broker evidence record for stage: {record.stage}")
        indexed[record.stage] = record
    return indexed


def _classify(
    *,
    stage: StrategyEvidenceStage,
    source: StrategyEvidenceRecord | None,
    broker: BrokerStageEvidenceRecord | None,
) -> StageComparisonResult:
    if source is None or broker is None:
        return StageComparisonResult(
            stage=stage,
            source_state=source.state if source else None,
            broker_semantic_state=broker.semantic_state if broker else None,
            broker_path_observed=broker.broker_path_observed if broker else None,
            reference_feed_aligned=broker.reference_feed_aligned if broker else False,
            comparison_state=ComparisonState.MISSING_OR_INCOMPLETE,
            canonical_equivalence_allowed=False,
            reason="source or broker stage evidence is absent",
        )

    if source.state is EvidenceState.OBSERVED and broker.semantic_state is EvidenceState.OBSERVED:
        if broker.reference_feed_aligned:
            return StageComparisonResult(
                stage,
                source.state,
                broker.semantic_state,
                broker.broker_path_observed,
                True,
                ComparisonState.BOTH_OBSERVED_REFERENCE_ALIGNED,
                True,
                "source stage and broker semantic stage are both observed with explicit reference-feed alignment",
            )
        return StageComparisonResult(
            stage,
            source.state,
            broker.semantic_state,
            broker.broker_path_observed,
            False,
            ComparisonState.BOTH_OBSERVED_REFERENCE_UNALIGNED,
            False,
            "source and broker semantic stages may both be observed, but canonical source-feed equivalence is not established",
        )

    if source.state is EvidenceState.OBSERVED and broker.semantic_state is EvidenceState.BLOCKED:
        if broker.broker_path_observed:
            state = ComparisonState.SOURCE_OBSERVED_BROKER_PATH_ONLY
            reason = "source stage is explicit and the broker path contains related price evidence, but broker semantic certification is blocked"
        else:
            state = ComparisonState.SOURCE_OBSERVED_BROKER_BLOCKED
            reason = "source stage is explicit, but broker semantic evidence is blocked"
        return StageComparisonResult(
            stage,
            source.state,
            broker.semantic_state,
            broker.broker_path_observed,
            broker.reference_feed_aligned,
            state,
            False,
            reason,
        )

    if source.state is EvidenceState.BLOCKED and broker.semantic_state is EvidenceState.OBSERVED:
        return StageComparisonResult(
            stage,
            source.state,
            broker.semantic_state,
            broker.broker_path_observed,
            broker.reference_feed_aligned,
            ComparisonState.SOURCE_BLOCKED_BROKER_OBSERVED,
            False,
            "broker stage is machine-observed, but the preserved source packet does not fully establish the canonical source stage",
        )

    if source.state is EvidenceState.BLOCKED and broker.semantic_state is EvidenceState.BLOCKED:
        if broker.broker_path_observed:
            state = ComparisonState.SOURCE_BLOCKED_BROKER_PATH_OBSERVED
            reason = "both semantic layers remain blocked although the broker path contains a related price observation"
        else:
            state = ComparisonState.BOTH_BLOCKED
            reason = "both source and broker semantic layers remain blocked"
        return StageComparisonResult(
            stage,
            source.state,
            broker.semantic_state,
            broker.broker_path_observed,
            broker.reference_feed_aligned,
            state,
            False,
            reason,
        )

    return StageComparisonResult(
        stage,
        source.state,
        broker.semantic_state,
        broker.broker_path_observed,
        broker.reference_feed_aligned,
        ComparisonState.MISSING_OR_INCOMPLETE,
        False,
        "stage evidence is missing or not yet comparable under the current Phase-3 contract",
    )


def compare_source_to_broker_stages(
    source_records: Iterable[StrategyEvidenceRecord],
    broker_records: Iterable[BrokerStageEvidenceRecord],
) -> tuple[StageComparisonResult, ...]:
    """Compare source-stage truth to broker-stage evidence without forcing equivalence.

    A related broker price touch/path is deliberately separate from a machine
    semantic observation. Canonical equivalence is allowed only when both source
    and broker semantic stages are observed AND reference-feed alignment is
    explicitly true.
    """
    source_index = index_evidence(source_records)
    broker_index = index_broker_evidence(broker_records)
    stages = tuple(dict.fromkeys((*source_index.keys(), *broker_index.keys())))
    return tuple(
        _classify(stage=stage, source=source_index.get(stage), broker=broker_index.get(stage))
        for stage in stages
    )
