from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from .backtest_sequence import BacktestStage


class R143SourceEvidenceError(ValueError):
    pass


class SourceEvidenceStatus(StrEnum):
    EXPLICIT = "explicit"
    PARTIAL = "partial"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class R143SourceStageEvidence:
    stage: BacktestStage
    status: SourceEvidenceStatus
    source_refs: tuple[str, ...]
    note: str
    machine_stage_certified: bool = False


@dataclass(frozen=True, slots=True)
class R143SourceEvidenceMap:
    episode_id: str
    source_locator: str
    stages: tuple[R143SourceStageEvidence, ...]
    complete_source_sequence_claim: bool
    promotion_allowed: bool = False
    performance_claim_allowed: bool = False
    live_execution_authorized: bool = False
    schema_version: str = "r143_source_evidence_map_v1"


_ROOT_KEYS = {
    "schema_version",
    "episode_id",
    "source_locator",
    "stages",
    "complete_source_sequence_claim",
    "promotion_allowed",
    "performance_claim_allowed",
    "live_execution_authorized",
}
_STAGE_KEYS = {"stage", "status", "source_refs", "note", "machine_stage_certified"}


def _exact_object(value: object, expected: set[str], *, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise R143SourceEvidenceError(f"{field} must be an object")
    observed = set(value)
    if observed != expected:
        raise R143SourceEvidenceError(
            f"{field} schema mismatch; missing={sorted(expected - observed)}, extra={sorted(observed - expected)}"
        )
    return value


def _text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise R143SourceEvidenceError(f"{field} must be non-empty text")
    return value.strip()


def load_r143_source_evidence_map(path: str | Path) -> R143SourceEvidenceMap:
    file_path = Path(path).expanduser().resolve()
    if not file_path.is_file():
        raise R143SourceEvidenceError("R-143 source evidence map is unavailable")
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise R143SourceEvidenceError("R-143 source evidence map must be valid UTF-8 JSON") from exc

    root = _exact_object(raw, _ROOT_KEYS, field="map")
    if root["schema_version"] != "r143_source_evidence_map_v1":
        raise R143SourceEvidenceError("unsupported R-143 source evidence schema_version")
    for key in ("promotion_allowed", "performance_claim_allowed", "live_execution_authorized"):
        if root[key] is not False:
            raise R143SourceEvidenceError(f"{key} must be false")
    if not isinstance(root["complete_source_sequence_claim"], bool):
        raise R143SourceEvidenceError("complete_source_sequence_claim must be boolean")

    raw_stages = root["stages"]
    if not isinstance(raw_stages, list) or len(raw_stages) != len(tuple(BacktestStage)):
        raise R143SourceEvidenceError("map must contain exactly all six R-143 stages")

    stages: list[R143SourceStageEvidence] = []
    for index, expected_stage in enumerate(BacktestStage):
        item = _exact_object(raw_stages[index], _STAGE_KEYS, field=f"stages[{index}]")
        stage_name = _text(item["stage"], field=f"stages[{index}].stage")
        if stage_name != expected_stage.name:
            raise R143SourceEvidenceError(
                f"stages must be in canonical R-143 order; expected {expected_stage.name} at index {index}"
            )
        status_text = _text(item["status"], field=f"stages[{index}].status")
        try:
            status = SourceEvidenceStatus(status_text)
        except ValueError as exc:
            raise R143SourceEvidenceError(f"unknown source evidence status: {status_text}") from exc

        refs = item["source_refs"]
        if not isinstance(refs, list):
            raise R143SourceEvidenceError(f"stages[{index}].source_refs must be an array")
        source_refs = tuple(_text(ref, field=f"stages[{index}].source_refs") for ref in refs)
        if status is SourceEvidenceStatus.EXPLICIT and not source_refs:
            raise R143SourceEvidenceError("explicit source evidence requires at least one source_ref")
        if item["machine_stage_certified"] is not False:
            raise R143SourceEvidenceError("source evidence map cannot machine-certify an R-143 stage")

        stages.append(
            R143SourceStageEvidence(
                stage=expected_stage,
                status=status,
                source_refs=source_refs,
                note=_text(item["note"], field=f"stages[{index}].note"),
            )
        )

    complete_source_sequence_claim = root["complete_source_sequence_claim"]
    if complete_source_sequence_claim and any(stage.status is not SourceEvidenceStatus.EXPLICIT for stage in stages):
        raise R143SourceEvidenceError(
            "complete_source_sequence_claim=true requires explicit source evidence for all six stages"
        )

    return R143SourceEvidenceMap(
        episode_id=_text(root["episode_id"], field="episode_id"),
        source_locator=_text(root["source_locator"], field="source_locator"),
        stages=tuple(stages),
        complete_source_sequence_claim=complete_source_sequence_claim,
    )
