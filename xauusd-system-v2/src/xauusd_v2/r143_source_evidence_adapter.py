from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .strategy_evidence_sequence import (
    EvidenceState,
    StrategyEvidenceRecord,
    StrategyEvidenceStage,
)


_SOURCE_STAGE_MAP = {
    "HCS_ZONE_REACTION": StrategyEvidenceStage.HCS_ZONE_REACTION,
    "TFS": StrategyEvidenceStage.TFS_CONFIRMED,
    "LAOL_MET": StrategyEvidenceStage.LAOL_MET,
    "TRUE_STOP_RESPECTED": StrategyEvidenceStage.TRUE_STOP_RESPECTED,
    "TEN_MIN_TRUE_STOP_ESTABLISHED": StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED,
    "TARGETS_AND_TIMING": StrategyEvidenceStage.TARGETS_AND_TIMING,
}

_EXPECTED_SOURCE_STAGES = tuple(_SOURCE_STAGE_MAP)


def _source_status_to_evidence_state(status: str) -> EvidenceState:
    if status == "explicit":
        return EvidenceState.OBSERVED
    if status in {"partial", "unresolved"}:
        return EvidenceState.BLOCKED
    raise ValueError(f"unsupported R-143 source evidence status: {status}")


def records_from_r143_source_evidence(payload: Mapping[str, Any]) -> tuple[StrategyEvidenceRecord, ...]:
    """Convert an existing R-143 source map into Phase-3 traceable evidence.

    `explicit` means the source explicitly labels/describes that stage and may be
    carried as OBSERVED source evidence. It does NOT imply machine certification.

    `partial` and `unresolved` remain BLOCKED because the source excerpt does not
    authorize a complete strategy-stage truth. They are never converted to false.
    """
    if payload.get("schema_version") != "r143_source_evidence_map_v1":
        raise ValueError("unsupported R-143 source evidence schema")

    episode_id = payload.get("episode_id")
    if not isinstance(episode_id, str) or not episode_id.strip():
        raise ValueError("episode_id is required")

    stages = payload.get("stages")
    if not isinstance(stages, list):
        raise ValueError("stages must be a list")

    by_stage: dict[str, Mapping[str, Any]] = {}
    for item in stages:
        if not isinstance(item, Mapping):
            raise ValueError("each R-143 source stage must be an object")
        source_stage = item.get("stage")
        if not isinstance(source_stage, str) or source_stage not in _SOURCE_STAGE_MAP:
            raise ValueError(f"unknown R-143 source stage: {source_stage!r}")
        if source_stage in by_stage:
            raise ValueError(f"duplicate R-143 source stage: {source_stage}")
        by_stage[source_stage] = item

    missing = [stage for stage in _EXPECTED_SOURCE_STAGES if stage not in by_stage]
    if missing:
        raise ValueError(f"R-143 source evidence map is missing stages: {', '.join(missing)}")

    records: list[StrategyEvidenceRecord] = []
    for source_stage in _EXPECTED_SOURCE_STAGES:
        item = by_stage[source_stage]
        status = item.get("status")
        if not isinstance(status, str):
            raise ValueError(f"status is required for stage {source_stage}")
        state = _source_status_to_evidence_state(status)

        source_refs = item.get("source_refs", [])
        if not isinstance(source_refs, list) or any(not isinstance(ref, str) for ref in source_refs):
            raise ValueError(f"source_refs must be a string list for stage {source_stage}")
        source_ref = ";".join(ref for ref in source_refs if ref.strip()) or None

        note = item.get("note", "")
        if not isinstance(note, str):
            raise ValueError(f"note must be a string for stage {source_stage}")

        machine_stage_certified = item.get("machine_stage_certified")
        if machine_stage_certified is not False:
            raise ValueError("source evidence adapter only accepts non-certified source-stage maps")

        records.append(
            StrategyEvidenceRecord(
                stage=_SOURCE_STAGE_MAP[source_stage],
                state=state,
                evidence_ref=f"r143_source_map:{episode_id}:{source_stage}",
                source_ref=source_ref,
                note=(
                    f"source_status={status}; machine_stage_certified=false; {note}"
                ).strip(),
            )
        )

    return tuple(records)
