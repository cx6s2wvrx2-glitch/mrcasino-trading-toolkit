from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BetaHCSDirection(StrEnum):
    BULL = "bull"
    BEAR = "bear"


class BetaHCSBoxState(StrEnum):
    FORMING = "FORMING"
    ESTABLISHED = "ESTABLISHED"
    RESPECTED = "RESPECTED"
    EST_RETEST = "EST_RETEST"
    FORMING_FRESH = "FORMING_FRESH"


@dataclass(frozen=True, slots=True)
class BetaTrackedManipulationBox:
    direction: BetaHCSDirection
    timeframe: str
    creation_time: int
    state: BetaHCSBoxState
    base_pattern: str
    top_val: float
    bottom_val: float
    original_top: float
    original_bottom: float
    hcs_count: int = 0


@dataclass(frozen=True, slots=True)
class BetaHCSInteraction:
    hcs: bool
    hcs_forming: bool
    next_hcs_count: int
    next_pattern_text: str
    creates_hcs_zone_in_supplied_beta: bool
    reason: str
    supplied_code_behavior_only: bool = True
    strategy_semantics_certified: bool = False


def evaluate_beta_hcs_interaction(
    *,
    box: BetaTrackedManipulationBox,
    current_direction: BetaHCSDirection,
    current_is_fu: bool,
    current_is_sn: bool,
    current_high: float,
    current_low: float,
    current_time: int,
    current_confirmed: bool,
) -> BetaHCSInteraction:
    """Faithfully shadow the core BETA 1 + LAOL HCS counter gate.

    The supplied Pine block:
    - ignores a box on another timeframe upstream;
    - ignores the source bar itself;
    - ignores boxes still in FORMING state;
    - requires the tracked base pattern to contain FU or SN;
    - requires a new same-direction FU or SN;
    - requires that new event to interact with the tracked box;
    - increments HCS count only when the current timeframe candle is confirmed;
    - exposes a forming HCS before confirmation;
    - creates separate HCS-zone objects only for timeframe strings 50 or 60 when
      the first HCS is confirmed.

    This function reproduces that implementation behavior only. It does not claim
    that the BETA rule is the complete source HCS grammar.
    """

    pattern_has_fu_or_sn = "FU" in box.base_pattern or "SN" in box.base_pattern
    same_direction = box.direction is current_direction
    new_fu_or_sn = current_is_fu or current_is_sn
    same_source_bar = box.creation_time == current_time
    box_is_forming = box.state is BetaHCSBoxState.FORMING

    if same_source_bar:
        return _no_hcs(box, "BETA skips the tracked box on its own creation candle")
    if box_is_forming:
        return _no_hcs(box, "BETA skips tracked boxes still in FORMING state")
    if not pattern_has_fu_or_sn:
        return _no_hcs(box, "BETA HCS base pattern must contain FU or SN")
    if not same_direction:
        return _no_hcs(box, "BETA HCS counter uses a new FU/SN in the same direction as the tracked box")
    if not new_fu_or_sn:
        return _no_hcs(box, "current event is neither FU nor SN")

    if box.direction is BetaHCSDirection.BEAR:
        interacts = current_high >= box.bottom_val and current_high <= box.original_top
    else:
        interacts = current_low <= box.top_val and current_low >= box.original_bottom

    if not interacts:
        return _no_hcs(box, "current same-direction FU/SN does not enter the tracked BETA box")

    if not current_confirmed:
        return BetaHCSInteraction(
            hcs=False,
            hcs_forming=True,
            next_hcs_count=box.hcs_count,
            next_pattern_text=box.base_pattern,
            creates_hcs_zone_in_supplied_beta=False,
            reason="BETA marks HCS forming while the interacting timeframe candle is unconfirmed",
        )

    next_count = box.hcs_count + 1
    return BetaHCSInteraction(
        hcs=True,
        hcs_forming=False,
        next_hcs_count=next_count,
        next_pattern_text=f"{box.base_pattern} [HCS X{next_count}]",
        creates_hcs_zone_in_supplied_beta=next_count == 1 and box.timeframe in {"50", "60"},
        reason="confirmed same-direction FU/SN interacts with tracked FU/SN box; BETA increments HCS count",
    )


def _no_hcs(box: BetaTrackedManipulationBox, reason: str) -> BetaHCSInteraction:
    return BetaHCSInteraction(
        hcs=False,
        hcs_forming=False,
        next_hcs_count=box.hcs_count,
        next_pattern_text=box.base_pattern,
        creates_hcs_zone_in_supplied_beta=False,
        reason=reason,
    )
