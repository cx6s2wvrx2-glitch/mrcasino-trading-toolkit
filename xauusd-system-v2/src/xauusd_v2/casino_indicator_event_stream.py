from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .beta_intra_negation_shadow import BetaIntraNegatingManipulation
from .casino_directional_marker_semantics import CasinoMarkerDirection
from .casino_indicator_events import (
    CasinoIndicatorEvent,
    beta_hcs_context_negation_event,
    beta_hcs_event,
    beta_hcs_retest_event,
    beta_negation_event,
    fu_event_from_legacy_helper_output,
)
from .helper_fu_shadow import HelperFUClass


@dataclass(frozen=True, slots=True)
class HCSCounterEventInput:
    direction: CasinoMarkerDirection
    count: int


@dataclass(frozen=True, slots=True)
class CasinoIndicatorEventFrame:
    symbol: str
    timeframe: str
    bar_time_utc: datetime
    events: tuple[CasinoIndicatorEvent, ...]
    supplied_indicator_event_count: int
    strategy_semantics_certified: bool = False


def build_supplied_indicator_event_frame(
    *,
    symbol: str,
    timeframe: str,
    bar_time_utc: datetime,
    bullish_fu_class: HelperFUClass = HelperFUClass.NONE,
    bearish_fu_class: HelperFUClass = HelperFUClass.NONE,
    hcs_events: tuple[HCSCounterEventInput, ...] = (),
    hcs_retest_directions: tuple[CasinoMarkerDirection, ...] = (),
    negating_manipulation: BetaIntraNegatingManipulation | None = None,
    negation_has_hcs_context: bool = False,
) -> CasinoIndicatorEventFrame:
    """Normalize supplied-code outputs into one chart/timeframe event frame.

    This is intentionally an adapter, not a new detector. Every event must already
    have been produced by the faithful Casino/BETA shadows or explicit indicator
    inputs. The function does not rediscover FU/HCS from OHLC and does not promote
    implementation events to certified strategy semantics.
    """

    if not symbol.strip():
        raise ValueError("symbol is required")
    if not timeframe.strip():
        raise ValueError("timeframe is required")
    if bar_time_utc.tzinfo is None or bar_time_utc.utcoffset() is None:
        raise ValueError("bar_time_utc must be timezone-aware")

    normalized_time = bar_time_utc.astimezone(UTC)
    events: list[CasinoIndicatorEvent] = []

    bullish = fu_event_from_legacy_helper_output(
        direction=CasinoMarkerDirection.BULLISH,
        helper_class=bullish_fu_class,
    )
    if bullish is not None:
        events.append(bullish)

    bearish = fu_event_from_legacy_helper_output(
        direction=CasinoMarkerDirection.BEARISH,
        helper_class=bearish_fu_class,
    )
    if bearish is not None:
        events.append(bearish)

    for hcs in hcs_events:
        events.append(beta_hcs_event(direction=hcs.direction, hcs_count=hcs.count))

    for direction in hcs_retest_directions:
        events.append(beta_hcs_retest_event(direction=direction))

    if negating_manipulation is not None:
        negation = beta_negation_event(negating_manipulation)
        if negation is not None:
            events.append(negation)

        hcs_negation_context = beta_hcs_context_negation_event(
            negating_manipulation,
            hcs_context=negation_has_hcs_context,
        )
        if hcs_negation_context is not None:
            events.append(hcs_negation_context)

    return CasinoIndicatorEventFrame(
        symbol=symbol,
        timeframe=timeframe,
        bar_time_utc=normalized_time,
        events=tuple(events),
        supplied_indicator_event_count=len(events),
        strategy_semantics_certified=False,
    )
