from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FURetestQualityState(StrEnum):
    STRONGEST = "strongest"
    STRONGER = "stronger"
    WEAK = "weak"
    BELOW_MINIMUM = "below_minimum"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class FURetestQualityResult:
    state: FURetestQualityState
    retest_counts: bool | None
    numeric_full_fu_fib_used: bool
    reason: str


def classify_fu_retest_quality(
    *,
    fu_wick_touched: bool | None,
    half_fu_wick_touched: bool | None,
    past_70_full_fu_fib: bool | None,
    full_fu_fib_anchor_certified: bool,
) -> FURetestQualityResult:
    """Implement only the source-confirmed portion of Reflection R-54.

    Source hierarchy:
    - touching 50% of the FU wick = STRONGEST;
    - touching the FU wick = STRONGER;
    - past 70% fib of the full FU without wick touch = WEAK but still counts.

    The compiled Reflection Master never explicitly defines the 0/100 anchor
    orientation of the full-candle fib. Therefore the 70% branch is unusable as a
    numeric detector until `full_fu_fib_anchor_certified=True` is supplied by a
    separately certified source/geometry layer. Wick-based branches do not require
    that unresolved anchor.
    """
    if fu_wick_touched is None or half_fu_wick_touched is None:
        return FURetestQualityResult(
            FURetestQualityState.NOT_CERTIFIED,
            None,
            False,
            "wick-touch evidence is incomplete",
        )

    if half_fu_wick_touched and not fu_wick_touched:
        return FURetestQualityResult(
            FURetestQualityState.NOT_CERTIFIED,
            None,
            False,
            "50%-of-wick touch is inconsistent with FU-wick touch being false",
        )

    if half_fu_wick_touched:
        return FURetestQualityResult(
            FURetestQualityState.STRONGEST,
            True,
            False,
            "Reflection R-54: touching 50% of the FU wick is the strongest retest grade",
        )

    if fu_wick_touched:
        return FURetestQualityResult(
            FURetestQualityState.STRONGER,
            True,
            False,
            "Reflection R-54: touching the FU wick is the stronger retest grade",
        )

    if not full_fu_fib_anchor_certified:
        return FURetestQualityResult(
            FURetestQualityState.NOT_CERTIFIED,
            None,
            False,
            "R-54 70%-of-full-FU branch is blocked because the full-candle fib 0/100 anchor remains unresolved",
        )

    if past_70_full_fu_fib is None:
        return FURetestQualityResult(
            FURetestQualityState.NOT_CERTIFIED,
            None,
            True,
            "certified fib geometry exists but 70% interaction evidence is missing",
        )

    if past_70_full_fu_fib:
        return FURetestQualityResult(
            FURetestQualityState.WEAK,
            True,
            True,
            "Reflection R-54: past 70% of the full FU without wick touch is a weak retest that still counts",
        )

    return FURetestQualityResult(
        FURetestQualityState.BELOW_MINIMUM,
        False,
        True,
        "with certified full-FU fib geometry, a no-wick retest that does not pass 70% is below the R-54 close-enough boundary",
    )
