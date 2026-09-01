from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class HCSNodeType(StrEnum):
    STRONG_FU = "strong_fu"
    ATTEMPTED_FU = "attempted_fu"
    FU_NEGATION = "fu_negation"


class HCSRetestState(StrEnum):
    EXACT_WICK = "exact_wick"
    NEAR_ENOUGH_SOURCE_CONFIRMED = "near_enough_source_confirmed"
    NO_RETEST = "no_retest"
    UNKNOWN = "unknown"


class HCSState(StrEnum):
    CONFIRMED = "confirmed"
    NOT_HCS = "not_hcs"
    NOT_CERTIFIED = "not_certified"


class HCSStrength(StrEnum):
    EXPLICIT_STRONGEST = "explicit_strongest"
    EXPLICIT_WEAKER = "explicit_weaker"
    UNRANKED = "unranked"


@dataclass(frozen=True, slots=True)
class HCSResult:
    state: HCSState
    strength: HCSStrength | None
    first_node: HCSNodeType
    second_node: HCSNodeType
    retest_state: HCSRetestState
    reason: str


def _source_strength(first: HCSNodeType, second: HCSNodeType) -> HCSStrength:
    nodes = {first, second}
    if first is HCSNodeType.STRONG_FU and second is HCSNodeType.STRONG_FU:
        return HCSStrength.EXPLICIT_STRONGEST
    if nodes == {HCSNodeType.ATTEMPTED_FU, HCSNodeType.FU_NEGATION}:
        return HCSStrength.EXPLICIT_WEAKER
    return HCSStrength.UNRANKED


def evaluate_hcs(
    *,
    first_node: HCSNodeType,
    second_node: HCSNodeType,
    retest_state: HCSRetestState,
) -> HCSResult:
    """Evaluate the approved HCS grammar without inventing a distance tolerance.

    R-125 defines HCS as a new FU formed on the retest of the last FU wick. The
    approved HCS source allows Strong FU, Attempted FU and FU negation forms.
    R-128 permits a 'near enough' HCS in context, but gives no numeric threshold;
    therefore near-enough is accepted only when supplied as source-confirmed
    semantic evidence, never computed here from a hidden price tolerance.
    """
    if retest_state is HCSRetestState.UNKNOWN:
        return HCSResult(
            HCSState.NOT_CERTIFIED,
            None,
            first_node,
            second_node,
            retest_state,
            "retest evidence is unknown; numeric near-enough tolerance is not certified",
        )
    if retest_state is HCSRetestState.NO_RETEST:
        return HCSResult(
            HCSState.NOT_HCS,
            None,
            first_node,
            second_node,
            retest_state,
            "second manipulation did not retest the last FU wick area",
        )

    return HCSResult(
        HCSState.CONFIRMED,
        _source_strength(first_node, second_node),
        first_node,
        second_node,
        retest_state,
        "eligible manipulation node formed on an exact or source-confirmed near-enough retest",
    )
