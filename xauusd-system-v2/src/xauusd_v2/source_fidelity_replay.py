from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from pathlib import Path
from typing import Any

from .agents.data_agent import MarketBar


class SourceFidelityReplayError(ValueError):
    pass


class AnchorPredicate(StrEnum):
    RANGE_TOUCH = "range_touch"
    LOW_EQUALS = "low_equals"
    HIGH_EQUALS = "high_equals"
    CLOSE_AT_OR_ABOVE = "close_at_or_above"
    CLOSE_AT_OR_BELOW = "close_at_or_below"


@dataclass(frozen=True, slots=True)
class SourcePriceAnchor:
    anchor_id: str
    level: Decimal
    predicate: AnchorPredicate
    source_ref: str


@dataclass(frozen=True, slots=True)
class ExpansionProbe:
    window_bars: int
    source_ref: str


@dataclass(frozen=True, slots=True)
class SourceFidelityFixture:
    episode_id: str
    source_locator: str
    timeframe_seconds: int
    window_start: datetime
    window_end: datetime
    anchors: tuple[SourcePriceAnchor, ...]
    expansion_probe: ExpansionProbe | None
    promotion_allowed: bool = False
    schema_version: str = "source_fidelity_fixture_v1"


@dataclass(frozen=True, slots=True)
class AnchorMatch:
    anchor_id: str
    level: Decimal
    predicate: AnchorPredicate
    source_ref: str
    matched: bool
    matched_at: datetime | None
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal | None
    reason: str


@dataclass(frozen=True, slots=True)
class ExpansionMatch:
    window_bars: int
    source_ref: str
    matched: bool
    start_at: datetime | None
    end_at: datetime | None
    low: Decimal | None
    high: Decimal | None
    range: Decimal | None
    reason: str


@dataclass(frozen=True, slots=True)
class SourceFidelityReplayResult:
    episode_id: str
    source_locator: str
    timeframe_seconds: int
    window_start: datetime
    window_end: datetime
    anchor_matches: tuple[AnchorMatch, ...]
    expansion_match: ExpansionMatch | None
    all_anchors_matched: bool
    expansion_probe_matched: bool
    expansion_finishes_before_first_anchor: bool | None
    semantic_stage_certification: bool = False
    performance_claim_allowed: bool = False
    promotion_allowed: bool = False
    strategy_truth_changed: bool = False
    live_execution_authorized: bool = False


_FIXTURE_KEYS = {
    "schema_version",
    "episode_id",
    "source_locator",
    "timeframe_seconds",
    "window_start",
    "window_end",
    "anchors",
    "expansion_probe",
    "promotion_allowed",
}
_ANCHOR_KEYS = {"anchor_id", "level", "predicate", "source_ref"}
_EXPANSION_KEYS = {"window_bars", "source_ref"}


def _require_exact_keys(value: object, expected: set[str], *, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SourceFidelityReplayError(f"{field} must be an object")
    observed = set(value)
    if observed != expected:
        raise SourceFidelityReplayError(
            f"{field} schema mismatch; missing={sorted(expected - observed)}, extra={sorted(observed - expected)}"
        )
    return value


def _required_text(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SourceFidelityReplayError(f"{key} is required and must be non-empty text")
    return value.strip()


def _aware_datetime(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise SourceFidelityReplayError(f"{field} must be an ISO-8601 timestamp")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise SourceFidelityReplayError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SourceFidelityReplayError(f"{field} must be timezone-aware")
    return parsed


def _positive_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise SourceFidelityReplayError(f"{field} must be a positive integer")
    return value


def _decimal(value: object, *, field: str) -> Decimal:
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        raise SourceFidelityReplayError(f"{field} must be a decimal-compatible value")
    try:
        parsed = Decimal(str(value))
    except InvalidOperation as exc:
        raise SourceFidelityReplayError(f"{field} must be a valid decimal") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise SourceFidelityReplayError(f"{field} must be finite and positive")
    return parsed


def load_source_fidelity_fixture(path: str | Path) -> SourceFidelityFixture:
    fixture_path = Path(path).expanduser().resolve()
    if not fixture_path.is_file():
        raise SourceFidelityReplayError("source fidelity fixture is unavailable")
    try:
        raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SourceFidelityReplayError("source fidelity fixture must be valid UTF-8 JSON") from exc

    item = _require_exact_keys(raw, _FIXTURE_KEYS, field="fixture")
    if item["schema_version"] != "source_fidelity_fixture_v1":
        raise SourceFidelityReplayError("unsupported source fidelity fixture schema_version")
    if item["promotion_allowed"] is not False:
        raise SourceFidelityReplayError("source fidelity fixtures must keep promotion_allowed=false")

    episode_id = _required_text(item, "episode_id")
    source_locator = _required_text(item, "source_locator")
    timeframe_seconds = _positive_int(item["timeframe_seconds"], field="timeframe_seconds")
    window_start = _aware_datetime(item["window_start"], field="window_start")
    window_end = _aware_datetime(item["window_end"], field="window_end")
    if window_end <= window_start:
        raise SourceFidelityReplayError("window_end must be later than window_start")

    raw_anchors = item["anchors"]
    if not isinstance(raw_anchors, list) or not raw_anchors:
        raise SourceFidelityReplayError("anchors must be a non-empty array")

    anchors: list[SourcePriceAnchor] = []
    seen_ids: set[str] = set()
    for index, raw_anchor in enumerate(raw_anchors):
        anchor_item = _require_exact_keys(raw_anchor, _ANCHOR_KEYS, field=f"anchors[{index}]")
        anchor_id = _required_text(anchor_item, "anchor_id")
        if anchor_id in seen_ids:
            raise SourceFidelityReplayError(f"duplicate anchor_id: {anchor_id}")
        seen_ids.add(anchor_id)
        predicate_text = _required_text(anchor_item, "predicate")
        try:
            predicate = AnchorPredicate(predicate_text)
        except ValueError as exc:
            raise SourceFidelityReplayError(
                f"anchors[{index}].predicate is not supported: {predicate_text}"
            ) from exc
        anchors.append(
            SourcePriceAnchor(
                anchor_id=anchor_id,
                level=_decimal(anchor_item["level"], field=f"anchors[{index}].level"),
                predicate=predicate,
                source_ref=_required_text(anchor_item, "source_ref"),
            )
        )

    raw_probe = item["expansion_probe"]
    expansion_probe: ExpansionProbe | None
    if raw_probe is None:
        expansion_probe = None
    else:
        probe_item = _require_exact_keys(raw_probe, _EXPANSION_KEYS, field="expansion_probe")
        window_bars = _positive_int(probe_item["window_bars"], field="expansion_probe.window_bars")
        expansion_probe = ExpansionProbe(
            window_bars=window_bars,
            source_ref=_required_text(probe_item, "source_ref"),
        )

    return SourceFidelityFixture(
        episode_id=episode_id,
        source_locator=source_locator,
        timeframe_seconds=timeframe_seconds,
        window_start=window_start,
        window_end=window_end,
        anchors=tuple(anchors),
        expansion_probe=expansion_probe,
    )


def _bar_decimal(value: float) -> Decimal:
    return Decimal(str(value))


def _matches(bar: MarketBar, anchor: SourcePriceAnchor) -> bool:
    level = anchor.level
    high = _bar_decimal(bar.high)
    low = _bar_decimal(bar.low)
    close = _bar_decimal(bar.close)

    if anchor.predicate is AnchorPredicate.RANGE_TOUCH:
        return low <= level <= high
    if anchor.predicate is AnchorPredicate.LOW_EQUALS:
        return low == level
    if anchor.predicate is AnchorPredicate.HIGH_EQUALS:
        return high == level
    if anchor.predicate is AnchorPredicate.CLOSE_AT_OR_ABOVE:
        return close >= level
    if anchor.predicate is AnchorPredicate.CLOSE_AT_OR_BELOW:
        return close <= level
    raise AssertionError(f"unhandled anchor predicate: {anchor.predicate}")


def _matched_anchor(anchor: SourcePriceAnchor, bar: MarketBar) -> AnchorMatch:
    return AnchorMatch(
        anchor_id=anchor.anchor_id,
        level=anchor.level,
        predicate=anchor.predicate,
        source_ref=anchor.source_ref,
        matched=True,
        matched_at=bar.timestamp,
        open=_bar_decimal(bar.open),
        high=_bar_decimal(bar.high),
        low=_bar_decimal(bar.low),
        close=_bar_decimal(bar.close),
        reason="first distinct closed bar satisfying this source-labelled price predicate in canonical anchor order",
    )


def _unmatched_anchor(anchor: SourcePriceAnchor, *, blocked: bool) -> AnchorMatch:
    return AnchorMatch(
        anchor_id=anchor.anchor_id,
        level=anchor.level,
        predicate=anchor.predicate,
        source_ref=anchor.source_ref,
        matched=False,
        matched_at=None,
        open=None,
        high=None,
        low=None,
        close=None,
        reason=(
            "not evaluated because a prior ordered anchor was not found"
            if blocked
            else "no distinct closed bar in the fixture window satisfied this source-labelled price predicate"
        ),
    )


def _largest_contiguous_expansion(
    bars: tuple[MarketBar, ...],
    *,
    probe: ExpansionProbe,
    timeframe_seconds: int,
) -> ExpansionMatch:
    count = probe.window_bars
    if len(bars) < count:
        return ExpansionMatch(
            window_bars=count,
            source_ref=probe.source_ref,
            matched=False,
            start_at=None,
            end_at=None,
            low=None,
            high=None,
            range=None,
            reason="fixture window contains fewer bars than the requested expansion window",
        )

    step = timedelta(seconds=timeframe_seconds)
    best: tuple[Decimal, int, Decimal, Decimal] | None = None
    for start in range(0, len(bars) - count + 1):
        window = bars[start : start + count]
        if any(window[offset].timestamp - window[offset - 1].timestamp != step for offset in range(1, count)):
            continue
        low = min(_bar_decimal(bar.low) for bar in window)
        high = max(_bar_decimal(bar.high) for bar in window)
        span = high - low
        if best is None or span > best[0]:
            best = (span, start, low, high)

    if best is None:
        return ExpansionMatch(
            window_bars=count,
            source_ref=probe.source_ref,
            matched=False,
            start_at=None,
            end_at=None,
            low=None,
            high=None,
            range=None,
            reason="no fully contiguous closed-bar window exists for the requested expansion probe",
        )

    span, start, low, high = best
    end_open = bars[start + count - 1].timestamp
    return ExpansionMatch(
        window_bars=count,
        source_ref=probe.source_ref,
        matched=True,
        start_at=bars[start].timestamp,
        end_at=end_open + step,
        low=low,
        high=high,
        range=span,
        reason="largest exact contiguous high-low range in the fixture window",
    )


def evaluate_source_fidelity_fixture(
    *,
    bars: tuple[MarketBar, ...],
    fixture: SourceFidelityFixture,
    timeframe_seconds: int,
) -> SourceFidelityReplayResult:
    if timeframe_seconds <= 0:
        raise SourceFidelityReplayError("timeframe_seconds must be positive")
    if timeframe_seconds != fixture.timeframe_seconds:
        raise SourceFidelityReplayError("fixture timeframe does not match supplied market data")

    window_bars = tuple(
        bar
        for bar in bars
        if fixture.window_start <= bar.timestamp < fixture.window_end and bar.is_closed
    )
    if not window_bars:
        raise SourceFidelityReplayError("fixture window contains no closed market bars")

    previous_timestamp: datetime | None = None
    for index, bar in enumerate(window_bars):
        if bar.timestamp.tzinfo is None or bar.timestamp.utcoffset() is None:
            raise SourceFidelityReplayError(f"window bar {index} timestamp must be timezone-aware")
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
            raise SourceFidelityReplayError("window bars must be strictly increasing")
        previous_timestamp = bar.timestamp

    matches: list[AnchorMatch] = []
    search_start = 0
    blocked = False
    for anchor in fixture.anchors:
        if blocked:
            matches.append(_unmatched_anchor(anchor, blocked=True))
            continue

        matched_index: int | None = None
        for index in range(search_start, len(window_bars)):
            if _matches(window_bars[index], anchor):
                matched_index = index
                break

        if matched_index is None:
            matches.append(_unmatched_anchor(anchor, blocked=False))
            blocked = True
            continue

        bar = window_bars[matched_index]
        matches.append(_matched_anchor(anchor, bar))
        # Source path ordering is intentionally conservative: every next anchor
        # must be observed on a later closed bar. We never infer intrabar order
        # from OHLC extremes.
        search_start = matched_index + 1

    all_anchors_matched = all(item.matched for item in matches)
    expansion_match = (
        _largest_contiguous_expansion(
            window_bars,
            probe=fixture.expansion_probe,
            timeframe_seconds=timeframe_seconds,
        )
        if fixture.expansion_probe is not None
        else None
    )
    expansion_probe_matched = expansion_match is None or expansion_match.matched

    expansion_before_first_anchor: bool | None = None
    first_anchor = matches[0] if matches else None
    if expansion_match is not None and expansion_match.matched and first_anchor is not None and first_anchor.matched:
        assert expansion_match.end_at is not None
        assert first_anchor.matched_at is not None
        expansion_before_first_anchor = expansion_match.end_at <= first_anchor.matched_at

    return SourceFidelityReplayResult(
        episode_id=fixture.episode_id,
        source_locator=fixture.source_locator,
        timeframe_seconds=timeframe_seconds,
        window_start=fixture.window_start,
        window_end=fixture.window_end,
        anchor_matches=tuple(matches),
        expansion_match=expansion_match,
        all_anchors_matched=all_anchors_matched,
        expansion_probe_matched=expansion_probe_matched,
        expansion_finishes_before_first_anchor=expansion_before_first_anchor,
    )
