from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math


class AcceptedRRState(StrEnum):
    SOURCE_CONCEPT_ONLY = "source_concept_only"
    NUMERIC_RULE_CANDIDATE = "numeric_rule_candidate"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class AcceptedRRResult:
    state: AcceptedRRState
    numeric_threshold_usable: bool
    reason: str


def evaluate_accepted_rr(
    *,
    source_concept_explicit: bool | None,
    rr_threshold: float | None = None,
    threshold_definition_certified: bool = False,
) -> AcceptedRRResult:
    """Preserve Reflection R-116 without inventing a fixed RR threshold.

    The approved corpus explicitly uses the phrase ``Accepted RR`` in the
    advanced x3 entry model, but does not define a numeric cutoff or formula.
    Therefore a number is never usable merely because it was supplied by a
    caller. A future numeric rule requires its own certified primary definition.
    """
    if source_concept_explicit is None:
        return AcceptedRRResult(
            AcceptedRRState.NOT_CERTIFIED,
            False,
            "evidence that the approved source explicitly uses Accepted RR is missing",
        )

    if rr_threshold is not None:
        if not math.isfinite(rr_threshold) or rr_threshold <= 0:
            raise ValueError("rr_threshold must be a positive finite value")
        if not threshold_definition_certified:
            return AcceptedRRResult(
                AcceptedRRState.NOT_CERTIFIED,
                False,
                "R-116 does not define a numeric Accepted RR threshold; supplied values cannot become strategy rules",
            )
        if not source_concept_explicit:
            return AcceptedRRResult(
                AcceptedRRState.NOT_CERTIFIED,
                False,
                "a certified numeric threshold cannot be attached to an unconfirmed source concept",
            )
        return AcceptedRRResult(
            AcceptedRRState.NUMERIC_RULE_CANDIDATE,
            True,
            "numeric threshold has separate certified source-definition evidence; still requires normal V2 promotion gates",
        )

    if not source_concept_explicit:
        return AcceptedRRResult(
            AcceptedRRState.NOT_CERTIFIED,
            False,
            "Accepted RR is not explicitly evidenced in the supplied source context",
        )

    return AcceptedRRResult(
        AcceptedRRState.SOURCE_CONCEPT_ONLY,
        False,
        "R-116 confirms the phrase Accepted RR but provides no numeric cutoff or formula",
    )
