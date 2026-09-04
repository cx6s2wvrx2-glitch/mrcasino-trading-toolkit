from __future__ import annotations

from collections.abc import Iterable

from .strategy_evidence_sequence import (
    EvidenceState,
    StrategyEvidenceRecord,
    StrategyEvidenceStage,
    index_evidence,
)


_STAGE_LABEL_GR = {
    StrategyEvidenceStage.DIRECTIONAL_CONTEXT: "Κατεύθυνση / top-down context",
    StrategyEvidenceStage.LIQUIDITY_CALCULATION: "Liquidity calculation",
    StrategyEvidenceStage.POI_ZONE_CONTEXT: "POI / zone context",
    StrategyEvidenceStage.HCS_ZONE_REACTION: "HCS zone reaction",
    StrategyEvidenceStage.TFS_CONFIRMED: "TFS επιβεβαιωμένο",
    StrategyEvidenceStage.LAOL_MET: "LAOL met",
    StrategyEvidenceStage.ALL_REQUIRED_10M_PLUS_TFS_FACTORS: "Όλοι οι απαιτούμενοι 10m+ TFS factors",
    StrategyEvidenceStage.TEN_MIN_PLUS_HCS_NEGATION_MANIPULATION: "10m+ HCS / Negation manipulation",
    StrategyEvidenceStage.TRUE_STOP_MAIN_POI_CONFIRMED: "True Stop Main POI επιβεβαιωμένο",
    StrategyEvidenceStage.TRUE_STOP_POI_RESPECTED: "Price respected True Stop POI",
    StrategyEvidenceStage.TRUE_STOP_RESPECTED: "True Stop respected",
    StrategyEvidenceStage.FINAL_LIQUIDITY_CALCULATION: "Final liquidity calculation",
    StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED: "10m True Stop established",
    StrategyEvidenceStage.TEN_MIN_TRUE_STOP_FORMING: "10m True Stop forming",
    StrategyEvidenceStage.FULL_TFS_FACTORS: "Full TFS factors",
    StrategyEvidenceStage.RETAIL_LIQUIDITY_MANIPULATED: "Retail liquidity manipulated",
    StrategyEvidenceStage.LTF_LAOL_TAKEN: "LTF LAOL taken",
    StrategyEvidenceStage.LTF_TRIGGER: "LTF HCS / Negation trigger",
    StrategyEvidenceStage.TARGETS_AND_TIMING: "Core + Major + LAOL targets / timing",
    StrategyEvidenceStage.RISK_GATE: "Risk gate",
}

_STATE_LABEL_GR = {
    EvidenceState.OBSERVED: "ΠΑΡΑΤΗΡΗΘΗΚΕ",
    EvidenceState.MISSING: "ΛΕΙΠΕΙ",
    EvidenceState.BLOCKED: "ΜΠΛΟΚΑΡΙΣΜΕΝΟ",
}

_SECTIONS = (
    (
        "1. ΠΛΑΙΣΙΟ ΠΡΙΝ ΑΠΟ ENTRY MODEL",
        (
            StrategyEvidenceStage.DIRECTIONAL_CONTEXT,
            StrategyEvidenceStage.LIQUIDITY_CALCULATION,
            StrategyEvidenceStage.POI_ZONE_CONTEXT,
        ),
    ),
    (
        "2. R-143 SOURCE SEQUENCE",
        (
            StrategyEvidenceStage.HCS_ZONE_REACTION,
            StrategyEvidenceStage.TFS_CONFIRMED,
            StrategyEvidenceStage.LAOL_MET,
            StrategyEvidenceStage.TRUE_STOP_RESPECTED,
            StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED,
            StrategyEvidenceStage.TARGETS_AND_TIMING,
        ),
    ),
    (
        "3. TRUE STOP EVIDENCE",
        (
            StrategyEvidenceStage.ALL_REQUIRED_10M_PLUS_TFS_FACTORS,
            StrategyEvidenceStage.TEN_MIN_PLUS_HCS_NEGATION_MANIPULATION,
            StrategyEvidenceStage.TRUE_STOP_MAIN_POI_CONFIRMED,
            StrategyEvidenceStage.TRUE_STOP_POI_RESPECTED,
            StrategyEvidenceStage.FINAL_LIQUIDITY_CALCULATION,
        ),
    ),
    (
        "4. R-145 LTF EXECUTION",
        (
            StrategyEvidenceStage.RETAIL_LIQUIDITY_MANIPULATED,
            StrategyEvidenceStage.LTF_LAOL_TAKEN,
            StrategyEvidenceStage.LTF_TRIGGER,
            StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED,
            StrategyEvidenceStage.TEN_MIN_TRUE_STOP_FORMING,
            StrategyEvidenceStage.FULL_TFS_FACTORS,
        ),
    ),
    (
        "5. TARGETS / RISK",
        (
            StrategyEvidenceStage.TARGETS_AND_TIMING,
            StrategyEvidenceStage.RISK_GATE,
        ),
    ),
)


def _render_record(record: StrategyEvidenceRecord | None, stage: StrategyEvidenceStage) -> str:
    label = _STAGE_LABEL_GR[stage]
    if record is None:
        return f"[ΜΠΛΟΚΑΡΙΣΜΕΝΟ] {label} | δεν έχει δοθεί evidence record"

    state = _STATE_LABEL_GR[record.state]
    parts = [f"[{state}] {label}"]
    if record.timeframe_minutes is not None:
        parts.append(f"TF={record.timeframe_minutes}m")
    if record.event_time:
        parts.append(f"time={record.event_time}")
    if record.evidence_ref:
        parts.append(f"evidence={record.evidence_ref}")
    if record.source_ref:
        parts.append(f"source={record.source_ref}")
    if record.note:
        parts.append(f"note={record.note}")
    return " | ".join(parts)


def render_strategy_sequence_review(records: Iterable[StrategyEvidenceRecord]) -> str:
    """Render a Greek human-review view of Phase-3 evidence.

    This renderer does not derive new strategy truth. It only makes the supplied
    provenance-bearing evidence ledger readable for human validation and the
    later visual/PDF artifact.
    """
    indexed = index_evidence(records)
    lines = [
        "XAUUSD V2 — STRATEGY SEQUENCE REVIEW",
        "Κατάσταση: RESEARCH / NOT STRATEGY-CERTIFIED / NO LIVE AUTHORITY",
        "",
    ]

    for title, stages in _SECTIONS:
        lines.append(title)
        for stage in stages:
            lines.append(_render_record(indexed.get(stage), stage))
        lines.append("")

    lines.extend(
        [
            "ΣΗΜΕΙΩΣΗ",
            "ΠΑΡΑΤΗΡΗΘΗΚΕ δεν σημαίνει trade allowed ή strategy certified.",
            "ΜΠΛΟΚΑΡΙΣΜΕΝΟ σημαίνει ότι λείπει επαρκής source/data/semantic authority και δεν επιτρέπεται υπόθεση.",
        ]
    )
    return "\n".join(lines)
