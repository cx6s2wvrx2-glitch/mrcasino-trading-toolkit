from __future__ import annotations

from dataclasses import dataclass

from .beta_hcs_shadow import BetaHCSDirection


@dataclass(frozen=True, slots=True)
class BetaHCSZone:
    direction: BetaHCSDirection
    top_val: float
    bottom_val: float
    is_broken: bool = False


@dataclass(frozen=True, slots=True)
class BetaHCSZoneUpdate:
    is_broken: bool
    retesting: bool
    delete_zone: bool
    next_top_val: float
    next_bottom_val: float
    reason: str
    supplied_code_behavior_only: bool = True
    strategy_semantics_certified: bool = False


def update_beta_hcs_zone(
    *,
    zone: BetaHCSZone,
    current_high: float,
    current_low: float,
) -> BetaHCSZoneUpdate:
    """Faithfully shadow ``f_manage_hcs_boxes`` from supplied BETA 1 + LAOL.

    Bear HCS zone:
    - becomes BROKEN when high > top;
    - while broken, high inside [bottom, top] means HCS RETESTING;
    - low below bottom deletes the zone;
    - low inside the zone can refine the top downward.

    Bull HCS zone is the mirrored supplied implementation:
    - becomes BROKEN when low < bottom;
    - while broken, low inside [bottom, top] means HCS RETESTING;
    - high above top deletes the zone;
    - low inside the zone can refine the bottom upward.

    This is implementation fidelity, not independent strategy certification.
    """

    broken = zone.is_broken
    top_val = zone.top_val
    bottom_val = zone.bottom_val

    if zone.direction is BetaHCSDirection.BEAR:
        if not broken and current_high > top_val:
            broken = True
        if not broken:
            return _result(broken, False, False, top_val, bottom_val, "bear HCS zone has not broken yet")

        retesting = current_high >= bottom_val and current_high <= top_val
        if current_low < bottom_val:
            return _result(broken, retesting, True, top_val, bottom_val, "BETA deletes broken bear HCS zone when low falls below its bottom")
        if current_low <= top_val and current_low >= bottom_val and current_low < top_val:
            top_val = current_low
        return _result(broken, retesting, False, top_val, bottom_val, "faithful broken bear HCS zone update")

    if not broken and current_low < bottom_val:
        broken = True
    if not broken:
        return _result(broken, False, False, top_val, bottom_val, "bull HCS zone has not broken yet")

    retesting = current_low >= bottom_val and current_low <= top_val
    if current_high > top_val:
        return _result(broken, retesting, True, top_val, bottom_val, "BETA deletes broken bull HCS zone when high rises above its top")
    if current_low >= bottom_val and current_low <= top_val and current_low > bottom_val:
        bottom_val = current_low
    return _result(broken, retesting, False, top_val, bottom_val, "faithful broken bull HCS zone update")


def _result(
    is_broken: bool,
    retesting: bool,
    delete_zone: bool,
    top_val: float,
    bottom_val: float,
    reason: str,
) -> BetaHCSZoneUpdate:
    return BetaHCSZoneUpdate(
        is_broken=is_broken,
        retesting=retesting,
        delete_zone=delete_zone,
        next_top_val=top_val,
        next_bottom_val=bottom_val,
        reason=reason,
    )
