from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .agents.data_agent import MarketBar
from .casino_historical_event_runner import run_supplied_indicator_history
from .casino_source_hcs_candidate import run_source_hcs_marker_proxy
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
    event list is then clipped to ``[start_utc, end_utc)``. A separate source-style
    HCS marker proxy is also calculated from Casino Strong/ATT output so the BETA HCS
    implementation can be compared with the governed source concept without silently
    treating either one as certified strategy truth.
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
    gap_affected_times: set[datetime] = set()
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
        gap_affected_times = {
            item.timestamp_utc.astimezone(UTC) for item in derived if item.gap_affected
        }
        gap_affected_derived_bar_count = len(gap_affected_times)
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
    source_proxy = run_source_hcs_marker_proxy(bars=replay_bars)
    selected_frames = tuple(
        frame for frame in run.frames if start <= frame.bar_time_utc < end
    )
    selected_source_candidates = tuple(
        item for item in source_proxy.candidates if start <= item.second_bar_time_utc < end
    )

    kind_counts: Counter[str] = Counter()
    direction_counts: Counter[str] = Counter()
    event_records: list[dict[str, Any]] = []
    beta_hcs_bar_times: set[datetime] = set()
    events_on_gap_affected_bar_count = 0
    for frame in selected_frames:
        frame_time = frame.bar_time_utc.astimezone(UTC)
        for event in frame.events:
            kind_counts[event.kind.value] += 1
            direction_counts[event.direction.value] += 1
            if event.kind.value == "hcs":
                beta_hcs_bar_times.add(frame_time)
            if frame_time in gap_affected_times:
                events_on_gap_affected_bar_count += 1
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
                    "derived_bar_gap_affected": frame_time in gap_affected_times,
                }
            )

    source_form_counts = Counter(item.form.value for item in selected_source_candidates)
    source_hcs_bar_times = {
        item.second_bar_time_utc.astimezone(UTC) for item in selected_source_candidates
    }
    source_candidate_records = [
        {
            "first_bar_time_utc": _z(item.first_bar_time_utc),
            "second_bar_time_utc": _z(item.second_bar_time_utc),
            "first_direction": item.first_direction.value,
            "second_direction": item.second_direction.value,
            "first_helper_class": item.first_helper_class.value,
            "second_helper_class": item.second_helper_class.value,
            "first_wick_low": str(item.first_wick_low),
            "first_wick_high": str(item.first_wick_high),
            "second_bar_low": str(item.second_bar_low),
            "second_bar_high": str(item.second_bar_high),
            "exact_last_marker_wick_retest": item.exact_last_marker_wick_retest,
            "same_direction": item.same_direction,
            "form": item.form.value,
            "source_strength_label_proxy": item.source_strength_label_proxy,
            "latest_prior_marker_node_count": item.latest_prior_marker_node_count,
            "derived_bar_gap_affected": item.second_bar_time_utc.astimezone(UTC) in gap_affected_times,
            "source_hcs_semantics_certified": False,
        }
        for item in selected_source_candidates
    ]

    selected_diag_count = sum(
        1 for item in run.diagnostics if start <= item.bar_time_utc < end
    )
    window_gap_times = {item for item in gap_affected_times if start <= item < end}
    overlap = beta_hcs_bar_times & source_hcs_bar_times
    beta_only = beta_hcs_bar_times - source_hcs_bar_times
    source_only = source_hcs_bar_times - beta_hcs_bar_times

    return {
        "schema_version": "casino_verified_indicator_history_report_v2",
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
        "source_hcs_marker_proxy_status": source_proxy.status,
        "source_hcs_marker_proxy_candidate_count": len(selected_source_candidates),
        "source_hcs_marker_proxy_counts_by_form": dict(sorted(source_form_counts.items())),
        "source_hcs_marker_proxy_candidates": source_candidate_records,
        "hcs_implementation_vs_source_marker_proxy": {
            "beta_hcs_event_bar_count": len(beta_hcs_bar_times),
            "source_marker_proxy_bar_count": len(source_hcs_bar_times),
            "overlap_bar_count": len(overlap),
            "beta_only_bar_count": len(beta_only),
            "source_proxy_only_bar_count": len(source_only),
            "overlap_bar_times_utc": [_z(item) for item in sorted(overlap)],
            "beta_only_bar_times_utc": [_z(item) for item in sorted(beta_only)],
            "source_proxy_only_bar_times_utc": [_z(item) for item in sorted(source_only)],
            "comparison_is_strategy_certification": False,
        },
        "gap_affected_derived_bar_count": gap_affected_derived_bar_count,
        "window_gap_affected_derived_bar_count": len(window_gap_times),
        "events_on_gap_affected_derived_bars": events_on_gap_affected_bar_count,
        "source_hcs_proxy_candidates_on_gap_affected_derived_bars": sum(
            1
            for item in selected_source_candidates
            if item.second_bar_time_utc.astimezone(UTC) in gap_affected_times
        ),
        "coverage_boundary": {
            "strong_attempted_source": "supplied Casino_v7 helper shadow plus supplied current-candle doji filter",
            "hcs_source": "supplied BETA broad FU/SN tracked-box HCS state machine",
            "hcs_retest_source": "supplied BETA 50/60-minute HCS box manager only",
            "source_hcs_marker_proxy": "latest prior supplied Casino Strong/ATT marker directional wick + exact OHLC intersection",
            "source_hcs_marker_proxy_same_direction_required": False,
            "source_hcs_marker_proxy_fu_negation_integrated": False,
            "source_hcs_marker_proxy_near_enough_retest_integrated": False,
            "multi_timeframe_negation_integrated": False,
            "fu_negation_source_semantics_integrated": False,
            "note": "Implementation replay and source-style marker proxy are deliberately separate from source-semantic certification.",
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
