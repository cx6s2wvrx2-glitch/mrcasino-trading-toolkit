from __future__ import annotations

from dataclasses import dataclass

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
    """Compare blind Agent-06 outputs only after the blind run is complete.

    This layer is deterministic and intentionally separate from Agent 06. It never
    grants VERIFIED status. Dataset promotion remains governed by `validation.py`
    and the dataset's own `promotion_allowed` flag.
    """
    predictions = batch.predictions
    expected_ids = {vector.id for vector in dataset.vectors}
    extra_ids = set(predictions) - expected_ids
    if extra_ids:
        raise ValueError(f"blind batch contains unknown vector ids: {sorted(extra_ids)!r}")

    outcomes = compare_predictions(dataset, predictions)
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
