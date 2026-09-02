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


# Coverage is deliberately explicit rather than inferred from label names.
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

ROUND_03_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage("GT-R03-001", CoverageState.PARTIAL, ("fu_quality", "fu_criteria"), "explicit Strong-FU visual is qualitative; no certified universal numeric threshold"),
    GroundTruthCoverage("GT-R03-002", CoverageState.PARTIAL, ("negation_semantic",), "explicit weekly visual lacks machine-readable broker OHLC fixture"),
    GroundTruthCoverage("GT-R03-003", CoverageState.PARTIAL, ("negation_semantic",), "explicit H1 visual lacks machine-readable broker OHLC fixture"),
    GroundTruthCoverage("GT-R03-004", CoverageState.PARTIAL, ("hcs_semantic",), "HCS visual is explicit but individual component classes/raw wick interactions are not machine-labelled"),
    GroundTruthCoverage("GT-R03-005", CoverageState.PARTIAL, ("hcs_semantic",), "HCS visual is explicit but individual component classes/raw wick interactions are not machine-labelled"),
    GroundTruthCoverage("GT-R03-006", CoverageState.RAW_BLOCKED, ("imbalance_observables", "broker_precision"), "explicit H1 imbalance label lacks broker-quality raw OHLC/tick fixture needed to certify exact geometry/tolerance"),
    GroundTruthCoverage("GT-R03-007", CoverageState.PARTIAL, ("imbalance_observables",), "classic imbalance is explicitly separate, but exact classic-zone raw boundaries still need dedicated primary/broker fixture certification"),
)

ROUND_04_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage("GT-R04-001", CoverageState.PARTIAL, ("hcs_semantic", "fu_completion", "fu_retest_quality"), "explicit H4 FU-retest visual now has source-backed wick-quality semantics, but the numeric >70% full-FU branch remains blocked because R-75 does not resolve the fib 0/100 orientation"),
    GroundTruthCoverage("GT-R04-002", CoverageState.PARTIAL, ("zone_geometry", "candidate_detectors.zone_lifecycle"), "older classic OB+ATT-FU+real-FU baseline must remain distinct from later Reflection zone geometry until cross-version certification"),
    GroundTruthCoverage("GT-R04-003", CoverageState.PARTIAL, ("candidate_detectors.zone_lifecycle",), "FU-wick respected visual is explicit but exact raw reaction/rejection boundary is not machine-labelled"),
    GroundTruthCoverage("GT-R04-004", CoverageState.PARTIAL, ("hcs_semantic",), "source gives qualitative HCS > ordinary OB+FU ordering; no numeric zone-strength model is certified"),
    GroundTruthCoverage("GT-R04-005", CoverageState.PARTIAL, ("candidate_detectors.zone_lifecycle",), "zone-of-manipulation transition is explicit but requires contextual HCS/reaction/refinement identity"),
    GroundTruthCoverage("GT-R04-006", CoverageState.PARTIAL, ("hcs_semantic", "candidate_detectors.zone_lifecycle"), "ATT-FU/HCS respected-once visual is explicit but does not define universal ATT-FU strength or future reaction behavior"),
)

ROUND_05_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage("GT-R05-001", CoverageState.EXECUTABLE, ("tfs_semantic", "hcs_semantic")),
    GroundTruthCoverage("GT-R05-002", CoverageState.EXECUTABLE, ("classic_zone_confirmation",)),
    GroundTruthCoverage("GT-R05-003", CoverageState.EXECUTABLE, ("doji_liquidity_semantic", "liquidity_taxonomy")),
    GroundTruthCoverage("GT-R05-004", CoverageState.EXECUTABLE, ("doji_liquidity_semantic",)),
    GroundTruthCoverage("GT-R05-005", CoverageState.EXECUTABLE, ("backtest_sequence",)),
)

ALL_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    ROUND_02_COVERAGE + ROUND_03_COVERAGE + ROUND_04_COVERAGE + ROUND_05_COVERAGE
)


def coverage_by_id() -> dict[str, GroundTruthCoverage]:
    """Backward-compatible Round-02 registry used by existing tests."""
    return {item.ground_truth_id: item for item in ROUND_02_COVERAGE}


def coverage_counts() -> dict[CoverageState, int]:
    """Backward-compatible Round-02 counts."""
    return _count(ROUND_02_COVERAGE)


def round_03_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_03_COVERAGE}


def round_03_coverage_counts() -> dict[CoverageState, int]:
    return _count(ROUND_03_COVERAGE)


def round_04_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_04_COVERAGE}


def round_04_coverage_counts() -> dict[CoverageState, int]:
    return _count(ROUND_04_COVERAGE)


def round_05_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_05_COVERAGE}


def round_05_coverage_counts() -> dict[CoverageState, int]:
    return _count(ROUND_05_COVERAGE)


def all_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ALL_COVERAGE}


def all_coverage_counts() -> dict[CoverageState, int]:
    return _count(ALL_COVERAGE)


def _count(items: tuple[GroundTruthCoverage, ...]) -> dict[CoverageState, int]:
    counts = {state: 0 for state in CoverageState}
    for item in items:
        counts[item.state] += 1
    return counts
