from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from .agents.data_agent import MarketBar
from .casino_directional_marker_semantics import CasinoMarkerDirection
from .casino_source_negation_candidate import run_source_marker_fu_negation_proxy
from .helper_fu_doji_shadow import apply_casino_v7_default_visible_filters
from .helper_fu_shadow import HelperFUClass, casino_v7_core_shadow


STATUS = "SOURCE_HCS_MARKER_PROXY_DIAGNOSTIC_COMPLETE_NOT_CERTIFIED"


class SourceHCSMarkerProxyForm(StrEnum):
    STRONG_STRONG = "strong_strong"
    STRONG_ATTEMPTED = "strong_attempted"
    ATTEMPTED_ATTEMPTED = "attempted_attempted"
    STRONG_NEGATION = "strong_negation"
    ATTEMPTED_NEGATION = "attempted_negation"
    NEGATION_NEGATION = "negation_negation"


@dataclass(frozen=True, slots=True)
class SourceHCSMarkerNode:
    bar_time_utc: datetime
    direction: CasinoMarkerDirection
    helper_class: HelperFUClass
    wick_low: float
    wick_high: float
    fu_negation_proxy: bool = False

    @property
    def has_nonzero_wick(self) -> bool:
        return self.wick_high > self.wick_low

    @property
    def semantic_role(self) -> str:
        if self.fu_negation_proxy:
            return "fu_negation"
        if self.helper_class is HelperFUClass.FU:
            return "strong_fu"
        return "attempted_fu"


@dataclass(frozen=True, slots=True)
class SourceHCSMarkerProxyCandidate:
    first_bar_time_utc: datetime
    second_bar_time_utc: datetime
    first_direction: CasinoMarkerDirection
    second_direction: CasinoMarkerDirection
    first_helper_class: HelperFUClass
    second_helper_class: HelperFUClass
    first_semantic_role: str
    second_semantic_role: str
    first_is_fu_negation_proxy: bool
    second_is_fu_negation_proxy: bool
    first_wick_low: float
    first_wick_high: float
    second_bar_low: float
    second_bar_high: float
    exact_last_marker_wick_retest: bool
    same_direction: bool
    form: SourceHCSMarkerProxyForm
    source_strength_label_proxy: str
    latest_prior_marker_node_count: int
    source_hcs_semantics_certified: bool = False
    source_occurrence_timestamp_certified: bool = False
    reference_feed_alignment_complete: bool = False
    promotion_allowed: bool = False
    live_execution_authorized: bool = False


@dataclass(frozen=True, slots=True)
class SourceHCSMarkerProxyRun:
    status: str
    input_bar_count: int
    closed_bar_count: int
    evaluated_bar_count: int
    marker_node_count: int
    candidate_count: int
    candidate_counts_by_form: tuple[tuple[str, int], ...]
    candidates: tuple[SourceHCSMarkerProxyCandidate, ...]
    latest_marker_only: bool = True
    exact_wick_intersection_only: bool = True
    same_direction_required: bool = False
    fu_negation_nodes_integrated: bool = True
    fu_negation_role_is_proxy_only: bool = True
    source_confirmed_near_enough_retest_integrated: bool = False
    source_hcs_semantics_certified: bool = False
    reference_feed_alignment_complete: bool = False
    performance_claim_allowed: bool = False
    promotion_allowed: bool = False
    live_execution_authorized: bool = False


def run_source_hcs_marker_proxy(
    *,
    bars: tuple[MarketBar, ...],
    doji_body_ratio_threshold: float = 0.30,
) -> SourceHCSMarkerProxyRun:
    """Observe a source-style HCS proxy from supplied Casino marker output.

    Source material allows Strong FU, Attempted FU and FU-negation node families in
    HCS. The physical A/F markers come from the supplied Casino helper. A visible
    Strong/F marker that independently satisfies the source-marker FU-negation proxy
    is therefore annotated with the semantic role ``fu_negation`` for HCS form
    classification. It remains one physical node, so it is never double-counted once
    as Strong and again as Negation.

    Each current physical marker node is compared only with node(s) on the most
    recent prior bar that emitted a marker. Exact OHLC intersection with that prior
    node's directional wick is required. Same direction is not required.

    All FU-negation role assignment remains proxy-only. No HCS, FU-negation,
    reference-feed, performance or execution certification is created here.
    """

    _validate_bars(bars)
    closed = tuple(bar for bar in bars if bar.is_closed)
    negation_run = run_source_marker_fu_negation_proxy(
        bars=bars,
        doji_body_ratio_threshold=doji_body_ratio_threshold,
    )
    negation_keys = {
        (item.negating_bar_time_utc.astimezone(UTC), item.negating_direction)
        for item in negation_run.candidates
    }

    latest_nodes: tuple[SourceHCSMarkerNode, ...] = ()
    candidates: list[SourceHCSMarkerProxyCandidate] = []
    marker_node_count = 0

    for index in range(1, len(closed)):
        previous = closed[index - 1]
        current = closed[index]
        core = casino_v7_core_shadow(
            open=current.open,
            high=current.high,
            low=current.low,
            close=current.close,
            previous_open=previous.open,
            previous_high=previous.high,
            previous_low=previous.low,
            previous_close=previous.close,
        )
        filtered = apply_casino_v7_default_visible_filters(
            open=current.open,
            high=current.high,
            low=current.low,
            close=current.close,
            branch_result=core,
            body_ratio_threshold=doji_body_ratio_threshold,
        )
        current_nodes = _nodes_for_bar(
            bar=current,
            bullish=filtered.bullish_after_filter,
            bearish=filtered.bearish_after_filter,
            negation_keys=negation_keys,
        )
        marker_node_count += len(current_nodes)

        if current_nodes and latest_nodes:
            for second in current_nodes:
                for first in latest_nodes:
                    if not first.has_nonzero_wick:
                        continue
                    retest = current.high >= first.wick_low and current.low <= first.wick_high
                    if not retest:
                        continue
                    form, label = _form(first, second)
                    candidates.append(
                        SourceHCSMarkerProxyCandidate(
                            first_bar_time_utc=first.bar_time_utc,
                            second_bar_time_utc=second.bar_time_utc,
                            first_direction=first.direction,
                            second_direction=second.direction,
                            first_helper_class=first.helper_class,
                            second_helper_class=second.helper_class,
                            first_semantic_role=first.semantic_role,
                            second_semantic_role=second.semantic_role,
                            first_is_fu_negation_proxy=first.fu_negation_proxy,
                            second_is_fu_negation_proxy=second.fu_negation_proxy,
                            first_wick_low=first.wick_low,
                            first_wick_high=first.wick_high,
                            second_bar_low=current.low,
                            second_bar_high=current.high,
                            exact_last_marker_wick_retest=True,
                            same_direction=first.direction is second.direction,
                            form=form,
                            source_strength_label_proxy=label,
                            latest_prior_marker_node_count=len(latest_nodes),
                        )
                    )

        if current_nodes:
            latest_nodes = current_nodes

    counts = Counter(item.form.value for item in candidates)
    return SourceHCSMarkerProxyRun(
        status=STATUS,
        input_bar_count=len(bars),
        closed_bar_count=len(closed),
        evaluated_bar_count=max(0, len(closed) - 1),
        marker_node_count=marker_node_count,
        candidate_count=len(candidates),
        candidate_counts_by_form=tuple(sorted(counts.items())),
        candidates=tuple(candidates),
    )


def _nodes_for_bar(
    *,
    bar: MarketBar,
    bullish: HelperFUClass,
    bearish: HelperFUClass,
    negation_keys: set[tuple[datetime, CasinoMarkerDirection]],
) -> tuple[SourceHCSMarkerNode, ...]:
    nodes: list[SourceHCSMarkerNode] = []
    timestamp = bar.timestamp.astimezone(UTC)
    if bullish is not HelperFUClass.NONE:
        nodes.append(
            SourceHCSMarkerNode(
                bar_time_utc=timestamp,
                direction=CasinoMarkerDirection.BULLISH,
                helper_class=bullish,
                wick_low=bar.low,
                wick_high=min(bar.open, bar.close),
                fu_negation_proxy=(timestamp, CasinoMarkerDirection.BULLISH) in negation_keys,
            )
        )
    if bearish is not HelperFUClass.NONE:
        nodes.append(
            SourceHCSMarkerNode(
                bar_time_utc=timestamp,
                direction=CasinoMarkerDirection.BEARISH,
                helper_class=bearish,
                wick_low=max(bar.open, bar.close),
                wick_high=bar.high,
                fu_negation_proxy=(timestamp, CasinoMarkerDirection.BEARISH) in negation_keys,
            )
        )
    return tuple(nodes)


def _form(
    first: SourceHCSMarkerNode,
    second: SourceHCSMarkerNode,
) -> tuple[SourceHCSMarkerProxyForm, str]:
    if first.fu_negation_proxy and second.fu_negation_proxy:
        return SourceHCSMarkerProxyForm.NEGATION_NEGATION, "UNRANKED_PROXY"

    if first.fu_negation_proxy or second.fu_negation_proxy:
        other = second if first.fu_negation_proxy else first
        if other.helper_class is HelperFUClass.ATT:
            return SourceHCSMarkerProxyForm.ATTEMPTED_NEGATION, "L1_PROXY_SOURCE_WEAK_FORM"
        return SourceHCSMarkerProxyForm.STRONG_NEGATION, "UNRANKED_PROXY"

    if first.helper_class is HelperFUClass.FU and second.helper_class is HelperFUClass.FU:
        return SourceHCSMarkerProxyForm.STRONG_STRONG, "L3_PROXY"
    if first.helper_class is HelperFUClass.ATT and second.helper_class is HelperFUClass.ATT:
        return SourceHCSMarkerProxyForm.ATTEMPTED_ATTEMPTED, "L1_PROXY"
    return SourceHCSMarkerProxyForm.STRONG_ATTEMPTED, "L2_PROXY"


def _validate_bars(bars: tuple[MarketBar, ...]) -> None:
    if len(bars) < 2:
        raise ValueError("at least two bars are required")
    previous: datetime | None = None
    provisional_seen = False
    for index, bar in enumerate(bars):
        if bar.timestamp.tzinfo is None or bar.timestamp.utcoffset() is None:
            raise ValueError(f"bar {index} timestamp must be timezone-aware")
        if previous is not None and bar.timestamp <= previous:
            raise ValueError("bars must be strictly increasing")
        previous = bar.timestamp
        if not bar.is_closed:
            if index != len(bars) - 1:
                raise ValueError("only the final bar may be provisional")
            provisional_seen = True
        elif provisional_seen:
            raise ValueError("closed bar cannot follow a provisional bar")
    if sum(1 for bar in bars if bar.is_closed) < 2:
        raise ValueError("at least two closed bars are required")
