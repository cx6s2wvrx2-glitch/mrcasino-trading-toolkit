from __future__ import annotations

from .certification_coverage import CoverageState, GroundTruthCoverage


ROUND_11_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage("GT-R11-001", CoverageState.PARTIAL, ("zone_geometry", "market_state_agent"), "primary 2022 chart context is explicit, but raw broker OHLC, exact coordinates and timestamps are not certified; 2022 method state cannot override later sources automatically"),
    GroundTruthCoverage("GT-R11-002", CoverageState.PARTIAL, ("fu_retest_quality", "zone_geometry", "market_state_agent"), "Daily/Weekly retest context is explicit, but the 50% geometry/anchor and raw broker sequence are not certified"),
    GroundTruthCoverage("GT-R11-003", CoverageState.PARTIAL, ("fu_completion", "fu_retest_quality", "liquidity_interaction"), "4H FU-zone/retest and external-liquidity context are labelled, but raw FU geometry and event order are not broker fixtures"),
    GroundTruthCoverage("GT-R11-004", CoverageState.PARTIAL, ("zone_geometry", "market_state_agent"), "over-zoning warning is explicit, but there is no certified universal numeric maximum for relevant zones"),
    GroundTruthCoverage("GT-R11-005", CoverageState.PARTIAL, ("liquidity_interaction", "zone_geometry", "market_state_agent"), "absence-of-zone/manipulated-liquidity scenario is explicit, but historical coordinates and path conditions are visual-only"),
    GroundTruthCoverage("GT-R11-006", CoverageState.PARTIAL, ("zone_geometry", "market_state_agent"), "repeated rejection and last-major-OB context are explicit, but exact zone geometry is not broker-labelled"),
    GroundTruthCoverage("GT-R11-007", CoverageState.PARTIAL, ("zone_geometry", "fu_retest_quality", "market_state_agent"), "refined-zone/FU-retest preparation is explicit, but 'fairly untested' and reversal confirmation remain qualitative"),
    GroundTruthCoverage("GT-R11-008", CoverageState.PARTIAL, ("zone_geometry", "market_state_agent"), "await-manipulation direction rule is explicit, but manipulation classification and exact zone coordinates are not raw-labelled"),
    GroundTruthCoverage("GT-R11-009", CoverageState.PARTIAL, ("doji_liquidity_semantic", "fu_completion", "market_state_agent"), "Monthly doji/FU and intraday-horizon separation are explicit, but raw Monthly candle and scenario timestamps are not certified"),
    GroundTruthCoverage("GT-R11-010", CoverageState.PARTIAL, ("doji_liquidity_semantic", "fu_retest_quality", "zone_geometry"), "Weekly doji/FU/zone context is explicit, but exact doji/FU geometry and zone refinement need broker fixtures"),
    GroundTruthCoverage("GT-R11-011", CoverageState.PARTIAL, ("fu_retest_quality", "zone_geometry"), "perfect Weekly FU-retest is source-labelled, but the old historical example lacks certified raw coordinates and does not establish expected return"),
    GroundTruthCoverage("GT-R11-012", CoverageState.PARTIAL, ("doji_liquidity_semantic", "liquidity_interaction", "market_state_agent"), "liquidity-take/doji-close scenario is explicit, but broker OHLC and exact branch timing are not certified"),
    GroundTruthCoverage("GT-R11-013", CoverageState.PARTIAL, ("zone_geometry",), "selective 4H refinement/overlap warning is explicit, but no universal numeric overlap or zone-count rule is certified"),
    GroundTruthCoverage("GT-R11-014", CoverageState.PARTIAL, ("fu_completion", "negation_semantic", "market_state_agent"), "Strong Weekly FU negating prior Weekly FU is source-labelled, but universal Strong-FU geometry and exact negation event data are not certified"),
    GroundTruthCoverage("GT-R11-015", CoverageState.PARTIAL, ("zone_geometry", "liquidity_interaction", "fu_retest_quality"), "FU-wick POI plus 'significant liquidity' retest condition is explicit, but significance and raw wick/retest geometry are not broker-labelled"),
    GroundTruthCoverage("GT-R11-016", CoverageState.PARTIAL, ("liquidity_interaction", "fu_completion", "zone_geometry"), "4H doji target/zone-retest buy context is explicit, but 'not enough to target' remains qualitative and raw levels are not certified"),
    GroundTruthCoverage("GT-R11-017", CoverageState.PARTIAL, ("zone_geometry",), "HTF strength and 1H true-zone refinement are explicit, but the historic 80+ pip spacing is not a universal certified rule"),
    GroundTruthCoverage("GT-R11-018", CoverageState.PARTIAL, ("market_state_agent", "liquidity_taxonomy"), "sell veto from absent obvious liquidity is explicit, but 'obvious'/'enough to target' remain qualitative and temporal"),
    GroundTruthCoverage("GT-R11-019", CoverageState.PARTIAL, ("liquidity_interaction", "target_semantic", "market_state_agent"), "downside-liquidity/swing-low scenario is explicit, but historic levels and long-term fundamental branch are not strategy constants"),
    GroundTruthCoverage("GT-R11-020", CoverageState.PARTIAL, ("fu_completion", "market_state_agent"), "Weekly manipulation/FU-break/wick-fill sequence is explicit, but exact manipulation geometry and event timing are not raw-labelled"),
    GroundTruthCoverage("GT-R11-021", CoverageState.PARTIAL, ("zone_geometry", "fu_completion", "liquidity_interaction"), "different buy/sell confirmations are explicit, but exact Daily FU/manipulation and wick-fill fixtures are missing"),
    GroundTruthCoverage("GT-R11-022", CoverageState.PARTIAL, ("fu_retest_quality", "tfs_research_scale"), "Strong 3H FU-retest label is explicit, but universal Strong-FU geometry/threshold is not certified"),
    GroundTruthCoverage("GT-R11-023", CoverageState.PARTIAL, ("liquidity_interaction",), "first generated liquidity is explicitly labelled, but the chart does not define a universal target/reversal rule from that fact"),
    GroundTruthCoverage("GT-R11-024", CoverageState.PARTIAL, ("doji_liquidity_semantic", "liquidity_interaction"), "doji plus clean trendline target is explicit, but exact liquidity geometry and target construction are not broker-labelled"),
    GroundTruthCoverage("GT-R11-025", CoverageState.PARTIAL, ("true_stop_semantic", "negation_semantic", "market_state_agent"), "True Stop and 1H+ manipulation transition are explicit, but exact True-Stop geometry and stage timestamps are not raw broker fixtures"),
    GroundTruthCoverage("GT-R11-026", CoverageState.PARTIAL, ("fu_completion", "hcs_semantic", "market_state_agent"), "Monthly ATT-FU/HCS condition is explicit, but the source candle is forming and raw close/manipulation evidence is not certified"),
    GroundTruthCoverage("GT-R11-027", CoverageState.PARTIAL, ("negation_semantic", "fu_completion", "market_state_agent"), "Weekly negation/prevalent-direction logic is explicit, but branch transitions and exact manipulation geometry are not raw-labelled"),
    GroundTruthCoverage("GT-R11-028", CoverageState.PARTIAL, ("zone_geometry", "market_state_agent", "fu_completion"), "fresh-LTF-with-HTF-reasoning rule is explicit, but execution-zone coordinates and swing-buy conditions are not machine-labelled"),
    GroundTruthCoverage("GT-R11-029", CoverageState.PARTIAL, ("fu_completion", "hcs_semantic", "market_state_agent"), "brief-sell versus later-retracement horizon shift is explicit, but open-condition and event timestamps are not certified"),
    GroundTruthCoverage("GT-R11-030", CoverageState.PARTIAL, ("imbalance_observables", "hcs_semantic", "x3_semantic", "ltf_execution"), "broker-specific non-imbalance statement is explicit, but exact OHLC tolerance and the multi-timeframe POI sequence require broker-aligned raw data"),
)


def round_11_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_11_COVERAGE}


def round_11_coverage_counts() -> dict[CoverageState, int]:
    counts = {state: 0 for state in CoverageState}
    for item in ROUND_11_COVERAGE:
        counts[item.state] += 1
    return counts
