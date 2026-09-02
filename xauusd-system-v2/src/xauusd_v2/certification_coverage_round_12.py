from __future__ import annotations

from .certification_coverage import CoverageState, GroundTruthCoverage


ROUND_12_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage("GT-R12-001", CoverageState.PARTIAL, ("fu_completion", "zone_geometry", "market_state_agent"), "forming Monthly FU / refinement logic is explicit, but raw Monthly close, manipulation geometry and zone bounds are not broker-certified"),
    GroundTruthCoverage("GT-R12-002", CoverageState.PARTIAL, ("liquidity_interaction", "broker_precision"), "cross-broker mismatch is explicit, but exact feed OHLC/tolerance and which broker is canonical are not certified here"),
    GroundTruthCoverage("GT-R12-003", CoverageState.PARTIAL, ("zone_geometry", "market_state_agent"), "zone-removal / retail-zone distinction is explicit, but a universal active-zone lifecycle algorithm is not defined"),
    GroundTruthCoverage("GT-R12-004", CoverageState.PARTIAL, ("liquidity_interaction",), "Daily last-liquidity reaction context is labelled, but exact liquidity geometry and event timestamps need raw broker data"),
    GroundTruthCoverage("GT-R12-005", CoverageState.PARTIAL, ("zone_geometry", "fu_retest_quality", "hcs_semantic"), "nearby-manipulation refinement and 4H FU/HCS labels are explicit, but exact geometry/removal trigger is visual-only"),
    GroundTruthCoverage("GT-R12-006", CoverageState.PARTIAL, ("doji_liquidity_semantic", "hcs_semantic", "market_state_agent"), "major-doji/1H-HCS roles are explicit, but doji geometry and horizon interaction are not raw-labelled"),
    GroundTruthCoverage("GT-R12-007", CoverageState.PARTIAL, ("fu_completion", "liquidity_interaction", "market_state_agent"), "forming Monthly FU plus major-liquidity condition is explicit, but historical level and monthly manipulation sequence are not machine fixtures"),
    GroundTruthCoverage("GT-R12-008", CoverageState.PARTIAL, ("fu_completion", "liquidity_interaction", "tfs_semantic", "zone_geometry"), "FU-POI interest conditioned on opposite liquidity and TF strength is explicit, but POI geometry/liquidity comparison need raw data"),
    GroundTruthCoverage("GT-R12-009", CoverageState.PARTIAL, ("doji_liquidity_semantic", "liquidity_interaction", "market_state_agent"), "major-area doji and swing-liquidity condition are explicit, but qualitative hold/major definitions are not numericized"),
    GroundTruthCoverage("GT-R12-010", CoverageState.PARTIAL, ("zone_geometry", "market_state_agent"), "Daily relevance versus retained refinement is explicit, but dynamic relevance state is not yet machine-labelled"),
    GroundTruthCoverage("GT-R12-011", CoverageState.PARTIAL, ("true_stop_semantic", "fu_completion", "market_state_agent"), "4H FU POI / True Stop / new manipulation reversal context is explicit, but exact TS and reversal geometry remain raw-blocked"),
    GroundTruthCoverage("GT-R12-012", CoverageState.PARTIAL, ("zone_geometry",), "1H concentrated-manipulation refinement purpose is explicit, but concentration has no certified numeric detector"),
    GroundTruthCoverage("GT-R12-013", CoverageState.PARTIAL, ("hcs_semantic", "zone_geometry"), "one-retet HCS-to-normal-zone transition is source-labelled, but universal deactivation semantics are not established"),
    GroundTruthCoverage("GT-R12-014", CoverageState.PARTIAL, ("zone_geometry", "ltf_execution"), "final 1H refinement role is explicit, but exact execution geometry and trigger remain context-dependent"),
    GroundTruthCoverage("GT-R12-015", CoverageState.PARTIAL, ("liquidity_interaction", "market_state_agent"), "liquidity-first HTF evaluation and stronger-sells state are explicit, but low-sweep/monthly-manipulation conditions need raw time-series labels"),
    GroundTruthCoverage("GT-R12-016", CoverageState.PARTIAL, ("tfs_semantic", "market_state_agent"), "2W strength being insufficient versus Monthly is explicit, but cross-TF strength comparison is not fully machine-calibrated"),
    GroundTruthCoverage("GT-R12-017", CoverageState.PARTIAL, ("zone_geometry", "market_state_agent"), "chart-clarity removal versus Daily reaction context is explicit, but visual removal is not a certified lifecycle rule"),
    GroundTruthCoverage("GT-R12-018", CoverageState.PARTIAL, ("doji_liquidity_semantic", "hcs_semantic", "fu_retest_quality"), "major 4H doji / overlap / 8H FU-HCS context is explicit, but exact multi-zone geometry and manipulation count are not certified"),
    GroundTruthCoverage("GT-R12-019", CoverageState.PARTIAL, ("hcs_semantic", "fu_completion", "fu_retest_quality", "zone_geometry"), "1H HCS to FU-zone/FU-retest refinement is explicit, but exact raw candle sequence is missing"),
    GroundTruthCoverage("GT-R12-020", CoverageState.PARTIAL, ("zone_geometry", "negation_semantic", "market_state_agent"), "Monthly zone/negation context is explicit, but historic targets and negation geometry are not strategy constants"),
    GroundTruthCoverage("GT-R12-021", CoverageState.PARTIAL, ("market_state_agent", "historical_reproducibility"), "unclosed HTF confirmation is an explicit negative case and semantic gating exists, but source chart timestamps/close fixtures are not raw-aligned"),
    GroundTruthCoverage("GT-R12-022", CoverageState.PARTIAL, ("negation_semantic", "hcs_semantic", "market_state_agent"), "negation-high/Daily-closure condition is explicit, but exact high construction and event geometry are not raw-labelled"),
    GroundTruthCoverage("GT-R12-023", CoverageState.PARTIAL, ("liquidity_interaction", "zone_geometry"), "post-target reaction / established 4H-zone narrative is explicit, but universal establishment criteria cannot be inferred from one visual"),
    GroundTruthCoverage("GT-R12-024", CoverageState.PARTIAL, ("true_stop_semantic", "hcs_semantic", "ltf_execution", "zone_geometry"), "8H True Stop/HCS break-to-reentry context is explicit, but exact TS geometry and re-entry trigger remain raw-blocked"),
)


def round_12_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_12_COVERAGE}


def round_12_coverage_counts() -> dict[CoverageState, int]:
    counts = {state: 0 for state in CoverageState}
    for item in ROUND_12_COVERAGE:
        counts[item.state] += 1
    return counts
