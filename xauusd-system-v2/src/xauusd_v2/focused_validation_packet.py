from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


FOCUSED_VERDICT_TAXONOMY = ("SUPPORTED", "CONTRADICTED", "INSUFFICIENT")


@dataclass(frozen=True, slots=True)
class FocusedValidationCase:
    vector_id: str
    source_locator: str
    candidate_claim: str


@dataclass(frozen=True, slots=True)
class FocusedValidationPacket:
    dataset_name: str
    cases: tuple[FocusedValidationCase, ...]
    verdict_taxonomy: tuple[str, ...] = FOCUSED_VERDICT_TAXONOMY


def focused_packet_payload(packet: FocusedValidationPacket) -> dict[str, object]:
    name = packet.dataset_name.strip()
    if not name:
        raise ValueError("focused packet dataset_name is required")
    if tuple(packet.verdict_taxonomy) != FOCUSED_VERDICT_TAXONOMY:
        raise ValueError("focused packet verdict taxonomy mismatch")
    if not packet.cases:
        raise ValueError("focused packet requires cases")

    ids: set[str] = set()
    cases: list[dict[str, str]] = []
    for case in packet.cases:
        vector_id = case.vector_id.strip()
        source_locator = case.source_locator.strip()
        candidate_claim = case.candidate_claim.strip()
        if not vector_id or not source_locator or not candidate_claim:
            raise ValueError("focused case requires vector_id, source_locator and candidate_claim")
        if vector_id in ids:
            raise ValueError(f"duplicate focused vector id: {vector_id}")
        ids.add(vector_id)
        cases.append(
            {
                "vector_id": vector_id,
                "source_locator": source_locator,
                "candidate_claim": candidate_claim,
            }
        )

    return {
        "version": 1,
        "protocol": "agent06_focused_claim_adjudication_v2",
        "dataset_name": name,
        "verdict_taxonomy": list(FOCUSED_VERDICT_TAXONOMY),
        "cases": cases,
    }


def focused_packet_sha256(packet: FocusedValidationPacket) -> str:
    encoded = json.dumps(
        focused_packet_payload(packet),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
