from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .agents.data_agent import MarketBar
from .casino_historical_event_runner import run_supplied_indicator_history
from .mt5_snapshot_load import load_verified_persisted_mt5_snapshot
from .mtf_aggregation import (
    MinuteOHLC,
    aggregate_minutes,
    load_broker_timezone,
    parse_timeframe_codes,
)
from .data_snapshot import load_xauusd_csv_snapshot_bytes


class CasinoHistoryReportError(ValueError):
    pass


def build_verified_indicator_history_report(
    ingestion_manifest: str | Path,
    *,
    timeframe_code: str,
    start_utc: datetime,
    end_utc: datetime,
) -> dict[str, Any]:
    """Replay supplied indicator behavior from a verified persisted MT5 snapshot.

    Replay state is built from all available closed history before ``end_utc`` so an
    HCS in the requested window can depend on an earlier tracked box. The returned
    event list is then clipped to ``[start_utc, end_utc)``. No reference-feed or
    strategy-semantic certification is implied.
    """

    start = _aware_utc(start_utc, field="start_utc")
    end = _aware_utc(end_utc, field="end_utc")
    if end <= start:
        raise CasinoHistoryReportError("end_utc must be after start_utc")

    verified = load_verified_persisted_mt5_snapshot(ingestion_manifest)
    if verified.snapshot.timeframe_seconds != 60:
        raise CasinoHistoryReportError("verified indicator history report currently requires an M1 persisted snapshot")

    bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
        verified.canonical_snapshot_path.read_bytes(),
        source_name=verified.snapshot.source_name,
        source_symbol=verified.snapshot.source_symbol,
        timeframe_seconds=verified.snapshot.timeframe_seconds,
        evaluation_time=verified.snapshot.coverage_end,
        source_file_name=verified.snapshot.source_file_name,
    )
    if reproduced != verified.snapshot:
        raise CasinoHistoryReportError("verified snapshot changed when canonical bytes were reproduced")

    code = timeframe_code.strip().upper()
    if not code:
        raise CasinoHistoryReportError("timeframe_code is required")

    gap_affected_derived_bar_count = 0
    broker_timezone_name: str | None = None
    if code == "M1":
        replay_bars = tuple(bar for bar in bars if bar.is_closed and bar.timestamp < end)
        timeframe_seconds = 60
    else:
        try:
            spec = parse_timeframe_codes((code,))[0]
        except ValueError as exc:
            raise CasinoHistoryReportError(str(exc)) from exc
        broker_timezone_name = _verified_source_timezone(verified.manifest_path)
        broker_timezone = load_broker_timezone(broker_timezone_name)
        minutes = tuple(
            MinuteOHLC(
                timestamp_utc=bar.timestamp,
                open_text=str(bar.open),
                high_text=str(bar.high),
                low_text=str(bar.low),
                close_text=str(bar.close),
            )
            for bar in bars
            if bar.is_closed and bar.timestamp < end
        )
        derived = aggregate_minutes(
            minutes=minutes,
            timeframe=spec,
            broker_timezone=broker_timezone,
            source_coverage_end_utc=min(verified.snapshot.coverage_end, end),
        )
        gap_affected_derived_bar_count = sum(1 for item in derived if item.gap_affected)
        replay_bars = tuple(
            MarketBar(
                timestamp=item.timestamp_utc,
                open=float(item.open_text),
                high=float(item.high_text),
                low=float(item.low_text),
                close=float(item.close_text),
                is_closed=True,
                source_name=verified.snapshot.source_name,
                source_symbol=verified.snapshot.source_symbol,
            )
            for item in derived
            if item.timestamp_utc < end
        )
        timeframe_seconds = spec.seconds

    if len(replay_bars) < 2:
        raise CasinoHistoryReportError("fewer than two closed replay bars are available before end_utc")

    run = run_supplied_indicator_history(
        bars=replay_bars,
        timeframe_seconds=timeframe_seconds,
        symbol="XAUUSD",
        timeframe=code,
    )
    selected_frames = tuple(
        frame for frame in run.frames if start <= frame.bar_time_utc < end
    )

    kind_counts: Counter[str] = Counter()
    direction_counts: Counter[str] = Counter()
    event_records: list[dict[str, Any]] = []
    for frame in selected_frames:
        for event in frame.events:
            kind_counts[event.kind.value] += 1
            direction_counts[event.direction.value] += 1
            event_records.append(
                {
                    "bar_time_utc": _z(frame.bar_time_utc),
                    "timeframe": frame.timeframe,
                    "kind": event.kind.value,
                    "direction": event.direction.value,
                    "source": event.source.value,
                    "marker_text": event.marker_text,
                    "visual_cue": None if event.visual_cue is None else event.visual_cue.value,
                    "hcs_count": event.hcs_count,
                    "relation_to_prior_event": event.relation_to_prior_event,
                    "forming": event.forming,
                    "confirmed": event.confirmed,
                    "contains_hcs_context": event.contains_hcs_context,
                    "strategy_semantics_certified": event.strategy_semantics_certified,
                }
            )

    selected_diag_count = sum(
        1 for item in run.diagnostics if start <= item.bar_time_utc < end
    )
    return {
        "schema_version": "casino_verified_indicator_history_report_v1",
        "status": run.status,
        "snapshot_id": verified.snapshot.snapshot_id,
        "normalized_sha256": verified.normalized_sha256,
        "broker_name": verified.snapshot.source_name,
        "broker_symbol": verified.snapshot.source_symbol,
        "broker_timezone": broker_timezone_name,
        "timeframe": code,
        "timeframe_seconds": timeframe_seconds,
        "window_start_utc": _z(start),
        "window_end_utc": _z(end),
        "replay_seed_first_bar_utc": _z(replay_bars[0].timestamp),
        "replay_bar_count_before_window_clip": len(replay_bars),
        "window_evaluated_bar_count": selected_diag_count,
        "window_event_frame_count": len(selected_frames),
        "window_event_count": len(event_records),
        "event_counts_by_kind": dict(sorted(kind_counts.items())),
        "event_counts_by_direction": dict(sorted(direction_counts.items())),
        "events": event_records,
        "gap_affected_derived_bar_count": gap_affected_derived_bar_count,
        "coverage_boundary": {
            "strong_attempted_source": "supplied Casino_v7 helper shadow plus supplied current-candle doji filter",
            "hcs_source": "supplied BETA broad FU/SN tracked-box HCS state machine",
            "hcs_retest_source": "supplied BETA 50/60-minute HCS box manager only",
            "multi_timeframe_negation_integrated": False,
            "fu_negation_source_semantics_integrated": False,
            "note": "Implementation replay is deliberately separate from source-semantic certification.",
        },
        "reference_feed_required_for_feed_sensitive_geometry": "FOREXCOM:XAUUSD",
        "reference_feed_alignment_complete": False,
        "strategy_semantics_certified": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }


def _verified_source_timezone(manifest_path: Path) -> str:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        value = payload["ingestion"]["source_timezone"]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise CasinoHistoryReportError("verified ingestion source timezone is unavailable") from exc
    text = str(value).strip()
    if not text:
        raise CasinoHistoryReportError("verified ingestion source timezone is blank")
    return text


def _aware_utc(value: datetime, *, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise CasinoHistoryReportError(f"{field} must be timezone-aware")
    return value.astimezone(UTC)


def _z(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
