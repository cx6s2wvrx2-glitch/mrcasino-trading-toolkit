from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .blind_validation_runner import BlindValidationBatchResult
from .validation import GroundTruthDataset, ValidationOutcome, compare_predictions


@dataclass(frozen=True, slots=True)
class BlindValidationComparisonReport:
    outcomes: tuple[ValidationOutcome, ...]
    agree: int
    disagree: int
    ambiguous: int
    total: int
    all_agree: bool
    promotion_allowed: bool = False


def compare_blind_batch(
    *,
    dataset: GroundTruthDataset,
    batch: BlindValidationBatchResult,
) -> BlindValidationComparisonReport:
    """Backward-compatible comparison for one ground-truth dataset."""
    return compare_blind_multi_batch(datasets=(dataset,), batch=batch)


def compare_blind_multi_batch(
    *,
    datasets: Iterable[GroundTruthDataset],
    batch: BlindValidationBatchResult,
) -> BlindValidationComparisonReport:
    """Compare one completed blind batch against multiple datasets afterwards.

    Agent 06 never sees this layer. Duplicate vector IDs across datasets are rejected,
    unknown predictions are rejected, and missing predictions become AMBIGUOUS through
    the existing deterministic ground-truth comparator. Agreement never promotes.
    """
    items = tuple(datasets)
    if not items:
        raise ValueError("at least one ground-truth dataset is required")

    expected_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    for dataset in items:
        for vector in dataset.vectors:
            if vector.id in expected_ids:
                duplicate_ids.add(vector.id)
            expected_ids.add(vector.id)
    if duplicate_ids:
        raise ValueError(f"duplicate vector ids across comparison datasets: {sorted(duplicate_ids)!r}")

    predictions = batch.predictions
    extra_ids = set(predictions) - expected_ids
    if extra_ids:
        raise ValueError(f"blind batch contains unknown vector ids: {sorted(extra_ids)!r}")

    outcomes = tuple(
        outcome
        for dataset in items
        for outcome in compare_predictions(dataset, predictions)
    )
    agree = sum(outcome.result == "AGREE" for outcome in outcomes)
    disagree = sum(outcome.result == "DISAGREE" for outcome in outcomes)
    ambiguous = sum(outcome.result == "AMBIGUOUS" for outcome in outcomes)
    total = len(outcomes)

    return BlindValidationComparisonReport(
        outcomes=outcomes,
        agree=agree,
        disagree=disagree,
        ambiguous=ambiguous,
        total=total,
        all_agree=bool(outcomes) and disagree == 0 and ambiguous == 0,
        promotion_allowed=False,
    )
