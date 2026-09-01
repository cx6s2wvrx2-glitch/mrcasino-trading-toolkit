from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Direction(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"


class TFSState(StrEnum):
    ESTABLISHED = "established"
    AS_FORMING_POWER_POI = "as_forming_power_poi"
    NOT_ESTABLISHED = "not_established"
    NOT_CERTIFIED = "not_certified"


class TFSEntryState(StrEnum):
    ENTRY_CANDIDATE = "entry_candidate"
    WAIT = "wait"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class TFSResult:
    state: TFSState
    direction: Direction | None
    reason: str


@dataclass(frozen=True, slots=True)
class TFSEntryResult:
    state: TFSEntryState
    direction: Direction | None
    reason: str


def evaluate_established_tfs(
    *,
    prevalent_direction: Direction | None,
    candle_closed: bool | None,
    confirmation_timeframe_minutes: int | None,
) -> TFSResult:
    """Evaluate R-107's confirmed prevalent-direction TFS state.

    R-107 requires confirmed prevalent direction and analysis only after candle
    close. Approved examples use 10/15min+ confirmation. This semantic gate uses
    10 minutes as the conservative minimum already reflected in the V2 source
    corpus; it does not decide which exact 10min+ timeframe is optimal.
    """
    if prevalent_direction is None or candle_closed is None or confirmation_timeframe_minutes is None:
        return TFSResult(TFSState.NOT_CERTIFIED, prevalent_direction, "required TFS evidence is missing")
    if confirmation_timeframe_minutes < 10:
        return TFSResult(
            TFSState.NOT_ESTABLISHED,
            prevalent_direction,
            "sub-10min evidence may refine but cannot establish TFS by itself",
        )
    if not candle_closed:
        return TFSResult(
            TFSState.NOT_ESTABLISHED,
            prevalent_direction,
            "R-107 analysis requires confirmed candle close",
        )
    return TFSResult(
        TFSState.ESTABLISHED,
        prevalent_direction,
        "confirmed prevalent direction on a closed 10min+ timeframe",
    )


def evaluate_hcs_establishment(*, left_fu_retested_first: bool | None, hcs_present: bool | None) -> TFSResult:
    """Apply R-180's HCS establishment prerequisite.

    HCS is established only after the left FU has first been retested. This is a
    semantic establishment gate; FU/HCS geometry is recognized upstream.
    """
    if left_fu_retested_first is None or hcs_present is None:
        return TFSResult(TFSState.NOT_CERTIFIED, None, "HCS establishment evidence is incomplete")
    if not hcs_present:
        return TFSResult(TFSState.NOT_ESTABLISHED, None, "no HCS is present")
    if not left_fu_retested_first:
        return TFSResult(
            TFSState.NOT_ESTABLISHED,
            None,
            "R-180 requires the left FU to be retested before HCS is established",
        )
    return TFSResult(TFSState.ESTABLISHED, None, "HCS present after prerequisite left-FU retest")


def evaluate_tfs_as_forming(
    *,
    established_prevalent_tfs_exists: bool | None,
    power_poi_present: bool | None,
    aligned_lower_tf_closure: bool | None,
) -> TFSResult:
    """Evaluate R-105/R-217 AS FORMING power-POI usage.

    AS FORMING is never an independent direction source. It is permitted only on
    top of already-established prevalent TFS; an aligned lower-TF closure is the
    confirmation mechanism described in R-105.
    """
    values = (established_prevalent_tfs_exists, power_poi_present, aligned_lower_tf_closure)
    if any(value is None for value in values):
        return TFSResult(TFSState.NOT_CERTIFIED, None, "forming-TFS evidence is incomplete")
    if not established_prevalent_tfs_exists:
        return TFSResult(
            TFSState.NOT_ESTABLISHED,
            None,
            "R-217 forbids AS FORMING from creating direction without established prevalent TFS",
        )
    if not power_poi_present or not aligned_lower_tf_closure:
        return TFSResult(TFSState.NOT_ESTABLISHED, None, "forming power-POI confirmation is incomplete")
    return TFSResult(
        TFSState.AS_FORMING_POWER_POI,
        None,
        "power POI forms inside already-established prevalent TFS with aligned lower-TF closure",
    )


def evaluate_tfs_entry(
    *,
    established_tfs: bool | None,
    established_tfs_retested: bool | None,
    prevalent_direction_confirmed: bool | None,
    direction: Direction | None,
) -> TFSEntryResult:
    """Apply R-182: entry is on the retest of established TFS with prevalent direction confirmed."""
    if (
        established_tfs is None
        or established_tfs_retested is None
        or prevalent_direction_confirmed is None
        or direction is None
    ):
        return TFSEntryResult(TFSEntryState.NOT_CERTIFIED, direction, "required TFS-entry evidence is missing")
    if not established_tfs or not established_tfs_retested or not prevalent_direction_confirmed:
        return TFSEntryResult(TFSEntryState.WAIT, direction, "R-182 entry prerequisites are not all satisfied")
    return TFSEntryResult(
        TFSEntryState.ENTRY_CANDIDATE,
        direction,
        "established TFS retested with confirmed prevalent direction; downstream liquidity/TS/risk gates still apply",
    )
