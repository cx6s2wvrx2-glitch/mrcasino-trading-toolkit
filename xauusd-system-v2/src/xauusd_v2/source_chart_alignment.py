from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .data_snapshot import DataSnapshotManifest


class SourceChartAlignmentState(StrEnum):
    ALIGNED_CANDIDATE = "aligned_candidate"
    MISSING_SOURCE_TIME = "missing_source_time"
    MISSING_BROKER_IDENTITY = "missing_broker_identity"
    BROKER_MISMATCH = "broker_mismatch"
    SYMBOL_MISMATCH = "symbol_mismatch"
    TIMEFRAME_MISMATCH = "timeframe_mismatch"
    WINDOW_OUTSIDE_SNAPSHOT = "window_outside_snapshot"
    OFF_BAR_GRID = "off_bar_grid"
    SNAPSHOT_NOT_CLOSED = "snapshot_not_closed"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class SourceChartAlignmentRequest:
    source_id: str
    source_locator: str
    canonical_symbol: str = "XAUUSD"
    broker_name: str | None = None
    source_symbol: str | None = None
    timeframe_seconds: int | None = None
    window_start: datetime | None = None
    window_end: datetime | None = None


@dataclass(frozen=True, slots=True)
class SourceChartAlignmentResult:
    state: SourceChartAlignmentState
    source_id: str
    source_locator: str
    snapshot_id: str
    aligned: bool
    reason: str


def align_source_chart_to_snapshot(
    *,
    request: SourceChartAlignmentRequest,
    snapshot: DataSnapshotManifest,
) -> SourceChartAlignmentResult:
    """Fail-closed alignment from a labelled source chart to immutable broker bars.

    This does not infer chart timestamps, broker identity, timeframe or symbol from
    pixels. All of those must be explicitly available in source provenance before a
    chart can become an historical-replay candidate.
    """
    source_id = request.source_id.strip()
    locator = request.source_locator.strip()
    canonical = request.canonical_symbol.strip().upper()
    if not source_id or not locator:
        raise ValueError("source_id and source_locator are required")
    if canonical != "XAUUSD":
        return _result(request, snapshot, SourceChartAlignmentState.NOT_CERTIFIED, "alignment accepts canonical XAUUSD only")
    if snapshot.canonical_symbol != "XAUUSD":
        return _result(request, snapshot, SourceChartAlignmentState.NOT_CERTIFIED, "snapshot is not canonical XAUUSD")

    if request.broker_name is None or request.source_symbol is None:
        return _result(
            request,
            snapshot,
            SourceChartAlignmentState.MISSING_BROKER_IDENTITY,
            "source chart broker/source-symbol identity is required; do not infer it from visual appearance",
        )
    broker = request.broker_name.strip()
    source_symbol = request.source_symbol.strip()
    if not broker or not source_symbol:
        return _result(
            request,
            snapshot,
            SourceChartAlignmentState.MISSING_BROKER_IDENTITY,
            "source chart broker/source-symbol identity is required",
        )

    if broker.casefold() != snapshot.source_name.strip().casefold():
        return _result(request, snapshot, SourceChartAlignmentState.BROKER_MISMATCH, "source chart broker does not match immutable snapshot source")
    if source_symbol.casefold() != snapshot.source_symbol.strip().casefold():
        return _result(request, snapshot, SourceChartAlignmentState.SYMBOL_MISMATCH, "source chart broker symbol does not match immutable snapshot symbol")

    if request.timeframe_seconds is None or request.timeframe_seconds <= 0:
        return _result(request, snapshot, SourceChartAlignmentState.NOT_CERTIFIED, "positive source-chart timeframe is required")
    if request.timeframe_seconds != snapshot.timeframe_seconds:
        return _result(request, snapshot, SourceChartAlignmentState.TIMEFRAME_MISMATCH, "source chart timeframe does not match immutable snapshot timeframe")

    start = request.window_start
    end = request.window_end
    if start is None or end is None:
        return _result(
            request,
            snapshot,
            SourceChartAlignmentState.MISSING_SOURCE_TIME,
            "source chart needs explicit start/end timestamps; image/date-only context is insufficient",
        )
    if start.tzinfo is None or start.utcoffset() is None or end.tzinfo is None or end.utcoffset() is None:
        return _result(request, snapshot, SourceChartAlignmentState.NOT_CERTIFIED, "source chart timestamps must be timezone-aware")
    if end <= start:
        return _result(request, snapshot, SourceChartAlignmentState.NOT_CERTIFIED, "source chart window_end must be after window_start")

    if not snapshot.closed_only:
        return _result(request, snapshot, SourceChartAlignmentState.SNAPSHOT_NOT_CLOSED, "historical source alignment requires a closed-only immutable snapshot")
    if start < snapshot.first_timestamp or end > snapshot.coverage_end:
        return _result(request, snapshot, SourceChartAlignmentState.WINDOW_OUTSIDE_SNAPSHOT, "source chart window is not fully covered by the immutable snapshot")

    interval = snapshot.timeframe_seconds
    start_offset = (start - snapshot.first_timestamp).total_seconds()
    end_offset = (end - snapshot.first_timestamp).total_seconds()
    if start_offset % interval != 0 or end_offset % interval != 0:
        return _result(request, snapshot, SourceChartAlignmentState.OFF_BAR_GRID, "source chart timestamps do not align to the immutable snapshot bar grid")

    return _result(
        request,
        snapshot,
        SourceChartAlignmentState.ALIGNED_CANDIDATE,
        "broker, symbol, timeframe, closed snapshot coverage and exact bar grid all align; still requires stage-level source certification",
        aligned=True,
    )


def _result(
    request: SourceChartAlignmentRequest,
    snapshot: DataSnapshotManifest,
    state: SourceChartAlignmentState,
    reason: str,
    *,
    aligned: bool = False,
) -> SourceChartAlignmentResult:
    return SourceChartAlignmentResult(
        state=state,
        source_id=request.source_id.strip(),
        source_locator=request.source_locator.strip(),
        snapshot_id=snapshot.snapshot_id,
        aligned=aligned,
        reason=reason,
    )
