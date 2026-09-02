from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from .agents.data_agent import MarketBar, XAUUSDDataAgent
from .broker_precision import BrokerPriceSpec, is_exact_same_broker_price, price_distance_in_ticks


class ParentChildAlignmentState(StrEnum):
    ALIGNED = "aligned"
    SOURCE_MISMATCH = "source_mismatch"
    SYMBOL_MISMATCH = "symbol_mismatch"
    COVERAGE_MISMATCH = "coverage_mismatch"
    OHLC_MISMATCH = "ohlc_mismatch"


@dataclass(frozen=True, slots=True)
class ParentChildAlignmentResult:
    state: ParentChildAlignmentState
    aligned: bool
    aggregate_open: float | None
    aggregate_high: float | None
    aggregate_low: float | None
    aggregate_close: float | None
    open_distance_ticks: Decimal | None
    high_distance_ticks: Decimal | None
    low_distance_ticks: Decimal | None
    close_distance_ticks: Decimal | None
    reason: str


def validate_parent_child_alignment(
    *,
    parent_bar: MarketBar,
    parent_timeframe_seconds: int,
    child_bars: tuple[MarketBar, ...],
    child_timeframe_seconds: int,
    evaluation_time: datetime,
    price_spec: BrokerPriceSpec,
) -> ParentChildAlignmentResult:
    """Verify that one parent broker bar is exactly reconstructible from child bars.

    The comparison uses the broker-declared digit precision; V2 never assumes a
    universal XAUUSD tick size or decimal count. This is a market-data integrity
    check only and has no strategy authority.
    """
    if parent_timeframe_seconds <= 0 or child_timeframe_seconds <= 0:
        raise ValueError("timeframes must be positive")
    if child_timeframe_seconds >= parent_timeframe_seconds:
        raise ValueError("child timeframe must be smaller than parent timeframe")
    if parent_timeframe_seconds % child_timeframe_seconds != 0:
        raise ValueError("child timeframe must divide parent timeframe exactly")
    if evaluation_time.tzinfo is None or evaluation_time.utcoffset() is None:
        raise ValueError("evaluation_time must be timezone-aware")
    if not child_bars:
        raise ValueError("child_bars cannot be empty")

    if parent_bar.source_name.strip() != price_spec.broker_name.strip():
        return ParentChildAlignmentResult(
            ParentChildAlignmentState.SOURCE_MISMATCH,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "parent broker/source does not match the declared broker price specification",
        )
    if parent_bar.source_symbol.strip() != price_spec.source_symbol.strip():
        return ParentChildAlignmentResult(
            ParentChildAlignmentState.SYMBOL_MISMATCH,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "parent source symbol does not match the declared broker price specification",
        )

    XAUUSDDataAgent().validate_batch(
        bars=(parent_bar,),
        timeframe_seconds=parent_timeframe_seconds,
        evaluation_time=evaluation_time,
        canonical_symbol="XAUUSD",
    )
    child_report, _ = XAUUSDDataAgent().validate_batch(
        bars=child_bars,
        timeframe_seconds=child_timeframe_seconds,
        evaluation_time=evaluation_time,
        canonical_symbol="XAUUSD",
    )
    if not parent_bar.is_closed or child_report.provisional_bars:
        raise ValueError("parent/child alignment requires closed bars only")

    if child_report.source_names != (parent_bar.source_name.strip(),):
        return ParentChildAlignmentResult(
            ParentChildAlignmentState.SOURCE_MISMATCH,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "child bars must come from the exact same broker/source as the parent bar",
        )
    if child_report.source_symbols != (parent_bar.source_symbol.strip(),):
        return ParentChildAlignmentResult(
            ParentChildAlignmentState.SYMBOL_MISMATCH,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "child bars must use the exact same broker symbol as the parent bar",
        )

    expected_count = parent_timeframe_seconds // child_timeframe_seconds
    parent_end = parent_bar.timestamp + timedelta(seconds=parent_timeframe_seconds)
    if len(child_bars) != expected_count:
        return ParentChildAlignmentResult(
            ParentChildAlignmentState.COVERAGE_MISMATCH,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "child bar count does not fully cover the parent interval",
        )
    for index, bar in enumerate(child_bars):
        expected_ts = parent_bar.timestamp + timedelta(seconds=index * child_timeframe_seconds)
        if bar.timestamp != expected_ts or bar.timestamp + timedelta(seconds=child_timeframe_seconds) > parent_end:
            return ParentChildAlignmentResult(
                ParentChildAlignmentState.COVERAGE_MISMATCH,
                False,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                "child timestamps do not exactly tile the parent interval",
            )

    aggregate_open = child_bars[0].open
    aggregate_high = max(bar.high for bar in child_bars)
    aggregate_low = min(bar.low for bar in child_bars)
    aggregate_close = child_bars[-1].close

    comparisons = (
        is_exact_same_broker_price(price_a=parent_bar.open, price_b=aggregate_open, spec=price_spec),
        is_exact_same_broker_price(price_a=parent_bar.high, price_b=aggregate_high, spec=price_spec),
        is_exact_same_broker_price(price_a=parent_bar.low, price_b=aggregate_low, spec=price_spec),
        is_exact_same_broker_price(price_a=parent_bar.close, price_b=aggregate_close, spec=price_spec),
    )
    distances = (
        price_distance_in_ticks(price_a=parent_bar.open, price_b=aggregate_open, spec=price_spec),
        price_distance_in_ticks(price_a=parent_bar.high, price_b=aggregate_high, spec=price_spec),
        price_distance_in_ticks(price_a=parent_bar.low, price_b=aggregate_low, spec=price_spec),
        price_distance_in_ticks(price_a=parent_bar.close, price_b=aggregate_close, spec=price_spec),
    )

    if not all(comparisons):
        return ParentChildAlignmentResult(
            ParentChildAlignmentState.OHLC_MISMATCH,
            False,
            aggregate_open,
            aggregate_high,
            aggregate_low,
            aggregate_close,
            *distances,
            reason="child bars do not reconstruct the parent OHLC at the broker's declared precision",
        )

    return ParentChildAlignmentResult(
        ParentChildAlignmentState.ALIGNED,
        True,
        aggregate_open,
        aggregate_high,
        aggregate_low,
        aggregate_close,
        *distances,
        reason="child bars exactly tile and reconstruct the closed parent bar at declared broker precision",
    )
