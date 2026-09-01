from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class LiquidityKind(StrEnum):
    BIG_WICK_TO_FILL = "big_wick_to_fill"
    UNMANIPULATED_DOJI = "unmanipulated_doji"
    BREAKOUT = "breakout"
    ATT_FU = "att_fu"


class LiquidityMarkingRole(StrEnum):
    CORE = "core"
    ADVANCED_OPTIONAL = "advanced_optional"
    REFINEMENT_CONTEXT = "refinement_context"
    OUTSIDE_R207_SCOPE = "outside_r207_scope"


@dataclass(frozen=True, slots=True)
class LiquidityTaxonomyResult:
    kind: LiquidityKind
    timeframe_minutes: int
    role: LiquidityMarkingRole
    reason: str


def classify_r207_liquidity_role(*, kind: LiquidityKind, timeframe_minutes: int) -> LiquidityTaxonomyResult:
    """Preserve the later Reflection R-207 scope for 30m+ liquidity marking.

    This function does not erase older source lists. It applies the newer operational
    rule specifically to the 30m+ core-marking workflow:
      - core: unfilled big wick, unmanipulated doji
      - breakout: optional/advanced
      - ATT-FU liquidity: refinement/concentrated-area context, not core marking
    """
    if timeframe_minutes <= 0:
        raise ValueError("timeframe_minutes must be positive")
    if timeframe_minutes < 30:
        return LiquidityTaxonomyResult(
            kind,
            timeframe_minutes,
            LiquidityMarkingRole.OUTSIDE_R207_SCOPE,
            "R-207 core marking rule is explicitly scoped to 30min+",
        )
    if kind in {LiquidityKind.BIG_WICK_TO_FILL, LiquidityKind.UNMANIPULATED_DOJI}:
        return LiquidityTaxonomyResult(
            kind,
            timeframe_minutes,
            LiquidityMarkingRole.CORE,
            "R-207 core 30m+ liquidity type",
        )
    if kind is LiquidityKind.BREAKOUT:
        return LiquidityTaxonomyResult(
            kind,
            timeframe_minutes,
            LiquidityMarkingRole.ADVANCED_OPTIONAL,
            "R-207 makes breakout liquidity optional/advanced",
        )
    return LiquidityTaxonomyResult(
        kind,
        timeframe_minutes,
        LiquidityMarkingRole.REFINEMENT_CONTEXT,
        "R-207 references ATT-FU liquidity in concentrated-area refinement context rather than core marking",
    )
