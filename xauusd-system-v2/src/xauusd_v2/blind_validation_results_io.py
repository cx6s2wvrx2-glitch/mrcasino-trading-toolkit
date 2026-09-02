from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .agents.validation_agent import IndependentValidationDecision
from .blind_validation_runner import BlindValidationBatchResult


@dataclass(frozen=True, slots=True)
class BlindPredictionFile:
    run_id: str
    model_provider: str
    model_name: str
    packet_sha256: str
    taxonomy_sha256: str
    case_count: int
    batch: BlindValidationBatchResult


_TOP_LEVEL_KEYS = {
    "version",
    "run_id",
    "model_provider",
    "model_name",
    "packet_sha256",
    "taxonomy_sha256",
    "case_count",
    "decisions",
    "ground_truth_loaded_by_this_process",
    "comparison_performed_by_this_process",
    "promotion_allowed",
}
_DECISION_KEYS = {
    "vector_id",
    "source_locator",
    "predicted_label",
    "confidence",
    "evidence",
    "ambiguities",
}


def load_blind_predictions(path: str | Path) -> BlindPredictionFile:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != _TOP_LEVEL_KEYS:
        raise ValueError("blind predictions top-level schema mismatch")
    if raw.get("version") != 1:
        raise ValueError("unsupported blind predictions version")
    if raw.get("ground_truth_loaded_by_this_process") is not False:
        raise ValueError("blind predictions do not prove ground-truth isolation")
    if raw.get("comparison_performed_by_this_process") is not False:
        raise ValueError("blind predictions indicate comparison occurred during blind run")
    if raw.get("promotion_allowed") is not False:
        raise ValueError("blind predictions must never allow promotion")

    run_id = str(raw.get("run_id", "")).strip()
    provider = str(raw.get("model_provider", "")).strip()
    model = str(raw.get("model_name", "")).strip()
    packet_sha256 = str(raw.get("packet_sha256", "")).strip().lower()
    taxonomy_sha256 = str(raw.get("taxonomy_sha256", "")).strip().lower()
    if not run_id or not provider or not model:
        raise ValueError("blind predictions require run/provider/model metadata")
    for name, digest in (("packet_sha256", packet_sha256), ("taxonomy_sha256", taxonomy_sha256)):
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError(f"invalid {name}")

    decisions_raw = raw.get("decisions")
    if not isinstance(decisions_raw, list) or not decisions_raw:
        raise ValueError("blind predictions require decisions")
    declared_count = raw.get("case_count")
    if not isinstance(declared_count, int) or declared_count != len(decisions_raw):
        raise ValueError("blind predictions case_count mismatch")

    decisions: list[IndependentValidationDecision] = []
    seen_ids: set[str] = set()
    for item in decisions_raw:
        if not isinstance(item, dict) or set(item) != _DECISION_KEYS:
            raise ValueError("blind prediction decision schema mismatch")
        vector_id = str(item.get("vector_id", "")).strip()
        source_locator = str(item.get("source_locator", "")).strip()
        if not vector_id or not source_locator:
            raise ValueError("blind prediction requires vector_id and source_locator")
        if vector_id in seen_ids:
            raise ValueError(f"duplicate blind prediction vector id: {vector_id}")
        seen_ids.add(vector_id)

        raw_label = item.get("predicted_label")
        predicted_label = None if raw_label is None else str(raw_label).strip() or None
        confidence = float(item.get("confidence", 0.0))
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("blind prediction confidence must be between 0 and 1")

        evidence_raw = item.get("evidence")
        ambiguities_raw = item.get("ambiguities")
        if not isinstance(evidence_raw, list) or not isinstance(ambiguities_raw, list):
            raise ValueError("blind prediction evidence/ambiguities must be arrays")
        evidence = tuple(str(value).strip() for value in evidence_raw if str(value).strip())
        ambiguities = tuple(str(value).strip() for value in ambiguities_raw if str(value).strip())
        decisions.append(
            IndependentValidationDecision(
                vector_id=vector_id,
                source_locator=source_locator,
                predicted_label=predicted_label,
                confidence=confidence,
                evidence=evidence,
                ambiguities=ambiguities,
            )
        )

    return BlindPredictionFile(
        run_id=run_id,
        model_provider=provider,
        model_name=model,
        packet_sha256=packet_sha256,
        taxonomy_sha256=taxonomy_sha256,
        case_count=declared_count,
        batch=BlindValidationBatchResult(decisions=tuple(decisions)),
    )
