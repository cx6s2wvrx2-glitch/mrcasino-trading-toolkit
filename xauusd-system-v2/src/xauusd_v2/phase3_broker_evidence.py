from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .phase3_stage_comparison import BrokerStageEvidenceRecord
from .strategy_evidence_sequence import EvidenceState, StrategyEvidenceStage


_STAGE_MAP = {stage.value: stage for stage in StrategyEvidenceStage}


def broker_records_from_payload(payload: Mapping[str, Any]) -> tuple[BrokerStageEvidenceRecord, ...]:
    """Parse a conservative Phase-3 broker evidence packet.

    The packet distinguishes a price-path observation from semantic stage
    certification. `reference_feed_aligned` is explicit and never inferred from
    price proximity or ordered path similarity.
    """
    if payload.get("schema_version") != "phase3_broker_stage_evidence_v1":
        raise ValueError("unsupported Phase-3 broker evidence schema")

    broker_symbol = payload.get("broker_symbol")
    if not isinstance(broker_symbol, str) or not broker_symbol.strip():
        raise ValueError("broker_symbol is required")

    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("records must be a list")

    parsed: list[BrokerStageEvidenceRecord] = []
    for item in records:
        if not isinstance(item, Mapping):
            raise ValueError("each broker stage evidence record must be an object")

        stage_raw = item.get("stage")
        if not isinstance(stage_raw, str) or stage_raw not in _STAGE_MAP:
            raise ValueError(f"unknown strategy evidence stage: {stage_raw!r}")

        state_raw = item.get("semantic_state")
        try:
            state = EvidenceState(state_raw)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"invalid semantic_state: {state_raw!r}") from exc

        path_observed = item.get("broker_path_observed")
        if path_observed is not None and not isinstance(path_observed, bool):
            raise ValueError("broker_path_observed must be boolean or null")

        evidence_ref = item.get("evidence_ref")
        if evidence_ref is not None and not isinstance(evidence_ref, str):
            raise ValueError("evidence_ref must be a string or null")

        event_time = item.get("event_time")
        if event_time is not None and not isinstance(event_time, str):
            raise ValueError("event_time must be a string or null")

        timeframe_minutes = item.get("timeframe_minutes")
        if timeframe_minutes is not None and not isinstance(timeframe_minutes, int):
            raise ValueError("timeframe_minutes must be an integer or null")

        machine_stage_certified = item.get("machine_stage_certified", False)
        reference_feed_aligned = item.get("reference_feed_aligned", False)
        if not isinstance(machine_stage_certified, bool) or not isinstance(reference_feed_aligned, bool):
            raise ValueError("certification/alignment flags must be booleans")

        note = item.get("note", "")
        if not isinstance(note, str):
            raise ValueError("note must be a string")

        parsed.append(
            BrokerStageEvidenceRecord(
                stage=_STAGE_MAP[stage_raw],
                semantic_state=state,
                broker_path_observed=path_observed,
                evidence_ref=evidence_ref,
                event_time=event_time,
                timeframe_minutes=timeframe_minutes,
                machine_stage_certified=machine_stage_certified,
                reference_feed_aligned=reference_feed_aligned,
                note=note,
            )
        )

    return tuple(parsed)
