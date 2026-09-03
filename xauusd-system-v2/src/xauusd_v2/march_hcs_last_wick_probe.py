from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from .agents.data_agent import MarketBar
from .data_snapshot import load_xauusd_csv_snapshot_bytes
from .fu_basic_candidate import BasicFUCandidateState, classify_basic_fu_candidate
from .march_semantic_probe import MarchSemanticProbeError, MarchSemanticProbeSpec, load_march_semantic_probe_specs
from .mt5_snapshot_load import load_verified_persisted_mt5_snapshot
from .primitive_replay_scan import PrimitiveReplayScanResult, scan_primitive_replay_window


class MarchHCSLastWickProbeError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class BasicFUProxy:
    bar_open: datetime
    direction: str
    wick_low: float
    wick_high: float


def _canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_immutable(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise MarchHCSLastWickProbeError(f"refusing to overwrite differing immutable artifact: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _price(value: float) -> str:
    return str(value)


def _decimal_price(value: float) -> Decimal:
    return Decimal(str(value))


def _level_touched(bar: MarketBar, level: Decimal) -> bool:
    return _decimal_price(bar.low) <= level <= _decimal_price(bar.high)


def _intersects(*, first_low: float, first_high: float, second_low: float, second_high: float) -> bool:
    return second_high >= first_low and second_low <= first_high


def _basic_proxy_series(
    bars: tuple[MarketBar, ...],
    *,
    timeframe_seconds: int,
) -> tuple[tuple[BasicFUProxy, ...], dict[datetime, dict[str, Any]]]:
    proxies: list[BasicFUProxy] = []
    observations: dict[datetime, dict[str, Any]] = {}
    step = timedelta(seconds=timeframe_seconds)

    for index, current in enumerate(bars):
        if index == 0:
            observations[current.timestamp] = {
                "state": "UNAVAILABLE_WINDOW_BOUNDARY",
                "direction": None,
                "reason": "previous closed bar is outside the explicit probe window",
            }
            continue
        previous = bars[index - 1]
        if current.timestamp - previous.timestamp != step:
            observations[current.timestamp] = {
                "state": "UNAVAILABLE_DATA_GAP",
                "direction": None,
                "reason": "previous closed bar is not contiguous",
            }
            continue
        result = classify_basic_fu_candidate(
            open=current.open,
            high=current.high,
            low=current.low,
            close=current.close,
            previous_high=previous.high,
            previous_low=previous.low,
        )
        direction = None
        if result.state is BasicFUCandidateState.BULLISH:
            direction = "bullish"
        elif result.state is BasicFUCandidateState.BEARISH:
            direction = "bearish"
        observations[current.timestamp] = {
            "state": result.state.value,
            "direction": direction,
            "reason": result.reason,
        }
        if direction is None:
            continue
        if direction == "bullish":
            wick_low = current.low
            wick_high = min(current.open, current.close)
        else:
            wick_low = max(current.open, current.close)
            wick_high = current.high
        if wick_high <= wick_low:
            continue
        proxies.append(
            BasicFUProxy(
                bar_open=current.timestamp,
                direction=direction,
                wick_low=wick_low,
                wick_high=wick_high,
            )
        )
    return tuple(proxies), observations


def _broad_hcs_by_time(primitive: PrimitiveReplayScanResult) -> dict[datetime, list[Any]]:
    result: dict[datetime, list[Any]] = {}
    for item in primitive.wick_interactions:
        if item.source_style_hcs_candidate:
            result.setdefault(item.interaction_bar_open, []).append(item)
    return result


def _diagnose_touch(
    *,
    bar: MarketBar,
    latest_prior: BasicFUProxy | None,
    current_basic: dict[str, Any],
    broad_hcs_items: list[Any],
) -> dict[str, Any]:
    current_basic_present = current_basic.get("direction") in {"bullish", "bearish"}
    exact_last_wick_retest = False
    if latest_prior is not None:
        exact_last_wick_retest = _intersects(
            first_low=latest_prior.wick_low,
            first_high=latest_prior.wick_high,
            second_low=bar.low,
            second_high=bar.high,
        )
    strict_proxy = latest_prior is not None and exact_last_wick_retest and current_basic_present
    broad_proxy = bool(broad_hcs_items)

    if latest_prior is None:
        diagnostic = "NO_PRIOR_BASIC_FU_PROXY"
    elif strict_proxy:
        diagnostic = "STRICT_LAST_WICK_BASIC_HCS_PROXY_PRESENT"
    elif exact_last_wick_retest and current_basic.get("state") == BasicFUCandidateState.AMBIGUOUS.value:
        diagnostic = "LAST_WICK_RETEST_PRESENT_SECOND_BASIC_FU_AMBIGUOUS"
    elif exact_last_wick_retest:
        diagnostic = "LAST_WICK_RETEST_PRESENT_SECOND_BASIC_FU_PROXY_ABSENT"
    elif current_basic_present:
        diagnostic = "SECOND_BASIC_FU_PROXY_PRESENT_NO_EXACT_LAST_WICK_RETEST"
    else:
        diagnostic = "NO_EXACT_LAST_WICK_RETEST_AND_NO_SECOND_BASIC_FU_PROXY"

    broad_first_bars = sorted(
        {
            item.first_bar_open.astimezone(UTC).isoformat().replace("+00:00", "Z")
            for item in broad_hcs_items
        }
    )
    broad_forms = sorted(
        {
            item.hcs_candidate_form.value
            for item in broad_hcs_items
            if item.hcs_candidate_form is not None
        }
    )
    return {
        "bar_open": bar.timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "open": _price(bar.open),
        "high": _price(bar.high),
        "low": _price(bar.low),
        "close": _price(bar.close),
        "basic_fu_state": current_basic.get("state"),
        "basic_fu_direction": current_basic.get("direction"),
        "latest_prior_basic_fu_proxy": None
        if latest_prior is None
        else {
            "bar_open": latest_prior.bar_open.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "direction": latest_prior.direction,
            "wick_low": _price(latest_prior.wick_low),
            "wick_high": _price(latest_prior.wick_high),
        },
        "exact_last_basic_fu_proxy_wick_retest": exact_last_wick_retest,
        "strict_last_wick_basic_hcs_proxy": strict_proxy,
        "broad_any_prior_basic_hcs_proxy": broad_proxy,
        "broad_any_prior_first_bar_opens": broad_first_bars,
        "broad_any_prior_forms": broad_forms,
        "broad_only_not_last_wick": broad_proxy and not strict_proxy,
        "diagnostic": diagnostic,
        "certified_hcs": False,
    }


def _probe_hcs_spec(
    bars: tuple[MarketBar, ...],
    primitive: PrimitiveReplayScanResult,
    spec: MarchSemanticProbeSpec,
) -> dict[str, Any]:
    if spec.primitive_family != "HCS":
        raise MarchHCSLastWickProbeError("strict last-wick diagnostic accepts HCS probes only")
    selected = tuple(
        bar for bar in bars if spec.window_start <= bar.timestamp < spec.window_end and bar.is_closed
    )
    if len(selected) < 2:
        raise MarchHCSLastWickProbeError(f"{spec.probe_id}: fewer than two closed bars in probe window")

    proxies, basic_by_time = _basic_proxy_series(selected, timeframe_seconds=spec.timeframe_seconds)
    broad_by_time = _broad_hcs_by_time(primitive)
    touches: list[dict[str, Any]] = []

    for bar in selected:
        if not _level_touched(bar, spec.level):
            continue
        prior = [item for item in proxies if item.bar_open < bar.timestamp]
        latest_prior = prior[-1] if prior else None
        touches.append(
            _diagnose_touch(
                bar=bar,
                latest_prior=latest_prior,
                current_basic=basic_by_time[bar.timestamp],
                broad_hcs_items=broad_by_time.get(bar.timestamp, []),
            )
        )

    strict_count = sum(1 for item in touches if item["strict_last_wick_basic_hcs_proxy"])
    broad_count = sum(1 for item in touches if item["broad_any_prior_basic_hcs_proxy"])
    broad_only_count = sum(1 for item in touches if item["broad_only_not_last_wick"])
    last_wick_retest_count = sum(1 for item in touches if item["exact_last_basic_fu_proxy_wick_retest"])
    second_basic_count = sum(1 for item in touches if item["basic_fu_direction"] is not None)
    ambiguous_second_count = sum(
        1 for item in touches if item["basic_fu_state"] == BasicFUCandidateState.AMBIGUOUS.value
    )

    if strict_count:
        diagnostic = "STRICT_LAST_WICK_BASIC_HCS_PROXY_PRESENT_ON_SOURCE_LEVEL_TOUCH"
    elif broad_count:
        diagnostic = "BROAD_ANY_PRIOR_PROXY_PRESENT_BUT_STRICT_LAST_WICK_PROXY_ABSENT"
    elif last_wick_retest_count and not second_basic_count:
        diagnostic = "LAST_WICK_RETEST_OBSERVED_BUT_SECOND_BASIC_FU_PROXY_ABSENT"
    elif second_basic_count and not last_wick_retest_count:
        diagnostic = "SECOND_BASIC_FU_PROXY_OBSERVED_BUT_LAST_WICK_RETEST_ABSENT"
    elif ambiguous_second_count:
        diagnostic = "AMBIGUOUS_SECOND_BASIC_FU_PROXY_ON_SOURCE_LEVEL_TOUCH"
    else:
        diagnostic = "NARROW_LAST_WICK_AND_SECOND_BASIC_FU_PROXY_NOT_COLOCATED"

    return {
        "probe_id": spec.probe_id,
        "source_role": spec.source_role,
        "level": str(spec.level),
        "level_touch_bar_count": len(touches),
        "strict_last_wick_basic_hcs_proxy_bar_count": strict_count,
        "broad_any_prior_basic_hcs_proxy_bar_count": broad_count,
        "broad_only_not_last_wick_bar_count": broad_only_count,
        "exact_last_wick_retest_bar_count": last_wick_retest_count,
        "second_basic_fu_proxy_bar_count": second_basic_count,
        "ambiguous_second_basic_fu_bar_count": ambiguous_second_count,
        "diagnostic": diagnostic,
        "touch_observations": touches,
        "source_occurrence_timestamp_certified": False,
        "certified_hcs_count": 0,
        "semantic_stage_certification": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }


def build_march_hcs_last_wick_report(
    ingestion_manifest: str | Path,
    *,
    probe_fixture: str | Path,
) -> dict[str, Any]:
    try:
        specs = tuple(item for item in load_march_semantic_probe_specs(probe_fixture) if item.primitive_family == "HCS")
    except MarchSemanticProbeError as exc:
        raise MarchHCSLastWickProbeError(str(exc)) from exc
    if not specs:
        raise MarchHCSLastWickProbeError("no governed HCS probes are available")

    verified = load_verified_persisted_mt5_snapshot(ingestion_manifest)
    if verified.snapshot.timeframe_seconds != 60:
        raise MarchHCSLastWickProbeError("March HCS last-wick diagnostic requires verified M1 data")
    bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
        verified.canonical_snapshot_path.read_bytes(),
        source_name=verified.snapshot.source_name,
        source_symbol=verified.snapshot.source_symbol,
        timeframe_seconds=verified.snapshot.timeframe_seconds,
        evaluation_time=verified.snapshot.coverage_end,
        source_file_name=verified.snapshot.source_file_name,
    )
    if reproduced != verified.snapshot:
        raise MarchHCSLastWickProbeError("verified snapshot changed when canonical bytes were reproduced")

    scans: dict[tuple[datetime, datetime], PrimitiveReplayScanResult] = {}
    records: list[dict[str, Any]] = []
    for spec in specs:
        key = (spec.window_start, spec.window_end)
        if key not in scans:
            scans[key] = scan_primitive_replay_window(
                bars=bars,
                timeframe_seconds=60,
                scan_start=spec.window_start,
                scan_end=spec.window_end,
                max_window_bars=20_000,
            )
        records.append(_probe_hcs_spec(bars, scans[key], spec))

    payload = {
        "schema_version": "march_hcs_last_wick_probe_v1",
        "status": "MARCH_HCS_LAST_WICK_DIAGNOSTIC_COMPLETE_NOT_CERTIFIED",
        "snapshot_id": verified.snapshot.snapshot_id,
        "normalized_sha256": verified.normalized_sha256,
        "broker_name": verified.snapshot.source_name,
        "broker_symbol": verified.snapshot.source_symbol,
        "hcs_probe_count": len(records),
        "probes": records,
        "current_primitive_overbreadth_observed": any(
            item["broad_only_not_last_wick_bar_count"] > 0 for item in records
        ),
        "coverage_boundary": {
            "source_hcs_retest_requirement": "retest of the last FU wick",
            "strict_diagnostic_retest_proxy": "exact range intersection with the latest prior basic-FU-candidate wick only",
            "strict_diagnostic_second_node_proxy": "basic FU candidate only",
            "source_hcs_node_types_not_operationalized_here": [
                "strong_fu_certification",
                "attempted_fu",
                "fu_negation",
                "source_confirmed_near_enough_retest",
            ],
            "note": (
                "This diagnostic deliberately narrows the existing any-prior-wick research proxy to the latest prior raw "
                "basic-FU candidate. It does not certify that proxy as the source's actual FU and it does not invent missing "
                "Attempted-FU, FU-negation, Strong-FU or near-enough raw rules."
            ),
        },
        "reference_feed_required_for_feed_sensitive_geometry": "FOREXCOM:XAUUSD",
        "reference_feed_alignment_complete": False,
        "source_occurrence_timestamps_certified": False,
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "strategy_truth_changed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }
    raw = _canonical_json_bytes(payload)
    report_sha = hashlib.sha256(raw).hexdigest()
    report_root = verified.store_root / "research-bundles" / "march-2023-hcs-last-wick" / report_sha
    _write_immutable(report_root / "report.json", raw)

    return {
        "status": payload["status"],
        "report_sha256": report_sha,
        "report_root": str(report_root),
        "snapshot_id": payload["snapshot_id"],
        "normalized_sha256": payload["normalized_sha256"],
        "hcs_probe_count": len(records),
        "current_primitive_overbreadth_observed": payload["current_primitive_overbreadth_observed"],
        "probes": records,
        "reference_feed_alignment_complete": False,
        "source_occurrence_timestamps_certified": False,
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }