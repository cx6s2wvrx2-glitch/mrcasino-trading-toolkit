from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .casino_historical_event_runner import run_supplied_indicator_history
from .casino_indicator_events import CasinoIndicatorEventKind
from .casino_source_hcs_candidate import run_source_hcs_marker_proxy
from .data_snapshot import load_xauusd_csv_snapshot_bytes
from .mt5_snapshot_load import load_verified_persisted_mt5_snapshot


STATUS = "MARCH_INDICATOR_SOURCE_LEVEL_PROBE_COMPLETE_NOT_CERTIFIED"


@dataclass(frozen=True, slots=True)
class MarchSourceProbeSpec:
    probe_id: str
    episode_id: str
    source_role: str
    primitive_family: str
    level: Decimal
    window_start: datetime
    window_end: datetime


def default_fixture_path() -> Path:
    return Path(__file__).resolve().parents[2] / "06_examples" / "MARCH_SOURCE_SEMANTIC_PROBES.json"


def load_probe_specs(path: str | Path | None = None) -> tuple[MarchSourceProbeSpec, ...]:
    fixture = default_fixture_path() if path is None else Path(path)
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    specs: list[MarchSourceProbeSpec] = []
    for item in payload.get("probes", []):
        if int(item.get("timeframe_seconds", 0)) != 60:
            continue
        specs.append(
            MarchSourceProbeSpec(
                probe_id=str(item["probe_id"]),
                episode_id=str(item["episode_id"]),
                source_role=str(item["source_role"]),
                primitive_family=str(item["primitive_family"]),
                level=Decimal(str(item["level"])),
                window_start=_parse_utc(str(item["window_start"])),
                window_end=_parse_utc(str(item["window_end"])),
            )
        )
    if not specs:
        raise ValueError("no governed M1 March probe specs found")
    return tuple(specs)


def build_march_indicator_source_level_probe(
    ingestion_manifest: str | Path,
    *,
    fixture_path: str | Path | None = None,
) -> dict[str, Any]:
    specs = load_probe_specs(fixture_path)
    max_end = max(item.window_end for item in specs)

    verified = load_verified_persisted_mt5_snapshot(ingestion_manifest)
    if verified.snapshot.timeframe_seconds != 60:
        raise ValueError("March indicator source-level probe requires an M1 persisted snapshot")

    bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
        verified.canonical_snapshot_path.read_bytes(),
        source_name=verified.snapshot.source_name,
        source_symbol=verified.snapshot.source_symbol,
        timeframe_seconds=verified.snapshot.timeframe_seconds,
        evaluation_time=verified.snapshot.coverage_end,
        source_file_name=verified.snapshot.source_file_name,
    )
    if reproduced != verified.snapshot:
        raise ValueError("verified snapshot changed when canonical bytes were reproduced")

    replay_bars = tuple(bar for bar in bars if bar.is_closed and bar.timestamp < max_end)
    if len(replay_bars) < 2:
        raise ValueError("insufficient closed M1 history for March probe")

    history = run_supplied_indicator_history(
        bars=replay_bars,
        timeframe_seconds=60,
        symbol="XAUUSD",
        timeframe="M1",
    )
    source_proxy = run_source_hcs_marker_proxy(bars=replay_bars)

    events_by_time: dict[datetime, list[Any]] = defaultdict(list)
    for frame in history.frames:
        events_by_time[frame.bar_time_utc.astimezone(UTC)].extend(frame.events)

    source_candidates_by_time: dict[datetime, list[Any]] = defaultdict(list)
    for candidate in source_proxy.candidates:
        source_candidates_by_time[candidate.second_bar_time_utc.astimezone(UTC)].append(candidate)

    probe_records: list[dict[str, Any]] = []
    for spec in specs:
        touches = tuple(
            bar
            for bar in replay_bars
            if spec.window_start <= bar.timestamp.astimezone(UTC) < spec.window_end
            and Decimal(str(bar.low)) <= spec.level <= Decimal(str(bar.high))
        )
        observations: list[dict[str, Any]] = []
        strong_touch_count = 0
        attempted_touch_count = 0
        dual_marker_touch_count = 0
        beta_hcs_touch_count = 0
        source_proxy_touch_count = 0
        source_forms: Counter[str] = Counter()

        for bar in touches:
            bar_time = bar.timestamp.astimezone(UTC)
            events = events_by_time.get(bar_time, [])
            marker_events = [
                event
                for event in events
                if event.kind in (
                    CasinoIndicatorEventKind.STRONG_FU,
                    CasinoIndicatorEventKind.ATTEMPTED_FU,
                )
            ]
            beta_hcs_events = [event for event in events if event.kind is CasinoIndicatorEventKind.HCS]
            candidates = source_candidates_by_time.get(bar_time, [])

            strong_here = sum(1 for event in marker_events if event.kind is CasinoIndicatorEventKind.STRONG_FU)
            attempted_here = sum(1 for event in marker_events if event.kind is CasinoIndicatorEventKind.ATTEMPTED_FU)
            strong_touch_count += int(strong_here > 0)
            attempted_touch_count += int(attempted_here > 0)
            dual_marker_touch_count += int(len(marker_events) > 1)
            beta_hcs_touch_count += int(bool(beta_hcs_events))
            source_proxy_touch_count += int(bool(candidates))
            source_forms.update(candidate.form.value for candidate in candidates)

            observations.append(
                {
                    "bar_open_utc": _z(bar_time),
                    "open": str(bar.open),
                    "high": str(bar.high),
                    "low": str(bar.low),
                    "close": str(bar.close),
                    "marker_events": [
                        {
                            "kind": event.kind.value,
                            "direction": event.direction.value,
                            "visual_cue": None if event.visual_cue is None else event.visual_cue.value,
                            "marker_text": event.marker_text,
                        }
                        for event in marker_events
                    ],
                    "dual_marker_same_bar": len(marker_events) > 1,
                    "beta_hcs_events": [
                        {
                            "direction": event.direction.value,
                            "marker_text": event.marker_text,
                            "hcs_count": event.hcs_count,
                        }
                        for event in beta_hcs_events
                    ],
                    "source_marker_proxy_candidates": [
                        {
                            "first_bar_time_utc": _z(candidate.first_bar_time_utc),
                            "first_direction": candidate.first_direction.value,
                            "second_direction": candidate.second_direction.value,
                            "first_helper_class": candidate.first_helper_class.value,
                            "second_helper_class": candidate.second_helper_class.value,
                            "first_wick_low": str(candidate.first_wick_low),
                            "first_wick_high": str(candidate.first_wick_high),
                            "form": candidate.form.value,
                            "source_strength_label_proxy": candidate.source_strength_label_proxy,
                            "same_direction": candidate.same_direction,
                            "latest_prior_marker_node_count": candidate.latest_prior_marker_node_count,
                        }
                        for candidate in candidates
                    ],
                    "source_occurrence_timestamp_certified": False,
                    "strategy_semantics_certified": False,
                }
            )

        probe_records.append(
            {
                "probe_id": spec.probe_id,
                "episode_id": spec.episode_id,
                "source_role": spec.source_role,
                "primitive_family": spec.primitive_family,
                "level": str(spec.level),
                "window_start_utc": _z(spec.window_start),
                "window_end_utc": _z(spec.window_end),
                "level_touch_bar_count": len(touches),
                "touch_bars_with_strong_fu_marker": strong_touch_count,
                "touch_bars_with_attempted_fu_marker": attempted_touch_count,
                "touch_bars_with_dual_marker_output": dual_marker_touch_count,
                "touch_bars_with_beta_hcs": beta_hcs_touch_count,
                "touch_bars_with_source_marker_proxy_hcs": source_proxy_touch_count,
                "source_marker_proxy_candidate_counts_by_form": dict(sorted(source_forms.items())),
                "touch_observations": observations,
                "source_occurrence_timestamp_certified": False,
                "strategy_semantics_certified": False,
            }
        )

    return {
        "schema_version": "march_indicator_source_level_probe_v1",
        "status": STATUS,
        "snapshot_id": verified.snapshot.snapshot_id,
        "normalized_sha256": verified.normalized_sha256,
        "broker_name": verified.snapshot.source_name,
        "broker_symbol": verified.snapshot.source_symbol,
        "timeframe": "M1",
        "probe_count": len(probe_records),
        "probes": probe_records,
        "coverage_boundary": {
            "strong_attempted_source": "supplied Casino_v7 helper shadow plus supplied current-candle doji filter",
            "beta_hcs_source": "supplied BETA broad FU/SN tracked-box HCS state machine",
            "source_hcs_marker_proxy": "latest prior supplied Casino Strong/ATT marker directional wick + exact OHLC intersection",
            "fu_negation_nodes_integrated_into_source_proxy": False,
            "same_direction_required_by_source_proxy": False,
            "near_enough_retest_rule_integrated": False,
        },
        "reference_feed_required_for_feed_sensitive_geometry": "FOREXCOM:XAUUSD",
        "reference_feed_alignment_complete": False,
        "source_occurrence_timestamps_certified": False,
        "strategy_semantics_certified": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }


def _parse_utc(text: str) -> datetime:
    value = text.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("probe timestamp must be timezone-aware")
    return parsed.astimezone(UTC)


def _z(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _print_summary(report: dict[str, Any]) -> None:
    print("\n========== MARCH M1 SOURCE-LEVEL INDICATOR PROBE ==========")
    for key in ("status", "snapshot_id", "broker_name", "broker_symbol", "timeframe"):
        print(f"{key}: {report.get(key)}")
    print(f"reference_feed_alignment_complete: {report.get('reference_feed_alignment_complete')}")
    print(f"strategy_semantics_certified: {report.get('strategy_semantics_certified')}")

    for probe in report.get("probes", []):
        print("\n------------------------------------------------------------")
        print(f"probe: {probe['probe_id']} | {probe['source_role']} | level={probe['level']}")
        print(
            "touches="
            f"{probe['level_touch_bar_count']} | strong={probe['touch_bars_with_strong_fu_marker']} "
            f"| attempted={probe['touch_bars_with_attempted_fu_marker']} "
            f"| dual={probe['touch_bars_with_dual_marker_output']} "
            f"| beta_hcs={probe['touch_bars_with_beta_hcs']} "
            f"| source_proxy_hcs={probe['touch_bars_with_source_marker_proxy_hcs']}"
        )
        print(f"source_proxy_forms: {probe['source_marker_proxy_candidate_counts_by_form']}")
        for obs in probe.get("touch_observations", []):
            markers = ", ".join(
                f"{item['kind']}:{item['direction']}:{item['visual_cue']}"
                for item in obs["marker_events"]
            ) or "none"
            beta = ", ".join(
                f"{item['direction']}:{item['marker_text']}"
                for item in obs["beta_hcs_events"]
            ) or "none"
            proxy = ", ".join(
                f"{item['form']}:{item['first_direction']}->{item['second_direction']}@{item['first_bar_time_utc']}"
                for item in obs["source_marker_proxy_candidates"]
            ) or "none"
            print(
                f"{obs['bar_open_utc']} | O={obs['open']} H={obs['high']} L={obs['low']} C={obs['close']} "
                f"| markers={markers} | beta_hcs={beta} | source_proxy={proxy}"
            )
    print("============================================================\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare governed March source levels with supplied Casino Strong/ATT and BETA/source-proxy HCS output on M1."
    )
    parser.add_argument("ingestion_manifest")
    parser.add_argument("--fixture", default=None)
    parser.add_argument("--json", action="store_true", help="print full JSON instead of concise summary")
    args = parser.parse_args()

    report = build_march_indicator_source_level_probe(
        args.ingestion_manifest,
        fixture_path=args.fixture,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_summary(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
