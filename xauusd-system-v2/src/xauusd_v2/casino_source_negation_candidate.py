from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .agents.data_agent import MarketBar
from .casino_directional_marker_semantics import CasinoMarkerDirection
from .helper_fu_doji_shadow import apply_casino_v7_default_visible_filters
from .helper_fu_shadow import HelperFUClass, casino_v7_core_shadow
from .negation_semantic import (
    Direction,
    ManipulationType,
    NegationState,
    evaluate_negation,
)


STATUS = "SOURCE_MARKER_FU_NEGATION_PROXY_COMPLETE_NOT_CERTIFIED"


@dataclass(frozen=True, slots=True)
class SourceMarkerNegationNode:
    bar_index: int
    bar_time_utc: datetime
    direction: CasinoMarkerDirection
    helper_class: HelperFUClass
    wick_low: float
    wick_high: float


@dataclass(frozen=True, slots=True)
class SourceMarkerFUNegationProxyCandidate:
    original_bar_index: int
    negating_bar_index: int
    original_bar_time_utc: datetime
    negating_bar_time_utc: datetime
    candle_offset: int
    original_direction: CasinoMarkerDirection
    negating_direction: CasinoMarkerDirection
    original_helper_class: HelperFUClass
    negating_helper_class: HelperFUClass
    original_wick_low: float
    original_wick_high: float
    negating_wick_low: float
    negating_wick_high: float
    latest_prior_marker_node_count: int
    semantic_state_if_helper_strong_is_complete_fu: NegationState
    helper_strong_used_as_complete_fu_proxy: bool = True
    raw_negation_semantics_certified: bool = False
    source_occurrence_timestamp_certified: bool = False
    reference_feed_alignment_complete: bool = False
    promotion_allowed: bool = False
    live_execution_authorized: bool = False


@dataclass(frozen=True, slots=True)
class SourceMarkerFUNegationProxyRun:
    status: str
    input_bar_count: int
    closed_bar_count: int
    evaluated_bar_count: int
    marker_node_count: int
    candidate_count: int
    candidates: tuple[SourceMarkerFUNegationProxyCandidate, ...]
    latest_prior_manipulation_only: bool = True
    max_candle_offset: int = 2
    negating_marker_must_be_strong_fu: bool = True
    attempted_original_allowed: bool = True
    x3_exception_integrated: bool = False
    raw_negation_semantics_certified: bool = False
    reference_feed_alignment_complete: bool = False
    performance_claim_allowed: bool = False
    promotion_allowed: bool = False
    live_execution_authorized: bool = False


def run_source_marker_fu_negation_proxy(
    *,
    bars: tuple[MarketBar, ...],
    doji_body_ratio_threshold: float = 0.30,
) -> SourceMarkerFUNegationProxyRun:
    """Observe ordinary FU-negation candidates from supplied A/F markers.

    Governed Reflection semantics say negation opposes the latest manipulation,
    occurs on candle +1 or +2, and ordinary FU negation requires the negating
    candle to complete as FU. Source examples allow the prior manipulation to be an
    ATT FU. The supplied Casino helper's visible ``F`` marker is therefore used only
    as an implementation proxy for the required complete-FU close.

    The most recent prior bar that emitted any visible A/F marker is the only prior
    manipulation considered. A current ``A`` marker is never promoted to ordinary
    FU negation. The x3 exception is deliberately not integrated here.

    This is a source-marker proxy, not source-semantic certification and not
    reference-feed alignment.
    """

    _validate_bars(bars)
    closed = tuple(bar for bar in bars if bar.is_closed)
    marker_nodes_by_index: dict[int, tuple[SourceMarkerNegationNode, ...]] = {}
    candidates: list[SourceMarkerFUNegationProxyCandidate] = []
    marker_node_count = 0

    for index in range(1, len(closed)):
        previous = closed[index - 1]
        current = closed[index]
        current_nodes = _visible_nodes_for_bar(
            index=index,
            previous=previous,
            current=current,
            doji_body_ratio_threshold=doji_body_ratio_threshold,
        )
        marker_nodes_by_index[index] = current_nodes
        marker_node_count += len(current_nodes)

        strong_current_nodes = tuple(
            node for node in current_nodes if node.helper_class is HelperFUClass.FU
        )
        if not strong_current_nodes:
            continue

        prior_index = _latest_prior_marker_index(
            marker_nodes_by_index=marker_nodes_by_index,
            current_index=index,
        )
        if prior_index is None:
            continue
        offset = index - prior_index
        prior_nodes = marker_nodes_by_index[prior_index]

        for second in strong_current_nodes:
            for first in prior_nodes:
                semantic = evaluate_negation(
                    original_direction=_semantic_direction(first.direction),
                    original_type=ManipulationType.FU,
                    candle_offset=offset,
                    candidate_direction=_semantic_direction(second.direction),
                    candidate_complete_fu=True,
                )
                if semantic.state is not NegationState.CONFIRMED:
                    continue
                candidates.append(
                    SourceMarkerFUNegationProxyCandidate(
                        original_bar_index=first.bar_index,
                        negating_bar_index=second.bar_index,
                        original_bar_time_utc=first.bar_time_utc,
                        negating_bar_time_utc=second.bar_time_utc,
                        candle_offset=offset,
                        original_direction=first.direction,
                        negating_direction=second.direction,
                        original_helper_class=first.helper_class,
                        negating_helper_class=second.helper_class,
                        original_wick_low=first.wick_low,
                        original_wick_high=first.wick_high,
                        negating_wick_low=second.wick_low,
                        negating_wick_high=second.wick_high,
                        latest_prior_marker_node_count=len(prior_nodes),
                        semantic_state_if_helper_strong_is_complete_fu=semantic.state,
                    )
                )

    return SourceMarkerFUNegationProxyRun(
        status=STATUS,
        input_bar_count=len(bars),
        closed_bar_count=len(closed),
        evaluated_bar_count=max(0, len(closed) - 1),
        marker_node_count=marker_node_count,
        candidate_count=len(candidates),
        candidates=tuple(candidates),
    )


def _visible_nodes_for_bar(
    *,
    index: int,
    previous: MarketBar,
    current: MarketBar,
    doji_body_ratio_threshold: float,
) -> tuple[SourceMarkerNegationNode, ...]:
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
    nodes: list[SourceMarkerNegationNode] = []
    timestamp = current.timestamp.astimezone(UTC)
    if filtered.bullish_after_filter is not HelperFUClass.NONE:
        nodes.append(
            SourceMarkerNegationNode(
                bar_index=index,
                bar_time_utc=timestamp,
                direction=CasinoMarkerDirection.BULLISH,
                helper_class=filtered.bullish_after_filter,
                wick_low=current.low,
                wick_high=min(current.open, current.close),
            )
        )
    if filtered.bearish_after_filter is not HelperFUClass.NONE:
        nodes.append(
            SourceMarkerNegationNode(
                bar_index=index,
                bar_time_utc=timestamp,
                direction=CasinoMarkerDirection.BEARISH,
                helper_class=filtered.bearish_after_filter,
                wick_low=max(current.open, current.close),
                wick_high=current.high,
            )
        )
    return tuple(nodes)


def _latest_prior_marker_index(
    *,
    marker_nodes_by_index: dict[int, tuple[SourceMarkerNegationNode, ...]],
    current_index: int,
) -> int | None:
    for offset in (1, 2):
        candidate_index = current_index - offset
        if candidate_index < 1:
            continue
        if marker_nodes_by_index.get(candidate_index):
            return candidate_index
    return None


def _semantic_direction(direction: CasinoMarkerDirection) -> Direction:
    if direction is CasinoMarkerDirection.BULLISH:
        return Direction.BULLISH
    return Direction.BEARISH


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
