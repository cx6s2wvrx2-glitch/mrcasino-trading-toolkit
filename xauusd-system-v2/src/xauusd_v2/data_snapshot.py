from __future__ import annotations

import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from .agents.base import AgentContractError
from .agents.data_agent import MarketBar, MarketDataValidationReport, XAUUSDDataAgent


class DataSnapshotError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class DataSnapshotManifest:
    snapshot_id: str
    sha256: str
    canonical_symbol: str
    timeframe_seconds: int
    source_name: str
    source_symbol: str
    source_file_name: str | None
    bar_count: int
    first_timestamp: datetime
    last_timestamp: datetime
    coverage_end: datetime
    closed_only: bool
    schema_version: str = "xauusd_ohlc_v1"


def _parse_timestamp(raw: str, *, row_number: int) -> datetime:
    text = raw.strip()
    if not text:
        raise DataSnapshotError(f"row {row_number}: timestamp is required")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        value = datetime.fromisoformat(text)
    except ValueError as exc:
        raise DataSnapshotError(f"row {row_number}: invalid ISO-8601 timestamp") from exc
    if value.tzinfo is None or value.utcoffset() is None:
        raise DataSnapshotError(f"row {row_number}: timestamp must be timezone-aware")
    return value


def _parse_price(raw: str, *, field_name: str, row_number: int) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError) as exc:
        raise DataSnapshotError(f"row {row_number}: invalid {field_name}") from exc


def load_xauusd_csv_snapshot(
    path: str | Path,
    *,
    source_name: str,
    source_symbol: str,
    timeframe_seconds: int,
    evaluation_time: datetime,
    data_agent: XAUUSDDataAgent | None = None,
) -> tuple[tuple[MarketBar, ...], DataSnapshotManifest, MarketDataValidationReport]:
    file_path = Path(path)
    return load_xauusd_csv_snapshot_bytes(
        file_path.read_bytes(),
        source_name=source_name,
        source_symbol=source_symbol,
        timeframe_seconds=timeframe_seconds,
        evaluation_time=evaluation_time,
        source_file_name=file_path.name,
        data_agent=data_agent,
    )


def load_xauusd_csv_snapshot_bytes(
    raw_bytes: bytes,
    *,
    source_name: str,
    source_symbol: str,
    timeframe_seconds: int,
    evaluation_time: datetime,
    source_file_name: str | None = None,
    data_agent: XAUUSDDataAgent | None = None,
) -> tuple[tuple[MarketBar, ...], DataSnapshotManifest, MarketDataValidationReport]:
    if not raw_bytes:
        raise DataSnapshotError("snapshot file is empty")
    if not source_name.strip() or not source_symbol.strip():
        raise DataSnapshotError("source_name and source_symbol are required")
    if timeframe_seconds <= 0:
        raise DataSnapshotError("timeframe_seconds must be positive")
    if evaluation_time.tzinfo is None or evaluation_time.utcoffset() is None:
        raise DataSnapshotError("evaluation_time must be timezone-aware")

    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataSnapshotError("snapshot must be UTF-8 CSV") from exc

    reader = csv.DictReader(io.StringIO(text))
    required = {"timestamp", "open", "high", "low", "close"}
    fields = set(reader.fieldnames or ())
    missing = sorted(required - fields)
    if missing:
        raise DataSnapshotError(f"missing required CSV columns: {', '.join(missing)}")

    bars: list[MarketBar] = []
    interval = timedelta(seconds=timeframe_seconds)
    for row_number, row in enumerate(reader, start=2):
        timestamp = _parse_timestamp(row["timestamp"], row_number=row_number)
        is_closed = timestamp + interval <= evaluation_time
        bars.append(
            MarketBar(
                timestamp=timestamp,
                open=_parse_price(row["open"], field_name="open", row_number=row_number),
                high=_parse_price(row["high"], field_name="high", row_number=row_number),
                low=_parse_price(row["low"], field_name="low", row_number=row_number),
                close=_parse_price(row["close"], field_name="close", row_number=row_number),
                is_closed=is_closed,
                source_name=source_name.strip(),
                source_symbol=source_symbol.strip(),
            )
        )

    if not bars:
        raise DataSnapshotError("snapshot contains no data rows")

    agent = data_agent or XAUUSDDataAgent()
    try:
        report, _ = agent.validate_batch(
            bars=tuple(bars),
            timeframe_seconds=timeframe_seconds,
            evaluation_time=evaluation_time,
            canonical_symbol="XAUUSD",
        )
    except AgentContractError as exc:
        raise DataSnapshotError(str(exc)) from exc

    digest = hashlib.sha256(raw_bytes).hexdigest()
    closed_only = report.provisional_bars == 0
    coverage_end = bars[-1].timestamp + interval if bars[-1].is_closed else bars[-1].timestamp
    manifest = DataSnapshotManifest(
        snapshot_id=f"sha256:{digest}",
        sha256=digest,
        canonical_symbol="XAUUSD",
        timeframe_seconds=timeframe_seconds,
        source_name=source_name.strip(),
        source_symbol=source_symbol.strip(),
        source_file_name=source_file_name,
        bar_count=len(bars),
        first_timestamp=bars[0].timestamp,
        last_timestamp=bars[-1].timestamp,
        coverage_end=coverage_end,
        closed_only=closed_only,
    )
    return tuple(bars), manifest, report
