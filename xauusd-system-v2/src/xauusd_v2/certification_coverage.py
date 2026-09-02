from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CoverageState(StrEnum):
    EXECUTABLE = "executable"
    PARTIAL = "partial"
    RAW_BLOCKED = "raw_blocked"
    CONTEXT_ONLY = "context_only"


@dataclass(frozen=True, slots=True)
class GroundTruthCoverage:
    ground_truth_id: str
    state: CoverageState
    components: tuple[str, ...]
    blocker: str | None = None


# Round-02 coverage is deliberately explicit rather than inferred from label names.
# None of these mappings is a VERIFIED promotion; they only state implementation
# coverage against already-labelled primary evidence.
ROUND_02_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage("GT-R02-001", CoverageState.EXECUTABLE, ("true_stop_semantic", "ltf_execution")),
    GroundTruthCoverage("GT-R02-002", CoverageState.EXECUTABLE, ("true_stop_semantic", "backtest_sequence")),
    GroundTruthCoverage("GT-R02-003", CoverageState.PARTIAL, ("true_stop_semantic",), "no universal numeric True-Stop strength score"),
    GroundTruthCoverage("GT-R02-004", CoverageState.PARTIAL, ("target_semantic", "true_stop_semantic"), "no certified fixed LAOL-to-TS distance"),
    GroundTruthCoverage("GT-R02-005", CoverageState.EXECUTABLE, ("target_semantic", "backtest_sequence")),
    GroundTruthCoverage("GT-R02-006", CoverageState.PARTIAL, ("target_semantic",), "active-vs-deferred LAOL priority remains context dependent"),
    GroundTruthCoverage("GT-R02-007", CoverageState.EXECUTABLE, ("target_semantic", "true_stop_semantic")),
    GroundTruthCoverage("GT-R02-008", CoverageState.EXECUTABLE, ("ltf_execution", "x3_semantic", "backtest_sequence")),
    GroundTruthCoverage("GT-R02-009", CoverageState.EXECUTABLE, ("x3_semantic", "true_stop_semantic", "ltf_execution")),
    GroundTruthCoverage("GT-R02-010", CoverageState.EXECUTABLE, ("ltf_execution",)),
    GroundTruthCoverage("GT-R02-011", CoverageState.EXECUTABLE, ("hcs_semantic", "tfs_semantic")),
    GroundTruthCoverage("GT-R02-012", CoverageState.PARTIAL, ("hcs_semantic",), "R-128 near-enough tolerance is qualitative, not numeric"),
    GroundTruthCoverage("GT-R02-013", CoverageState.EXECUTABLE, ("candidate_detectors.zone_lifecycle",)),
    GroundTruthCoverage("GT-R02-014", CoverageState.PARTIAL, ("candidate_detectors.zone_lifecycle", "zone_geometry"), "zone expansion/refinement requires contextual zone identity"),
    GroundTruthCoverage("GT-R02-015", CoverageState.EXECUTABLE, ("candidate_detectors.zone_lifecycle",)),
    GroundTruthCoverage("GT-R02-016", CoverageState.EXECUTABLE, ("zone_geometry.true_orderblock",)),
    GroundTruthCoverage("GT-R02-017", CoverageState.PARTIAL, ("zone_geometry.one_min_strong_fu_zone", "fu_quality"), "universal Strong-FU calibration is not certified"),
    GroundTruthCoverage("GT-R02-018", CoverageState.EXECUTABLE, ("candidate_detectors.weakest_att_fu_zone",)),
    GroundTruthCoverage("GT-R02-019", CoverageState.PARTIAL, ("true_stop_semantic", "x3_semantic"), "exact raw TS-respect wick/body geometry is not certified"),
    GroundTruthCoverage("GT-R02-020", CoverageState.CONTEXT_ONLY, ("market_state_agent", "backtest_sequence"), "single top-down sequence is not yet a raw end-to-end detector fixture"),
)


def coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_02_COVERAGE}


def coverage_counts() -> dict[CoverageState, int]:
    counts = {state: 0 for state in CoverageState}
    for item in ROUND_02_COVERAGE:
        counts[item.state] += 1
    return counts
