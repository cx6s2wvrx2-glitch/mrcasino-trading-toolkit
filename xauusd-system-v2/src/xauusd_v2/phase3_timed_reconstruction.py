from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .phase3_stage_comparison import (
    BrokerStageEvidenceRecord,
    StageComparisonResult,
    compare_source_to_broker_stages,
    index_broker_evidence,
)
from .strategy_evidence_sequence import (
    EvidenceState,
    StrategyEvidenceRecord,
    StrategyEvidenceStage,
    index_evidence,
)


_R143_ORDER = (
    StrategyEvidenceStage.HCS_ZONE_REACTION,
    StrategyEvidenceStage.TFS_CONFIRMED,
    StrategyEvidenceStage.LAOL_MET,
    StrategyEvidenceStage.TRUE_STOP_RESPECTED,
    StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED,
    StrategyEvidenceStage.TARGETS_AND_TIMING,
)

_STAGE_GR = {
    StrategyEvidenceStage.HCS_ZONE_REACTION: "Αντίδραση σε HCS / manipulation zone",
    StrategyEvidenceStage.TFS_CONFIRMED: "TFS / επικρατούσα κατεύθυνση",
    StrategyEvidenceStage.LAOL_MET: "LAOL met",
    StrategyEvidenceStage.TRUE_STOP_RESPECTED: "True Stop respected",
    StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED: "10m True Stop established",
    StrategyEvidenceStage.TARGETS_AND_TIMING: "Core + major + LAOL στόχοι / timing",
}

_STATE_GR = {
    EvidenceState.OBSERVED: "ΠΑΡΑΤΗΡΗΘΗΚΕ",
    EvidenceState.MISSING: "ΛΕΙΠΕΙ",
    EvidenceState.BLOCKED: "ΜΠΛΟΚΑΡΙΣΜΕΝΟ",
}


@dataclass(frozen=True, slots=True)
class TimedStageRow:
    stage: StrategyEvidenceStage
    stage_label_gr: str
    source_state: EvidenceState | None
    source_ref: str | None
    source_note: str
    broker_event_time: str | None
    broker_timeframe_minutes: int | None
    broker_path_observed: bool | None
    broker_semantic_state: EvidenceState | None
    broker_evidence_ref: str | None
    broker_note: str
    reference_feed_aligned: bool
    canonical_equivalence_allowed: bool
    comparison_state: str
    allowed_conclusion: str


def _validate_event_time(value: str | None) -> None:
    if value is None:
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"broker event_time is not valid ISO-8601: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ValueError("broker event_time must be timezone-aware")


def _allowed_conclusion(result: StageComparisonResult) -> str:
    if result.canonical_equivalence_allowed:
        return "CANONICAL_EQUIVALENCE_ALLOWED"
    if result.broker_path_observed is True:
        return "BROKER_PATH_ONLY_SEMANTIC_NOT_CERTIFIED"
    if result.source_state is EvidenceState.OBSERVED:
        return "SOURCE_LABEL_ONLY_BROKER_SEMANTIC_BLOCKED"
    return "SEMANTIC_STAGE_UNRESOLVED"


def build_timed_stage_rows(
    source_records: Iterable[StrategyEvidenceRecord],
    broker_records: Iterable[BrokerStageEvidenceRecord],
) -> tuple[TimedStageRow, ...]:
    """Build a stage-by-stage timed reconstruction without semantic promotion.

    The row intentionally keeps source label, broker timestamp/path evidence,
    broker semantic state and reference-feed alignment as separate dimensions.
    A broker timestamp or price-path observation can never by itself upgrade a
    source-labelled stage to canonical strategy truth.
    """
    source_records = tuple(source_records)
    broker_records = tuple(broker_records)
    source_index = index_evidence(source_records)
    broker_index = index_broker_evidence(broker_records)
    comparison_index = {
        result.stage: result
        for result in compare_source_to_broker_stages(source_records, broker_records)
    }

    rows: list[TimedStageRow] = []
    for stage in _R143_ORDER:
        source = source_index.get(stage)
        broker = broker_index.get(stage)
        result = comparison_index.get(stage)
        if result is None:
            continue
        if broker is not None:
            _validate_event_time(broker.event_time)

        rows.append(
            TimedStageRow(
                stage=stage,
                stage_label_gr=_STAGE_GR.get(stage, stage.value),
                source_state=source.state if source else None,
                source_ref=source.source_ref if source else None,
                source_note=source.note if source else "",
                broker_event_time=broker.event_time if broker else None,
                broker_timeframe_minutes=broker.timeframe_minutes if broker else None,
                broker_path_observed=broker.broker_path_observed if broker else None,
                broker_semantic_state=broker.semantic_state if broker else None,
                broker_evidence_ref=broker.evidence_ref if broker else None,
                broker_note=broker.note if broker else "",
                reference_feed_aligned=result.reference_feed_aligned,
                canonical_equivalence_allowed=result.canonical_equivalence_allowed,
                comparison_state=result.comparison_state.value,
                allowed_conclusion=_allowed_conclusion(result),
            )
        )

    return tuple(rows)


def render_timed_reconstruction_gr(rows: Iterable[TimedStageRow], *, title: str) -> str:
    """Render a compact Greek timeline suitable for human validation artifacts."""
    lines = [
        title,
        "ΠΗΓΗ → BROKER ΧΡΟΝΟΣ/TF → BROKER SEMANTIC → FOREXCOM ALIGNMENT → ΕΠΙΤΡΕΠΟΜΕΝΟ ΣΥΜΠΕΡΑΣΜΑ",
        "",
    ]

    for index, row in enumerate(rows, start=1):
        source_state = _STATE_GR.get(row.source_state, "ΔΕΝ ΥΠΑΡΧΕΙ") if row.source_state else "ΔΕΝ ΥΠΑΡΧΕΙ"
        broker_state = (
            _STATE_GR.get(row.broker_semantic_state, "ΔΕΝ ΥΠΑΡΧΕΙ")
            if row.broker_semantic_state
            else "ΔΕΝ ΥΠΑΡΧΕΙ"
        )
        path = "ΝΑΙ" if row.broker_path_observed is True else "ΟΧΙ" if row.broker_path_observed is False else "ΑΓΝΩΣΤΟ"
        event_time = row.broker_event_time or "—"
        timeframe = f"{row.broker_timeframe_minutes}m" if row.broker_timeframe_minutes else "—"
        aligned = "ΝΑΙ" if row.reference_feed_aligned else "ΟΧΙ"
        equivalent = "ΝΑΙ" if row.canonical_equivalence_allowed else "ΟΧΙ"

        lines.extend(
            [
                f"{index}. {row.stage_label_gr}",
                f"   Πηγή: {source_state}",
                f"   Source ref: {row.source_ref or '—'}",
                f"   Broker ώρα / TF: {event_time} / {timeframe}",
                f"   Broker price/path: {path}",
                f"   Broker semantic: {broker_state}",
                f"   FOREXCOM aligned: {aligned}",
                f"   Canonical equivalence: {equivalent}",
                f"   Τι επιτρέπεται να πούμε: {row.allowed_conclusion}",
                f"   Broker note: {row.broker_note or '—'}",
                "",
            ]
        )

    lines.extend(
        [
            "ΚΑΝΟΝΑΣ ΑΝΑΓΝΩΣΗΣ",
            "Broker price/path observation ≠ strategy semantic certification.",
            "Ίδια τιμή ή σωστή χρονική διαδρομή δεν μετατρέπει από μόνη της ένα FU/HCS/TFS/True Stop/LAOL σε πιστοποιημένο stage.",
            "Performance / promotion / live execution authority: false.",
        ]
    )
    return "\n".join(lines)
