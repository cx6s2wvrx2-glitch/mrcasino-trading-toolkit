from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ClassicZoneState(StrEnum):
    POTENTIAL_NOT_CONFIRMED = "potential_not_confirmed"
    CONFIRMED_SAME_TF = "confirmed_same_tf"
    ZONE_OF_MANIPULATION = "zone_of_manipulation"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class ClassicZoneConfirmationResult:
    state: ClassicZoneState
    confirmed_for_same_tf_moves: bool
    reason: str


def evaluate_classic_zone_confirmation(
    *,
    first_same_tf_reaction: bool | None,
    manipulated_lower_tf_reaction: bool | None,
) -> ClassicZoneConfirmationResult:
    """Apply the older primary Zones-source confirmation boundary only.

    This module is intentionally separate from later Reflection zone lifecycle rules.
    The older source states:
    - first same-TF reaction makes the zone relevant for future same-TF moves;
    - without that same-TF reaction, a manipulated LTF reaction is called a zone of manipulation;
    - until the first reaction, the zone is only potential/not confirmed.
    """
    if first_same_tf_reaction is None or manipulated_lower_tf_reaction is None:
        return ClassicZoneConfirmationResult(
            ClassicZoneState.NOT_CERTIFIED,
            False,
            "same-TF and lower-TF reaction evidence are both required",
        )

    if first_same_tf_reaction:
        return ClassicZoneConfirmationResult(
            ClassicZoneState.CONFIRMED_SAME_TF,
            True,
            "first same-timeframe reaction confirms relevance for future same-TF moves",
        )

    if manipulated_lower_tf_reaction:
        return ClassicZoneConfirmationResult(
            ClassicZoneState.ZONE_OF_MANIPULATION,
            False,
            "without same-TF confirmation, manipulated lower-TF reaction is a zone of manipulation",
        )

    return ClassicZoneConfirmationResult(
        ClassicZoneState.POTENTIAL_NOT_CONFIRMED,
        False,
        "until the first reaction the zone remains potential and not confirmed",
    )
