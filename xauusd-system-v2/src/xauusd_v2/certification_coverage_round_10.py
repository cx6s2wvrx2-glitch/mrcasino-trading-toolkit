from __future__ import annotations

from .certification_coverage import CoverageState, GroundTruthCoverage


ROUND_10_COVERAGE: tuple[GroundTruthCoverage, ...] = (
    GroundTruthCoverage("GT-R10-001", CoverageState.PARTIAL, ("doji_liquidity_semantic", "target_semantic", "market_state_agent"), "partial-take persistence is explicit in the 2021 chart but exact doji/take geometry and timing priority are not raw broker-labelled"),
    GroundTruthCoverage("GT-R10-002", CoverageState.PARTIAL, ("fu_completion", "market_state_agent", "target_semantic"), "conditional Monthly Attempted-FU scenario is explicit, but the historical level and complete condition geometry are chart-specific"),
    GroundTruthCoverage("GT-R10-003", CoverageState.PARTIAL, ("fu_completion", "market_state_agent", "target_semantic"), "weekly-FU break branch is explicit as a 2021 forecast scenario, not a certified universal transition rule"),
    GroundTruthCoverage("GT-R10-004", CoverageState.PARTIAL, ("fu_retest_quality", "market_state_agent"), "remaining within previous FU is explicit, but exact containment/reaction geometry is not machine-labelled"),
    GroundTruthCoverage("GT-R10-005", CoverageState.PARTIAL, ("fu_retest_quality", "liquidity_taxonomy", "ltf_execution"), "negative FU-retest versus equal-lows case is explicit, but double-bottom/equal-low raw tolerance is not certified"),
    GroundTruthCoverage("GT-R10-006", CoverageState.PARTIAL, ("fu_completion", "historical_reproducibility", "market_state_agent"), "conditional weekly branches are explicit, but historic target coordinates and exact retest-rejection trigger are not portable fixtures"),
    GroundTruthCoverage("GT-R10-007", CoverageState.PARTIAL, ("fu_retest_quality", "market_state_agent"), "held Daily FU retest is explicitly labelled strong swing context, but no numeric strength/probability is source-certified"),
    GroundTruthCoverage("GT-R10-008", CoverageState.PARTIAL, ("fu_completion", "market_state_agent"), "Daily Attempted-FU selling-pressure interpretation is temporal 2021 context and lacks a universal later-version promotion rule"),
    GroundTruthCoverage("GT-R10-009", CoverageState.PARTIAL, ("liquidity_taxonomy", "ltf_execution", "market_state_agent"), "liquidity-before-buy-POI ordering is explicit in this case, but not certified as universal across later strategy versions"),
    GroundTruthCoverage("GT-R10-010", CoverageState.PARTIAL, ("fu_completion", "ltf_execution", "market_state_agent"), "Daily Attempted FU contributes to a sell POI in context, but the complete POI/location/trigger specification is not raw-labelled"),
    GroundTruthCoverage("GT-R10-011", CoverageState.PARTIAL, ("fu_completion", "market_state_agent", "liquidity_taxonomy"), "continuation with liquidity left behind is explicit, but persistence/priority across timeframes remains contextual"),
    GroundTruthCoverage("GT-R10-012", CoverageState.PARTIAL, ("zone_geometry", "ltf_execution", "market_state_agent"), "multi-timeframe refinement is explicit, but the deterministic refinement selection algorithm is not specified"),
    GroundTruthCoverage("GT-R10-013", CoverageState.PARTIAL, ("fu_completion", "ltf_execution", "liquidity_taxonomy"), "direct negative example exists, but exact 'liquidity lies close beneath' distance/tolerance is qualitative and not numeric"),
    GroundTruthCoverage("GT-R10-014", CoverageState.PARTIAL, ("fu_completion", "market_state_agent", "liquidity_taxonomy"), "generated liquidity left behind under strong multi-TF FU is explicit, but revisit priority and duration are not certified"),
    GroundTruthCoverage("GT-R10-015", CoverageState.PARTIAL, ("fu_retest_quality", "doji_liquidity_semantic", "market_state_agent"), "interim buys before later sell POI are explicit, but the full multi-horizon state transition is not machine-labelled"),
    GroundTruthCoverage("GT-R10-016", CoverageState.PARTIAL, ("market_state_agent", "target_semantic", "ltf_execution"), "order-flow shift after institutional buy POI is a source narrative with explicit target direction but no deterministic raw transition fixture"),
    GroundTruthCoverage("GT-R10-017", CoverageState.PARTIAL, ("broker_precision", "doji_liquidity_semantic", "xauusd_data_agent"), "MT4-versus-TradingView doji disagreement is explicit, but the exact broker/feed OHLC records are not preserved as machine-readable fixtures"),
    GroundTruthCoverage("GT-R10-018", CoverageState.PARTIAL, ("fu_retest_quality", "market_state_agent", "historical_reproducibility"), "4H FU-plus-zone reaction and failure branch are explicit, but raw zone/failure tolerance is not labelled"),
    GroundTruthCoverage("GT-R10-019", CoverageState.PARTIAL, ("liquidity_taxonomy", "fu_retest_quality", "market_state_agent"), "deferred lower-TF liquidity under Weekly/4H context is explicit, but no universal deferral rule or timing window is defined"),
    GroundTruthCoverage("GT-R10-020", CoverageState.PARTIAL, ("ltf_execution", "liquidity_taxonomy", "market_state_agent"), "entry area explicitly waits for liquidity take plus other confirmations, but the other confirmations are not enumerated in this chart"),
)


def round_10_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_10_COVERAGE}


def round_10_coverage_counts() -> dict[CoverageState, int]:
    counts = {state: 0 for state in CoverageState}
    for item in ROUND_10_COVERAGE:
        counts[item.state] += 1
    return counts
