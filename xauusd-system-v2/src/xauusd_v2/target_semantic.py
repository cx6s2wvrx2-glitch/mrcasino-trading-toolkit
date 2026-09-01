from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TargetClass(StrEnum):
    CORE_BREAKOUT_LIQUIDITY = "core_breakout_liquidity"
    MAJOR_LIQUIDITY = "major_liquidity"
    OPPOSITE_LAOL = "opposite_laol"
    TRAIL_LEVEL = "trail_level"


class TargetState(StrEnum):
    MINIMUM_TARGET_ELIGIBLE = "minimum_target_eligible"
    CONTEXT_TARGET_CANDIDATE = "context_target_candidate"
    NOT_ELIGIBLE = "not_eligible"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class TargetResult:
    state: TargetState
    target_class: TargetClass
    reason: str


def evaluate_target(
    *,
    target_class: TargetClass,
    opposite_laol_or_poi_respected: bool | None,
    target_level_identified: bool | None,
    trail_selection_certified: bool | None = None,
) -> TargetResult:
    """Evaluate source-supported target classes without inventing trail selection.

    R-141 makes Core Breakout Liquidity the minimum target after the opposite
    LAOL/POI is respected. R-143 includes core + major + LAOL in target/timing.
    R-137 states prior trail steps become targets, but R-150 leaves the exact trail
    level selection rule unresolved; TRAIL_LEVEL therefore requires an explicit
    upstream certification flag.
    """
    if opposite_laol_or_poi_respected is None or target_level_identified is None:
        return TargetResult(TargetState.NOT_CERTIFIED, target_class, "target prerequisite evidence is missing")
    if not opposite_laol_or_poi_respected or not target_level_identified:
        return TargetResult(TargetState.NOT_ELIGIBLE, target_class, "target is not eligible before POI respect and level identification")

    if target_class is TargetClass.CORE_BREAKOUT_LIQUIDITY:
        return TargetResult(
            TargetState.MINIMUM_TARGET_ELIGIBLE,
            target_class,
            "R-141 identifies Core Breakout Liquidity as the minimum target after opposite LAOL/POI respect",
        )

    if target_class is TargetClass.TRAIL_LEVEL:
        if trail_selection_certified is None:
            return TargetResult(
                TargetState.NOT_CERTIFIED,
                target_class,
                "R-150 trail-level selection remains unresolved",
            )
        if not trail_selection_certified:
            return TargetResult(TargetState.NOT_ELIGIBLE, target_class, "selected trail level has not passed certification")

    return TargetResult(
        TargetState.CONTEXT_TARGET_CANDIDATE,
        target_class,
        "source-recognized contextual target; exact timing/selection remains downstream",
    )
