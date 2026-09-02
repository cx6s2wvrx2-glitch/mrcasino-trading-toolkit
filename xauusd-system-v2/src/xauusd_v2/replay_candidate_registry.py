from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ReplayCandidateState(StrEnum):
    READY = "ready"
    TIMESTAMP_BLOCKED = "timestamp_blocked"
    RAW_DATA_BLOCKED = "raw_data_blocked"
    CONTEXT_ONLY = "context_only"


@dataclass(frozen=True, slots=True)
class ReplayCandidate:
    candidate_id: str
    source_id: str
    locator: str
    state: ReplayCandidateState
    sequence_evidence: str
    blocker: str | None = None


# This registry is intentionally conservative. A chart/episode can carry excellent
# semantic sequence evidence without being admissible as a historical replay fixture.
# Historical replay requires reliable stage-level availability timestamps; date-only
# context or visually inferred candle times are insufficient.
REPLAY_CANDIDATES: tuple[ReplayCandidate, ...] = (
    ReplayCandidate(
        candidate_id="RC-001",
        source_id="f88aa3b8-2900-4829-a565-3d12580d591e",
        locator="GIANNO_CASINO_REFLECTION_MASTER.pdf#pages:35-37#section:Delta3-Delta6",
        state=ReplayCandidateState.TIMESTAMP_BLOCKED,
        sequence_evidence=(
            "Primary/top-priority source explicitly names the R-143 order and shows the "
            "TS-respected -> LAOL-taken -> new 10m HCS TS establishment ladder."
        ),
        blocker=(
            "The compiled pages do not expose reliable machine-readable occurrence and availability "
            "timestamps for every R-143 stage; do not infer them from chart pixel positions."
        ),
    ),
    ReplayCandidate(
        candidate_id="RC-002",
        source_id="8a73b7d8-923c-4222-bc95-f5597a90edde",
        locator="GIANNO_CASINO_BACKTEST_ASKISEIS_01.pdf#exercise:3",
        state=ReplayCandidateState.CONTEXT_ONLY,
        sequence_evidence=(
            "Top-priority exercises define the manual liquidity/top-down backtest protocol and provide "
            "ground-truth training context."
        ),
        blocker=(
            "The exercise protocol is not a single fully timestamped R-143 market session; it cannot be "
            "converted into an end-to-end replay by assigning synthetic stage times."
        ),
    ),
    ReplayCandidate(
        candidate_id="RC-003",
        source_id="b271d0b8-a86b-4d65-a4ae-b7e49d5803a6",
        locator="top down analysis (1).zip#sequence:2023-11-01",
        state=ReplayCandidateState.RAW_DATA_BLOCKED,
        sequence_evidence=(
            "Primary Mr Casino chronological top-down visual sequence is suitable for market-context "
            "cross-checking and later raw-bar alignment."
        ),
        blocker=(
            "The visual sequence is date-scoped but not yet aligned to immutable broker OHLC bars with "
            "stage-level availability times; raw broker data alignment is required before replay."
        ),
    ),
)


def replay_candidates_by_id() -> dict[str, ReplayCandidate]:
    return {candidate.candidate_id: candidate for candidate in REPLAY_CANDIDATES}


def replay_candidate_counts() -> dict[ReplayCandidateState, int]:
    counts = {state: 0 for state in ReplayCandidateState}
    for candidate in REPLAY_CANDIDATES:
        counts[candidate.state] += 1
    return counts
