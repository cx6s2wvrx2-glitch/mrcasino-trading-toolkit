from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum


class BacktestStage(IntEnum):
    HCS_ZONE_REACTION = 1
    TFS = 2
    LAOL_MET = 3
    TRUE_STOP_RESPECTED = 4
    TEN_MIN_TRUE_STOP_ESTABLISHED = 5
    TARGETS_AND_TIMING = 6


class SequenceState(StrEnum):
    COMPLETE_CANDIDATE = "complete_candidate"
    IN_PROGRESS = "in_progress"
    INVALID_ORDER = "invalid_order"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class BacktestSequenceResult:
    state: SequenceState
    highest_completed_stage: BacktestStage | None
    next_required_stage: BacktestStage | None
    reason: str


def evaluate_r143_sequence(
    *,
    hcs_zone_reaction: bool | None,
    tfs_confirmed: bool | None,
    laol_met: bool | None,
    true_stop_respected: bool | None,
    ten_min_true_stop_established: bool | None,
    targets_and_timing_defined: bool | None,
) -> BacktestSequenceResult:
    """Evaluate the official R-143 strategy-backtest order, fail closed.

    R-143: HCS zone reaction -> TFS -> LAOL met -> TS respected -> 10min TS
    established -> core + major + LAOL target/timing.

    A later stage cannot compensate for a missing earlier stage. The result is a
    backtest/certification candidate only and carries no live execution authority.
    """
    ordered = (
        (BacktestStage.HCS_ZONE_REACTION, hcs_zone_reaction),
        (BacktestStage.TFS, tfs_confirmed),
        (BacktestStage.LAOL_MET, laol_met),
        (BacktestStage.TRUE_STOP_RESPECTED, true_stop_respected),
        (BacktestStage.TEN_MIN_TRUE_STOP_ESTABLISHED, ten_min_true_stop_established),
        (BacktestStage.TARGETS_AND_TIMING, targets_and_timing_defined),
    )

    if any(value is None for _, value in ordered):
        first_unknown = next(stage for stage, value in ordered if value is None)
        return BacktestSequenceResult(
            SequenceState.NOT_CERTIFIED,
            None,
            first_unknown,
            "required R-143 sequence evidence is missing",
        )

    first_false_index: int | None = None
    for index, (_, value) in enumerate(ordered):
        if value is False:
            first_false_index = index
            break

    if first_false_index is None:
        return BacktestSequenceResult(
            SequenceState.COMPLETE_CANDIDATE,
            BacktestStage.TARGETS_AND_TIMING,
            None,
            "all R-143 stages are present in source order",
        )

    # If any later stage is true after the first missing stage, the supplied
    # sequence is internally inconsistent with the official ordering.
    if any(value is True for _, value in ordered[first_false_index + 1 :]):
        missing_stage = ordered[first_false_index][0]
        return BacktestSequenceResult(
            SequenceState.INVALID_ORDER,
            ordered[first_false_index - 1][0] if first_false_index > 0 else None,
            missing_stage,
            "a later stage was supplied before an earlier required R-143 stage",
        )

    highest = ordered[first_false_index - 1][0] if first_false_index > 0 else None
    next_required = ordered[first_false_index][0]
    return BacktestSequenceResult(
        SequenceState.IN_PROGRESS,
        highest,
        next_required,
        "sequence is valid so far; wait for the next official R-143 stage",
    )
