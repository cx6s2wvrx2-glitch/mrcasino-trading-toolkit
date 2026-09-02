from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .backtest_sequence import BacktestSequenceResult, BacktestStage, SequenceState, evaluate_r143_sequence


@dataclass(frozen=True, slots=True)
class TimedStageConfirmation:
    stage: BacktestStage
    occurred_at: datetime
    available_at: datetime
    source_ref: str

    def __post_init__(self) -> None:
        if self.occurred_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("replay timestamps must be timezone-aware")
        if self.available_at < self.occurred_at:
            raise ValueError("stage evidence cannot be available before it occurs")
        if not self.source_ref.strip():
            raise ValueError("source_ref is required")


@dataclass(frozen=True, slots=True)
class ComponentReplayResult:
    evaluation_time: datetime
    sequence: BacktestSequenceResult
    visible_confirmations: tuple[TimedStageConfirmation, ...]
    future_confirmations_hidden: int
    lookahead_used: bool = False


def replay_r143_at(
    confirmations: tuple[TimedStageConfirmation, ...],
    *,
    evaluation_time: datetime,
) -> ComponentReplayResult:
    """Replay R-143 using only evidence available at `evaluation_time`.

    `occurred_at` is when the market event/confirmation happened.
    `available_at` is when the strategy could legitimately know it, e.g. candle close.
    Evidence with `available_at > evaluation_time` is invisible even if it exists in the
    full historical dataset. This prevents historical lookahead/repainting.
    """
    if evaluation_time.tzinfo is None:
        raise ValueError("evaluation_time must be timezone-aware")

    visible = tuple(
        sorted(
            (item for item in confirmations if item.available_at <= evaluation_time),
            key=lambda item: (item.occurred_at, int(item.stage)),
        )
    )
    hidden_count = len(confirmations) - len(visible)

    # Preserve only the earliest legitimate confirmation for each stage.
    first_by_stage: dict[BacktestStage, TimedStageConfirmation] = {}
    for item in visible:
        first_by_stage.setdefault(item.stage, item)

    # R-143 is an ordered event sequence, not merely a final set of booleans.
    # If a later stage was confirmed before an earlier stage, flag invalid order even
    # when the missing stage appears later in historical data.
    previous_time: datetime | None = None
    previous_stage: BacktestStage | None = None
    for stage in BacktestStage:
        item = first_by_stage.get(stage)
        if item is None:
            continue
        if previous_time is not None and item.occurred_at < previous_time:
            return ComponentReplayResult(
                evaluation_time=evaluation_time,
                sequence=BacktestSequenceResult(
                    state=SequenceState.INVALID_ORDER,
                    highest_completed_stage=previous_stage,
                    next_required_stage=stage,
                    reason="R-143 stage confirmations occurred out of source order",
                ),
                visible_confirmations=visible,
                future_confirmations_hidden=hidden_count,
                lookahead_used=False,
            )
        previous_time = item.occurred_at
        previous_stage = stage

    present = {stage: stage in first_by_stage for stage in BacktestStage}
    sequence = evaluate_r143_sequence(
        hcs_zone_reaction=present[BacktestStage.HCS_ZONE_REACTION],
        tfs_confirmed=present[BacktestStage.TFS],
        laol_met=present[BacktestStage.LAOL_MET],
        true_stop_respected=present[BacktestStage.TRUE_STOP_RESPECTED],
        ten_min_true_stop_established=present[BacktestStage.TEN_MIN_TRUE_STOP_ESTABLISHED],
        targets_and_timing_defined=present[BacktestStage.TARGETS_AND_TIMING],
    )
    return ComponentReplayResult(
        evaluation_time=evaluation_time,
        sequence=sequence,
        visible_confirmations=visible,
        future_confirmations_hidden=hidden_count,
        lookahead_used=False,
    )
