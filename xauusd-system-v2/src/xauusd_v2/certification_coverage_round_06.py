from __future__ import annotations

from .certification_coverage import CoverageState, GroundTruthCoverage


ROUND_06_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage(
        "GT-R06-001",
        CoverageState.PARTIAL,
        ("market_state_agent", "tfs_semantic", "x3_semantic"),
        "explicit Monthly prevalent-buys chart lacks a raw broker fixture and full machine-labelled HTF state inputs",
    ),
    GroundTruthCoverage(
        "GT-R06-002",
        CoverageState.PARTIAL,
        ("market_state_agent", "hcs_semantic", "tfs_semantic"),
        "current market-state foundation does not yet encode source-certified cross-timeframe strength priority for a weaker counter-HCS versus prevalent Monthly direction",
    ),
    GroundTruthCoverage(
        "GT-R06-003",
        CoverageState.PARTIAL,
        ("market_state_agent", "negation_semantic", "tfs_semantic"),
        "forming 3W negation is explicit context, but raw confirmation/closure and HTF transition state are not machine-labelled",
    ),
    GroundTruthCoverage(
        "GT-R06-004",
        CoverageState.PARTIAL,
        ("hcs_semantic", "candidate_detectors.zone_lifecycle"),
        "2W untested HCS zone is explicit, but raw zone coordinates and reaction history are not broker-aligned fixtures",
    ),
    GroundTruthCoverage(
        "GT-R06-005",
        CoverageState.PARTIAL,
        ("classic_zone_confirmation", "candidate_detectors.zone_lifecycle"),
        "source says the weekly zone is no longer active after prior reaction, but the exact cross-version zone family/reaction-count mapping is not universally certified",
    ),
    GroundTruthCoverage(
        "GT-R06-006",
        CoverageState.PARTIAL,
        ("x3_semantic", "market_state_agent"),
        "4D x3 is explicitly only a first major sign; the remaining swing-confirmation inputs are contextual and not raw-labelled",
    ),
    GroundTruthCoverage(
        "GT-R06-007",
        CoverageState.EXECUTABLE,
        ("tfs_semantic", "historical_reproducibility", "market_state_agent"),
    ),
    GroundTruthCoverage(
        "GT-R06-008",
        CoverageState.PARTIAL,
        ("hcs_semantic", "ltf_execution", "market_state_agent"),
        "4H HCS retest POI is explicitly key for LTF entries, but the conditioned HTF-respect state and LTF trigger are not machine-labelled in this visual",
    ),
)


def round_06_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_06_COVERAGE}


def round_06_coverage_counts() -> dict[CoverageState, int]:
    counts = {state: 0 for state in CoverageState}
    for item in ROUND_06_COVERAGE:
        counts[item.state] += 1
    return counts
