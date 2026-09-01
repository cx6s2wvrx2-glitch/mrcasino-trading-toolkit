from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CertificationState(StrEnum):
    NOT_CERTIFIED = "not_certified"
    INACTIVE = "inactive"
    ACTIVE = "active"
    EXPIRED = "expired"
    WAIT = "wait"
    READY_CANDIDATE = "ready_candidate"


class ZoneType(StrEnum):
    BROKEN_FU_WICK = "broken_fu_wick"
    BROKEN_HCS = "broken_hcs"
    WEAKEST_ATT_FU = "weakest_att_fu"
    UNTESTED_FU_WICK = "untested_fu_wick"


@dataclass(frozen=True, slots=True)
class ZoneLifecycleResult:
    state: CertificationState
    reaction_quota: int
    reason: str


@dataclass(frozen=True, slots=True)
class EntryGateResult:
    state: CertificationState
    reason: str


_ZONE_QUOTAS = {
    ZoneType.BROKEN_FU_WICK: 1,
    ZoneType.BROKEN_HCS: 2,
    ZoneType.WEAKEST_ATT_FU: 1,
    ZoneType.UNTESTED_FU_WICK: 1,
}


def evaluate_zone_lifecycle(
    *,
    zone_type: ZoneType,
    body_close_break: bool | None,
    main_same_tf_reactions: int,
    timeframe_minutes: int | None = None,
) -> ZoneLifecycleResult:
    """Candidate semantic detector over already-recognized zone primitives.

    It deliberately does not detect FU/HCS geometry from OHLC. It only applies
    source-supported activation/timeframe/quota rules to supplied semantic facts.
    """
    if main_same_tf_reactions < 0:
        raise ValueError("main_same_tf_reactions cannot be negative")

    quota = _ZONE_QUOTAS[zone_type]

    if zone_type is ZoneType.WEAKEST_ATT_FU:
        if timeframe_minutes is None:
            return ZoneLifecycleResult(CertificationState.NOT_CERTIFIED, quota, "timeframe required")
        if timeframe_minutes < 180:
            return ZoneLifecycleResult(CertificationState.NOT_CERTIFIED, quota, "weakest ATT-FU zone is 3h+ only")

    if zone_type in {ZoneType.BROKEN_FU_WICK, ZoneType.BROKEN_HCS}:
        if body_close_break is None:
            return ZoneLifecycleResult(CertificationState.NOT_CERTIFIED, quota, "body-close activation evidence missing")
        if not body_close_break:
            return ZoneLifecycleResult(CertificationState.INACTIVE, quota, "broken-zone activation requires body close")

    if main_same_tf_reactions >= quota:
        return ZoneLifecycleResult(CertificationState.EXPIRED, quota, "main confirmed reaction quota consumed")

    return ZoneLifecycleResult(CertificationState.ACTIVE, quota, "candidate zone remains within main reaction quota")


def evaluate_standard_entry_gate(
    *,
    liquidity_calculation_resolved: bool | None,
    ltf_laol_taken: bool | None,
    ts_10m_established: bool | None,
    ts_respected: bool | None,
    htf_context_aligned: bool | None,
    ltf_trigger_present: bool | None,
) -> EntryGateResult:
    """Fail-closed semantic gate based on the official sequence.

    This is NOT a raw market detector and does not authorize live trading.
    Every input must come from a separately certified detector/label.
    """
    fields = {
        "liquidity_calculation_resolved": liquidity_calculation_resolved,
        "ltf_laol_taken": ltf_laol_taken,
        "ts_10m_established": ts_10m_established,
        "ts_respected": ts_respected,
        "htf_context_aligned": htf_context_aligned,
        "ltf_trigger_present": ltf_trigger_present,
    }
    missing = [name for name, value in fields.items() if value is None]
    if missing:
        return EntryGateResult(CertificationState.NOT_CERTIFIED, f"missing evidence: {', '.join(missing)}")

    failed = [name for name, value in fields.items() if value is False]
    if failed:
        return EntryGateResult(CertificationState.WAIT, f"required gate not met: {', '.join(failed)}")

    return EntryGateResult(
        CertificationState.READY_CANDIDATE,
        "all semantic gates present; still requires independent certification and deterministic risk veto",
    )
