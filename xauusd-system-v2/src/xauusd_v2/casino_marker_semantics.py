from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .helper_fu_shadow import HelperFUClass


class CasinoVisibleMarker(StrEnum):
    ATTEMPTED_FU = "A"
    STRONG_FU = "F"


class CasinoMarkerMeaning(StrEnum):
    ATTEMPTED_FU = "attempted_fu"
    STRONG_FU = "strong_fu"


@dataclass(frozen=True, slots=True)
class CasinoMarkerSemanticEvidence:
    """User-clarified meaning of visible markers in the supplied Casino indicator.

    Explicit user clarification on 2026-09-04, supported by a screenshot of the
    supplied Casino indicator running on MNQ1! 15m:

    - ``A`` = Attempted FU
    - ``F`` = Strong FU

    The screenshot is used as marker/implementation ground truth only. It is not
    XAUUSD market-data evidence and does not certify a universal Strong-FU numeric
    threshold or the raw strategy semantics behind the indicator's classification.
    """

    marker: CasinoVisibleMarker
    meaning: CasinoMarkerMeaning
    authority: str
    marker_meaning_user_clarified: bool
    raw_strategy_semantics_certified: bool
    universal_strong_fu_threshold_certified: bool


def semantic_for_visible_marker(marker: CasinoVisibleMarker) -> CasinoMarkerSemanticEvidence:
    if marker is CasinoVisibleMarker.ATTEMPTED_FU:
        meaning = CasinoMarkerMeaning.ATTEMPTED_FU
    elif marker is CasinoVisibleMarker.STRONG_FU:
        meaning = CasinoMarkerMeaning.STRONG_FU
    else:  # pragma: no cover - defensive for non-enum callers
        raise ValueError(f"unsupported Casino marker: {marker!r}")

    return CasinoMarkerSemanticEvidence(
        marker=marker,
        meaning=meaning,
        authority="explicit_user_clarification_on_supplied_casino_indicator",
        marker_meaning_user_clarified=True,
        raw_strategy_semantics_certified=False,
        universal_strong_fu_threshold_certified=False,
    )


def visible_marker_from_legacy_helper_class(helper_class: HelperFUClass) -> CasinoVisibleMarker | None:
    """Interpret legacy helper labels using the user-clarified visible legend.

    The legacy shadow deliberately keeps the original implementation enum names
    (``FU`` / ``ATT``) for fidelity. This adapter gives those outputs their visible
    indicator meaning without rewriting the historical helper implementation:

    - HelperFUClass.FU  -> visible ``F`` -> Strong FU marker
    - HelperFUClass.ATT -> visible ``A`` -> Attempted FU marker
    - HelperFUClass.NONE -> no marker
    """

    if helper_class is HelperFUClass.FU:
        return CasinoVisibleMarker.STRONG_FU
    if helper_class is HelperFUClass.ATT:
        return CasinoVisibleMarker.ATTEMPTED_FU
    if helper_class is HelperFUClass.NONE:
        return None
    raise ValueError(f"unsupported helper FU class: {helper_class!r}")
