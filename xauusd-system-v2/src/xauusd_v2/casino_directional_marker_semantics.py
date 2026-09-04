from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .casino_marker_semantics import (
    CasinoMarkerMeaning,
    CasinoVisibleMarker,
    semantic_for_visible_marker,
    visible_marker_from_legacy_helper_class,
)
from .helper_fu_shadow import HelperFUClass


class CasinoMarkerDirection(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"


class CasinoMarkerVisualCue(StrEnum):
    BRIGHT_GREEN = "bright_green"
    FADED_GREEN = "faded_green"
    BRIGHT_RED = "bright_red"
    FADED_RED = "faded_red"


@dataclass(frozen=True, slots=True)
class CasinoDirectionalMarkerEvidence:
    direction: CasinoMarkerDirection
    marker: CasinoVisibleMarker
    meaning: CasinoMarkerMeaning
    visual_cue: CasinoMarkerVisualCue
    authority: str
    legend_user_clarified: bool
    raw_strategy_semantics_certified: bool


def directional_marker_from_legacy_helper_class(
    *,
    direction: CasinoMarkerDirection,
    helper_class: HelperFUClass,
) -> CasinoDirectionalMarkerEvidence | None:
    """Apply the user's explicit four-way visual legend to legacy helper output.

    User clarification supplied on 2026-09-04:
    - bright green  = bullish Strong FU
    - faded green   = bullish Attempted FU
    - bright red    = bearish Strong FU
    - faded red     = bearish Attempted FU

    The mapping is indicator/implementation evidence. It does not certify a
    universal numeric Strong-FU threshold or independently certify raw strategy
    semantics.
    """

    marker = visible_marker_from_legacy_helper_class(helper_class)
    if marker is None:
        return None

    semantic = semantic_for_visible_marker(marker)
    if direction is CasinoMarkerDirection.BULLISH:
        visual_cue = (
            CasinoMarkerVisualCue.BRIGHT_GREEN
            if marker is CasinoVisibleMarker.STRONG_FU
            else CasinoMarkerVisualCue.FADED_GREEN
        )
    elif direction is CasinoMarkerDirection.BEARISH:
        visual_cue = (
            CasinoMarkerVisualCue.BRIGHT_RED
            if marker is CasinoVisibleMarker.STRONG_FU
            else CasinoMarkerVisualCue.FADED_RED
        )
    else:  # pragma: no cover - defensive for non-enum callers
        raise ValueError(f"unsupported Casino marker direction: {direction!r}")

    return CasinoDirectionalMarkerEvidence(
        direction=direction,
        marker=marker,
        meaning=semantic.meaning,
        visual_cue=visual_cue,
        authority="explicit_user_clarification_on_supplied_casino_indicator",
        legend_user_clarified=True,
        raw_strategy_semantics_certified=False,
    )
