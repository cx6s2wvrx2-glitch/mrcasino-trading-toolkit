from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .replay_candidate_registry import ReplayCandidate, ReplayCandidateState
from .source_chart_alignment import SourceChartAlignmentResult, SourceChartAlignmentState


class ReplayCandidateReadinessState(StrEnum):
    READY_CANDIDATE = "ready_candidate"
    BLOCKED_CONTEXT_ONLY = "blocked_context_only"
    BLOCKED_ALIGNMENT = "blocked_alignment"
    BLOCKED_STAGE_TIMESTAMPS = "blocked_stage_timestamps"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class ReplayCandidateReadinessResult:
    candidate_id: str
    state: ReplayCandidateReadinessState
    replay_ready: bool
    reason: str


def evaluate_replay_candidate_readiness(
    *,
    candidate: ReplayCandidate,
    alignment: SourceChartAlignmentResult | None,
    stage_timestamps_certified: bool | None,
) -> ReplayCandidateReadinessResult:
    """Require both raw-bar alignment and stage-level timestamp certification.

    Static registry status is provenance/context information. It cannot be bypassed by
    passing an unrelated alignment result, and `ALIGNED_CANDIDATE` alone is never
    enough to make a source episode replay-ready.
    """
    if candidate.state is ReplayCandidateState.CONTEXT_ONLY:
        return ReplayCandidateReadinessResult(
            candidate.candidate_id,
            ReplayCandidateReadinessState.BLOCKED_CONTEXT_ONLY,
            False,
            "context-only source is not a single timestampable end-to-end replay session",
        )

    if alignment is None:
        return ReplayCandidateReadinessResult(
            candidate.candidate_id,
            ReplayCandidateReadinessState.BLOCKED_ALIGNMENT,
            False,
            "immutable broker-bar alignment report is required",
        )

    if alignment.source_id != candidate.source_id or alignment.source_locator != candidate.locator:
        return ReplayCandidateReadinessResult(
            candidate.candidate_id,
            ReplayCandidateReadinessState.BLOCKED_ALIGNMENT,
            False,
            "alignment provenance does not match the replay candidate source/locator",
        )

    if alignment.state is not SourceChartAlignmentState.ALIGNED_CANDIDATE or not alignment.aligned:
        return ReplayCandidateReadinessResult(
            candidate.candidate_id,
            ReplayCandidateReadinessState.BLOCKED_ALIGNMENT,
            False,
            f"source chart is not aligned to immutable broker bars: {alignment.state.value}",
        )

    if stage_timestamps_certified is not True:
        return ReplayCandidateReadinessResult(
            candidate.candidate_id,
            ReplayCandidateReadinessState.BLOCKED_STAGE_TIMESTAMPS,
            False,
            "aligned chart still lacks certified occurrence/availability timestamps for each required R-143 stage",
        )

    return ReplayCandidateReadinessResult(
        candidate.candidate_id,
        ReplayCandidateReadinessState.READY_CANDIDATE,
        True,
        "source provenance, immutable broker alignment and stage-level timestamps are present; candidate may enter historical replay",
    )
