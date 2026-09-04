from __future__ import annotations

import argparse
import json
from datetime import datetime
from typing import Any

from .casino_history_report import build_verified_indicator_history_report
from .casino_human_review import build_greek_human_review


def _datetime(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError("timestamp must be timezone-aware")
    return parsed


def build_summary_text(report: dict[str, Any], *, marker_limit: int = 40) -> str:
    if marker_limit < 0:
        raise ValueError("marker_limit must be non-negative")
    lines: list[str] = ["========== VERIFIED INDICATOR HISTORY REPLAY =========="]
    for key in (
        "status",
        "snapshot_id",
        "normalized_sha256",
        "broker_name",
        "broker_symbol",
        "broker_timezone",
        "timeframe",
        "window_start_utc",
        "window_end_utc",
        "replay_bar_count_before_window_clip",
        "window_evaluated_bar_count",
        "window_event_frame_count",
        "window_event_count",
        "source_hcs_marker_proxy_candidate_count",
        "source_marker_fu_negation_proxy_candidate_count",
        "source_hcs_plus_negation_proxy_candidate_count",
        "analysis_event_stream_frame_count",
        "analysis_event_stream_event_count",
        "window_gap_affected_derived_bar_count",
        "events_on_gap_affected_derived_bars",
        "reference_feed_alignment_complete",
        "strategy_semantics_certified",
    ):
        lines.append(f"{key}: {report.get(key)}")

    lines.append("")
    lines.append("event_counts_by_kind:")
    for key, value in report.get("event_counts_by_kind", {}).items():
        lines.append(f"  {key}: {value}")

    lines.append("")
    lines.append("event_counts_by_direction:")
    for key, value in report.get("event_counts_by_direction", {}).items():
        lines.append(f"  {key}: {value}")

    lines.append("")
    lines.append("analysis_event_stream_counts_by_kind:")
    for key, value in report.get("analysis_event_stream_counts_by_kind", {}).items():
        lines.append(f"  {key}: {value}")

    lines.append("")
    lines.append("source_hcs_marker_proxy_counts_by_form:")
    for key, value in report.get("source_hcs_marker_proxy_counts_by_form", {}).items():
        lines.append(f"  {key}: {value}")

    comparison = report.get("hcs_implementation_vs_source_marker_proxy", {})
    lines.append("")
    lines.append("HCS IMPLEMENTATION vs SOURCE-MARKER PROXY:")
    for key in (
        "beta_hcs_event_bar_count",
        "source_marker_proxy_bar_count",
        "overlap_bar_count",
        "beta_only_bar_count",
        "source_proxy_only_bar_count",
    ):
        lines.append(f"  {key}: {comparison.get(key)}")

    beta_hcs = [item for item in report.get("events", []) if item.get("kind") == "hcs"]
    lines.append("")
    lines.append(f"BETA HCS EVENTS: {len(beta_hcs)}")
    for item in beta_hcs:
        lines.append(
            " | ".join(
                (
                    str(item.get("bar_time_utc")),
                    str(item.get("direction")),
                    str(item.get("marker_text")),
                    f"hcs_count={item.get('hcs_count')}",
                    f"gap={item.get('derived_bar_gap_affected')}",
                )
            )
        )

    source_candidates = report.get("source_hcs_marker_proxy_candidates", [])
    lines.append("")
    lines.append(f"SOURCE-STYLE HCS MARKER PROXY CANDIDATES: {len(source_candidates)}")
    for item in source_candidates:
        role_text = f"{item.get('first_semantic_role')}->{item.get('second_semantic_role')}"
        lines.append(
            " | ".join(
                (
                    f"{item.get('first_bar_time_utc')} -> {item.get('second_bar_time_utc')}",
                    f"{item.get('first_direction')}->{item.get('second_direction')}",
                    str(item.get("form")),
                    role_text,
                    str(item.get("source_strength_label_proxy")),
                    f"same_direction={item.get('same_direction')}",
                    f"latest_nodes={item.get('latest_prior_marker_node_count')}",
                    f"gap={item.get('derived_bar_gap_affected')}",
                )
            )
        )

    negation_candidates = report.get("source_marker_fu_negation_proxy_candidates", [])
    lines.append("")
    lines.append(f"SOURCE-MARKER FU NEGATION PROXY CANDIDATES: {len(negation_candidates)}")
    for item in negation_candidates:
        lines.append(
            " | ".join(
                (
                    f"{item.get('original_bar_time_utc')} -> {item.get('negating_bar_time_utc')}",
                    f"{item.get('original_direction')}->{item.get('negating_direction')}",
                    f"{item.get('original_helper_class')}->{item.get('negating_helper_class')}",
                    f"offset=+{item.get('candle_offset')}",
                    f"latest_nodes={item.get('latest_prior_marker_node_count')}",
                    f"gap={item.get('derived_bar_gap_affected')}",
                )
            )
        )

    hcs_negation_candidates = report.get("source_hcs_plus_negation_proxy_candidates", [])
    lines.append("")
    lines.append(f"SOURCE HCS + NEGATION PROXY CANDIDATES: {len(hcs_negation_candidates)}")
    for item in hcs_negation_candidates:
        lines.append(
            " | ".join(
                (
                    f"HCS {item.get('hcs_first_bar_time_utc')} -> {item.get('hcs_bar_time_utc')}",
                    f"NEG -> {item.get('negating_bar_time_utc')}",
                    f"{item.get('hcs_direction')}->{item.get('negating_direction')}",
                    str(item.get("hcs_form")),
                    f"offset=+{item.get('negation_candle_offset')}",
                    f"gap={item.get('derived_bar_gap_affected')}",
                )
            )
        )

    analysis_frames = report.get("analysis_event_stream_frames", [])
    lines.append("")
    lines.append(f"FIRST {marker_limit} UNIFIED ANALYSIS FRAMES:")
    for frame in analysis_frames[:marker_limit]:
        event_text = []
        for event in frame.get("events", []):
            candidate_suffix = " [candidate]" if event.get("candidate_only") else ""
            event_text.append(
                f"{event.get('kind')}:{event.get('direction')}"
                f"@{event.get('provenance')}{candidate_suffix}"
            )
        lines.append(
            " | ".join(
                (
                    str(frame.get("bar_time_utc")),
                    "; ".join(event_text) if event_text else "no_events",
                    f"gap={frame.get('derived_bar_gap_affected')}",
                )
            )
        )

    lines.append("")
    lines.append(f"FIRST {marker_limit} STRONG/ATT EVENTS:")
    shown = 0
    for item in report.get("events", []):
        if item.get("kind") not in {"strong_fu", "attempted_fu"}:
            continue
        lines.append(
            " | ".join(
                (
                    str(item.get("bar_time_utc")),
                    str(item.get("kind")),
                    str(item.get("direction")),
                    str(item.get("visual_cue")),
                    f"gap={item.get('derived_bar_gap_affected')}",
                )
            )
        )
        shown += 1
        if shown >= marker_limit:
            break

    lines.append("=======================================================")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay supplied Casino/BETA indicator events from a verified persisted XAUUSD MT5 snapshot."
    )
    parser.add_argument("ingestion_manifest")
    parser.add_argument("--timeframe", default="M15", help="M1, M5, M10, M15, M30, H1, H4, H8 or D1")
    parser.add_argument("--start", required=True, type=_datetime)
    parser.add_argument("--end", required=True, type=_datetime)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--summary", action="store_true", help="print a technical comparison-oriented summary instead of full JSON")
    output_group.add_argument("--review", action="store_true", help="print a compact Greek human-readable review")
    parser.add_argument("--marker-limit", type=int, default=40, help="rows to print from the unified timeline and Strong/ATT list with --summary")
    parser.add_argument("--compound-limit", type=int, default=12, help="compound unified frames to print with --review")
    args = parser.parse_args()

    report = build_verified_indicator_history_report(
        args.ingestion_manifest,
        timeframe_code=args.timeframe,
        start_utc=args.start,
        end_utc=args.end,
    )
    if args.review:
        print(build_greek_human_review(report, compound_limit=args.compound_limit))
    elif args.summary:
        print(build_summary_text(report, marker_limit=args.marker_limit))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
