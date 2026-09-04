from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from .backtest_sequence import BacktestSequenceResult, evaluate_r143_sequence
from .ltf_execution import (
    LTFExecutionMode,
    LTFExecutionResult,
    LTFExecutionState,
    LTFExecutionTrigger,
    evaluate_r145_ltf_execution,
)
from .true_stop_semantic import (
    LTFTrigger,
    TrueStopEntryResult,
    TrueStopEntryState,
    TrueStopResult,
    evaluate_true_stop_entry,
    evaluate_true_stop_main_poi,
    evaluate_true_stop_respect,
)


class EvidenceState(StrEnum):
    OBSERVED = "observed"
    MISSING = "missing"
    BLOCKED = "blocked"


class StrategyEvidenceStage(StrEnum):
    DIRECTIONAL_CONTEXT = "directional_context"
    LIQUIDITY_CALCULATION = "liquidity_calculation"
    POI_ZONE_CONTEXT = "poi_zone_context"
    HCS_ZONE_REACTION = "hcs_zone_reaction"
    TFS_CONFIRMED = "tfs_confirmed"
    LAOL_MET = "laol_met"
    ALL_REQUIRED_10M_PLUS_TFS_FACTORS = "all_required_10m_plus_tfs_factors"
    TEN_MIN_PLUS_HCS_NEGATION_MANIPULATION = "ten_min_plus_hcs_negation_manipulation"
    TRUE_STOP_MAIN_POI_CONFIRMED = "true_stop_main_poi_confirmed"
    TRUE_STOP_POI_RESPECTED = "true_stop_poi_respected"
    TRUE_STOP_RESPECTED = "true_stop_respected"
    FINAL_LIQUIDITY_CALCULATION = "final_liquidity_calculation"
    TEN_MIN_TRUE_STOP_ESTABLISHED = "ten_min_true_stop_established"
    TEN_MIN_TRUE_STOP_FORMING = "ten_min_true_stop_forming"
    FULL_TFS_FACTORS = "full_tfs_factors"
    RETAIL_LIQUIDITY_MANIPULATED = "retail_liquidity_manipulated"
    LTF_LAOL_TAKEN = "ltf_laol_taken"
    LTF_TRIGGER = "ltf_trigger"
    TARGETS_AND_TIMING = "targets_and_timing"
    RISK_GATE = "risk_gate"


class ContextGateState(StrEnum):
    READY_FOR_MODEL_REVIEW = "ready_for_model_review"
    WAIT = "wait"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class StrategyEvidenceRecord:
    stage: StrategyEvidenceStage
    state: EvidenceState
    evidence_ref: str | None = None
    source_ref: str | None = None
    event_time: str | None = None
    timeframe_minutes: int | None = None
    note: str = ""

    def __post_init__(self) -> None:
        if self.timeframe_minutes is not None and self.timeframe_minutes <= 0:
            raise ValueError("timeframe_minutes must be positive when supplied")
        if self.state is EvidenceState.OBSERVED and not (
            (self.evidence_ref and self.evidence_ref.strip())
            or (self.source_ref and self.source_ref.strip())
        ):
            raise ValueError("observed evidence requires evidence_ref or source_ref provenance")


@dataclass(frozen=True, slots=True)
class ContextGateResult:
    state: ContextGateState
    first_unready_stage: StrategyEvidenceStage | None
    reason: str


_CONTEXT_REQUIRED_STAGES = (
    StrategyEvidenceStage.DIRECTIONAL_CONTEXT,
    StrategyEvidenceStage.LIQUIDITY_CALCULATION,
    StrategyEvidenceStage.POI_ZONE_CONTEXT,
)

_R143_STAGE_MAP = {
    "hcs_zone_reaction": StrategyEvidenceStage.HCS_ZONE_REACTION,
    "tfs_confirmed": StrategyEvidenceStage.TFS_CONFIRMED,
    "laol_met": StrategyEvidenceStage.LAOL_MET,
    "true_stop_respected": StrategyEvidenceStage.TRUE_STOP_RESPECTED,
    "ten_min_true_stop_established": StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED,
    "targets_and_timing_defined": StrategyEvidenceStage.TARGETS_AND_TIMING,
}


def index_evidence(records: Iterable[StrategyEvidenceRecord]) -> dict[StrategyEvidenceStage, StrategyEvidenceRecord]:
    indexed: dict[StrategyEvidenceStage, StrategyEvidenceRecord] = {}
    for record in records:
        if record.stage in indexed:
            raise ValueError(f"duplicate evidence record for stage: {record.stage}")
        indexed[record.stage] = record
    return indexed


def evidence_state_to_optional_bool(record: StrategyEvidenceRecord | None) -> bool | None:
    """Convert traceable phase-3 evidence into fail-closed semantic input.

    OBSERVED -> True
    MISSING  -> False
    BLOCKED or absent -> None

    BLOCKED is deliberately not treated as False because it means the system
    cannot currently decide the strategy truth for that stage from authorized
    source/data evidence.
    """
    if record is None or record.state is EvidenceState.BLOCKED:
        return None
    return record.state is EvidenceState.OBSERVED


def evaluate_pre_entry_context(records: Iterable[StrategyEvidenceRecord]) -> ContextGateResult:
    """Evaluate only the universal context gate, never entry authorization.

    The source-backed entry drafts require directional/top-down context,
    liquidity calculation and relevant POI/zone context before an entry model is
    reviewed. This function does not require or infer a particular entry family.
    """
    indexed = index_evidence(records)

    for stage in _CONTEXT_REQUIRED_STAGES:
        record = indexed.get(stage)
        if record is None or record.state is EvidenceState.BLOCKED:
            return ContextGateResult(
                ContextGateState.BLOCKED,
                stage,
                "required context evidence is unresolved or not supplied",
            )
        if record.state is EvidenceState.MISSING:
            return ContextGateResult(
                ContextGateState.WAIT,
                stage,
                "context sequence is not ready; required evidence has not been observed",
            )

    return ContextGateResult(
        ContextGateState.READY_FOR_MODEL_REVIEW,
        None,
        "directional context, liquidity calculation and POI/zone context are all observed; entry-family gates still remain",
    )


def evaluate_r143_evidence(records: Iterable[StrategyEvidenceRecord]) -> BacktestSequenceResult:
    """Run the official R-143 order from provenance-bearing evidence records.

    This is an adapter over the existing fail-closed R-143 evaluator. It adds
    traceability but does not change any strategy semantics or certify a trade.
    """
    indexed = index_evidence(records)

    values = {
        name: evidence_state_to_optional_bool(indexed.get(stage))
        for name, stage in _R143_STAGE_MAP.items()
    }

    return evaluate_r143_sequence(**values)


def evaluate_true_stop_main_poi_evidence(records: Iterable[StrategyEvidenceRecord]) -> TrueStopResult:
    """Compose the existing True-Stop Main-POI semantic gate from traceable evidence."""
    indexed = index_evidence(records)
    return evaluate_true_stop_main_poi(
        all_required_10m_plus_tfs_factors_aligned=evidence_state_to_optional_bool(
            indexed.get(StrategyEvidenceStage.ALL_REQUIRED_10M_PLUS_TFS_FACTORS)
        ),
        ten_min_plus_hcs_or_negation_manipulation_present=evidence_state_to_optional_bool(
            indexed.get(StrategyEvidenceStage.TEN_MIN_PLUS_HCS_NEGATION_MANIPULATION)
        ),
    )


def evaluate_true_stop_respect_evidence(records: Iterable[StrategyEvidenceRecord]) -> TrueStopResult:
    """Keep Main-POI existence separate from later price respect."""
    indexed = index_evidence(records)
    return evaluate_true_stop_respect(
        main_poi_confirmed=evidence_state_to_optional_bool(
            indexed.get(StrategyEvidenceStage.TRUE_STOP_MAIN_POI_CONFIRMED)
        ),
        price_respected_poi=evidence_state_to_optional_bool(
            indexed.get(StrategyEvidenceStage.TRUE_STOP_POI_RESPECTED)
        ),
    )


def evaluate_true_stop_entry_evidence(
    records: Iterable[StrategyEvidenceRecord],
    *,
    trigger: LTFTrigger | None,
) -> TrueStopEntryResult:
    """Evaluate TS entry refinement only after respect + final liquidity calculation."""
    indexed = index_evidence(records)
    trigger_record = indexed.get(StrategyEvidenceStage.LTF_TRIGGER)
    true_stop_respected = evidence_state_to_optional_bool(indexed.get(StrategyEvidenceStage.TRUE_STOP_RESPECTED))
    final_liquidity = evidence_state_to_optional_bool(indexed.get(StrategyEvidenceStage.FINAL_LIQUIDITY_CALCULATION))

    if trigger_record is not None and trigger_record.state is EvidenceState.MISSING:
        if true_stop_respected is True and final_liquidity is True:
            return TrueStopEntryResult(
                TrueStopEntryState.WAIT,
                None,
                "True Stop and final liquidity are resolved but the LTF HCS/negation trigger has not been observed",
            )
    if trigger_record is None or trigger_record.state is EvidenceState.BLOCKED:
        effective_trigger = None
    elif trigger_record.state is EvidenceState.OBSERVED:
        if trigger is None:
            return TrueStopEntryResult(
                TrueStopEntryState.NOT_CERTIFIED,
                None,
                "LTF trigger evidence is observed but the HCS/negation trigger type was not supplied",
            )
        effective_trigger = trigger
    else:
        effective_trigger = None

    return evaluate_true_stop_entry(
        true_stop_respected=true_stop_respected,
        ltf_trigger=effective_trigger,
        final_liquidity_calculation_resolved=final_liquidity,
    )


def evaluate_r145_evidence(
    records: Iterable[StrategyEvidenceRecord],
    *,
    trigger: LTFExecutionTrigger | None,
    mode: LTFExecutionMode,
) -> LTFExecutionResult:
    """Run R-145 from provenance-bearing evidence without creating direction.

    The source order retail-liquidity manipulation -> LTF LAOL taken -> approved
    LTF trigger is preserved by the existing evaluator. Confirmed and aggressive
    10m/TFS prerequisites remain separate exactly as implemented there.
    """
    indexed = index_evidence(records)

    retail = evidence_state_to_optional_bool(indexed.get(StrategyEvidenceStage.RETAIL_LIQUIDITY_MANIPULATED))
    ltf_laol = evidence_state_to_optional_bool(indexed.get(StrategyEvidenceStage.LTF_LAOL_TAKEN))
    trigger_record = indexed.get(StrategyEvidenceStage.LTF_TRIGGER)

    if trigger_record is None or trigger_record.state is EvidenceState.BLOCKED:
        effective_trigger = None
    elif trigger_record.state is EvidenceState.MISSING:
        if retail is True and ltf_laol is True:
            return LTFExecutionResult(
                LTFExecutionState.WAIT,
                None,
                mode,
                "R-145 context is present but the approved LTF trigger has not been observed",
            )
        effective_trigger = None
    else:
        if trigger is None:
            return LTFExecutionResult(
                LTFExecutionState.NOT_CERTIFIED,
                None,
                mode,
                "LTF trigger evidence is observed but the approved trigger type was not supplied",
            )
        effective_trigger = trigger

    return evaluate_r145_ltf_execution(
        retail_liquidity_manipulated=retail,
        ltf_laol_taken=ltf_laol,
        trigger=effective_trigger,
        mode=mode,
        ten_min_ts_established=evidence_state_to_optional_bool(
            indexed.get(StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED)
        ),
        ten_min_ts_forming=evidence_state_to_optional_bool(
            indexed.get(StrategyEvidenceStage.TEN_MIN_TRUE_STOP_FORMING)
        ),
        full_tfs_factors_present=evidence_state_to_optional_bool(
            indexed.get(StrategyEvidenceStage.FULL_TFS_FACTORS)
        ),
    )
