from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class LTFExecutionTrigger(StrEnum):
    ONE_MIN_NEGATION = "1m_negation"
    THREE_MIN_HCS_NEGATION = "3m_hcs_negation"


class LTFExecutionMode(StrEnum):
    CONFIRMED = "confirmed"
    AGGRESSIVE = "aggressive"


class LTFExecutionState(StrEnum):
    ENTRY_CANDIDATE = "entry_candidate"
    WAIT = "wait"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class LTFExecutionResult:
    state: LTFExecutionState
    trigger: LTFExecutionTrigger | None
    mode: LTFExecutionMode
    reason: str


def evaluate_r145_ltf_execution(
    *,
    retail_liquidity_manipulated: bool | None,
    ltf_laol_taken: bool | None,
    trigger: LTFExecutionTrigger | None,
    mode: LTFExecutionMode,
    ten_min_ts_established: bool | None,
    ten_min_ts_forming: bool | None,
    full_tfs_factors_present: bool | None,
) -> LTFExecutionResult:
    """Evaluate Reflection R-145 LTF execution without authorizing a trade.

    Standard sequence: retail liquidity manipulated -> LTF LAOL taken -> one of
    the explicitly named LTF triggers. Confirmed mode requires established 10m TS.
    Aggressive mode is allowed only with full TFS factors + 10m TS forming.
    Optional zone confluence is deliberately not made mandatory because the source
    calls it possible rather than required.
    """
    required_common = (retail_liquidity_manipulated, ltf_laol_taken, trigger)
    if any(value is None for value in required_common):
        return LTFExecutionResult(
            LTFExecutionState.NOT_CERTIFIED,
            trigger,
            mode,
            "required retail-liquidity/LAOL/trigger evidence is missing",
        )
    if not retail_liquidity_manipulated or not ltf_laol_taken:
        return LTFExecutionResult(
            LTFExecutionState.WAIT,
            trigger,
            mode,
            "R-145 requires retail liquidity manipulation followed by LTF LAOL taken",
        )

    if mode is LTFExecutionMode.CONFIRMED:
        if ten_min_ts_established is None:
            return LTFExecutionResult(
                LTFExecutionState.NOT_CERTIFIED,
                trigger,
                mode,
                "10m TS establishment evidence is missing",
            )
        if not ten_min_ts_established:
            return LTFExecutionResult(
                LTFExecutionState.WAIT,
                trigger,
                mode,
                "confirmed execution waits for 10m TS establishment",
            )
        return LTFExecutionResult(
            LTFExecutionState.ENTRY_CANDIDATE,
            trigger,
            mode,
            "R-145 confirmed LTF sequence is present; downstream risk/execution gates remain",
        )

    if ten_min_ts_forming is None or full_tfs_factors_present is None:
        return LTFExecutionResult(
            LTFExecutionState.NOT_CERTIFIED,
            trigger,
            mode,
            "aggressive execution requires explicit 10m-forming and full-TFS evidence",
        )
    if not ten_min_ts_forming or not full_tfs_factors_present:
        return LTFExecutionResult(
            LTFExecutionState.WAIT,
            trigger,
            mode,
            "aggressive R-145 exception is not fully supported",
        )
    return LTFExecutionResult(
        LTFExecutionState.ENTRY_CANDIDATE,
        trigger,
        mode,
        "aggressive R-145 exception: full TFS factors + 10m TS forming; downstream risk gate remains",
    )
