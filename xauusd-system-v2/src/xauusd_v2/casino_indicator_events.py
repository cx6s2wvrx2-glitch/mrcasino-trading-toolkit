from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .casino_directional_marker_semantics import (
    CasinoMarkerDirection,
    CasinoMarkerVisualCue,
    directional_marker_from_legacy_helper_class,
)
from .helper_fu_shadow import HelperFUClass


class CasinoIndicatorEventKind(StrEnum):
    STRONG_FU = "strong_fu"
    ATTEMPTED_FU = "attempted_fu"
    FU_NEGATION = "fu_negation"
    HCS = "hcs"
    HCS_NEGATION = "hcs_negation"
    HCS_RETEST = "hcs_retest"


class CasinoIndicatorEventSource(StrEnum):
    SUPPLIED_CASINO_HELPER = "supplied_casino_helper"
    SUPPLIED_BETA_STATE_MACHINE = "supplied_beta_state_machine"
    USER_CLARIFIED_VISUAL = "user_clarified_visual"


@dataclass(frozen=True, slots=True)
class CasinoIndicatorEvent:
    kind: CasinoIndicatorEventKind
    direction: CasinoMarkerDirection
    source: CasinoIndicatorEventSource
    marker_text: str | None = None
    visual_cue: CasinoMarkerVisualCue | None = None
    hcs_count: int | None = None
    relation_to_prior_event: str | None = None
    implementation_event_observed: bool = True
    strategy_semantics_certified: bool = False


def fu_event_from_legacy_helper_output(
    *,
    direction: CasinoMarkerDirection,
    helper_class: HelperFUClass,
) -> CasinoIndicatorEvent | None:
    """Translate the supplied Casino helper's FU/ATT output into event vocabulary."""

    marker = directional_marker_from_legacy_helper_class(
        direction=direction,
        helper_class=helper_class,
    )
    if marker is None:
        return None

    kind = (
        CasinoIndicatorEventKind.STRONG_FU
        if helper_class is HelperFUClass.FU
        else CasinoIndicatorEventKind.ATTEMPTED_FU
    )
    return CasinoIndicatorEvent(
        kind=kind,
        direction=direction,
        source=CasinoIndicatorEventSource.SUPPLIED_CASINO_HELPER,
        marker_text=marker.marker.value,
        visual_cue=marker.visual_cue,
    )


def beta_hcs_event(
    *,
    direction: CasinoMarkerDirection,
    hcs_count: int,
) -> CasinoIndicatorEvent:
    """Represent the supplied BETA state machine's HCS counter output.

    BETA increments ``hcs_count`` when a new FU/SN interaction qualifies against
    a tracked same-direction FU/SN box and renders ``[HCS Xn]``. This adapter
    records that implementation event without promoting it to certified strategy
    truth.
    """

    if hcs_count < 1:
        raise ValueError("hcs_count must be >= 1")
    return CasinoIndicatorEvent(
        kind=CasinoIndicatorEventKind.HCS,
        direction=direction,
        source=CasinoIndicatorEventSource.SUPPLIED_BETA_STATE_MACHINE,
        marker_text=f"HCS X{hcs_count}",
        hcs_count=hcs_count,
        relation_to_prior_event="retest_of_tracked_fu_or_sn_zone",
    )


def beta_hcs_retest_event(*, direction: CasinoMarkerDirection) -> CasinoIndicatorEvent:
    """Represent BETA's explicit Bull/Bear HCS RETESTING state."""

    return CasinoIndicatorEvent(
        kind=CasinoIndicatorEventKind.HCS_RETEST,
        direction=direction,
        source=CasinoIndicatorEventSource.SUPPLIED_BETA_STATE_MACHINE,
        marker_text="HCS RETESTING",
        relation_to_prior_event="retest_of_tracked_hcs_zone",
    )
