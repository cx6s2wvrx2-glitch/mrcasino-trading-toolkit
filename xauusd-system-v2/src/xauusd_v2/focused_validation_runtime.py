from __future__ import annotations

import hashlib
import json
from typing import Callable, Mapping

from .agents.validation_agent import IndependentValidationAgent, IndependentValidationDecision
from .blind_validation_multimodal_runtime import (
    MultimodalBlindValidationRuntimeManifest,
    MultimodalImageAudit,
    MultimodalRuntimeCaseAudit,
    ResumableBlindCase,
    _validate_resumed_case,
)
from .blind_validation_runner import BlindValidationBatchResult
from .focused_validation_packet import FocusedValidationPacket, focused_packet_sha256
from .primary_context_payload import PrimaryContextPayload


def execute_focused_validation_runtime(
    *,
    run_id: str,
    model_provider: str,
    model_name: str,
    packet: FocusedValidationPacket,
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
        raise ValueError("focused packet must contain cases")

    resume = dict(resume_cases or {})
    packet_ids = {case.vector_id for case in packet.cases}
    unknown_resume_ids = set(resume) - packet_ids
    if unknown_resume_ids:
        raise ValueError("resume checkpoint contains vector IDs outside focused packet")

    decisions: list[IndependentValidationDecision] = []
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
            raise ValueError(f"primary context changed within focused run for {case.source_locator}")
        fingerprints[case.source_locator] = fingerprint

        resumed = resume.get(case.vector_id)
        if resumed is not None:
            _validate_resumed_case(
                resumed=resumed,
                vector_id=case.vector_id,
                source_locator=case.source_locator,
                text_sha=text_sha,
                image_fingerprint=image_fingerprint,
                taxonomy=packet.verdict_taxonomy,
            )
            decision = resumed.decision
            audit = resumed.audit
        else:
            decision, _ = agent.validate_multimodal(
                vector_id=case.vector_id,
                source_locator=case.source_locator,
                source_context=payload,
                allowed_labels=packet.verdict_taxonomy,
                focus=case.candidate_claim,
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
        list(packet.verdict_taxonomy),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    manifest = MultimodalBlindValidationRuntimeManifest(
        run_id=normalized_run_id,
        model_provider=provider,
        model_name=model,
        packet_sha256=focused_packet_sha256(packet),
        taxonomy_sha256=hashlib.sha256(taxonomy_encoded).hexdigest(),
        case_count=len(packet.cases),
        completed_count=len(audits),
        abstained_count=sum(item.abstained for item in audits),
        image_case_count=sum(bool(item.images) for item in audits),
        cases=tuple(audits),
        promotion_allowed=False,
    )
    return BlindValidationBatchResult(decisions=tuple(decisions)), manifest
