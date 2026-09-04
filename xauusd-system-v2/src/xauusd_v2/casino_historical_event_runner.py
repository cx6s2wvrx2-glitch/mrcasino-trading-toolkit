from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from math import isfinite

from .agents.data_agent import MarketBar
from .beta_hcs_retest_shadow import BetaHCSZone, update_beta_hcs_zone
from .beta_hcs_shadow import (
    BetaHCSBoxState,
    BetaHCSDirection,
    BetaTrackedManipulationBox,
    evaluate_beta_hcs_interaction,
)
from .casino_directional_marker_semantics import CasinoMarkerDirection
from .casino_indicator_event_stream import (
    CasinoIndicatorEventFrame,
    HCSCounterEventInput,
    build_supplied_indicator_event_frame,
)
from .helper_fu_doji_shadow import apply_casino_v7_default_visible_filters
from .helper_fu_shadow import beta_fu_core_shadow, casino_v7_core_shadow


STATUS = "SUPPLIED_INDICATOR_HISTORY_REPLAY_COMPLETE_NOT_CERTIFIED"


@dataclass(frozen=True, slots=True)
class CasinoHistoricalBarDiagnostic:
    bar_time_utc: datetime
    casino_bullish_branch: str
    casino_bearish_branch: str
    casino_helper_doji: bool
    beta_bullish_fu_candidate: bool
    beta_bearish_fu_candidate: bool
    beta_bullish_sn_candidate: bool
    beta_bearish_sn_candidate: bool
    emitted_hcs_counts: tuple[tuple[str, int], ...]


@dataclass(frozen=True, slots=True)
class CasinoHistoricalEventRun:
    status: str
    symbol: str
    timeframe: str
    timeframe_seconds: int
    input_bar_count: int
    closed_bar_count: int
    evaluated_bar_count: int
    event_frame_count: int
    supplied_indicator_event_count: int
    frames: tuple[CasinoIndicatorEventFrame, ...]
    diagnostics: tuple[CasinoHistoricalBarDiagnostic, ...]
    implementation_behavior_replayed: bool = True
    strategy_semantics_certified: bool = False
    reference_feed_alignment_complete: bool = False
    performance_claim_allowed: bool = False
    promotion_allowed: bool = False
    live_execution_authorized: bool = False


@dataclass(slots=True)
class _TrackedBox:
    direction: BetaHCSDirection
    timeframe: str
    creation_time: int
    state: BetaHCSBoxState
    base_pattern: str
    pattern_text: str
    top_val: float
    bottom_val: float
    original_top: float
    original_bottom: float
    hcs_count: int = 0
    protection_end_time: int | None = None
    protection_active: bool = True
    est_wick_high: float | None = None
    est_wick_low: float | None = None

    def public_box(self) -> BetaTrackedManipulationBox:
        return BetaTrackedManipulationBox(
            direction=self.direction,
            timeframe=self.timeframe,
            creation_time=self.creation_time,
            state=self.state,
            base_pattern=self.base_pattern,
            top_val=self.top_val,
            bottom_val=self.bottom_val,
            original_top=self.original_top,
            original_bottom=self.original_bottom,
            hcs_count=self.hcs_count,
        )


class _BetaSingleTimeframeState:
    """Sequential shadow of the supplied BETA FU/HCS box mechanics for one timeframe.

    This deliberately replays only the supplied BETA pieces already extracted into
    V2: broad FU/SN candidates, tracked FU/SN boxes, HCS counting and 50/60-minute
    HCS-zone retesting. Multi-timeframe established-manipulation aggregation and
    negation remain a later layer and are not invented here.
    """

    def __init__(
        self,
        *,
        timeframe_seconds: int,
        beta_soft_start: bool,
        beta_show_hcs_boxes: bool,
    ) -> None:
        self.timeframe_seconds = timeframe_seconds
        self.timeframe = _beta_timeframe_string(timeframe_seconds)
        self.beta_soft_start = beta_soft_start
        self.beta_show_hcs_boxes = beta_show_hcs_boxes
        self.boxes: list[_TrackedBox] = []  # newest first, matching array.unshift
        self.hcs_zones: list[BetaHCSZone] = []

    @property
    def hcs_enabled(self) -> bool:
        if self.timeframe_seconds % 60 != 0:
            return False
        minutes = self.timeframe_seconds // 60
        if 1 <= minutes <= 20:
            return True
        if 30 <= minutes <= 120:
            return self.beta_soft_start
        return False

    def process_bar(
        self,
        *,
        previous: MarketBar,
        current: MarketBar,
    ) -> tuple[
        tuple[HCSCounterEventInput, ...],
        tuple[CasinoMarkerDirection, ...],
        bool,
        bool,
        bool,
        bool,
    ]:
        beta = beta_fu_core_shadow(
            open=current.open,
            high=current.high,
            low=current.low,
            close=current.close,
            previous_high=previous.high,
            previous_low=previous.low,
        )
        bull_sn, bear_sn = _beta_sn_candidates(previous=previous, current=current, is_x3=beta.is_x3)

        hcs_inputs: list[HCSCounterEventInput] = []
        new_hcs_zones: list[BetaHCSZone] = []
        current_time = _epoch_ms(current.timestamp)

        if self.hcs_enabled:
            for direction, current_is_fu, current_is_sn in (
                (BetaHCSDirection.BEAR, beta.bearish_fu_candidate, bear_sn),
                (BetaHCSDirection.BULL, beta.bullish_fu_candidate, bull_sn),
            ):
                if not (current_is_fu or current_is_sn):
                    continue
                for box in self.boxes:
                    result = evaluate_beta_hcs_interaction(
                        box=box.public_box(),
                        current_direction=direction,
                        current_is_fu=current_is_fu,
                        current_is_sn=current_is_sn,
                        current_high=current.high,
                        current_low=current.low,
                        current_time=current_time,
                        current_confirmed=True,
                    )
                    if not result.hcs:
                        continue
                    box.hcs_count = result.next_hcs_count
                    box.pattern_text = result.next_pattern_text
                    hcs_inputs.append(
                        HCSCounterEventInput(
                            direction=_casino_direction(direction),
                            count=result.next_hcs_count,
                        )
                    )
                    if (
                        self.beta_show_hcs_boxes
                        and result.creates_hcs_zone_in_supplied_beta
                    ):
                        new_hcs_zones.append(
                            BetaHCSZone(
                                direction=direction,
                                top_val=box.original_top,
                                bottom_val=box.original_bottom,
                            )
                        )
                    # Pine deduplicates HCS by direction + timeframe candle time.
                    break

        bear_hcs = any(item.direction is CasinoMarkerDirection.BEARISH for item in hcs_inputs)
        bull_hcs = any(item.direction is CasinoMarkerDirection.BULLISH for item in hcs_inputs)

        if self.hcs_enabled:
            self._create_current_box(
                direction=BetaHCSDirection.BEAR,
                current=current,
                current_is_fu=beta.bearish_fu_candidate,
                current_is_sn=bear_sn,
                current_is_hcs=bear_hcs,
            )
            self._create_current_box(
                direction=BetaHCSDirection.BULL,
                current=current,
                current_is_fu=beta.bullish_fu_candidate,
                current_is_sn=bull_sn,
                current_is_hcs=bull_hcs,
            )
            self._manage_tracked_boxes(current=current)

        self.hcs_zones.extend(new_hcs_zones)
        hcs_retests = self._manage_hcs_zones(current=current)

        return (
            tuple(hcs_inputs),
            hcs_retests,
            beta.bullish_fu_candidate,
            beta.bearish_fu_candidate,
            bull_sn,
            bear_sn,
        )

    def _create_current_box(
        self,
        *,
        direction: BetaHCSDirection,
        current: MarketBar,
        current_is_fu: bool,
        current_is_sn: bool,
        current_is_hcs: bool,
    ) -> None:
        if not (current_is_fu or current_is_sn or current_is_hcs):
            return
        creation_time = _epoch_ms(current.timestamp)
        if any(
            box.creation_time == creation_time
            and box.direction is direction
            and box.timeframe == self.timeframe
            for box in self.boxes
        ):
            return

        parts: list[str] = []
        if current_is_sn:
            parts.append("SN")
        if current_is_fu:
            parts.append("FU")
        if current_is_hcs:
            parts.append("[HCS ✓]")
        prefix = "Bear" if direction is BetaHCSDirection.BEAR else "Bull"
        pattern = prefix + " " + " + ".join(parts)
        body_top = max(current.open, current.close)
        body_bottom = min(current.open, current.close)
        if direction is BetaHCSDirection.BEAR:
            top_val = current.high
            bottom_val = body_top
        else:
            top_val = body_bottom
            bottom_val = current.low

        self.boxes.insert(
            0,
            _TrackedBox(
                direction=direction,
                timeframe=self.timeframe,
                creation_time=creation_time,
                state=BetaHCSBoxState.FORMING,
                base_pattern=pattern,
                pattern_text=pattern,
                top_val=top_val,
                bottom_val=bottom_val,
                original_top=top_val,
                original_bottom=bottom_val,
            ),
        )

    def _manage_tracked_boxes(self, *, current: MarketBar) -> None:
        current_time = _epoch_ms(current.timestamp)
        protection_candles = 3 if _is_beta_entry_timeframe(self.timeframe_seconds) else 1
        survivors: list[_TrackedBox] = []

        # Pine manages from the oldest array element back toward index zero.
        for box in reversed(self.boxes):
            if box.direction is BetaHCSDirection.BEAR:
                if current.high > box.original_top:
                    continue
            else:
                if current.low < box.original_bottom:
                    continue

            if box.state is BetaHCSBoxState.FORMING:
                box.state = BetaHCSBoxState.ESTABLISHED
                box.protection_end_time = current_time + self.timeframe_seconds * 1000 * protection_candles
                box.protection_active = True
                box.est_wick_high = current.high
                box.est_wick_low = current.low
                survivors.append(box)
                continue

            if box.direction is BetaHCSDirection.BEAR:
                self._manage_bear_box(box=box, current=current, current_time=current_time)
            else:
                self._manage_bull_box(box=box, current=current, current_time=current_time)
            survivors.append(box)

        # Restore newest-first order used by the HCS scan.
        self.boxes = list(reversed(survivors))

    @staticmethod
    def _manage_bear_box(*, box: _TrackedBox, current: MarketBar, current_time: int) -> None:
        if box.state is BetaHCSBoxState.ESTABLISHED:
            touched = current.high >= box.bottom_val and current.high < box.original_top
            if box.protection_active:
                if touched:
                    in_est_wick = (
                        box.est_wick_high is not None
                        and box.est_wick_low is not None
                        and box.est_wick_low <= current.high <= box.est_wick_high
                    )
                    box.state = BetaHCSBoxState.EST_RETEST if in_est_wick else BetaHCSBoxState.FORMING_FRESH
                if box.protection_end_time is not None and current_time >= box.protection_end_time:
                    box.protection_active = False
            elif touched:
                box.state = BetaHCSBoxState.RESPECTED
                if box.bottom_val < current.high < box.top_val:
                    box.bottom_val = current.high
            return

        if box.state is BetaHCSBoxState.FORMING_FRESH:
            if box.protection_end_time is not None and current_time >= box.protection_end_time:
                box.state = BetaHCSBoxState.RESPECTED
                box.protection_active = False
            return

        if box.state is BetaHCSBoxState.EST_RETEST:
            if box.protection_end_time is not None and current_time >= box.protection_end_time:
                box.state = BetaHCSBoxState.RESPECTED
                box.protection_active = False
            return

        if box.state is BetaHCSBoxState.RESPECTED:
            touching = current.high >= box.bottom_val and current.low <= box.top_val
            if touching and box.bottom_val < current.high < box.top_val:
                box.bottom_val = current.high

    @staticmethod
    def _manage_bull_box(*, box: _TrackedBox, current: MarketBar, current_time: int) -> None:
        if box.state is BetaHCSBoxState.ESTABLISHED:
            touched = current.low <= box.top_val and current.low > box.original_bottom
            if box.protection_active:
                if touched:
                    in_est_wick = (
                        box.est_wick_high is not None
                        and box.est_wick_low is not None
                        and box.est_wick_low <= current.low <= box.est_wick_high
                    )
                    box.state = BetaHCSBoxState.EST_RETEST if in_est_wick else BetaHCSBoxState.FORMING_FRESH
                if box.protection_end_time is not None and current_time >= box.protection_end_time:
                    box.protection_active = False
            elif touched:
                box.state = BetaHCSBoxState.RESPECTED
                if box.bottom_val < current.low < box.top_val:
                    box.top_val = current.low
            return

        if box.state is BetaHCSBoxState.FORMING_FRESH:
            if box.protection_end_time is not None and current_time >= box.protection_end_time:
                box.state = BetaHCSBoxState.RESPECTED
                box.protection_active = False
            return

        if box.state is BetaHCSBoxState.EST_RETEST:
            if box.protection_end_time is not None and current_time >= box.protection_end_time:
                box.state = BetaHCSBoxState.RESPECTED
                box.protection_active = False
            return

        if box.state is BetaHCSBoxState.RESPECTED:
            touching = current.low <= box.top_val and current.high >= box.bottom_val
            if touching and box.bottom_val < current.low < box.top_val:
                box.top_val = current.low

    def _manage_hcs_zones(self, *, current: MarketBar) -> tuple[CasinoMarkerDirection, ...]:
        if not self.beta_show_hcs_boxes or not self.hcs_zones:
            return ()
        next_zones: list[BetaHCSZone] = []
        retesting: set[CasinoMarkerDirection] = set()
        for zone in self.hcs_zones:
            update = update_beta_hcs_zone(
                zone=zone,
                current_high=current.high,
                current_low=current.low,
            )
            if update.retesting:
                retesting.add(_casino_direction(zone.direction))
            if update.delete_zone:
                continue
            next_zones.append(
                BetaHCSZone(
                    direction=zone.direction,
                    top_val=update.next_top_val,
                    bottom_val=update.next_bottom_val,
                    is_broken=update.is_broken,
                )
            )
        self.hcs_zones = next_zones
        order = (CasinoMarkerDirection.BEARISH, CasinoMarkerDirection.BULLISH)
        return tuple(direction for direction in order if direction in retesting)


def run_supplied_indicator_history(
    *,
    bars: tuple[MarketBar, ...],
    timeframe_seconds: int,
    symbol: str = "XAUUSD",
    timeframe: str | None = None,
    doji_body_ratio_threshold: float = 0.30,
    beta_soft_start: bool = True,
    beta_show_hcs_boxes: bool = True,
    include_empty_frames: bool = False,
) -> CasinoHistoricalEventRun:
    """Replay supplied Casino/BETA indicator behavior over ordered historical bars.

    Closed bars are processed strictly left-to-right. The final provisional bar, if
    present, is ignored. Casino_v7 supplies the Strong/ATT marker class; the supplied
    BETA mechanics independently supply broad FU/SN-driven HCS/HCS-retest state.
    These implementation outputs are normalized into the common event stream and are
    never promoted here to certified strategy semantics.
    """

    _validate_history_input(bars=bars, timeframe_seconds=timeframe_seconds, symbol=symbol)
    tf = timeframe or _display_timeframe(timeframe_seconds)
    closed = tuple(bar for bar in bars if bar.is_closed)
    beta_state = _BetaSingleTimeframeState(
        timeframe_seconds=timeframe_seconds,
        beta_soft_start=beta_soft_start,
        beta_show_hcs_boxes=beta_show_hcs_boxes,
    )

    frames: list[CasinoIndicatorEventFrame] = []
    diagnostics: list[CasinoHistoricalBarDiagnostic] = []
    total_events = 0

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
        (
            hcs_inputs,
            hcs_retests,
            beta_bull_fu,
            beta_bear_fu,
            beta_bull_sn,
            beta_bear_sn,
        ) = beta_state.process_bar(previous=previous, current=current)

        frame = build_supplied_indicator_event_frame(
            symbol=symbol,
            timeframe=tf,
            bar_time_utc=current.timestamp,
            bullish_fu_class=filtered.bullish_after_filter,
            bearish_fu_class=filtered.bearish_after_filter,
            hcs_events=hcs_inputs,
            hcs_retest_directions=hcs_retests,
        )
        total_events += frame.supplied_indicator_event_count
        if include_empty_frames or frame.events:
            frames.append(frame)

        diagnostics.append(
            CasinoHistoricalBarDiagnostic(
                bar_time_utc=current.timestamp.astimezone(UTC),
                casino_bullish_branch=core.bullish_branch,
                casino_bearish_branch=core.bearish_branch,
                casino_helper_doji=filtered.is_doji_by_helper_parameter,
                beta_bullish_fu_candidate=beta_bull_fu,
                beta_bearish_fu_candidate=beta_bear_fu,
                beta_bullish_sn_candidate=beta_bull_sn,
                beta_bearish_sn_candidate=beta_bear_sn,
                emitted_hcs_counts=tuple(
                    (item.direction.value, item.count) for item in hcs_inputs
                ),
            )
        )

    return CasinoHistoricalEventRun(
        status=STATUS,
        symbol=symbol,
        timeframe=tf,
        timeframe_seconds=timeframe_seconds,
        input_bar_count=len(bars),
        closed_bar_count=len(closed),
        evaluated_bar_count=max(0, len(closed) - 1),
        event_frame_count=len(frames),
        supplied_indicator_event_count=total_events,
        frames=tuple(frames),
        diagnostics=tuple(diagnostics),
    )


def _beta_sn_candidates(
    *,
    previous: MarketBar,
    current: MarketBar,
    is_x3: bool,
) -> tuple[bool, bool]:
    both_sides = max(current.open, current.close) < current.high and min(current.open, current.close) > current.low
    bull = (
        current.high > previous.high
        and current.low < previous.low
        and max(current.open, current.close) < previous.high
        and min(current.open, current.close) > previous.low
        and current.open < current.close
        and not is_x3
        and both_sides
    )
    bear = (
        current.high > previous.high
        and current.low < previous.low
        and min(current.open, current.close) > previous.low
        and max(current.open, current.close) < previous.high
        and current.open > current.close
        and not is_x3
        and both_sides
    )
    return bull, bear


def _validate_history_input(
    *,
    bars: tuple[MarketBar, ...],
    timeframe_seconds: int,
    symbol: str,
) -> None:
    if timeframe_seconds <= 0:
        raise ValueError("timeframe_seconds must be positive")
    if symbol.strip().upper() != "XAUUSD":
        raise ValueError("historical indicator runner is XAUUSD-only")
    if len(bars) < 2:
        raise ValueError("at least two bars are required")

    provisional_seen = False
    previous_time: datetime | None = None
    for index, bar in enumerate(bars):
        values = (bar.open, bar.high, bar.low, bar.close)
        if not all(isfinite(value) for value in values):
            raise ValueError(f"bar {index} has non-finite OHLC")
        if bar.low > min(bar.open, bar.close) or bar.high < max(bar.open, bar.close) or bar.low > bar.high:
            raise ValueError(f"bar {index} has invalid OHLC")
        if bar.timestamp.tzinfo is None or bar.timestamp.utcoffset() is None:
            raise ValueError(f"bar {index} timestamp must be timezone-aware")
        if previous_time is not None and bar.timestamp <= previous_time:
            raise ValueError("bars must be strictly increasing")
        previous_time = bar.timestamp
        if not bar.is_closed:
            if index != len(bars) - 1:
                raise ValueError("only the final bar may be provisional")
            provisional_seen = True
        elif provisional_seen:
            raise ValueError("closed bar cannot follow a provisional bar")

    if sum(1 for bar in bars if bar.is_closed) < 2:
        raise ValueError("at least two closed bars are required")


def _epoch_ms(value: datetime) -> int:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return int(value.astimezone(UTC).timestamp() * 1000)


def _display_timeframe(timeframe_seconds: int) -> str:
    if timeframe_seconds % 60 == 0:
        return f"M{timeframe_seconds // 60}"
    return f"{timeframe_seconds}s"


def _beta_timeframe_string(timeframe_seconds: int) -> str:
    if timeframe_seconds % 60 != 0:
        return ""
    minutes = timeframe_seconds // 60
    return str(minutes)


def _is_beta_entry_timeframe(timeframe_seconds: int) -> bool:
    return timeframe_seconds % 60 == 0 and 1 <= timeframe_seconds // 60 <= 5


def _casino_direction(direction: BetaHCSDirection) -> CasinoMarkerDirection:
    if direction is BetaHCSDirection.BEAR:
        return CasinoMarkerDirection.BEARISH
    return CasinoMarkerDirection.BULLISH
