from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from .agents.data_agent import MarketBar
from .casino_directional_marker_semantics import CasinoMarkerDirection
from .helper_fu_doji_shadow import apply_casino_v7_default_visible_filters
from .helper_fu_shadow import HelperFUClass, casino_v7_core_shadow


STATUS = "SOURCE_HCS_MARKER_PROXY_DIAGNOSTIC_COMPLETE_NOT_CERTIFIED"


class SourceHCSMarkerProxyForm(StrEnum):
    STRONG_STRONG = "strong_strong"
    STRONG_ATTEMPTED = "strong_attempted"
    ATTEMPTED_ATTEMPTED = "attempted_attempted"


@dataclass(frozen=True, slots=True)
class SourceHCSMarkerNode:
    bar_time_utc: datetime
    direction: CasinoMarkerDirection
    helper_class: HelperFUClass
    wick_low: float
    wick_high: float

    @property
    def has_nonzero_wick(self) -> bool:
        return self.wick_high > self.wick_low


@dataclass(frozen=True, slots=True)
class SourceHCSMarkerProxyCandidate:
    first_bar_time_utc: datetime
    second_bar_time_utc: datetime
    first_direction: CasinoMarkerDirection
    second_direction: CasinoMarkerDirection
    first_helper_class: HelperFUClass
    second_helper_class: HelperFUClass
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
    fu_negation_nodes_integrated: bool = False
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
    """Observe a narrow source-style HCS proxy from supplied Casino marker output.

    Source material defines HCS around two FU-family nodes retesting each other and
    explicitly allows Strong FU, Attempted FU and FU-negation node families. This
    diagnostic operationalizes only the supplied Casino_v7 Strong/ATT marker output
    after the helper's default visible filters. It compares every current marker node
    with the marker node(s) on the most recent prior bar that emitted a marker and
    requires exact OHLC intersection with that prior marker's directional wick. It
    deliberately does not require same direction, because that boundary is not settled
    by the source examples currently governed.

    This is observability only. Casino helper output is implementation evidence, the
    exact wick rule is a research proxy, FU-negation is not integrated here, and no
    source HCS certification or reference-feed alignment is claimed.
    """

    _validate_bars(bars)
    closed = tuple(bar for bar in bars if bar.is_closed)
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
                    form, label = _form(first.helper_class, second.helper_class)
                    candidates.append(
                        SourceHCSMarkerProxyCandidate(
                            first_bar_time_utc=first.bar_time_utc,
                            second_bar_time_utc=second.bar_time_utc,
                            first_direction=first.direction,
                            second_direction=second.direction,
                            first_helper_class=first.helper_class,
                            second_helper_class=second.helper_class,
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
            )
        )
    return tuple(nodes)


def _form(
    first: HelperFUClass,
    second: HelperFUClass,
) -> tuple[SourceHCSMarkerProxyForm, str]:
    if first is HelperFUClass.FU and second is HelperFUClass.FU:
        return SourceHCSMarkerProxyForm.STRONG_STRONG, "L3_PROXY"
    if first is HelperFUClass.ATT and second is HelperFUClass.ATT:
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
