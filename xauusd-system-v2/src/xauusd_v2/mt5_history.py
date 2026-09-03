from __future__ import annotations

import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, tzinfo
from math import isfinite
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .agents.data_agent import MarketBar, MarketDataValidationReport, XAUUSDDataAgent
from .data_snapshot import DataSnapshotManifest, DataSnapshotError, load_xauusd_csv_snapshot_bytes


class MT5HistoryError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class MT5SupplementalBar:
    """Non-strategy MT5 export fields retained only for provenance/data-quality work."""

    timestamp_utc: datetime
    tick_volume: int | None = None
    real_volume: int | None = None
    spread_points: int | None = None


@dataclass(frozen=True, slots=True)
class MT5HistoryIngestionManifest:
    broker_name: str
    broker_symbol: str
    canonical_symbol: str
    timeframe_seconds: int
    source_timezone: str
    source_file_name: str | None
    source_sha256: str
    source_size_bytes: int
    normalized_snapshot_id: str
    normalized_sha256: str
    bar_count: int
    first_timestamp_utc: datetime
    last_timestamp_utc: datetime
    detected_delimiter: str
    detected_headers: tuple[str, ...]
    gap_count: int
    gap_durations_seconds: tuple[int, ...]
    optional_columns: tuple[str, ...]
    schema_version: str = "mt5_history_adapter_v1"


@dataclass(frozen=True, slots=True)
class MT5HistoryIngestionResult:
    bars: tuple[MarketBar, ...]
    snapshot: DataSnapshotManifest
    validation: MarketDataValidationReport
    ingestion: MT5HistoryIngestionManifest
    supplemental: tuple[MT5SupplementalBar, ...]
    canonical_csv_bytes: bytes


_HEADER_ALIASES = {
    "date": {"date", "<date>"},
    "time": {"time", "<time>"},
    "open": {"open", "<open>"},
    "high": {"high", "<high>"},
    "low": {"low", "<low>"},
    "close": {"close", "<close>"},
    "tick_volume": {"tickvol", "tick_volume", "tick volume", "<tickvol>", "<tick_volume>"},
    "real_volume": {"vol", "volume", "real_volume", "real volume", "<vol>", "<volume>"},
    "spread": {"spread", "<spread>"},
}


def _normalize_header(value: str) -> str:
    return value.strip().lower().replace("\ufeff", "")


def _map_headers(
    fieldnames: Iterable[str] | None,
    *,
    require_time: bool = True,
) -> dict[str, str]:
    if not fieldnames:
        raise MT5HistoryError("MT5 export has no header row")
    normalized_to_original: dict[str, str] = {}
    for original in fieldnames:
        normalized = _normalize_header(original)
        if not normalized:
            continue
        if normalized in normalized_to_original:
            raise MT5HistoryError(f"duplicate MT5 header after normalization: {original}")
        normalized_to_original[normalized] = original

    mapping: dict[str, str] = {}
    for canonical, aliases in _HEADER_ALIASES.items():
        matches = [normalized_to_original[alias] for alias in aliases if alias in normalized_to_original]
        if len(matches) > 1:
            raise MT5HistoryError(f"multiple columns map to MT5 field {canonical}: {matches}")
        if matches:
            mapping[canonical] = matches[0]

    required = ["date", "open", "high", "low", "close"]
    if require_time:
        required.insert(1, "time")
    missing = [name for name in required if name not in mapping]
    if missing:
        raise MT5HistoryError(f"missing required MT5 columns: {', '.join(missing)}")
    return mapping


def _detect_delimiter(text: str) -> str:
    sample = text[:8192]
    candidates = ("\t", ",", ";")
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="\t,;")
        if dialect.delimiter in candidates:
            return dialect.delimiter
    except csv.Error:
        pass
    first_line = sample.splitlines()[0] if sample.splitlines() else ""
    counts = {candidate: first_line.count(candidate) for candidate in candidates}
    delimiter = max(counts, key=counts.get)
    if counts[delimiter] <= 0:
        raise MT5HistoryError("could not detect MT5 export delimiter")
    return delimiter


def _parse_source_timezone(value: str) -> tuple[tzinfo, str]:
    raw = value.strip()
    if not raw:
        raise MT5HistoryError("source_timezone is required; broker timezone must never be inferred")
    if raw.upper() == "UTC" or raw == "Z":
        return timezone.utc, "UTC"

    offset_text = raw.upper().removeprefix("UTC")
    if offset_text.startswith(("+", "-")):
        sign = 1 if offset_text[0] == "+" else -1
        body = offset_text[1:]
        parts = body.split(":")
        if len(parts) not in (1, 2) or not all(part.isdigit() for part in parts):
            raise MT5HistoryError("invalid fixed source_timezone offset")
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) == 2 else 0
        if hours > 23 or minutes > 59:
            raise MT5HistoryError("invalid fixed source_timezone offset")
        delta = timedelta(hours=hours, minutes=minutes) * sign
        name = f"UTC{raw[-len(offset_text):]}" if raw.upper().startswith("UTC") else f"UTC{offset_text}"
        return timezone(delta, name), name

    try:
        zone = ZoneInfo(raw)
    except ZoneInfoNotFoundError as exc:
        raise MT5HistoryError(
            "source_timezone must be UTC, an explicit UTC offset, or a valid IANA timezone"
        ) from exc
    return zone, raw


def _parse_mt5_datetime(
    date_raw: str,
    time_raw: str,
    *,
    row_number: int,
    source_tz: tzinfo,
) -> datetime:
    date_text = date_raw.strip()
    time_text = time_raw.strip()
    if not date_text or not time_text:
        raise MT5HistoryError(f"row {row_number}: MT5 date/time is required")
    combined = f"{date_text} {time_text}"
    formats = (
        "%Y.%m.%d %H:%M:%S",
        "%Y.%m.%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    )
    parsed: datetime | None = None
    for fmt in formats:
        try:
            parsed = datetime.strptime(combined, fmt)
            break
        except ValueError:
            continue
    if parsed is None:
        raise MT5HistoryError(f"row {row_number}: unsupported MT5 date/time format")
    localized = parsed.replace(tzinfo=source_tz)
    return localized.astimezone(timezone.utc)


def _parse_float(value: str | None, *, field_name: str, row_number: int) -> float:
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise MT5HistoryError(f"row {row_number}: invalid {field_name}") from exc
    if not isfinite(parsed):
        raise MT5HistoryError(f"row {row_number}: non-finite {field_name}")
    return parsed


def _parse_optional_int(value: str | None, *, field_name: str, row_number: int) -> int | None:
    if value is None or not str(value).strip():
        return None
    text = str(value).strip()
    try:
        parsed = int(text)
    except ValueError as exc:
        raise MT5HistoryError(f"row {row_number}: invalid {field_name}") from exc
    if parsed < 0:
        raise MT5HistoryError(f"row {row_number}: {field_name} cannot be negative")
    return parsed


def _canonical_csv_bytes(rows: list[tuple[datetime, float, float, float, float]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("timestamp", "open", "high", "low", "close"))
    for timestamp, open_, high, low, close in rows:
        iso = timestamp.isoformat().replace("+00:00", "Z")
        writer.writerow((iso, repr(open_), repr(high), repr(low), repr(close)))
    return stream.getvalue().encode("utf-8")


def load_mt5_xauusd_history(
    path: str | Path,
    *,
    broker_name: str,
    broker_symbol: str,
    source_timezone: str,
    timeframe_seconds: int,
    evaluation_time: datetime,
    data_agent: XAUUSDDataAgent | None = None,
) -> MT5HistoryIngestionResult:
    file_path = Path(path)
    return load_mt5_xauusd_history_bytes(
        file_path.read_bytes(),
        broker_name=broker_name,
        broker_symbol=broker_symbol,
        source_timezone=source_timezone,
        timeframe_seconds=timeframe_seconds,
        evaluation_time=evaluation_time,
        source_file_name=file_path.name,
        data_agent=data_agent,
    )


def load_mt5_xauusd_history_bytes(
    raw_bytes: bytes,
    *,
    broker_name: str,
    broker_symbol: str,
    source_timezone: str,
    timeframe_seconds: int,
    evaluation_time: datetime,
    source_file_name: str | None = None,
    data_agent: XAUUSDDataAgent | None = None,
) -> MT5HistoryIngestionResult:
    if not raw_bytes:
        raise MT5HistoryError("MT5 history export is empty")
    if not broker_name.strip():
        raise MT5HistoryError("broker_name is required")
    if not broker_symbol.strip():
        raise MT5HistoryError("broker_symbol is required")
    if timeframe_seconds <= 0:
        raise MT5HistoryError("timeframe_seconds must be positive")
    if evaluation_time.tzinfo is None or evaluation_time.utcoffset() is None:
        raise MT5HistoryError("evaluation_time must be timezone-aware")

    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise MT5HistoryError("MT5 history export must be UTF-8 text") from exc

    delimiter = _detect_delimiter(text)
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    is_daily = timeframe_seconds == 86_400
    mapping = _map_headers(reader.fieldnames, require_time=not is_daily)
    source_tz, normalized_timezone = _parse_source_timezone(source_timezone)

    rows: list[tuple[datetime, float, float, float, float]] = []
    supplemental: list[MT5SupplementalBar] = []
    previous_timestamp: datetime | None = None
    gap_durations: list[int] = []
    interval = timedelta(seconds=timeframe_seconds)

    for row_number, row in enumerate(reader, start=2):
        time_raw = row.get(mapping["time"], "") if "time" in mapping else "00:00:00"
        timestamp = _parse_mt5_datetime(
            row.get(mapping["date"], ""),
            time_raw,
            row_number=row_number,
            source_tz=source_tz,
        )
        if previous_timestamp is not None:
            if timestamp <= previous_timestamp:
                raise MT5HistoryError("MT5 bars must be strictly increasing with no duplicate timestamps")

            if is_daily:
                previous_local_date = previous_timestamp.astimezone(source_tz).date()
                current_local_date = timestamp.astimezone(source_tz).date()
                day_step = (current_local_date - previous_local_date).days
                if day_step <= 0:
                    raise MT5HistoryError("MT5 daily bars must advance on the broker-local calendar")
                if day_step > 1:
                    gap_durations.append((day_step - 1) * 86_400)
            else:
                difference = timestamp - previous_timestamp
                if difference > interval:
                    gap_durations.append(int(difference.total_seconds() - timeframe_seconds))
                elif difference < interval:
                    raise MT5HistoryError("MT5 bars overlap or are off the declared timeframe grid")
        previous_timestamp = timestamp

        open_ = _parse_float(row.get(mapping["open"]), field_name="open", row_number=row_number)
        high = _parse_float(row.get(mapping["high"]), field_name="high", row_number=row_number)
        low = _parse_float(row.get(mapping["low"]), field_name="low", row_number=row_number)
        close = _parse_float(row.get(mapping["close"]), field_name="close", row_number=row_number)
        if low > min(open_, close) or high < max(open_, close) or low > high:
            raise MT5HistoryError(f"row {row_number}: invalid OHLC geometry")
        rows.append((timestamp, open_, high, low, close))
        supplemental.append(
            MT5SupplementalBar(
                timestamp_utc=timestamp,
                tick_volume=_parse_optional_int(
                    row.get(mapping["tick_volume"]) if "tick_volume" in mapping else None,
                    field_name="tick_volume",
                    row_number=row_number,
                ),
                real_volume=_parse_optional_int(
                    row.get(mapping["real_volume"]) if "real_volume" in mapping else None,
                    field_name="real_volume",
                    row_number=row_number,
                ),
                spread_points=_parse_optional_int(
                    row.get(mapping["spread"]) if "spread" in mapping else None,
                    field_name="spread",
                    row_number=row_number,
                ),
            )
        )

    if not rows:
        raise MT5HistoryError("MT5 history export contains no data rows")

    canonical_bytes = _canonical_csv_bytes(rows)
    try:
        bars, snapshot, validation = load_xauusd_csv_snapshot_bytes(
            canonical_bytes,
            source_name=broker_name.strip(),
            source_symbol=broker_symbol.strip(),
            timeframe_seconds=timeframe_seconds,
            evaluation_time=evaluation_time,
            source_file_name=source_file_name,
            data_agent=data_agent,
        )
    except DataSnapshotError as exc:
        raise MT5HistoryError(str(exc)) from exc

    source_digest = hashlib.sha256(raw_bytes).hexdigest()
    optional_columns = tuple(
        name for name in ("tick_volume", "real_volume", "spread") if name in mapping
    )
    ingestion = MT5HistoryIngestionManifest(
        broker_name=broker_name.strip(),
        broker_symbol=broker_symbol.strip(),
        canonical_symbol="XAUUSD",
        timeframe_seconds=timeframe_seconds,
        source_timezone=normalized_timezone,
        source_file_name=source_file_name,
        source_sha256=source_digest,
        source_size_bytes=len(raw_bytes),
        normalized_snapshot_id=snapshot.snapshot_id,
        normalized_sha256=snapshot.sha256,
        bar_count=len(bars),
        first_timestamp_utc=bars[0].timestamp,
        last_timestamp_utc=bars[-1].timestamp,
        detected_delimiter="TAB" if delimiter == "\t" else delimiter,
        detected_headers=tuple(reader.fieldnames or ()),
        gap_count=len(gap_durations),
        gap_durations_seconds=tuple(gap_durations),
        optional_columns=optional_columns,
    )
    return MT5HistoryIngestionResult(
        bars=bars,
        snapshot=snapshot,
        validation=validation,
        ingestion=ingestion,
        supplemental=tuple(supplemental),
        canonical_csv_bytes=canonical_bytes,
    )
