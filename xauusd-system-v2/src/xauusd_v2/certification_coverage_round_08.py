from __future__ import annotations

from .certification_coverage import CoverageState, GroundTruthCoverage


ROUND_08_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage("GT-R08-001", CoverageState.PARTIAL, ("fu_criteria", "fu_quality", "tfs_semantic", "market_state_agent"), "multi-month established-vs-forming strength interaction is explicit but not raw broker-labelled and no universal Strong-FU threshold exists"),
    GroundTruthCoverage("GT-R08-002", CoverageState.PARTIAL, ("market_state_agent", "tfs_semantic"), "current Market State Agent foundation does not yet model simultaneous overall/swing and intraday prevalent directions as separate horizons"),
    GroundTruthCoverage("GT-R08-003", CoverageState.PARTIAL, ("fu_retest_quality", "market_state_agent", "zone_geometry"), "3W FU-retest respect is a source condition but raw retest geometry/closure and Monthly-3W refinement bounds are not broker fixtures"),
    GroundTruthCoverage("GT-R08-004", CoverageState.PARTIAL, ("hcs_semantic", "market_state_agent", "tfs_semantic"), "11D HCS respect provides conditional swing backing but session-by-session confirmation is contextual and not machine-labelled"),
    GroundTruthCoverage("GT-R08-005", CoverageState.PARTIAL, ("hcs_semantic", "zone_geometry"), "key 4D HCS zone and need for another refinement are explicit but the additional refinement selection rule/coordinates are not machine-labelled"),
    GroundTruthCoverage("GT-R08-006", CoverageState.PARTIAL, ("classic_zone_confirmation", "doji_liquidity_semantic", "zone_geometry"), "untested zone-of-manipulation label is explicit but raw 30m-doji relation and zone bounds are not broker-aligned"),
    GroundTruthCoverage("GT-R08-007", CoverageState.PARTIAL, ("hcs_semantic", "market_state_agent", "negation_semantic"), "2D HCS reaction is explicit first confirmation for sells but the 1963 manipulation boundary and later valid-negation conditions are not raw-labelled"),
    GroundTruthCoverage("GT-R08-008", CoverageState.PARTIAL, ("fu_completion", "fu_retest_quality", "market_state_agent"), "Daily ATT-FU retest and not-relevant-yet lower zone are explicit but exact raw ATT-FU fixture and dynamic relevance state are not machine-labelled"),
    GroundTruthCoverage("GT-R08-009", CoverageState.PARTIAL, ("x3_semantic", "hcs_semantic", "negation_semantic"), "11H x3 reaction is explicit, while the source phrase many FU retests/strong manipulation intentionally has no certified numeric threshold"),
    GroundTruthCoverage("GT-R08-010", CoverageState.PARTIAL, ("ltf_execution", "market_state_agent", "true_stop_semantic"), "LTF-manipulation versus eventual HTF-reaction staging is explicit but event timestamps and 1942 true-stop raw geometry are not machine-labelled"),
)


def round_08_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_08_COVERAGE}


def round_08_coverage_counts() -> dict[CoverageState, int]:
    counts = {state: 0 for state in CoverageState}
    for item in ROUND_08_COVERAGE:
        counts[item.state] += 1
    return counts
