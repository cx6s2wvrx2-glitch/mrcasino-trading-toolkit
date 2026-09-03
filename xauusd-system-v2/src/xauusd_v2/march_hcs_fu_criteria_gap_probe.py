from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .agents.data_agent import MarketBar
from .data_snapshot import load_xauusd_csv_snapshot_bytes
from .fu_completion import FUCompletionClass, classify_fu_completion
from .fu_criteria import FUCriteriaState, evaluate_fu_criteria
from .fu_observables import extract_fu_observables
from .march_hcs_second_node_probe import (
    BasicFUProxy,
    _basic_proxy_series,
    _intersects,
    _level_touched,
    _previous_contiguous,
)
from .march_semantic_probe import MarchSemanticProbeError, MarchSemanticProbeSpec, load_march_semantic_probe_specs
from .mt5_snapshot_load import load_verified_persisted_mt5_snapshot


class MarchHCSFUCriteriaGapProbeError(ValueError):
    pass


def _canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_immutable(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise MarchHCSFUCriteriaGapProbeError(f"refusing to overwrite differing immutable artifact: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _price(value: float) -> str:
    return str(value)


def _conditional_node_family(classification: FUCompletionClass) -> str:
    if classification in {
        FUCompletionClass.ATTEMPTED_FU_FORM_1,
        FUCompletionClass.ATTEMPTED_FU_FORM_2,
    }:
        return "attempted_fu"
    if classification is FUCompletionClass.COMPLETE_FU:
        return "complete_fu_not_equated_to_strong_fu"
    return "none"


def _observe_fu_criteria_gap(
    *,
    current: MarketBar,
    previous: MarketBar,
    latest_prior: BasicFUProxy | None,
) -> dict[str, Any]:
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

    observed_criteria = evaluate_fu_criteria(
        liquidity_taken=None,
        opposite_direction_move=None,
        same_candle=None,
    )
    observed_completion = classify_fu_completion(
        new_high_or_low=new_high_or_low,
        fu_criteria_met=None,
        close=current.close,
        previous_open=previous.open,
        previous_close=previous.close,
    )
    conditional_completion = classify_fu_completion(
        new_high_or_low=new_high_or_low,
        fu_criteria_met=True,
        close=current.close,
        previous_open=previous.open,
        previous_close=previous.close,
    )

    exact_retest = False
    if latest_prior is not None:
        exact_retest = _intersects(
            first_low=latest_prior.wick_low,
            first_high=latest_prior.wick_high,
            second_low=current.low,
            second_high=current.high,
        )

    if (
        exact_retest
        and observed_completion.classification is FUCompletionClass.NOT_CERTIFIED
        and conditional_completion.classification is FUCompletionClass.ATTEMPTED_FU_FORM_2
    ):
        diagnostic = "EXACT_RETEST_CONDITIONAL_ATTEMPTED_FU_FORM_2_IF_FU_CRITERIA_MET"
    elif (
        exact_retest
        and observed_completion.classification is FUCompletionClass.ATTEMPTED_FU_FORM_1
    ):
        diagnostic = "EXACT_RETEST_REFLECTION_ATTEMPTED_FU_FORM_1_LOWER_BOUND"
    elif (
        exact_retest
        and observed_completion.classification is FUCompletionClass.NOT_CERTIFIED
        and conditional_completion.classification is FUCompletionClass.COMPLETE_FU
    ):
        diagnostic = "EXACT_RETEST_CONDITIONAL_COMPLETE_FU_IF_FU_CRITERIA_MET"
    elif exact_retest:
        diagnostic = "EXACT_RETEST_FU_COMPLETION_REMAINS_OUTSIDE_CURRENT_CONDITIONAL_CLASSES"
    else:
        diagnostic = "NO_EXACT_LATEST_BASIC_FU_PROXY_WICK_RETEST_ON_THIS_TOUCH"

    return {
        "bar_open": _iso(current.timestamp),
        "open": _price(current.open),
        "high": _price(current.high),
        "low": _price(current.low),
        "close": _price(current.close),
        "previous_bar": {
            "bar_open": _iso(previous.timestamp),
            "open": _price(previous.open),
            "high": _price(previous.high),
            "low": _price(previous.low),
            "close": _price(previous.close),
        },
        "latest_prior_basic_fu_proxy": None
        if latest_prior is None
        else {
            "bar_open": _iso(latest_prior.bar_open),
            "direction": latest_prior.direction,
            "wick_low": _price(latest_prior.wick_low),
            "wick_high": _price(latest_prior.wick_high),
        },
        "exact_latest_basic_fu_proxy_wick_retest": exact_retest,
        "raw_fu_observables": {
            "direction": observables.direction.value,
            "swept_previous_high": observables.swept_previous_high,
            "swept_previous_low": observables.swept_previous_low,
            "swept_both_sides": observables.swept_both_sides,
            "new_high_or_low_relative_to_previous_bar": new_high_or_low,
            "close_within_previous_body": observables.close_within_previous_body,
            "close_above_previous_body": observables.close_above_previous_body,
            "close_below_previous_body": observables.close_below_previous_body,
        },
        "observed_fu_criteria": {
            "state": observed_criteria.state.value,
            "liquidity_taken": observed_criteria.liquidity_taken,
            "opposite_direction_move": observed_criteria.opposite_direction_move,
            "same_candle": observed_criteria.same_candle,
            "reason": observed_criteria.reason,
            "parent_m1_ohlc_does_not_supply_required_semantic_sequence": True,
        },
        "observed_reflection_completion": {
            "classification": observed_completion.classification.value,
            "reason": observed_completion.reason,
        },
        "conditional_if_fu_criteria_met": {
            "classification": conditional_completion.classification.value,
            "node_family": _conditional_node_family(conditional_completion.classification),
            "reason": conditional_completion.reason,
            "counterfactual_only": True,
            "fu_criteria_are_not_asserted_met": True,
        },
        "diagnostic": diagnostic,
        "fu_criteria_certified": False,
        "attempted_fu_node_certified": False,
        "strong_fu_node_certified": False,
        "fu_negation_node_certified": False,
        "certified_hcs": False,
    }


def _probe_hcs_spec(
    bars: tuple[MarketBar, ...],
    spec: MarchSemanticProbeSpec,
) -> dict[str, Any]:
    if spec.primitive_family != "HCS":
        raise MarchHCSFUCriteriaGapProbeError("FU-criteria-gap diagnostic accepts HCS probes only")

    selected = tuple(
        bar for bar in bars if spec.window_start <= bar.timestamp < spec.window_end and bar.is_closed
    )
    if len(selected) < 2:
        raise MarchHCSFUCriteriaGapProbeError(f"{spec.probe_id}: fewer than two closed bars in probe window")

    proxies = _basic_proxy_series(selected, timeframe_seconds=spec.timeframe_seconds)
    observations: list[dict[str, Any]] = []

    for index, bar in enumerate(selected):
        if not _level_touched(bar, spec.level):
            continue
        previous = _previous_contiguous(selected, index, timeframe_seconds=spec.timeframe_seconds)
        if previous is None:
            observations.append(
                {
                    "bar_open": _iso(bar.timestamp),
                    "diagnostic": "PREVIOUS_BAR_UNAVAILABLE_OR_NONCONTIGUOUS",
                    "fu_criteria_certified": False,
                    "certified_hcs": False,
                }
            )
            continue
        prior = [item for item in proxies if item.bar_open < bar.timestamp]
        latest_prior = prior[-1] if prior else None
        observations.append(
            _observe_fu_criteria_gap(
                current=bar,
                previous=previous,
                latest_prior=latest_prior,
            )
        )

    exact = [item for item in observations if item.get("exact_latest_basic_fu_proxy_wick_retest") is True]
    conditional_att2 = [
        item
        for item in exact
        if item.get("conditional_if_fu_criteria_met", {}).get("classification")
        == FUCompletionClass.ATTEMPTED_FU_FORM_2.value
        and item.get("observed_fu_criteria", {}).get("state") == FUCriteriaState.NOT_CERTIFIED.value
    ]
    conditional_complete = [
        item
        for item in exact
        if item.get("conditional_if_fu_criteria_met", {}).get("classification")
        == FUCompletionClass.COMPLETE_FU.value
        and item.get("observed_fu_criteria", {}).get("state") == FUCriteriaState.NOT_CERTIFIED.value
    ]
    att1_lower_bound = [
        item
        for item in exact
        if item.get("observed_reflection_completion", {}).get("classification")
        == FUCompletionClass.ATTEMPTED_FU_FORM_1.value
    ]

    if conditional_att2:
        diagnostic = "EXACT_RETEST_HAS_CONDITIONAL_ATTEMPTED_FU_FORM_2_BLOCKED_BY_FU_CRITERIA"
    elif conditional_complete:
        diagnostic = "EXACT_RETEST_HAS_CONDITIONAL_COMPLETE_FU_BLOCKED_BY_FU_CRITERIA"
    elif att1_lower_bound:
        diagnostic = "EXACT_RETEST_HAS_REFLECTION_ATTEMPTED_FU_FORM_1_LOWER_BOUND"
    elif exact:
        diagnostic = "EXACT_RETEST_PRESENT_WITHOUT_CURRENT_COMPLETION_LOCALIZATION"
    else:
        diagnostic = "NO_EXACT_LATEST_BASIC_FU_PROXY_WICK_RETEST_ON_SOURCE_LEVEL_TOUCH"

    return {
        "probe_id": spec.probe_id,
        "source_role": spec.source_role,
        "level": str(spec.level),
        "level_touch_bar_count": len(observations),
        "exact_latest_basic_fu_proxy_wick_retest_bar_count": len(exact),
        "conditional_attempted_fu_form_2_on_exact_retest_bar_count": len(conditional_att2),
        "conditional_complete_fu_on_exact_retest_bar_count": len(conditional_complete),
        "reflection_attempted_fu_form_1_lower_bound_on_exact_retest_bar_count": len(att1_lower_bound),
        "diagnostic": diagnostic,
        "touch_observations": observations,
        "source_occurrence_timestamp_certified": False,
        "fu_criteria_certified": False,
        "semantic_stage_certification": False,
        "strategy_truth_changed": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }


def build_march_hcs_fu_criteria_gap_report(
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
        raise MarchHCSFUCriteriaGapProbeError(str(exc)) from exc
    if not specs:
        raise MarchHCSFUCriteriaGapProbeError("no governed HCS probes are available")

    verified = load_verified_persisted_mt5_snapshot(ingestion_manifest)
    if verified.snapshot.timeframe_seconds != 60:
        raise MarchHCSFUCriteriaGapProbeError("March HCS FU-criteria-gap diagnostic requires verified M1 data")

    bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
        verified.canonical_snapshot_path.read_bytes(),
        source_name=verified.snapshot.source_name,
        source_symbol=verified.snapshot.source_symbol,
        timeframe_seconds=verified.snapshot.timeframe_seconds,
        evaluation_time=verified.snapshot.coverage_end,
        source_file_name=verified.snapshot.source_file_name,
    )
    if reproduced != verified.snapshot:
        raise MarchHCSFUCriteriaGapProbeError("verified snapshot changed when canonical bytes were reproduced")

    records = [_probe_hcs_spec(bars, spec) for spec in specs]
    payload = {
        "schema_version": "march_hcs_fu_criteria_gap_probe_v1",
        "status": "MARCH_HCS_FU_CRITERIA_GAP_DIAGNOSTIC_COMPLETE_NOT_CERTIFIED",
        "snapshot_id": verified.snapshot.snapshot_id,
        "normalized_sha256": verified.normalized_sha256,
        "broker_name": verified.snapshot.source_name,
        "broker_symbol": verified.snapshot.source_symbol,
        "hcs_probe_count": len(records),
        "probes": records,
        "coverage_boundary": {
            "purpose": "localize whether an exact HCS-level retest would map to a Reflection completion class only if upstream FU criteria were later certified",
            "fu_criteria_source_contract": "liquidity taken plus opposite-direction move in the same candle",
            "previous_candle_sweep_is_not_universal_liquidity_truth": True,
            "parent_m1_ohlc_does_not_certify_intrabar_order_or_marked_liquidity_take": True,
            "conditional_fu_criteria_met_branch_is_counterfactual_only": True,
            "complete_fu_is_not_equated_to_strong_fu": True,
            "attempted_fu_form_2_is_not_certified_without_fu_criteria": True,
            "att_fu_wick_geometry_is_not_invented": True,
            "source_occurrence_timestamp_is_not_inferred": True,
        },
        "reference_feed_required_for_feed_sensitive_geometry": "FOREXCOM:XAUUSD",
        "reference_feed_alignment_complete": False,
        "source_occurrence_timestamps_certified": False,
        "fu_criteria_certified": False,
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "strategy_truth_changed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }
    raw = _canonical_json_bytes(payload)
    report_sha = hashlib.sha256(raw).hexdigest()
    report_root = verified.store_root / "research-bundles" / "march-2023-hcs-fu-criteria-gap" / report_sha
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
        "fu_criteria_certified": False,
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "strategy_truth_changed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }
