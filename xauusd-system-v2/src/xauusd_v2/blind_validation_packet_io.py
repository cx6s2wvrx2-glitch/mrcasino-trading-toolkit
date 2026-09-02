from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .blind_validation_packet import BlindValidationCase, BlindValidationPacket


_FORBIDDEN_KEYS = {
    "expected_label",
    "expected_class",
    "evidence",
    "forbidden_inference",
    "ground_truth_answer",
    "promotion_allowed",
}
_TOP_LEVEL_KEYS = {"version", "dataset_name", "taxonomy", "cases"}
_CASE_KEYS = {"vector_id", "source_locator"}


def _reject_answer_fields(value: Any, *, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in _FORBIDDEN_KEYS:
                raise ValueError(f"blind packet contains forbidden answer field at {path}.{key}")
            _reject_answer_fields(item, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_answer_fields(item, path=f"{path}[{index}]")


def blind_packet_payload(packet: BlindValidationPacket) -> dict[str, Any]:
    if not packet.dataset_name.strip():
        raise ValueError("blind packet dataset_name is required")
    if len(packet.taxonomy) < 2:
        raise ValueError("blind packet taxonomy requires at least two labels")
    if len(set(packet.taxonomy)) != len(packet.taxonomy):
        raise ValueError("blind packet taxonomy contains duplicate labels")
    if not packet.cases:
        raise ValueError("blind packet requires cases")
    ids = [case.vector_id for case in packet.cases]
    if len(set(ids)) != len(ids):
        raise ValueError("blind packet contains duplicate vector ids")
    return {
        "version": 1,
        "dataset_name": packet.dataset_name,
        "taxonomy": list(packet.taxonomy),
        "cases": [asdict(case) for case in packet.cases],
    }


def write_blind_packet(packet: BlindValidationPacket, path: str | Path) -> None:
    destination = Path(path)
    payload = blind_packet_payload(packet)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def load_blind_packet(path: str | Path) -> BlindValidationPacket:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("blind packet file must contain one JSON object")
    _reject_answer_fields(raw)
    if set(raw) != _TOP_LEVEL_KEYS:
        raise ValueError("blind packet top-level schema mismatch")
    if raw.get("version") != 1:
        raise ValueError("unsupported blind packet version")

    dataset_name = str(raw.get("dataset_name", "")).strip()
    if not dataset_name:
        raise ValueError("blind packet dataset_name is required")

    taxonomy_raw = raw.get("taxonomy")
    if not isinstance(taxonomy_raw, list):
        raise ValueError("blind packet taxonomy must be an array")
    taxonomy = tuple(str(item).strip() for item in taxonomy_raw)
    if len(taxonomy) < 2 or any(not item for item in taxonomy):
        raise ValueError("blind packet taxonomy requires at least two non-empty labels")
    if len(set(taxonomy)) != len(taxonomy):
        raise ValueError("blind packet taxonomy contains duplicate labels")

    cases_raw = raw.get("cases")
    if not isinstance(cases_raw, list) or not cases_raw:
        raise ValueError("blind packet requires non-empty cases")
    cases: list[BlindValidationCase] = []
    seen_ids: set[str] = set()
    for item in cases_raw:
        if not isinstance(item, dict) or set(item) != _CASE_KEYS:
            raise ValueError("blind packet case schema mismatch")
        vector_id = str(item.get("vector_id", "")).strip()
        source_locator = str(item.get("source_locator", "")).strip()
        if not vector_id or not source_locator:
            raise ValueError("blind packet case requires vector_id and source_locator")
        if vector_id in seen_ids:
            raise ValueError(f"duplicate blind packet vector id: {vector_id}")
        seen_ids.add(vector_id)
        cases.append(BlindValidationCase(vector_id=vector_id, source_locator=source_locator))

    return BlindValidationPacket(
        dataset_name=dataset_name,
        taxonomy=taxonomy,
        cases=tuple(cases),
    )
