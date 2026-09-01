from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class X3State(StrEnum):
    CONFIRMED = "confirmed"
    NOT_X3 = "not_x3"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class X3Result:
    state: X3State
    fu_characteristics_same_candle: bool | None
    negation_characteristics_same_candle: bool | None
    reason: str


def evaluate_x3_primitive(
    *,
    fu_characteristics_same_candle: bool | None,
    negation_characteristics_same_candle: bool | None,
) -> X3Result:
    """Implement final Reflection R-213 x3 semantics.

    R-213 supersedes older geometric guesses: x3 is a candle containing BOTH FU
    and negation characteristics at macro level in the same candle. Upstream raw
    detectors must establish those characteristics separately; no range/body-count
    heuristic is invented here.
    """
    if fu_characteristics_same_candle is None or negation_characteristics_same_candle is None:
        return X3Result(
            X3State.NOT_CERTIFIED,
            fu_characteristics_same_candle,
            negation_characteristics_same_candle,
            "both FU and negation characteristic evidence are required",
        )
    if fu_characteristics_same_candle and negation_characteristics_same_candle:
        return X3Result(
            X3State.CONFIRMED,
            True,
            True,
            "same candle contains both FU and negation characteristics per final R-213 definition",
        )
    return X3Result(
        X3State.NOT_X3,
        fu_characteristics_same_candle,
        negation_characteristics_same_candle,
        "both source-required characteristics are not present in the same candle",
    )
