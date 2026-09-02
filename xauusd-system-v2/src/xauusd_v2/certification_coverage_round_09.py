from __future__ import annotations

from .certification_coverage import CoverageState, GroundTruthCoverage


ROUND_09_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage("GT-R09-001", CoverageState.PARTIAL, ("candidate_detectors.zone_lifecycle", "market_state_agent"), "source confirms contextual zone adjustments as price action develops but does not specify a universal deterministic adjustment algorithm"),
    GroundTruthCoverage("GT-R09-002", CoverageState.PARTIAL, ("ltf_execution", "market_state_agent"), "HTF-reaction/LTF-break-retest relationship is explicitly labelled, but exact break/retest raw geometry and trigger criteria are not machine-labelled"),
    GroundTruthCoverage("GT-R09-003", CoverageState.PARTIAL, ("doji_liquidity_semantic", "target_semantic"), "the 15m doji is explicitly a major target in this chart context, but the target-selection priority and raw broker fixture are not certified universally"),
    GroundTruthCoverage("GT-R09-004", CoverageState.PARTIAL, ("candidate_detectors.zone_lifecycle", "hcs_semantic", "zone_geometry"), "Monthly zone removal is explicit while other areas remain tracked, but the source does not state the removal decision rule or full raw zone identities"),
)


def round_09_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_09_COVERAGE}


def round_09_coverage_counts() -> dict[CoverageState, int]:
    counts = {state: 0 for state in CoverageState}
    for item in ROUND_09_COVERAGE:
        counts[item.state] += 1
    return counts
