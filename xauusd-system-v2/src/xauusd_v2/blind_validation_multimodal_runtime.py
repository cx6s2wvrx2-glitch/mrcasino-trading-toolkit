from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Callable, Mapping

from .agents.validation_agent import IndependentValidationAgent, IndependentValidationDecision
from .blind_validation_packet import BlindValidationPacket
from .blind_validation_runner import BlindValidationBatchResult
from .blind_validation_runtime import blind_packet_sha256
from .primary_context_payload import PrimaryContextPayload


@dataclass(frozen=True, slots=True)
class MultimodalImageAudit:
    mime_type: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class MultimodalRuntimeCaseAudit:
    vector_id: str
    source_locator: str
    source_text_sha256: str | None
    images: tuple[MultimodalImageAudit, ...]
    predicted_label: str | None
    abstained: bool


@dataclass(frozen=True, slots=True)
class MultimodalBlindValidationRuntimeManifest:
    run_id: str
    model_provider: str
    model_name: str
    packet_sha256: str
    taxonomy_sha256: str
    case_count: int
    completed_count: int
    abstained_count: int
    image_case_count: int
    cases: tuple[MultimodalRuntimeCaseAudit, ...]
    promotion_allowed: bool = False


@dataclass(frozen=True, slots=True)
class ResumableBlindCase:
    decision: IndependentValidationDecision
    audit: MultimodalRuntimeCaseAudit


def _validate_resumed_case(
    *,
    resumed: ResumableBlindCase,
    vector_id: str,
    source_locator: str,
    text_sha: str | None,
    image_fingerprint: tuple[tuple[str, str, int], ...],
    taxonomy: tuple[str, ...],
) -> None:
    decision = resumed.decision
    audit = resumed.audit
    if decision.vector_id != vector_id or audit.vector_id != vector_id:
        raise ValueError(f"resume checkpoint vector mismatch for {vector_id}")
    if decision.source_locator != source_locator or audit.source_locator != source_locator:
        raise ValueError(f"resume checkpoint locator mismatch for {vector_id}")
    if decision.predicted_label is not None and decision.predicted_label not in taxonomy:
        raise ValueError(f"resume checkpoint label is outside frozen taxonomy for {vector_id}")
    if audit.predicted_label != decision.predicted_label or audit.abstained != decision.abstained:
        raise ValueError(f"resume checkpoint decision/audit mismatch for {vector_id}")
    if audit.source_text_sha256 != text_sha:
        raise ValueError(f"resume checkpoint primary text changed for {vector_id}")
    checkpoint_images = tuple((item.mime_type, item.sha256, item.size_bytes) for item in audit.images)
    if checkpoint_images != image_fingerprint:
        raise ValueError(f"resume checkpoint primary images changed for {vector_id}")


def execute_multimodal_blind_validation_runtime(
    *,
    run_id: str,
    model_provider: str,
    model_name: str,
    packet: BlindValidationPacket,
    agent: IndependentValidationAgent,
    source_context_resolver: Callable[[str], PrimaryContextPayload],
    resume_cases: Mapping[str, ResumableBlindCase] | None = None,
    on_case_completed: Callable[[int, int, IndependentValidationDecision, MultimodalRuntimeCaseAudit], None]
    | None = None,
) -> tuple[BlindValidationBatchResult, MultimodalBlindValidationRuntimeManifest]:
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

    resume = dict(resume_cases or {})
    packet_ids = {case.vector_id for case in packet.cases}
    unknown_resume_ids = set(resume) - packet_ids
    if unknown_resume_ids:
        raise ValueError("resume checkpoint contains vector IDs outside frozen packet")

    decisions = []
    audits: list[MultimodalRuntimeCaseAudit] = []
    fingerprints: dict[str, tuple[str | None, tuple[tuple[str, str, int], ...]]] = {}
    total = len(packet.cases)

    for position, case in enumerate(packet.cases, start=1):
        payload = source_context_resolver(case.source_locator).normalized()
        text_sha = hashlib.sha256(payload.text.encode("utf-8")).hexdigest() if payload.text else None
        image_fingerprint = tuple(
            (image.mime_type, image.sha256, image.size_bytes) for image in payload.images
        )
        fingerprint = (text_sha, image_fingerprint)
        previous = fingerprints.get(case.source_locator)
        if previous is not None and previous != fingerprint:
            raise ValueError(f"primary context changed within blind run for {case.source_locator}")
        fingerprints[case.source_locator] = fingerprint

        resumed = resume.get(case.vector_id)
        if resumed is not None:
            _validate_resumed_case(
                resumed=resumed,
                vector_id=case.vector_id,
                source_locator=case.source_locator,
                text_sha=text_sha,
                image_fingerprint=image_fingerprint,
                taxonomy=packet.taxonomy,
            )
            decision = resumed.decision
            audit = resumed.audit
        else:
            decision, _ = agent.validate_multimodal(
                vector_id=case.vector_id,
                source_locator=case.source_locator,
                source_context=payload,
                allowed_labels=packet.taxonomy,
                focus=case.focus,
            )
            audit = MultimodalRuntimeCaseAudit(
                vector_id=case.vector_id,
                source_locator=case.source_locator,
                source_text_sha256=text_sha,
                images=tuple(
                    MultimodalImageAudit(
                        mime_type=image.mime_type,
                        sha256=image.sha256,
                        size_bytes=image.size_bytes,
                    )
                    for image in payload.images
                ),
                predicted_label=decision.predicted_label,
                abstained=decision.abstained,
            )
            if on_case_completed is not None:
                on_case_completed(position, total, decision, audit)

        decisions.append(decision)
        audits.append(audit)

    taxonomy_encoded = json.dumps(
        list(packet.taxonomy), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    manifest = MultimodalBlindValidationRuntimeManifest(
        run_id=normalized_run_id,
        model_provider=provider,
        model_name=model,
        packet_sha256=blind_packet_sha256(packet),
        taxonomy_sha256=hashlib.sha256(taxonomy_encoded).hexdigest(),
        case_count=len(packet.cases),
        completed_count=len(audits),
        abstained_count=sum(item.abstained for item in audits),
        image_case_count=sum(bool(item.images) for item in audits),
        cases=tuple(audits),
        promotion_allowed=False,
    )
    return BlindValidationBatchResult(decisions=tuple(decisions)), manifest
