from __future__ import annotations

from .certification_coverage import CoverageState, GroundTruthCoverage


# Round 13 is visual primary evidence. Every case remains PARTIAL until the
# relevant broker-aligned candle sequence / exact geometry is certified.
_COMPONENTS: dict[int, tuple[str, ...]] = {
    1:("true_stop_semantic","market_state_agent"),2:("zone_geometry",),3:("zone_geometry","market_state_agent"),
    4:("market_state_agent","tfs_semantic"),5:("hcs_semantic","negation_semantic","market_state_agent"),6:("zone_geometry","ltf_execution"),
    7:("imbalance_observables","liquidity_interaction","broker_precision"),8:("negation_semantic","market_state_agent","historical_reproducibility"),
    9:("zone_geometry","market_state_agent"),10:("zone_geometry","market_state_agent"),11:("hcs_semantic","negation_semantic","fu_completion"),
    12:("hcs_semantic","tfs_semantic"),13:("zone_geometry","market_state_agent"),14:("zone_geometry","market_state_agent"),
    15:("zone_geometry","hcs_semantic","liquidity_interaction"),16:("zone_geometry","liquidity_interaction","tfs_semantic"),
    17:("hcs_semantic","liquidity_interaction","market_state_agent"),18:("ltf_execution","hcs_semantic","negation_semantic","fu_completion"),
    19:("true_stop_semantic","negation_semantic","ltf_execution"),20:("negation_semantic","zone_geometry","market_state_agent"),
    21:("hcs_semantic","liquidity_interaction"),22:("hcs_semantic","historical_reproducibility","market_state_agent"),
    23:("ltf_execution","market_state_agent"),24:("true_stop_semantic","fu_completion","hcs_semantic","zone_geometry"),
    25:("negation_semantic","hcs_semantic","true_stop_semantic","zone_geometry"),26:("zone_geometry","market_state_agent"),
    27:("negation_semantic","doji_liquidity_semantic","market_state_agent"),28:("fu_retest_quality","ltf_execution","zone_geometry"),
    29:("hcs_semantic","true_stop_semantic","market_state_agent"),
}

_SPECIAL: dict[int, str] = {
    7:"broker-specific imbalance/news-liquidity evidence needs exact broker OHLC and event-time fixtures; no universal imbalance tolerance is inferred",
    12:"source phrase 'one more major reaction' is temporal/contextual and is not a certified fixed HCS-zone lifecycle count",
    13:"multi-reaction weakening is an expectation explicitly not confirmation; no fixed reaction-count break rule is certified",
    18:"dense 1M entry chain is explicit, but each component needs broker-aligned event order and one-pip/equal-high language needs declared broker precision",
    22:"price slowing is only a first sign; the required 30M+ closure needs exact close-time and source-chart alignment before replay certification",
    23:"roughly 70-pip management example is historical/contextual and cannot become a universal hold/close threshold",
    26:"150-pip historical reaction is an observed outcome, not expected return or target policy",
}

ROUND_13_COVERAGE: tuple[GroundTruthCoverage, ...] = tuple(
    GroundTruthCoverage(
        f"GT-R13-{i:03d}",
        CoverageState.PARTIAL,
        _COMPONENTS[i],
        _SPECIAL.get(i, "primary visual claim is explicit, but exact broker-aligned OHLC, event timestamps and/or zone/manipulation geometry are not certified; temporal 2023 application evidence cannot auto-promote a detector"),
    )
    for i in range(1, 30)
)


def round_13_coverage_by_id() -> dict[str, GroundTruthCoverage]:
    return {item.ground_truth_id: item for item in ROUND_13_COVERAGE}


def round_13_coverage_counts() -> dict[CoverageState, int]:
    counts = {state: 0 for state in CoverageState}
    for item in ROUND_13_COVERAGE:
        counts[item.state] += 1
    return counts
