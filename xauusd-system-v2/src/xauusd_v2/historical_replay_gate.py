from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .backtest_sequence import SequenceState
from .component_replay import ComponentReplayResult


class HistoricalReplayGateState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    EMPTY = "EMPTY"


@dataclass(frozen=True, slots=True)
class HistoricalReplayGateReport:
    state: HistoricalReplayGateState
    total_sessions: int
    complete_candidates: int
    valid_in_progress: int
    invalid_order: int
    not_certified: int
    lookahead_violations: int
    blockers: tuple[str, ...]

    @property
    def historical_reproducible(self) -> bool:
        return self.state is HistoricalReplayGateState.PASS


def evaluate_historical_replay_batch(
    results: tuple[ComponentReplayResult, ...],
) -> HistoricalReplayGateReport:
    """Evaluate reproducibility separately from trade frequency/performance.

    A session that reaches only IN_PROGRESS is a valid historical no-entry path and
    does not fail reproducibility. INVALID_ORDER, NOT_CERTIFIED or any lookahead use
    fails the batch. No profitability claim is made here.
    """
    if not results:
        return HistoricalReplayGateReport(
            state=HistoricalReplayGateState.EMPTY,
            total_sessions=0,
            complete_candidates=0,
            valid_in_progress=0,
            invalid_order=0,
            not_certified=0,
            lookahead_violations=0,
            blockers=("historical replay batch is empty",),
        )

    complete = sum(r.sequence.state is SequenceState.COMPLETE_CANDIDATE for r in results)
    in_progress = sum(r.sequence.state is SequenceState.IN_PROGRESS for r in results)
    invalid = sum(r.sequence.state is SequenceState.INVALID_ORDER for r in results)
    not_certified = sum(r.sequence.state is SequenceState.NOT_CERTIFIED for r in results)
    lookahead = sum(bool(r.lookahead_used) for r in results)

    blockers: list[str] = []
    if invalid:
        blockers.append(f"{invalid} session(s) violate R-143 stage order")
    if not_certified:
        blockers.append(f"{not_certified} session(s) have missing required evidence")
    if lookahead:
        blockers.append(f"{lookahead} session(s) used future/unavailable evidence")

    state = HistoricalReplayGateState.PASS if not blockers else HistoricalReplayGateState.FAIL
    return HistoricalReplayGateReport(
        state=state,
        total_sessions=len(results),
        complete_candidates=complete,
        valid_in_progress=in_progress,
        invalid_order=invalid,
        not_certified=not_certified,
        lookahead_violations=lookahead,
        blockers=tuple(blockers),
    )
