from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable

from .replay_alignment import SourcePriceAnchor, VerifiedReplaySlice


class ReplayAnchorPathError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class TouchCluster:
    start_timestamp_utc: str
    end_timestamp_utc: str
    bar_count: int
    low_min: str
    high_max: str
    first_open: str
    last_close: str
    previous_bar_close: str | None
    next_bar_close: str | None


@dataclass(frozen=True, slots=True)
class AnchorPathFacts:
    anchor_id: str
    price: str
    start_utc: str
    end_utc: str
    bar_count: int
    first_timestamp_utc: str
    last_timestamp_utc: str
    window_open: str
    window_close: str
    window_low_min: str
    window_high_max: str
    touch_bar_count: int
    touch_cluster_count: int
    touch_clusters: tuple[TouchCluster, ...]
    strict_low_below_bar_count: int
    close_below_bar_count: int
    strict_high_above_bar_count: int
    close_above_bar_count: int
    first_strict_low_below_timestamp_utc: str | None
    first_close_below_timestamp_utc: str | None
    first_strict_high_above_timestamp_utc: str | None
    first_close_above_timestamp_utc: str | None


def parse_aware_timestamp(value: str, *, field: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ReplayAnchorPathError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ReplayAnchorPathError(f"{field} must be timezone-aware")
    return parsed.astimezone(UTC)


def _decimal(value: object, *, field: str) -> Decimal:
    try:
        text = str(value).strip()
        if not text:
            raise InvalidOperation
        parsed = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise ReplayAnchorPathError(f"{field} must be a decimal") from exc
    if not parsed.is_finite():
        raise ReplayAnchorPathError(f"{field} must be finite")
    return parsed


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def select_anchor(anchors: Iterable[SourcePriceAnchor], anchor_id: str) -> SourcePriceAnchor:
    wanted = anchor_id.strip()
    if not wanted:
        raise ReplayAnchorPathError("anchor_id is required")
    matches = [anchor for anchor in anchors if anchor.anchor_id == wanted]
    if len(matches) != 1:
        raise ReplayAnchorPathError(f"anchor_id must match exactly one source anchor: {wanted}")
    return matches[0]


def measure_anchor_path(
    replay: VerifiedReplaySlice,
    anchor: SourcePriceAnchor,
    *,
    start_utc: datetime,
    end_utc: datetime,
) -> AnchorPathFacts:
    if start_utc.tzinfo is None or start_utc.utcoffset() is None:
        raise ReplayAnchorPathError("start_utc must be timezone-aware")
    if end_utc.tzinfo is None or end_utc.utcoffset() is None:
        raise ReplayAnchorPathError("end_utc must be timezone-aware")
    start = start_utc.astimezone(UTC)
    end = end_utc.astimezone(UTC)
    if start >= end:
        raise ReplayAnchorPathError("path window requires start_utc < end_utc")

    rows: list[dict[str, object]] = []
    with replay.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"timestamp", "open", "high", "low", "close"}
        missing = sorted(required - set(reader.fieldnames or ()))
        if missing:
            raise ReplayAnchorPathError(f"replay CSV missing fields: {', '.join(missing)}")
        for row_no, row in enumerate(reader, start=2):
            timestamp = parse_aware_timestamp(row["timestamp"], field=f"row {row_no} timestamp")
            if timestamp < start:
                continue
            if timestamp >= end:
                break
            open_value = _decimal(row["open"], field=f"row {row_no} open")
            high = _decimal(row["high"], field=f"row {row_no} high")
            low = _decimal(row["low"], field=f"row {row_no} low")
            close = _decimal(row["close"], field=f"row {row_no} close")
            if low > min(open_value, close) or high < max(open_value, close) or low > high:
                raise ReplayAnchorPathError(f"row {row_no} has invalid OHLC geometry")
            rows.append(
                {
                    "timestamp": timestamp,
                    "open": open_value,
                    "high": high,
                    "low": low,
                    "close": close,
                }
            )

    if not rows:
        raise ReplayAnchorPathError("requested path window contains no replay bars")

    level = anchor.price
    touch_flags = [row["low"] <= level <= row["high"] for row in rows]
    clusters: list[TouchCluster] = []
    index = 0
    while index < len(rows):
        if not touch_flags[index]:
            index += 1
            continue
        start_index = index
        while index + 1 < len(rows) and touch_flags[index + 1]:
            index += 1
        end_index = index
        cluster_rows = rows[start_index : end_index + 1]
        clusters.append(
            TouchCluster(
                start_timestamp_utc=_iso(cluster_rows[0]["timestamp"]),
                end_timestamp_utc=_iso(cluster_rows[-1]["timestamp"]),
                bar_count=len(cluster_rows),
                low_min=str(min(row["low"] for row in cluster_rows)),
                high_max=str(max(row["high"] for row in cluster_rows)),
                first_open=str(cluster_rows[0]["open"]),
                last_close=str(cluster_rows[-1]["close"]),
                previous_bar_close=(str(rows[start_index - 1]["close"]) if start_index > 0 else None),
                next_bar_close=(str(rows[end_index + 1]["close"]) if end_index + 1 < len(rows) else None),
            )
        )
        index += 1

    def first_timestamp(predicate) -> str | None:
        for row in rows:
            if predicate(row):
                return _iso(row["timestamp"])
        return None

    return AnchorPathFacts(
        anchor_id=anchor.anchor_id,
        price=str(level),
        start_utc=_iso(start),
        end_utc=_iso(end),
        bar_count=len(rows),
        first_timestamp_utc=_iso(rows[0]["timestamp"]),
        last_timestamp_utc=_iso(rows[-1]["timestamp"]),
        window_open=str(rows[0]["open"]),
        window_close=str(rows[-1]["close"]),
        window_low_min=str(min(row["low"] for row in rows)),
        window_high_max=str(max(row["high"] for row in rows)),
        touch_bar_count=sum(1 for flag in touch_flags if flag),
        touch_cluster_count=len(clusters),
        touch_clusters=tuple(clusters),
        strict_low_below_bar_count=sum(1 for row in rows if row["low"] < level),
        close_below_bar_count=sum(1 for row in rows if row["close"] < level),
        strict_high_above_bar_count=sum(1 for row in rows if row["high"] > level),
        close_above_bar_count=sum(1 for row in rows if row["close"] > level),
        first_strict_low_below_timestamp_utc=first_timestamp(lambda row: row["low"] < level),
        first_close_below_timestamp_utc=first_timestamp(lambda row: row["close"] < level),
        first_strict_high_above_timestamp_utc=first_timestamp(lambda row: row["high"] > level),
        first_close_above_timestamp_utc=first_timestamp(lambda row: row["close"] > level),
    )
