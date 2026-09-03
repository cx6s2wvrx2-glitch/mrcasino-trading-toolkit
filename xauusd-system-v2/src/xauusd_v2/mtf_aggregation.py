from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class MTFAggregationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class TimeframeSpec:
    code: str
    minutes: int

    @property
    def seconds(self) -> int:
        return self.minutes * 60


SUPPORTED_TIMEFRAMES: tuple[TimeframeSpec, ...] = (
    TimeframeSpec("M5", 5),
    TimeframeSpec("M10", 10),
    TimeframeSpec("M15", 15),
    TimeframeSpec("M30", 30),
    TimeframeSpec("H1", 60),
    TimeframeSpec("H4", 240),
    TimeframeSpec("H8", 480),
    TimeframeSpec("D1", 1440),
)
_TIMEFRAME_BY_CODE = {item.code: item for item in SUPPORTED_TIMEFRAMES}
_BLOCKED_11H_ALIASES = {"H11", "11H", "M660", "660"}


@dataclass(frozen=True, slots=True)
class MinuteOHLC:
    timestamp_utc: datetime
    open_text: str
    high_text: str
    low_text: str
    close_text: str
    open_value: Decimal = field(init=False, repr=False)
    high_value: Decimal = field(init=False, repr=False)
    low_value: Decimal = field(init=False, repr=False)
    close_value: Decimal = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.timestamp_utc.tzinfo is None or self.timestamp_utc.utcoffset() is None:
            raise MTFAggregationError("minute timestamp must be timezone-aware")
        object.__setattr__(self, "open_value", _decimal(self.open_text, field_name="open"))
        object.__setattr__(self, "high_value", _decimal(self.high_text, field_name="high"))
        object.__setattr__(self, "low_value", _decimal(self.low_text, field_name="low"))
        object.__setattr__(self, "close_value", _decimal(self.close_text, field_name="close"))
        if (
            self.low_value > min(self.open_value, self.close_value)
            or self.high_value < max(self.open_value, self.close_value)
            or self.low_value > self.high_value
        ):
            raise MTFAggregationError("minute has invalid OHLC geometry")


@dataclass(frozen=True, slots=True)
class DerivedBarCandidate:
    timeframe_code: str
    timeframe_seconds: int
    timestamp_utc: datetime
    broker_open_time: datetime
    bucket_end_utc: datetime
    open_text: str
    high_text: str
    low_text: str
    close_text: str
    child_count: int
    expected_slots: int
    leading_missing_minutes: int
    internal_missing_minutes: int
    trailing_missing_minutes: int
    first_child_timestamp_utc: datetime
    last_child_timestamp_utc: datetime

    @property
    def gap_affected(self) -> bool:
        return (
            self.leading_missing_minutes > 0
            or self.internal_missing_minutes > 0
            or self.trailing_missing_minutes > 0
        )


@dataclass(slots=True)
class _WorkingBucket:
    start_utc: datetime
    start_local: datetime
    end_utc: datetime
    open_text: str
    high_text: str
    high_value: Decimal
    low_text: str
    low_value: Decimal
    close_text: str
    first_child_timestamp_utc: datetime
    last_child_timestamp_utc: datetime
    child_count: int
    internal_missing_minutes: int


def parse_timeframe_codes(value: str | Iterable[str]) -> tuple[TimeframeSpec, ...]:
    if isinstance(value, str):
        raw_items = value.split(",")
    else:
        raw_items = list(value)
    specs: list[TimeframeSpec] = []
    seen: set[str] = set()
    for raw in raw_items:
        code = str(raw).strip().upper()
        if not code:
            continue
        if code in _BLOCKED_11H_ALIASES:
            raise MTFAggregationError(
                "11h synthesis is blocked: B-07/R-118 does not certify the candle/session anchor"
            )
        spec = _TIMEFRAME_BY_CODE.get(code)
        if spec is None:
            allowed = ", ".join(item.code for item in SUPPORTED_TIMEFRAMES)
            raise MTFAggregationError(f"unsupported derived timeframe {code!r}; allowed: {allowed}")
        if code not in seen:
            specs.append(spec)
            seen.add(code)
    if not specs:
        raise MTFAggregationError("at least one supported timeframe is required")
    return tuple(specs)


def load_broker_timezone(value: str) -> ZoneInfo:
    text = value.strip()
    if not text:
        raise MTFAggregationError("source timezone is required and must never be inferred")
    try:
        return ZoneInfo(text)
    except ZoneInfoNotFoundError as exc:
        raise MTFAggregationError("source timezone must be a valid IANA timezone") from exc


def broker_bucket_bounds(
    *,
    timestamp_utc: datetime,
    timeframe: TimeframeSpec,
    broker_timezone: ZoneInfo,
) -> tuple[datetime, datetime, datetime]:
    if timestamp_utc.tzinfo is None or timestamp_utc.utcoffset() is None:
        raise MTFAggregationError("timestamp must be timezone-aware")
    local = timestamp_utc.astimezone(broker_timezone)
    return broker_bucket_bounds_from_local(
        broker_local_timestamp=local,
        timeframe=timeframe,
        broker_timezone=broker_timezone,
    )


def broker_bucket_bounds_from_local(
    *,
    broker_local_timestamp: datetime,
    timeframe: TimeframeSpec,
    broker_timezone: ZoneInfo,
) -> tuple[datetime, datetime, datetime]:
    if broker_local_timestamp.tzinfo is None or broker_local_timestamp.utcoffset() is None:
        raise MTFAggregationError("broker-local timestamp must be timezone-aware")
    if timeframe.code not in _TIMEFRAME_BY_CODE:
        raise MTFAggregationError("only governed standard timeframes may be aggregated")
    local = broker_local_timestamp
    local_midnight = datetime(
        local.year,
        local.month,
        local.day,
        tzinfo=broker_timezone,
    )
    minute_of_day = local.hour * 60 + local.minute
    bucket_minute = (minute_of_day // timeframe.minutes) * timeframe.minutes
    start_local = local_midnight + timedelta(minutes=bucket_minute)
    end_local = start_local + timedelta(minutes=timeframe.minutes)
    return start_local.astimezone(UTC), end_local.astimezone(UTC), start_local


class TimeframeAggregator:
    """Stream closed M1 OHLC into one broker-local higher-timeframe candidate series.

    This is market-data construction only. It does not certify MT5 native candle
    boundaries, does not fill missing minutes, and has no strategy authority.
    """

    def __init__(
        self,
        *,
        timeframe: TimeframeSpec,
        broker_timezone: ZoneInfo,
        source_coverage_end_utc: datetime,
    ) -> None:
        if timeframe.code not in _TIMEFRAME_BY_CODE:
            raise MTFAggregationError("unsupported timeframe specification")
        if source_coverage_end_utc.tzinfo is None or source_coverage_end_utc.utcoffset() is None:
            raise MTFAggregationError("source coverage end must be timezone-aware")
        self.timeframe = timeframe
        self.broker_timezone = broker_timezone
        self.source_coverage_end_utc = source_coverage_end_utc.astimezone(UTC)
        self._bucket: _WorkingBucket | None = None
        self._previous_minute_timestamp: datetime | None = None
        self.omitted_trailing_partial_buckets = 0

    def add(self, minute: MinuteOHLC) -> DerivedBarCandidate | None:
        timestamp = minute.timestamp_utc.astimezone(UTC)
        if self._previous_minute_timestamp is not None and timestamp <= self._previous_minute_timestamp:
            raise MTFAggregationError("source M1 bars must be strictly increasing")
        self._previous_minute_timestamp = timestamp

        if (
            self._bucket is not None
            and self._bucket.start_utc <= timestamp < self._bucket.end_utc
        ):
            self._extend_bucket(self._bucket, minute)
            return None

        local = timestamp.astimezone(self.broker_timezone)
        start_utc, end_utc, start_local = broker_bucket_bounds_from_local(
            broker_local_timestamp=local,
            timeframe=self.timeframe,
            broker_timezone=self.broker_timezone,
        )
        flushed: DerivedBarCandidate | None = None
        if self._bucket is not None:
            flushed = self._finish_bucket(self._bucket)
        self._bucket = self._new_bucket(
            minute=minute,
            start_utc=start_utc,
            end_utc=end_utc,
            start_local=start_local,
        )
        return flushed

    def finish(self) -> DerivedBarCandidate | None:
        if self._bucket is None:
            return None
        bucket = self._bucket
        self._bucket = None
        candidate = self._finish_bucket(bucket)
        if candidate is None:
            self.omitted_trailing_partial_buckets += 1
        return candidate

    def _new_bucket(
        self,
        *,
        minute: MinuteOHLC,
        start_utc: datetime,
        end_utc: datetime,
        start_local: datetime,
    ) -> _WorkingBucket:
        return _WorkingBucket(
            start_utc=start_utc,
            start_local=start_local,
            end_utc=end_utc,
            open_text=minute.open_text,
            high_text=minute.high_text,
            high_value=minute.high_value,
            low_text=minute.low_text,
            low_value=minute.low_value,
            close_text=minute.close_text,
            first_child_timestamp_utc=minute.timestamp_utc.astimezone(UTC),
            last_child_timestamp_utc=minute.timestamp_utc.astimezone(UTC),
            child_count=1,
            internal_missing_minutes=0,
        )

    def _extend_bucket(self, bucket: _WorkingBucket, minute: MinuteOHLC) -> None:
        timestamp = minute.timestamp_utc.astimezone(UTC)
        delta_minutes = int((timestamp - bucket.last_child_timestamp_utc).total_seconds() // 60)
        if delta_minutes <= 0:
            raise MTFAggregationError("source M1 bars must be strictly increasing")
        if delta_minutes > 1:
            bucket.internal_missing_minutes += delta_minutes - 1

        if minute.high_value > bucket.high_value:
            bucket.high_value = minute.high_value
            bucket.high_text = minute.high_text
        if minute.low_value < bucket.low_value:
            bucket.low_value = minute.low_value
            bucket.low_text = minute.low_text
        bucket.close_text = minute.close_text
        bucket.last_child_timestamp_utc = timestamp
        bucket.child_count += 1

    def _finish_bucket(self, bucket: _WorkingBucket) -> DerivedBarCandidate | None:
        # The final source horizon may cut through a higher-TF candle. Never emit
        # that candle as closed merely because the last available M1 bar is closed.
        if bucket.end_utc > self.source_coverage_end_utc:
            return None

        expected_slots = int((bucket.end_utc - bucket.start_utc).total_seconds() // 60)
        leading = int(
            (bucket.first_child_timestamp_utc - bucket.start_utc).total_seconds() // 60
        )
        trailing = int(
            (bucket.end_utc - bucket.last_child_timestamp_utc).total_seconds() // 60
        ) - 1
        if leading < 0 or trailing < 0 or expected_slots <= 0:
            raise MTFAggregationError("invalid broker-local bucket geometry")
        if (
            leading
            + bucket.internal_missing_minutes
            + bucket.child_count
            + trailing
            != expected_slots
        ):
            raise MTFAggregationError("M1 coverage diagnostics do not reconcile to bucket slots")

        return DerivedBarCandidate(
            timeframe_code=self.timeframe.code,
            timeframe_seconds=self.timeframe.seconds,
            timestamp_utc=bucket.start_utc,
            broker_open_time=bucket.start_local,
            bucket_end_utc=bucket.end_utc,
            open_text=bucket.open_text,
            high_text=bucket.high_text,
            low_text=bucket.low_text,
            close_text=bucket.close_text,
            child_count=bucket.child_count,
            expected_slots=expected_slots,
            leading_missing_minutes=leading,
            internal_missing_minutes=bucket.internal_missing_minutes,
            trailing_missing_minutes=trailing,
            first_child_timestamp_utc=bucket.first_child_timestamp_utc,
            last_child_timestamp_utc=bucket.last_child_timestamp_utc,
        )


def aggregate_minutes(
    *,
    minutes: Iterable[MinuteOHLC],
    timeframe: TimeframeSpec,
    broker_timezone: ZoneInfo,
    source_coverage_end_utc: datetime,
) -> tuple[DerivedBarCandidate, ...]:
    aggregator = TimeframeAggregator(
        timeframe=timeframe,
        broker_timezone=broker_timezone,
        source_coverage_end_utc=source_coverage_end_utc,
    )
    output: list[DerivedBarCandidate] = []
    for minute in minutes:
        candidate = aggregator.add(minute)
        if candidate is not None:
            output.append(candidate)
    final = aggregator.finish()
    if final is not None:
        output.append(final)
    return tuple(output)


def _decimal(value: str, *, field_name: str) -> Decimal:
    text = str(value).strip()
    if not text:
        raise MTFAggregationError(f"{field_name} is required")
    try:
        parsed = Decimal(text)
    except InvalidOperation as exc:
        raise MTFAggregationError(f"invalid {field_name}") from exc
    if not parsed.is_finite():
        raise MTFAggregationError(f"{field_name} must be finite")
    return parsed
