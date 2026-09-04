from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BetaIntraDirection(StrEnum):
    BULL = "bull"
    BEAR = "bear"


@dataclass(frozen=True, slots=True)
class BetaIntraEMComponents:
    third: bool = False
    first: bool = False
    laol: bool = False
    sn_double: bool = False
    tbe: bool = False
    hcs: bool = False
    hcs_forming: bool = False

    @property
    def any_em(self) -> bool:
        return any((self.third, self.first, self.laol, self.sn_double, self.tbe, self.hcs, self.hcs_forming))

    @property
    def contains_hcs(self) -> bool:
        return self.hcs or self.hcs_forming


@dataclass(frozen=True, slots=True)
class BetaIntraNegatingManipulation:
    detected: bool
    direction: BetaIntraDirection | None
    forming: bool
    confirmed: bool
    contains_hcs_component: bool
    reason: str
    supplied_code_behavior_only: bool = True
    strategy_semantics_certified: bool = False


def evaluate_beta_intra_negating_manipulation(
    *,
    last_valid_direction: BetaIntraDirection | None,
    last_valid_broken: bool,
    candidate_direction: BetaIntraDirection,
    components: BetaIntraEMComponents,
    candidate_confirmed: bool,
) -> BetaIntraNegatingManipulation:
    """Shadow BETA's opposite established-manipulation detection.

    BETA checks for a bearish negating manipulation when the latest valid direction
    is bull, and vice versa, provided the latest valid structure is not broken. The
    opposite candidate can be composed from third/first/LAOL/double-SN/TBE/HCS
    established-manipulation states.
    """

    if last_valid_direction is None:
        return _none("BETA has no latest valid direction to negate")
    if last_valid_broken:
        return _none("BETA suppresses this negation check when latest valid structure is broken")
    if candidate_direction is last_valid_direction:
        return _none("candidate established manipulation is not opposite the latest valid direction")
    if not components.any_em:
        return _none("no opposite established-manipulation component detected")

    return BetaIntraNegatingManipulation(
        detected=True,
        direction=candidate_direction,
        forming=not candidate_confirmed,
        confirmed=candidate_confirmed,
        contains_hcs_component=components.contains_hcs,
        reason="opposite BETA established manipulation detected against latest valid direction",
    )


def beta_negation_has_hcs_context(
    *,
    bear_hcs_retesting: bool,
    bull_hcs_retesting: bool,
    same_direction_em_form_found: bool,
    negating_pattern_contains_hcs: bool,
) -> bool:
    """Faithfully represent BETA's ``*_neg_hcs_condition`` gate."""

    return (
        bear_hcs_retesting
        or bull_hcs_retesting
        or (same_direction_em_form_found and negating_pattern_contains_hcs)
    )


def _none(reason: str) -> BetaIntraNegatingManipulation:
    return BetaIntraNegatingManipulation(
        detected=False,
        direction=None,
        forming=False,
        confirmed=False,
        contains_hcs_component=False,
        reason=reason,
    )
