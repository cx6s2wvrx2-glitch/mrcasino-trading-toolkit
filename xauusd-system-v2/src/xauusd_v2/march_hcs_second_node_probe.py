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
from .fu_completion import FUCompletionClass, classify_fu_completion
from .fu_observables import extract_fu_observables
from .helper_fu_shadow import HelperFUClass, beta_fu_core_shadow, casino_v7_core_shadow
from .march_semantic_probe import MarchSemanticProbeError, MarchSemanticProbeSpec, load_march_semantic_probe_specs
from .mt5_snapshot_load import load_verified_persisted_mt5_snapshot


class MarchHCSSecondNodeProbeError(ValueError):
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
            raise MarchHCSSecondNodeProbeError(f"refusing to overwrite differing immutable artifact: {path}")
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
) -> tuple[BasicFUProxy, ...]:
    proxies: list[BasicFUProxy] = []
    step = timedelta(seconds=timeframe_seconds)

    for index, current in enumerate(bars):
        if index == 0:
            continue
        previous = bars[index - 1]
        if current.timestamp - previous.timestamp != step:
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
    return tuple(proxies)


def _previous_contiguous(
    bars: tuple[MarketBar, ...],
    index: int,
    *,
    timeframe_seconds: int,
) -> MarketBar | None:
    if index <= 0:
        return None
    previous = bars[index - 1]
    current = bars[index]
    if current.timestamp - previous.timestamp != timedelta(seconds=timeframe_seconds):
        return None
    return previous


def _helper_class_present(value: HelperFUClass, target: HelperFUClass) -> bool:
    return value is target


def _observe_second_node(
    *,
    current: MarketBar,
    previous: MarketBar,
    latest_prior: BasicFUProxy | None,
    timeframe_seconds: int,
) -> dict[str, Any]:
    basic = classify_basic_fu_candidate(
        open=current.open,
        high=current.high,
        low=current.low,
        close=current.close,
        previous_high=previous.high,
        previous_low=previous.low,
    )
    observables = extract_fu_observables(
        open=current.open,
        high=current.high,
        low=current.low,
        close=current.close,
        previous_open=previous.open,
        previous_high=previous.high,
        previous_low=previous.low,
        previous_close=previous.close,
    )
    new_high_or_low = observables.swept_previous_high or observables.swept_previous_low
    reflection = classify_fu_completion(
        new_high_or_low=new_high_or_low,
        fu_criteria_met=None,
        close=current.close,
        previous_open=previous.open,
        previous_close=previous.close,
    )
    v7 = casino_v7_core_shadow(
        open=current.open,
        high=current.high,
        low=current.low,
        close=current.close,
        previous_open=previous.open,
        previous_high=previous.high,
        previous_low=previous.low,
        previous_close=previous.close,
    )
    beta = beta_fu_core_shadow(
        open=current.open,
        high=current.high,
        low=current.low,
        close=current.close,
        previous_high=previous.high,
        previous_low=previous.low,
    )

    exact_last_wick_retest = False
    bars_since_latest_prior: int | None = None
    if latest_prior is not None:
        exact_last_wick_retest = _intersects(
            first_low=latest_prior.wick_low,
            first_high=latest_prior.wick_high,
            second_low=current.low,
            second_high=current.high,
        )
        delta_seconds = int((current.timestamp - latest_prior.bar_open).total_seconds())
        if delta_seconds >= 0 and delta_seconds % timeframe_seconds == 0:
            bars_since_latest_prior = delta_seconds // timeframe_seconds

    v7_att = (
        _helper_class_present(v7.bullish, HelperFUClass.ATT)
        or _helper_class_present(v7.bearish, HelperFUClass.ATT)
    )
    v7_fu = (
        _helper_class_present(v7.bullish, HelperFUClass.FU)
        or _helper_class_present(v7.bearish, HelperFUClass.FU)
    )
    beta_candidate = beta.bullish_fu_candidate or beta.bearish_fu_candidate
    basic_present = basic.state in {BasicFUCandidateState.BULLISH, BasicFUCandidateState.BEARISH}
    reflection_att1 = reflection.classification is FUCompletionClass.ATTEMPTED_FU_FORM_1

    if exact_last_wick_retest and not basic_present and reflection_att1:
        diagnostic = "LAST_WICK_RETEST_WITH_REFLECTION_ATTEMPTED_FU_FORM_1"
    elif exact_last_wick_retest and not basic_present and v7_att:
        diagnostic = "LAST_WICK_RETEST_WITH_V7_ATT_IMPLEMENTATION_EVIDENCE"
    elif exact_last_wick_retest and not basic_present and beta_candidate:
        diagnostic = "LAST_WICK_RETEST_WITH_BETA_FU_CANDIDATE_IMPLEMENTATION_EVIDENCE"
    elif exact_last_wick_retest and not basic_present:
        diagnostic = "LAST_WICK_RETEST_SECOND_NODE_REMAINS_UNRESOLVED"
    elif exact_last_wick_retest and basic_present:
        diagnostic = "LAST_WICK_RETEST_WITH_BASIC_FU_PROXY"
    else:
        diagnostic = "NO_EXACT_LAST_WICK_RETEST_ON_THIS_LEVEL_TOUCH"

    return {
        "bar_open": current.timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "open": _price(current.open),
        "high": _price(current.high),
        "low": _price(current.low),
        "close": _price(current.close),
        "previous_bar": {
            "bar_open": previous.timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "open": _price(previous.open),
            "high": _price(previous.high),
            "low": _price(previous.low),
            "close": _price(previous.close),
        },
        "latest_prior_basic_fu_proxy": None
        if latest_prior is None
        else {
            "bar_open": latest_prior.bar_open.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "direction": latest_prior.direction,
            "wick_low": _price(latest_prior.wick_low),
            "wick_high": _price(latest_prior.wick_high),
        },
        "bars_since_latest_prior_basic_fu_proxy": bars_since_latest_prior,
        "exact_last_basic_fu_proxy_wick_retest": exact_last_wick_retest,
        "basic_fu_state": basic.state.value,
        "basic_fu_reason": basic.reason,
        "fu_observables": {
            "direction": observables.direction.value,
            "swept_previous_high": observables.swept_previous_high,
            "swept_previous_low": observables.swept_previous_low,
            "swept_both_sides": observables.swept_both_sides,
            "close_within_previous_body": observables.close_within_previous_body,
            "close_above_previous_body": observables.close_above_previous_body,
            "close_below_previous_body": observables.close_below_previous_body,
            "bullish_reversal_candidate": observables.bullish_reversal_candidate,
            "bearish_reversal_candidate": observables.bearish_reversal_candidate,
        },
        "reflection_completion_lower_bound": {
            "classification": reflection.classification.value,
            "reason": reflection.reason,
            "fu_criteria_supplied": False,
            "certified_complete_fu": False,
        },
        "casino_v7_shadow": {
            "bullish": v7.bullish.value,
            "bearish": v7.bearish.value,
            "bullish_branch": v7.bullish_branch,
            "bearish_branch": v7.bearish_branch,
            "implementation_evidence_only": True,
        },
        "beta_fu_shadow": {
            "bullish_fu_candidate": beta.bullish_fu_candidate,
            "bearish_fu_candidate": beta.bearish_fu_candidate,
            "is_x3": beta.is_x3,
            "self_negation_together": beta.self_negation_together,
            "implementation_evidence_only": True,
        },
        "diagnostic": diagnostic,
        "attempted_fu_node_certified": False,
        "fu_negation_node_certified": False,
        "strong_fu_node_certified": False,
        "certified_hcs": False,
    }


def _probe_hcs_spec(
    bars: tuple[MarketBar, ...],
    spec: MarchSemanticProbeSpec,
) -> dict[str, Any]:
    if spec.primitive_family != "HCS":
        raise MarchHCSSecondNodeProbeError("second-node diagnostic accepts HCS probes only")

    selected = tuple(
        bar for bar in bars if spec.window_start <= bar.timestamp < spec.window_end and bar.is_closed
    )
    if len(selected) < 2:
        raise MarchHCSSecondNodeProbeError(f"{spec.probe_id}: fewer than two closed bars in probe window")

    proxies = _basic_proxy_series(selected, timeframe_seconds=spec.timeframe_seconds)
    observations: list[dict[str, Any]] = []

    for index, bar in enumerate(selected):
        if not _level_touched(bar, spec.level):
            continue
        previous = _previous_contiguous(selected, index, timeframe_seconds=spec.timeframe_seconds)
        if previous is None:
            observations.append(
                {
                    "bar_open": bar.timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z"),
                    "diagnostic": "PREVIOUS_BAR_UNAVAILABLE_OR_NONCONTIGUOUS",
                    "certified_hcs": False,
                }
            )
            continue
        prior = [item for item in proxies if item.bar_open < bar.timestamp]
        latest_prior = prior[-1] if prior else None
        observations.append(
            _observe_second_node(
                current=bar,
                previous=previous,
                latest_prior=latest_prior,
                timeframe_seconds=spec.timeframe_seconds,
            )
        )

    exact_retests = [
        item for item in observations if item.get("exact_last_basic_fu_proxy_wick_retest") is True
    ]
    basic_misses_on_retest = [
        item for item in exact_retests
        if item.get("basic_fu_state") not in {
            BasicFUCandidateState.BULLISH.value,
            BasicFUCandidateState.BEARISH.value,
        }
    ]
    reflection_att1 = [
        item for item in basic_misses_on_retest
        if item.get("reflection_completion_lower_bound", {}).get("classification")
        == FUCompletionClass.ATTEMPTED_FU_FORM_1.value
    ]
    v7_att = [
        item for item in basic_misses_on_retest
        if HelperFUClass.ATT.value
        in {
            item.get("casino_v7_shadow", {}).get("bullish"),
            item.get("casino_v7_shadow", {}).get("bearish"),
        }
    ]
    beta_candidates = [
        item for item in basic_misses_on_retest
        if item.get("beta_fu_shadow", {}).get("bullish_fu_candidate")
        or item.get("beta_fu_shadow", {}).get("bearish_fu_candidate")
    ]

    if reflection_att1:
        diagnostic = "BASIC_FU_GAP_HAS_REFLECTION_ATTEMPTED_FU_FORM_1_EVIDENCE"
    elif v7_att:
        diagnostic = "BASIC_FU_GAP_HAS_V7_ATT_IMPLEMENTATION_EVIDENCE"
    elif beta_candidates:
        diagnostic = "BASIC_FU_GAP_HAS_BETA_FU_IMPLEMENTATION_EVIDENCE"
    elif basic_misses_on_retest:
        diagnostic = "BASIC_FU_GAP_REMAINS_AFTER_SECOND_NODE_OBSERVABILITY"
    elif exact_retests:
        diagnostic = "EXACT_RETESTS_ALREADY_HAVE_BASIC_FU_PROXY"
    else:
        diagnostic = "NO_EXACT_LAST_WICK_RETEST_ON_SOURCE_LEVEL_TOUCH"

    return {
        "probe_id": spec.probe_id,
        "source_role": spec.source_role,
        "level": str(spec.level),
        "level_touch_bar_count": len(observations),
        "exact_last_wick_retest_bar_count": len(exact_retests),
        "basic_fu_miss_on_exact_retest_bar_count": len(basic_misses_on_retest),
        "reflection_attempted_fu_form_1_on_basic_miss_retest_bar_count": len(reflection_att1),
        "v7_att_shadow_on_basic_miss_retest_bar_count": len(v7_att),
        "beta_fu_shadow_on_basic_miss_retest_bar_count": len(beta_candidates),
        "diagnostic": diagnostic,
        "touch_observations": observations,
        "source_occurrence_timestamp_certified": False,
        "semantic_stage_certification": False,
        "strategy_truth_changed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }


def build_march_hcs_second_node_report(
    ingestion_manifest: str | Path,
    *,
    probe_fixture: str | Path,
) -> dict[str, Any]:
    try:
        specs = tuple(
            item
            for item in load_march_semantic_probe_specs(probe_fixture)
            if item.primitive_family == "HCS"
        )
    except MarchSemanticProbeError as exc:
        raise MarchHCSSecondNodeProbeError(str(exc)) from exc
    if not specs:
        raise MarchHCSSecondNodeProbeError("no governed HCS probes are available")

    verified = load_verified_persisted_mt5_snapshot(ingestion_manifest)
    if verified.snapshot.timeframe_seconds != 60:
        raise MarchHCSSecondNodeProbeError("March HCS second-node diagnostic requires verified M1 data")

    bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
        verified.canonical_snapshot_path.read_bytes(),
        source_name=verified.snapshot.source_name,
        source_symbol=verified.snapshot.source_symbol,
        timeframe_seconds=verified.snapshot.timeframe_seconds,
        evaluation_time=verified.snapshot.coverage_end,
        source_file_name=verified.snapshot.source_file_name,
    )
    if reproduced != verified.snapshot:
        raise MarchHCSSecondNodeProbeError("verified snapshot changed when canonical bytes were reproduced")

    records = [_probe_hcs_spec(bars, spec) for spec in specs]

    payload = {
        "schema_version": "march_hcs_second_node_probe_v1",
        "status": "MARCH_HCS_SECOND_NODE_DIAGNOSTIC_COMPLETE_NOT_CERTIFIED",
        "snapshot_id": verified.snapshot.snapshot_id,
        "normalized_sha256": verified.normalized_sha256,
        "broker_name": verified.snapshot.source_name,
        "broker_symbol": verified.snapshot.source_symbol,
        "hcs_probe_count": len(records),
        "probes": records,
        "coverage_boundary": {
            "purpose": (
                "Explain exact-last-wick HCS touches that the narrow basic-FU second-node proxy misses."
            ),
            "reflection_completion_rule": (
                "Attempted FU form 1 is observable when there is no new high/low. "
                "Complete FU and Attempted FU form 2 remain not certified without upstream FU-criteria evidence."
            ),
            "legacy_helper_shadows": (
                "Casino_v7 and BETA 1 + LAOL outputs are implementation evidence only and do not certify source semantics."
            ),
            "fu_negation": (
                "Not operationalized as a certified node here because raw candle direction is not promoted to "
                "certified manipulation direction and complete-FU evidence remains upstream."
            ),
            "source_hcs_node_types": ["strong_fu", "attempted_fu", "fu_negation"],
            "no_numeric_tolerance": True,
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
    report_root = verified.store_root / "research-bundles" / "march-2023-hcs-second-node" / report_sha
    _write_immutable(report_root / "report.json", raw)

    return {
        "status": payload["status"],
        "report_sha256": report_sha,
        "report_root": str(report_root),
        "snapshot_id": payload["snapshot_id"],
        "normalized_sha256": payload["normalized_sha256"],
        "hcs_probe_count": len(records),
        "probes": records,
        "reference_feed_alignment_complete": False,
        "source_occurrence_timestamps_certified": False,
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }
