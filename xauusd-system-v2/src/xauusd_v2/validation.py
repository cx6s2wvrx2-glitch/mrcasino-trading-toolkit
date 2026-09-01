from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


ALLOWED_EXPECTED_CLASSES = {"valid", "invalid", "edge_case", "neutral"}
ALLOWED_RESULTS = {"AGREE", "DISAGREE", "AMBIGUOUS"}


@dataclass(frozen=True, slots=True)
class GroundTruthVector:
    id: str
    source_locator: str
    expected_label: str
    expected_class: str
    evidence: tuple[str, ...]
    forbidden_inference: str

    @property
    def image_file(self) -> str:
        """Backward-compatible alias for Round 01 datasets."""
        return self.source_locator


@dataclass(frozen=True, slots=True)
class GroundTruthDataset:
    name: str
    status: str
    source_episode: str
    promotion_allowed: bool
    vectors: tuple[GroundTruthVector, ...]


@dataclass(frozen=True, slots=True)
class ValidationOutcome:
    vector_id: str
    result: str
    expected_label: str
    predicted_label: str | None


def load_ground_truth(path: str | Path) -> GroundTruthDataset:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))

    raw_vectors = payload.get("test_vectors", [])
    if not raw_vectors:
        raise ValueError("ground-truth dataset must contain test_vectors")

    vectors: list[GroundTruthVector] = []
    seen_ids: set[str] = set()

    for raw in raw_vectors:
        vector_id = str(raw["id"]).strip()
        if not vector_id or vector_id in seen_ids:
            raise ValueError(f"duplicate or empty vector id: {vector_id!r}")
        seen_ids.add(vector_id)

        expected_class = str(raw["expected_class"]).strip()
        if expected_class not in ALLOWED_EXPECTED_CLASSES:
            raise ValueError(f"unsupported expected_class: {expected_class}")

        expected_label = str(raw["expected_label"]).strip()
        if not expected_label:
            raise ValueError(f"missing expected_label for {vector_id}")

        evidence = tuple(str(item).strip() for item in raw.get("evidence", []) if str(item).strip())
        if not evidence:
            raise ValueError(f"missing evidence for {vector_id}")

        source_locator = str(raw.get("source_locator") or raw.get("image_file") or "").strip()
        if not source_locator:
            raise ValueError(f"missing source_locator/image_file for {vector_id}")

        vectors.append(
            GroundTruthVector(
                id=vector_id,
                source_locator=source_locator,
                expected_label=expected_label,
                expected_class=expected_class,
                evidence=evidence,
                forbidden_inference=str(raw.get("forbidden_inference", "")).strip(),
            )
        )

    return GroundTruthDataset(
        name=str(payload["dataset"]),
        status=str(payload["status"]),
        source_episode=str(payload["source_episode"]),
        promotion_allowed=bool(payload.get("promotion_allowed", False)),
        vectors=tuple(vectors),
    )


def compare_predictions(
    dataset: GroundTruthDataset,
    predictions: Mapping[str, str | None],
) -> tuple[ValidationOutcome, ...]:
    outcomes: list[ValidationOutcome] = []

    for vector in dataset.vectors:
        predicted = predictions.get(vector.id)
        if predicted is None or not str(predicted).strip():
            result = "AMBIGUOUS"
            normalized_prediction = None
        else:
            normalized_prediction = str(predicted).strip()
            result = "AGREE" if normalized_prediction == vector.expected_label else "DISAGREE"

        outcomes.append(
            ValidationOutcome(
                vector_id=vector.id,
                result=result,
                expected_label=vector.expected_label,
                predicted_label=normalized_prediction,
            )
        )

    return tuple(outcomes)


def can_promote_dataset(
    dataset: GroundTruthDataset,
    outcomes: tuple[ValidationOutcome, ...],
    *,
    blind_independent_validator: bool,
    historical_reproducible: bool,
) -> bool:
    """Fail closed: agreement alone is never enough for VERIFIED promotion."""
    if not dataset.promotion_allowed:
        return False
    if not blind_independent_validator or not historical_reproducible:
        return False
    return bool(outcomes) and all(outcome.result == "AGREE" for outcome in outcomes)
