from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .agents.data_agent import MarketBar
from .casino_directional_marker_semantics import CasinoMarkerDirection
from .casino_source_hcs_candidate import (
    SourceHCSMarkerProxyForm,
    run_source_hcs_marker_proxy,
)
from .casino_source_negation_candidate import run_source_marker_fu_negation_proxy


STATUS = "SOURCE_HCS_PLUS_NEGATION_PROXY_COMPLETE_NOT_CERTIFIED"


@dataclass(frozen=True, slots=True)
class SourceHCSPlusNegationProxyCandidate:
    hcs_first_bar_time_utc: datetime
    hcs_bar_time_utc: datetime
    negating_bar_time_utc: datetime
    negation_candle_offset: int
    hcs_first_direction: CasinoMarkerDirection
    hcs_direction: CasinoMarkerDirection
    negating_direction: CasinoMarkerDirection
    hcs_form: SourceHCSMarkerProxyForm
    hcs_second_semantic_role: str
    hcs_exact_last_marker_wick_retest: bool
    negation_opposes_hcs_second_node: bool
    hcs_source_proxy_certified: bool = False
    fu_negation_source_proxy_certified: bool = False
    hcs_plus_negation_semantics_certified: bool = False
    reference_feed_alignment_complete: bool = False
    performance_claim_allowed: bool = False
    promotion_allowed: bool = False
    live_execution_authorized: bool = False


@dataclass(frozen=True, slots=True)
class SourceHCSPlusNegationProxyRun:
    status: str
    hcs_candidate_count: int
    fu_negation_candidate_count: int
    composite_candidate_count: int
    candidates: tuple[SourceHCSPlusNegationProxyCandidate, ...]
    requires_negation_of_hcs_second_node: bool = True
    allowed_negation_offsets: tuple[int, int] = (1, 2)
    excludes_negation_of_negation_x3: bool = True
    hcs_plus_negation_semantics_certified: bool = False
    reference_feed_alignment_complete: bool = False
    performance_claim_allowed: bool = False
    promotion_allowed: bool = False
    live_execution_authorized: bool = False


def run_source_hcs_plus_negation_proxy(
    *,
    bars: tuple[MarketBar, ...],
    doji_body_ratio_threshold: float = 0.30,
) -> SourceHCSPlusNegationProxyRun:
    """Observe a narrow ``HCS + negation`` composite from source-marker proxies.

    Reflection states that negations can occur up to two candles later and labels a
    negation occurring on HCS context as ``HCS + negation``. This implementation
    uses the narrowest direct temporal interpretation: a source-style HCS must first
    form, then that HCS candidate's physical second node must be the latest
    manipulation negated by an opposite Strong/F marker at +1 or +2.

    If the HCS second node is itself already a FU-negation proxy, a later negation of
    that node is excluded here because it enters negation-of-negation / x3 territory,
    whose raw grammar is deliberately unresolved.

    This is a compositional proxy only; it does not certify HCS, FU negation, x3,
    reference-feed equivalence, strategy performance or execution readiness.
    """

    hcs_run = run_source_hcs_marker_proxy(
        bars=bars,
        doji_body_ratio_threshold=doji_body_ratio_threshold,
    )
    negation_run = run_source_marker_fu_negation_proxy(
        bars=bars,
        doji_body_ratio_threshold=doji_body_ratio_threshold,
    )

    hcs_by_second_node: dict[tuple[datetime, CasinoMarkerDirection], list] = {}
    for hcs in hcs_run.candidates:
        if hcs.second_is_fu_negation_proxy:
            continue
        key = (hcs.second_bar_time_utc, hcs.second_direction)
        hcs_by_second_node.setdefault(key, []).append(hcs)

    candidates: list[SourceHCSPlusNegationProxyCandidate] = []
    for negation in negation_run.candidates:
        key = (negation.original_bar_time_utc, negation.original_direction)
        for hcs in hcs_by_second_node.get(key, ()): 
            candidates.append(
                SourceHCSPlusNegationProxyCandidate(
                    hcs_first_bar_time_utc=hcs.first_bar_time_utc,
                    hcs_bar_time_utc=hcs.second_bar_time_utc,
                    negating_bar_time_utc=negation.negating_bar_time_utc,
                    negation_candle_offset=negation.candle_offset,
                    hcs_first_direction=hcs.first_direction,
                    hcs_direction=hcs.second_direction,
                    negating_direction=negation.negating_direction,
                    hcs_form=hcs.form,
                    hcs_second_semantic_role=hcs.second_semantic_role,
                    hcs_exact_last_marker_wick_retest=hcs.exact_last_marker_wick_retest,
                    negation_opposes_hcs_second_node=(
                        negation.original_direction is hcs.second_direction
                        and negation.negating_direction is not hcs.second_direction
                    ),
                )
            )

    return SourceHCSPlusNegationProxyRun(
        status=STATUS,
        hcs_candidate_count=hcs_run.candidate_count,
        fu_negation_candidate_count=negation_run.candidate_count,
        composite_candidate_count=len(candidates),
        candidates=tuple(candidates),
    )
