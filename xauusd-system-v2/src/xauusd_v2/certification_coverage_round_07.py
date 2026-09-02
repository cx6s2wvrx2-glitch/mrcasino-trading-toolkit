from __future__ import annotations

from .certification_coverage import CoverageState, GroundTruthCoverage


ROUND_07_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage("GT-R07-001", CoverageState.PARTIAL, ("market_state_agent", "candidate_detectors.zone_lifecycle"), "Monthly zone reaction is explicit as a first sign, but raw zone/reaction state and HTF transition evidence are not machine-labelled"),
    GroundTruthCoverage("GT-R07-002", CoverageState.PARTIAL, ("negation_semantic", "market_state_agent", "tfs_semantic"), "source defines 2W sell strength but explicitly withholds confirmation; cross-timeframe strength precedence is not yet encoded as a certified ranking engine"),
    GroundTruthCoverage("GT-R07-003", CoverageState.PARTIAL, ("hcs_semantic", "zone_geometry", "market_state_agent"), "multi-timeframe zone stacking/refinement is explicit but the exact merged raw geometry is source-case-specific"),
    GroundTruthCoverage("GT-R07-004", CoverageState.PARTIAL, ("target_semantic", "market_state_agent"), "overall new-high target is conditional on strongest manipulation base and is not a machine-labelled immediate target state"),
    GroundTruthCoverage("GT-R07-005", CoverageState.PARTIAL, ("doji_liquidity_semantic", "liquidity_taxonomy", "market_state_agent"), "weaker Daily-doji/1H relevance is explicit, but raw doji identity/strength and daily-bias weighting are not machine-labelled"),
    GroundTruthCoverage("GT-R07-006", CoverageState.PARTIAL, ("hcs_semantic", "classic_zone_confirmation"), "12H HCS first touch of zone of manipulation is explicit but raw zone bounds/touch chronology are not broker fixtures"),
    GroundTruthCoverage("GT-R07-007", CoverageState.PARTIAL, ("doji_liquidity_semantic", "liquidity_taxonomy"), "Major 4H/8H doji is explicitly labelled but lacks a broker-quality raw fixture for doji geometry and manipulation status"),
    GroundTruthCoverage("GT-R07-008", CoverageState.PARTIAL, ("candidate_detectors.zone_lifecycle", "doji_liquidity_semantic"), "source keeps the reacted doji zone relevant; exact lifecycle family and reaction-consumption rule require case-aligned raw evidence"),
    GroundTruthCoverage("GT-R07-009", CoverageState.PARTIAL, ("hcs_semantic", "fu_criteria", "zone_geometry"), "4H HCS refinement role and separate FU POI are explicit but raw ranges and interaction sequence are not machine-labelled"),
    GroundTruthCoverage("GT-R07-010", CoverageState.PARTIAL, ("hcs_semantic", "ltf_execution", "market_state_agent"), "lower-TF HCS/1H zone relevance is explicit but there is no certified numeric strength/ranking model to promote it beyond LTF context"),
)


def round_07_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_07_COVERAGE}


def round_07_coverage_counts() -> dict[CoverageState, int]:
    counts = {state: 0 for state in CoverageState}
    for item in ROUND_07_COVERAGE:
        counts[item.state] += 1
    return counts
