from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from math import isfinite

from .agents.data_agent import MarketBar
from .fu_basic_candidate import BasicFUCandidateState, classify_basic_fu_candidate


class PrimitiveReplayScanError(ValueError):
    pass


class CandidateDirection(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"


class HCSCandidateForm(StrEnum):
    CONTINUATION = "continuation"
    NEGATION = "negation"


@dataclass(frozen=True, slots=True)
class PrimitiveFUCandidate:
    event_id: str
    bar_open: datetime
    available_at: datetime
    direction: CandidateDirection
    open: float
    high: float
    low: float
    close: float
    previous_high: float
    previous_low: float
    swept_previous_high: bool
    swept_previous_low: bool
    candidate_wick_low: float
    candidate_wick_high: float
    candidate_wick_has_extent: bool
    source_rule: str = "basic_previous_candle_liquidity_plus_opposite_move_candidate"
    certified_fu: bool = False


@dataclass(frozen=True, slots=True)
class WickInteractionObservation:
    first_event_id: str
    first_bar_open: datetime
    interaction_bar_open: datetime
    interaction_available_at: datetime
    candidate_wick_low: float
    candidate_wick_high: float
    interaction_low: float
    interaction_high: float
    basic_fu_candidate_on_interaction_bar: bool
    second_direction: CandidateDirection | None
    hcs_candidate_form: HCSCandidateForm | None
    source_style_hcs_candidate: bool
    certified_hcs: bool
    reason: str


@dataclass(frozen=True, slots=True)
class PrimitiveReplayScanResult:
    timeframe_seconds: int
    scan_start: datetime
    scan_end: datetime
    bar_count: int
    fu_candidates: tuple[PrimitiveFUCandidate, ...]
    wick_interactions: tuple[WickInteractionObservation, ...]
    source_style_hcs_candidates: int
    ambiguous_basic_fu_bars: int
    adjacency_gap_pairs_skipped: int
    certified_fu_count: int = 0
    certified_hcs_count: int = 0
    strategy_truth_changed: bool = False
    promotion_allowed: bool = False
    live_execution_authorized: bool = False


def _direction_from_state(state: BasicFUCandidateState) -> CandidateDirection | None:
    if state is BasicFUCandidateState.BULLISH:
        return CandidateDirection.BULLISH
    if state is BasicFUCandidateState.BEARISH:
        return CandidateDirection.BEARISH
    return None


def _validate_bar(bar: MarketBar, *, index: int) -> None:
    if bar.timestamp.tzinfo is None or bar.timestamp.utcoffset() is None:
        raise PrimitiveReplayScanError(f"bar {index} timestamp must be timezone-aware")
    values = (bar.open, bar.high, bar.low, bar.close)
    if not all(isfinite(value) for value in values):
        raise PrimitiveReplayScanError(f"bar {index} contains non-finite OHLC")
    if bar.high < max(bar.open, bar.close) or bar.low > min(bar.open, bar.close) or bar.low > bar.high:
        raise PrimitiveReplayScanError(f"bar {index} has invalid OHLC geometry")


def _wick_interval(bar: MarketBar, direction: CandidateDirection) -> tuple[float, float]:
    if direction is CandidateDirection.BULLISH:
        return bar.low, min(bar.open, bar.close)
    return max(bar.open, bar.close), bar.high


def _intersects(*, first_low: float, first_high: float, second_low: float, second_high: float) -> bool:
    return second_high >= first_low and second_low <= first_high


def scan_primitive_replay_window(
    *,
    bars: tuple[MarketBar, ...],
    timeframe_seconds: int,
    scan_start: datetime,
    scan_end: datetime,
    max_window_bars: int = 20_000,
) -> PrimitiveReplayScanResult:
    """Scan a finite closed-bar window for source-safe primitive observations.

    This scanner deliberately stops below strategy truth:

    - a raw FU item is only the narrow existing *basic FU candidate* (previous-side
      liquidity sweep + opposite candle direction), not a certified FU;
    - the relevant swept-side candle wick interval is recorded objectively;
    - every later closed bar in the explicit scan window that intersects that wick
      interval is recorded as an interaction observation;
    - if the interaction bar is itself a basic FU candidate, the pair is marked as a
      source-style HCS *candidate* because the primary HCS grammar says that price
      forms a new FU while retesting the last FU wick;
    - same-direction pairs are labelled continuation-form candidates and opposite-
      direction pairs negation-form candidates. Neither direction is excluded;
    - no near-enough tolerance, Strong-FU threshold, 70% fib rule, doji threshold,
      x3 grammar or unstated expiry is invented here.

    The caller supplies an explicit finite scan window. This avoids smuggling a
    strategy lookback/expiry horizon into the detector while keeping research scans
    computationally bounded. No intrabar ordering is inferred from OHLC. Basic-FU
    classification is also skipped across missing/non-contiguous parent bars instead
    of pretending two bars separated by a market-data gap were consecutive candles.
    """
    if timeframe_seconds <= 0:
        raise PrimitiveReplayScanError("timeframe_seconds must be positive")
    if max_window_bars <= 1:
        raise PrimitiveReplayScanError("max_window_bars must be greater than one")
    for name, value in (("scan_start", scan_start), ("scan_end", scan_end)):
        if value.tzinfo is None or value.utcoffset() is None:
            raise PrimitiveReplayScanError(f"{name} must be timezone-aware")
    if scan_end <= scan_start:
        raise PrimitiveReplayScanError("scan_end must be later than scan_start")

    selected = tuple(bar for bar in bars if scan_start <= bar.timestamp < scan_end and bar.is_closed)
    if len(selected) < 2:
        raise PrimitiveReplayScanError("scan window requires at least two closed bars")
    if len(selected) > max_window_bars:
        raise PrimitiveReplayScanError(
            f"scan window has {len(selected)} bars, above explicit research safety limit {max_window_bars}"
        )

    previous_timestamp: datetime | None = None
    step = timedelta(seconds=timeframe_seconds)
    for index, bar in enumerate(selected):
        _validate_bar(bar, index=index)
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
            raise PrimitiveReplayScanError("scan bars must be strictly increasing")
        previous_timestamp = bar.timestamp

    per_bar_state: list[BasicFUCandidateState | None] = [None]
    candidates: list[PrimitiveFUCandidate] = []
    ambiguous_count = 0
    gap_pairs_skipped = 0

    for index in range(1, len(selected)):
        previous = selected[index - 1]
        current = selected[index]
        if current.timestamp - previous.timestamp != step:
            per_bar_state.append(None)
            gap_pairs_skipped += 1
            continue
        result = classify_basic_fu_candidate(
            open=current.open,
            high=current.high,
            low=current.low,
            close=current.close,
            previous_high=previous.high,
            previous_low=previous.low,
        )
        per_bar_state.append(result.state)
        if result.state is BasicFUCandidateState.AMBIGUOUS:
            ambiguous_count += 1
            continue
        direction = _direction_from_state(result.state)
        if direction is None:
            continue
        wick_low, wick_high = _wick_interval(current, direction)
        event_id = f"basic-fu:{current.timestamp.isoformat()}:{direction.value}"
        candidates.append(
            PrimitiveFUCandidate(
                event_id=event_id,
                bar_open=current.timestamp,
                available_at=current.timestamp + step,
                direction=direction,
                open=current.open,
                high=current.high,
                low=current.low,
                close=current.close,
                previous_high=previous.high,
                previous_low=previous.low,
                swept_previous_high=result.swept_previous_high,
                swept_previous_low=result.swept_previous_low,
                candidate_wick_low=wick_low,
                candidate_wick_high=wick_high,
                candidate_wick_has_extent=wick_high > wick_low,
            )
        )

    index_by_open = {bar.timestamp: index for index, bar in enumerate(selected)}
    direction_by_open = {item.bar_open: item.direction for item in candidates}
    interactions: list[WickInteractionObservation] = []

    for first in candidates:
        if not first.candidate_wick_has_extent:
            continue
        first_index = index_by_open[first.bar_open]
        for second_index in range(first_index + 1, len(selected)):
            bar = selected[second_index]
            if not _intersects(
                first_low=first.candidate_wick_low,
                first_high=first.candidate_wick_high,
                second_low=bar.low,
                second_high=bar.high,
            ):
                continue
            second_direction = direction_by_open.get(bar.timestamp)
            if second_direction is None:
                interactions.append(
                    WickInteractionObservation(
                        first_event_id=first.event_id,
                        first_bar_open=first.bar_open,
                        interaction_bar_open=bar.timestamp,
                        interaction_available_at=bar.timestamp + step,
                        candidate_wick_low=first.candidate_wick_low,
                        candidate_wick_high=first.candidate_wick_high,
                        interaction_low=bar.low,
                        interaction_high=bar.high,
                        basic_fu_candidate_on_interaction_bar=False,
                        second_direction=None,
                        hcs_candidate_form=None,
                        source_style_hcs_candidate=False,
                        certified_hcs=False,
                        reason="later closed bar intersects the candidate swept-side wick interval; no basic FU candidate formed on this bar",
                    )
                )
                continue

            form = (
                HCSCandidateForm.CONTINUATION
                if second_direction is first.direction
                else HCSCandidateForm.NEGATION
            )
            interactions.append(
                WickInteractionObservation(
                    first_event_id=first.event_id,
                    first_bar_open=first.bar_open,
                    interaction_bar_open=bar.timestamp,
                    interaction_available_at=bar.timestamp + step,
                    candidate_wick_low=first.candidate_wick_low,
                    candidate_wick_high=first.candidate_wick_high,
                    interaction_low=bar.low,
                    interaction_high=bar.high,
                    basic_fu_candidate_on_interaction_bar=True,
                    second_direction=second_direction,
                    hcs_candidate_form=form,
                    source_style_hcs_candidate=True,
                    certified_hcs=False,
                    reason=(
                        "basic FU candidate formed on a later closed-bar interaction with the first candidate's swept-side wick interval; "
                        "this mirrors the source HCS grammar but remains NOT CERTIFIED because upstream full FU criteria are unresolved"
                    ),
                )
            )

    return PrimitiveReplayScanResult(
        timeframe_seconds=timeframe_seconds,
        scan_start=scan_start,
        scan_end=scan_end,
        bar_count=len(selected),
        fu_candidates=tuple(candidates),
        wick_interactions=tuple(interactions),
        source_style_hcs_candidates=sum(1 for item in interactions if item.source_style_hcs_candidate),
        ambiguous_basic_fu_bars=ambiguous_count,
        adjacency_gap_pairs_skipped=gap_pairs_skipped,
    )
