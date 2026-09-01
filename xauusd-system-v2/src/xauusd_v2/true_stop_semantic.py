from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TrueStopState(StrEnum):
    MAIN_POI_CANDIDATE = "main_poi_candidate"
    RESPECTED = "respected"
    NOT_TRUE_STOP = "not_true_stop"
    NOT_CERTIFIED = "not_certified"


class TrueStopEntryState(StrEnum):
    ENTRY_CANDIDATE = "entry_candidate"
    WAIT = "wait"
    NOT_CERTIFIED = "not_certified"


class LTFTrigger(StrEnum):
    HCS = "hcs"
    NEGATION = "negation"


@dataclass(frozen=True, slots=True)
class TrueStopResult:
    state: TrueStopState
    reason: str


@dataclass(frozen=True, slots=True)
class TrueStopEntryResult:
    state: TrueStopEntryState
    trigger: LTFTrigger | None
    reason: str


def evaluate_true_stop_main_poi(
    *,
    all_required_10m_plus_tfs_factors_aligned: bool | None,
    ten_min_plus_hcs_or_negation_manipulation_present: bool | None,
) -> TrueStopResult:
    """Evaluate R-108's True Stop/Main POI definition at semantic level.

    True Stop is the low/high where all required 10min+ TFS factors align; each
    true PA wave is represented by 10min+ HCS/negation manipulation. The exact
    price level is supplied upstream by certified structure detectors.
    """
    if all_required_10m_plus_tfs_factors_aligned is None or ten_min_plus_hcs_or_negation_manipulation_present is None:
        return TrueStopResult(TrueStopState.NOT_CERTIFIED, "required 10min+ True Stop evidence is incomplete")
    if not all_required_10m_plus_tfs_factors_aligned or not ten_min_plus_hcs_or_negation_manipulation_present:
        return TrueStopResult(
            TrueStopState.NOT_TRUE_STOP,
            "R-108 requires aligned 10min+ TFS factors and 10min+ HCS/negation manipulation",
        )
    return TrueStopResult(
        TrueStopState.MAIN_POI_CANDIDATE,
        "all required 10min+ TFS factors align at a manipulation-defined Main POI",
    )


def evaluate_true_stop_respect(*, main_poi_confirmed: bool | None, price_respected_poi: bool | None) -> TrueStopResult:
    """Separate True Stop existence from later respect/hold behavior."""
    if main_poi_confirmed is None or price_respected_poi is None:
        return TrueStopResult(TrueStopState.NOT_CERTIFIED, "True Stop respect evidence is incomplete")
    if not main_poi_confirmed:
        return TrueStopResult(TrueStopState.NOT_TRUE_STOP, "no confirmed Main POI exists to evaluate")
    if not price_respected_poi:
        return TrueStopResult(TrueStopState.NOT_TRUE_STOP, "candidate Main POI was not respected")
    return TrueStopResult(TrueStopState.RESPECTED, "confirmed Main POI was respected")


def evaluate_true_stop_entry(
    *,
    true_stop_respected: bool | None,
    ltf_trigger: LTFTrigger | None,
    final_liquidity_calculation_resolved: bool | None,
) -> TrueStopEntryResult:
    """Apply R-108's downstream entry requirements.

    LTF HCS/negation is allowed only after True Stop respect and final liquidity
    calculation. This returns an entry candidate only; risk/execution remain
    downstream and cannot be authorized here.
    """
    if true_stop_respected is None or final_liquidity_calculation_resolved is None or ltf_trigger is None:
        return TrueStopEntryResult(TrueStopEntryState.NOT_CERTIFIED, ltf_trigger, "required True Stop entry evidence is missing")
    if not true_stop_respected or not final_liquidity_calculation_resolved:
        return TrueStopEntryResult(TrueStopEntryState.WAIT, ltf_trigger, "True Stop respect and final liquidity calculation must both be satisfied")
    return TrueStopEntryResult(
        TrueStopEntryState.ENTRY_CANDIDATE,
        ltf_trigger,
        "respected True Stop + LTF HCS/negation + final liquidity calculation; downstream risk gate still required",
    )
