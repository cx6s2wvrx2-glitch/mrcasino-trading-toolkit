from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Callable

from .agents.validation_agent import IndependentValidationAgent
from .blind_validation_packet import BlindValidationPacket
from .blind_validation_runner import BlindValidationBatchResult, run_blind_validation_batch


@dataclass(frozen=True, slots=True)
class BlindRuntimeCaseAudit:
    vector_id: str
    source_locator: str
    source_context_sha256: str
    predicted_label: str | None
    abstained: bool


@dataclass(frozen=True, slots=True)
class BlindValidationRuntimeManifest:
    run_id: str
    model_provider: str
    model_name: str
    packet_sha256: str
    taxonomy_sha256: str
    case_count: int
    completed_count: int
    abstained_count: int
    cases: tuple[BlindRuntimeCaseAudit, ...]
    promotion_allowed: bool = False


def blind_packet_sha256(packet: BlindValidationPacket) -> str:
    """Stable fingerprint of exactly what Agent 06 is allowed to receive."""
    payload = {
        "dataset_name": packet.dataset_name,
        "taxonomy": list(packet.taxonomy),
        "cases": [asdict(case) for case in packet.cases],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def execute_blind_validation_runtime(
    *,
    run_id: str,
    model_provider: str,
    model_name: str,
    packet: BlindValidationPacket,
    agent: IndependentValidationAgent,
    source_context_resolver: Callable[[str], str],
) -> tuple[BlindValidationBatchResult, BlindValidationRuntimeManifest]:
    """Execute one auditable blind validation run without introducing answer leakage.

    The manifest stores hashes of resolved primary contexts, never ground-truth labels,
    expected classes, analyst evidence or forbidden-inference notes. Predictions are
    outputs of Agent 06 and are safe to audit after generation. Promotion is always false.
    """
    normalized_run_id = run_id.strip()
    provider = model_provider.strip()
    model = model_name.strip()
    if not normalized_run_id:
        raise ValueError("run_id is required")
    if not provider:
        raise ValueError("model_provider is required")
    if not model:
        raise ValueError("model_name is required")
    if not packet.cases:
        raise ValueError("blind packet must contain cases")

    context_hashes: dict[str, str] = {}

    def audited_resolver(locator: str) -> str:
        context = source_context_resolver(locator)
        normalized = context.strip()
        if not normalized:
            raise ValueError(f"source context resolver returned empty content for {locator}")
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        previous = context_hashes.get(locator)
        if previous is not None and previous != digest:
            raise ValueError(f"source context changed within blind run for {locator}")
        context_hashes[locator] = digest
        return normalized

    batch = run_blind_validation_batch(
        packet=packet,
        agent=agent,
        source_context_resolver=audited_resolver,
    )
    decisions = {decision.vector_id: decision for decision in batch.decisions}
    audits: list[BlindRuntimeCaseAudit] = []
    for case in packet.cases:
        decision = decisions.get(case.vector_id)
        if decision is None:
            raise ValueError(f"blind runtime missing decision for {case.vector_id}")
        digest = context_hashes.get(case.source_locator)
        if digest is None:
            raise ValueError(f"blind runtime missing context audit for {case.vector_id}")
        audits.append(
            BlindRuntimeCaseAudit(
                vector_id=case.vector_id,
                source_locator=case.source_locator,
                source_context_sha256=digest,
                predicted_label=decision.predicted_label,
                abstained=decision.abstained,
            )
        )

    taxonomy_encoded = json.dumps(
        list(packet.taxonomy), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    abstained = sum(case.abstained for case in audits)
    manifest = BlindValidationRuntimeManifest(
        run_id=normalized_run_id,
        model_provider=provider,
        model_name=model,
        packet_sha256=blind_packet_sha256(packet),
        taxonomy_sha256=hashlib.sha256(taxonomy_encoded).hexdigest(),
        case_count=len(packet.cases),
        completed_count=len(audits),
        abstained_count=abstained,
        cases=tuple(audits),
        promotion_allowed=False,
    )
    return batch, manifest
