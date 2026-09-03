from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .focused_validation_packet import (
    FOCUSED_VERDICT_TAXONOMY,
    FocusedValidationCase,
    FocusedValidationPacket,
    focused_packet_payload,
)


_TOP_LEVEL_KEYS = {"version", "protocol", "dataset_name", "verdict_taxonomy", "cases"}
_CASE_KEYS = {"vector_id", "source_locator", "candidate_claim"}
_FORBIDDEN_KEYS = {
    "expected_verdict",
    "ground_truth_answer",
    "expected_class",
    "evidence",
    "forbidden_inference",
    "promotion_allowed",
}


def _reject_answer_fields(value: Any, *, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in _FORBIDDEN_KEYS:
                raise ValueError(f"focused packet contains forbidden answer field at {path}.{key}")
            _reject_answer_fields(item, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_answer_fields(item, path=f"{path}[{index}]")


def write_focused_packet(packet: FocusedValidationPacket, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            focused_packet_payload(packet),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def load_focused_packet(path: str | Path) -> FocusedValidationPacket:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("focused packet must contain one JSON object")
    _reject_answer_fields(raw)
    if set(raw) != _TOP_LEVEL_KEYS:
        raise ValueError("focused packet top-level schema mismatch")
    if raw.get("version") != 1:
        raise ValueError("unsupported focused packet version")
    if raw.get("protocol") != "agent06_focused_claim_adjudication_v2":
        raise ValueError("focused packet protocol mismatch")

    dataset_name = str(raw.get("dataset_name", "")).strip()
    if not dataset_name:
        raise ValueError("focused packet dataset_name is required")

    taxonomy_raw = raw.get("verdict_taxonomy")
    if not isinstance(taxonomy_raw, list):
        raise ValueError("focused packet verdict_taxonomy must be an array")
    taxonomy = tuple(str(item).strip() for item in taxonomy_raw)
    if taxonomy != FOCUSED_VERDICT_TAXONOMY:
        raise ValueError("focused packet verdict taxonomy mismatch")

    cases_raw = raw.get("cases")
    if not isinstance(cases_raw, list) or not cases_raw:
        raise ValueError("focused packet requires non-empty cases")
    cases: list[FocusedValidationCase] = []
    seen: set[str] = set()
    for item in cases_raw:
        if not isinstance(item, dict) or set(item) != _CASE_KEYS:
            raise ValueError("focused packet case schema mismatch")
        vector_id = str(item.get("vector_id", "")).strip()
        source_locator = str(item.get("source_locator", "")).strip()
        candidate_claim = str(item.get("candidate_claim", "")).strip()
        if not vector_id or not source_locator or not candidate_claim:
            raise ValueError("focused case requires vector_id, source_locator and candidate_claim")
        if vector_id in seen:
            raise ValueError(f"duplicate focused vector id: {vector_id}")
        seen.add(vector_id)
        cases.append(
            FocusedValidationCase(
                vector_id=vector_id,
                source_locator=source_locator,
                candidate_claim=candidate_claim,
            )
        )

    return FocusedValidationPacket(
        dataset_name=dataset_name,
        verdict_taxonomy=taxonomy,
        cases=tuple(cases),
    )
