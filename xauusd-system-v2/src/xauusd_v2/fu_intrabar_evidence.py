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


class FUIntrabarEvidenceState(StrEnum):
    NO_LIQUIDITY_TAKE = "no_liquidity_take"
    TAKE_ON_FINAL_CHILD_BAR = "take_on_final_child_bar"
    POST_TAKE_PATH_AVAILABLE = "post_take_path_available"


@dataclass(frozen=True, slots=True)
class FUIntrabarEvidence:
    state: FUIntrabarEvidenceState
    reference_id: str
    liquidity_side: LiquiditySide
    parent_start: datetime
    parent_end: datetime
    child_timeframe_seconds: int
    first_take_timestamp: datetime | None
    first_take_child_index: int | None
    post_take_bar_count: int
    returned_through_reference_after_take: bool | None
    farthest_post_take_price_in_expected_direction: float | None
    post_take_excursion_from_reference: float | None
    reason: str


def extract_fu_intrabar_evidence(
    *,
    parent_start: datetime,
    parent_timeframe_seconds: int,
    child_timeframe_seconds: int,
    child_bars: tuple[MarketBar, ...],
    reference: MarkedLiquidityReference,
    evaluation_time: datetime,
) -> FUIntrabarEvidence:
    """Extract ordered lower-timeframe evidence around a marked-liquidity take.

    This is deliberately an evidence extractor, not an FU classifier. Approved
    Casino material says an FU takes liquidity and *then* moves in the opposite
    direction inside the same parent candle. Parent OHLC cannot prove that order.
    Ordered lower-timeframe bars can prove when the marked level was first taken
    and what price did afterwards, but this module does not invent a minimum
    reversal distance or body-color rule.
    """
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
        raise ValueError("intrabar evidence requires closed child bars only")
    if len(report.source_names) != 1 or len(report.source_symbols) != 1:
        raise ValueError("intrabar evidence must come from one broker/source series")

    expected_count = parent_timeframe_seconds // child_timeframe_seconds
    if len(child_bars) != expected_count:
        raise ValueError("child bars must fully cover the parent candle with no missing intervals")

    for index, bar in enumerate(child_bars):
        expected_timestamp = parent_start + timedelta(seconds=index * child_timeframe_seconds)
        if bar.timestamp != expected_timestamp:
            raise ValueError("child bars must exactly tile the parent candle in timestamp order")
        if bar.timestamp < parent_start or bar.timestamp + timedelta(seconds=child_timeframe_seconds) > parent_end:
            raise ValueError("child bar falls outside the parent candle")

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
        return FUIntrabarEvidence(
            state=FUIntrabarEvidenceState.NO_LIQUIDITY_TAKE,
            reference_id=reference.reference_id,
            liquidity_side=reference.side,
            parent_start=parent_start,
            parent_end=parent_end,
            child_timeframe_seconds=child_timeframe_seconds,
            first_take_timestamp=None,
            first_take_child_index=None,
            post_take_bar_count=0,
            returned_through_reference_after_take=None,
            farthest_post_take_price_in_expected_direction=None,
            post_take_excursion_from_reference=None,
            reason="no child bar traded beyond the supplied marked-liquidity reference",
        )

    post_take = child_bars[first_take_index + 1 :]
    first_take_timestamp = child_bars[first_take_index].timestamp
    if not post_take:
        return FUIntrabarEvidence(
            state=FUIntrabarEvidenceState.TAKE_ON_FINAL_CHILD_BAR,
            reference_id=reference.reference_id,
            liquidity_side=reference.side,
            parent_start=parent_start,
            parent_end=parent_end,
            child_timeframe_seconds=child_timeframe_seconds,
            first_take_timestamp=first_take_timestamp,
            first_take_child_index=first_take_index,
            post_take_bar_count=0,
            returned_through_reference_after_take=None,
            farthest_post_take_price_in_expected_direction=None,
            post_take_excursion_from_reference=None,
            reason="liquidity was first taken in the final child bar, so no later intrabar path exists inside the parent candle",
        )

    if reference.side is LiquiditySide.ABOVE:
        farthest = min(bar.low for bar in post_take)
        returned = any(bar.low < reference.level for bar in post_take)
        excursion = max(0.0, reference.level - farthest)
    else:
        farthest = max(bar.high for bar in post_take)
        returned = any(bar.high > reference.level for bar in post_take)
        excursion = max(0.0, farthest - reference.level)

    return FUIntrabarEvidence(
        state=FUIntrabarEvidenceState.POST_TAKE_PATH_AVAILABLE,
        reference_id=reference.reference_id,
        liquidity_side=reference.side,
        parent_start=parent_start,
        parent_end=parent_end,
        child_timeframe_seconds=child_timeframe_seconds,
        first_take_timestamp=first_take_timestamp,
        first_take_child_index=first_take_index,
        post_take_bar_count=len(post_take),
        returned_through_reference_after_take=returned,
        farthest_post_take_price_in_expected_direction=farthest,
        post_take_excursion_from_reference=excursion,
        reason="ordered child bars provide post-take path evidence; no minimum reversal threshold or FU label is inferred",
    )
