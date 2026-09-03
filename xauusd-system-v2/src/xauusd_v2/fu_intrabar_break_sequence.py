from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from .agents.data_agent import MarketBar, XAUUSDDataAgent
from .liquidity_interaction import (
    LiquidityInteractionState,
    LiquiditySide,
    MarkedLiquidityReference,
    evaluate_marked_liquidity_interaction,
)


class FUIntrabarBreakSequenceState(StrEnum):
    NO_LIQUIDITY_TAKE = "no_liquidity_take"
    POST_TAKE_OPPOSITE_BREAK_OBSERVED = "post_take_opposite_break_observed"
    BREAK_ON_TAKE_CHILD_ORDER_UNRESOLVED = "break_on_take_child_order_unresolved"
    NO_POST_TAKE_OPPOSITE_BREAK = "no_post_take_opposite_break"


@dataclass(frozen=True, slots=True)
class FUIntrabarBreakSequenceEvidence:
    """Ordered child-bar evidence for the B-01 previous-extreme-break candidate.

    This does not certify FU semantics or resolve B-01 globally. It answers only:
    after a supplied marked-liquidity reference was first taken inside a closed
    parent candle, did a later child bar break the previous candle's opposite
    extreme?

    A break occurring inside the SAME child bar as the first liquidity take is
    deliberately order-unresolved because that child's OHLC still lacks intrabar
    ordering.
    """

    state: FUIntrabarBreakSequenceState
    reference_id: str
    liquidity_side: LiquiditySide
    expected_fu_direction: str
    opposite_previous_extreme_name: str
    opposite_previous_extreme_level: float

    parent_start: datetime
    parent_end: datetime
    child_timeframe_seconds: int

    first_take_timestamp: datetime | None
    first_take_child_index: int | None
    post_take_bar_count: int

    opposite_break_before_take_observed: bool | None
    opposite_break_on_take_child_observed: bool | None
    post_take_opposite_break_observed: bool | None
    first_post_take_break_timestamp: datetime | None
    first_post_take_break_child_index: int | None

    candidate_sequence_supported: bool
    fu_semantics_certified: bool
    b01_globally_resolved: bool
    strategy_truth_changed: bool
    reason: str


def extract_fu_intrabar_break_sequence(
    *,
    parent_start: datetime,
    parent_timeframe_seconds: int,
    child_timeframe_seconds: int,
    child_bars: tuple[MarketBar, ...],
    reference: MarkedLiquidityReference,
    previous_high: float,
    previous_low: float,
    evaluation_time: datetime,
) -> FUIntrabarBreakSequenceEvidence:
    """Extract ordered B-01 candidate evidence without inventing a threshold."""

    if parent_start.tzinfo is None or parent_start.utcoffset() is None:
        raise ValueError("parent_start must be timezone-aware")
    if evaluation_time.tzinfo is None or evaluation_time.utcoffset() is None:
        raise ValueError("evaluation_time must be timezone-aware")
    if parent_timeframe_seconds <= 0 or child_timeframe_seconds <= 0:
        raise ValueError("timeframes must be positive")
    if child_timeframe_seconds >= parent_timeframe_seconds:
        raise ValueError("child timeframe must be smaller than parent timeframe")
    if parent_timeframe_seconds % child_timeframe_seconds != 0:
        raise ValueError("child timeframe must divide the parent timeframe exactly")
    if previous_low > previous_high:
        raise ValueError("previous low cannot exceed previous high")
    if not child_bars:
        raise ValueError("child_bars cannot be empty")

    parent_end = parent_start + timedelta(seconds=parent_timeframe_seconds)
    if parent_end > evaluation_time:
        raise ValueError("parent candle must be closed at evaluation_time")

    report, _ = XAUUSDDataAgent().validate_batch(
        bars=child_bars,
        timeframe_seconds=child_timeframe_seconds,
        evaluation_time=evaluation_time,
        canonical_symbol="XAUUSD",
    )
    if report.provisional_bars:
        raise ValueError("intrabar break evidence requires closed child bars only")
    if len(report.source_names) != 1 or len(report.source_symbols) != 1:
        raise ValueError("intrabar break evidence must come from one broker/source series")

    expected_count = parent_timeframe_seconds // child_timeframe_seconds
    if len(child_bars) != expected_count:
        raise ValueError("child bars must fully cover the parent candle with no missing intervals")

    for index, bar in enumerate(child_bars):
        expected_timestamp = parent_start + timedelta(seconds=index * child_timeframe_seconds)
        if bar.timestamp != expected_timestamp:
            raise ValueError("child bars must exactly tile the parent candle in timestamp order")
        if bar.timestamp < parent_start or bar.timestamp + timedelta(seconds=child_timeframe_seconds) > parent_end:
            raise ValueError("child bar falls outside the parent candle")

    if reference.side is LiquiditySide.BELOW:
        expected_direction = "bullish"
        opposite_name = "previous_high"
        opposite_level = previous_high

        def breaks_opposite(bar: MarketBar) -> bool:
            return bar.high > previous_high

    else:
        expected_direction = "bearish"
        opposite_name = "previous_low"
        opposite_level = previous_low

        def breaks_opposite(bar: MarketBar) -> bool:
            return bar.low < previous_low

    first_take_index: int | None = None
    for index, bar in enumerate(child_bars):
        interaction = evaluate_marked_liquidity_interaction(
            reference=reference,
            candle_high=bar.high,
            candle_low=bar.low,
        )
        if interaction.state is LiquidityInteractionState.TAKEN:
            first_take_index = index
            break

    if first_take_index is None:
        return FUIntrabarBreakSequenceEvidence(
            state=FUIntrabarBreakSequenceState.NO_LIQUIDITY_TAKE,
            reference_id=reference.reference_id,
            liquidity_side=reference.side,
            expected_fu_direction=expected_direction,
            opposite_previous_extreme_name=opposite_name,
            opposite_previous_extreme_level=opposite_level,
            parent_start=parent_start,
            parent_end=parent_end,
            child_timeframe_seconds=child_timeframe_seconds,
            first_take_timestamp=None,
            first_take_child_index=None,
            post_take_bar_count=0,
            opposite_break_before_take_observed=None,
            opposite_break_on_take_child_observed=None,
            post_take_opposite_break_observed=None,
            first_post_take_break_timestamp=None,
            first_post_take_break_child_index=None,
            candidate_sequence_supported=False,
            fu_semantics_certified=False,
            b01_globally_resolved=False,
            strategy_truth_changed=False,
            reason="the supplied marked liquidity was never taken inside the parent candle",
        )

    first_take_bar = child_bars[first_take_index]
    break_before_take = any(breaks_opposite(bar) for bar in child_bars[:first_take_index])
    break_on_take_child = breaks_opposite(first_take_bar)

    first_post_break_index: int | None = None
    for index in range(first_take_index + 1, len(child_bars)):
        if breaks_opposite(child_bars[index]):
            first_post_break_index = index
            break

    post_take_count = len(child_bars) - first_take_index - 1
    if first_post_break_index is not None:
        state = FUIntrabarBreakSequenceState.POST_TAKE_OPPOSITE_BREAK_OBSERVED
        first_post_timestamp = child_bars[first_post_break_index].timestamp
        candidate_supported = True
        reason = (
            "a later child bar breaks the previous candle's opposite extreme after the first marked-liquidity take; "
            "this supports the B-01 previous-extreme-break candidate at child-bar resolution only"
        )
    elif break_on_take_child:
        state = FUIntrabarBreakSequenceState.BREAK_ON_TAKE_CHILD_ORDER_UNRESOLVED
        first_post_timestamp = None
        candidate_supported = False
        reason = (
            "the liquidity take child also breaks the opposite previous extreme, but that child OHLC cannot prove which happened first"
        )
    else:
        state = FUIntrabarBreakSequenceState.NO_POST_TAKE_OPPOSITE_BREAK
        first_post_timestamp = None
        candidate_supported = False
        reason = (
            "marked liquidity was taken, but no later child bar breaks the previous candle's opposite extreme inside the parent"
        )

    return FUIntrabarBreakSequenceEvidence(
        state=state,
        reference_id=reference.reference_id,
        liquidity_side=reference.side,
        expected_fu_direction=expected_direction,
        opposite_previous_extreme_name=opposite_name,
        opposite_previous_extreme_level=opposite_level,
        parent_start=parent_start,
        parent_end=parent_end,
        child_timeframe_seconds=child_timeframe_seconds,
        first_take_timestamp=first_take_bar.timestamp,
        first_take_child_index=first_take_index,
        post_take_bar_count=post_take_count,
        opposite_break_before_take_observed=break_before_take,
        opposite_break_on_take_child_observed=break_on_take_child,
        post_take_opposite_break_observed=first_post_break_index is not None,
        first_post_take_break_timestamp=first_post_timestamp,
        first_post_take_break_child_index=first_post_break_index,
        candidate_sequence_supported=candidate_supported,
        fu_semantics_certified=False,
        b01_globally_resolved=False,
        strategy_truth_changed=False,
        reason=reason,
    )
