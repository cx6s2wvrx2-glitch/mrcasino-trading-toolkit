from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

from .data_snapshot import load_xauusd_csv_snapshot_bytes
from .mt5_snapshot_load import VerifiedPersistedMT5Snapshot, load_verified_persisted_mt5_snapshot
from .primitive_replay_scan import scan_primitive_replay_window
from .r143_source_evidence import load_r143_source_evidence_map
from .source_fidelity_replay import evaluate_source_fidelity_fixture, load_source_fidelity_fixture
from .source_primitive_bridge import build_source_primitive_bridge


class MarchReplayBundleError(ValueError):
    pass


_EPISODES = (
    (
        "2023-03-30-buy",
        "SOURCE_FIDELITY_2023_03_30_BUY.json",
        "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
    ),
    (
        "2023-03-31-sell",
        "SOURCE_FIDELITY_2023_03_31_SELL.json",
        "R143_SOURCE_EVIDENCE_2023_03_31_SELL.json",
    ),
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_immutable_json(path: Path, payload: object) -> str:
    raw = _canonical_json_bytes(payload)
    digest = hashlib.sha256(raw).hexdigest()
    if path.exists():
        if path.read_bytes() != raw:
            raise MarchReplayBundleError(f"refusing to overwrite differing immutable artifact: {path}")
        return digest
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return digest


def _source_report(verified: VerifiedPersistedMT5Snapshot, result: Any) -> dict[str, Any]:
    passed = result.all_anchors_matched and result.expansion_probe_matched
    return {
        "schema_version": "source_fidelity_replay_report_v1",
        "status": "SOURCE_FIDELITY_REPLAY_PASS" if passed else "SOURCE_FIDELITY_REPLAY_INCOMPLETE",
        "episode_id": result.episode_id,
        "source_locator": result.source_locator,
        "snapshot_id": verified.snapshot.snapshot_id,
        "normalized_sha256": verified.normalized_sha256,
        "broker_name": verified.snapshot.source_name,
        "broker_symbol": verified.snapshot.source_symbol,
        "timeframe_seconds": result.timeframe_seconds,
        "window_start": result.window_start,
        "window_end": result.window_end,
        "anchor_count": len(result.anchor_matches),
        "matched_anchor_count": sum(1 for item in result.anchor_matches if item.matched),
        "all_anchors_matched": result.all_anchors_matched,
        "anchors": [asdict(item) for item in result.anchor_matches],
        "expansion_probe": asdict(result.expansion_match) if result.expansion_match is not None else None,
        "expansion_probe_matched": result.expansion_probe_matched,
        "expansion_finishes_before_first_anchor": result.expansion_finishes_before_first_anchor,
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "strategy_truth_changed": False,
        "live_execution_authorized": False,
        "reference_feed_alignment_complete": False,
        "reference_feed_required": "FOREXCOM:XAUUSD",
    }


def _primitive_report(verified: VerifiedPersistedMT5Snapshot, result: Any) -> dict[str, Any]:
    return {
        "schema_version": "primitive_replay_scan_report_v1",
        "status": "PRIMITIVE_REPLAY_SCAN_COMPLETE_NOT_CERTIFIED",
        "snapshot_id": verified.snapshot.snapshot_id,
        "normalized_sha256": verified.normalized_sha256,
        "broker_name": verified.snapshot.source_name,
        "broker_symbol": verified.snapshot.source_symbol,
        "timeframe_seconds": result.timeframe_seconds,
        "scan_start": result.scan_start,
        "scan_end": result.scan_end,
        "bar_count": result.bar_count,
        "basic_fu_candidate_count": len(result.fu_candidates),
        "ambiguous_basic_fu_bar_count": result.ambiguous_basic_fu_bars,
        "adjacency_gap_pairs_skipped": result.adjacency_gap_pairs_skipped,
        "wick_interaction_count_total": len(result.wick_interactions),
        "source_style_hcs_candidate_count": result.source_style_hcs_candidates,
        "candidate_only_output": False,
        "fu_candidates": [asdict(item) for item in result.fu_candidates],
        "wick_interactions": [asdict(item) for item in result.wick_interactions],
        "certified_fu_count": 0,
        "certified_hcs_count": 0,
        "blockers_preserved": ["B-01", "B-02", "B-03", "B-05"],
        "strategy_truth_changed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }


def _evidence_summary(path: Path) -> dict[str, Any]:
    evidence = load_r143_source_evidence_map(path)
    return {
        "episode_id": evidence.episode_id,
        "source_locator": evidence.source_locator,
        "complete_source_sequence_claim": evidence.complete_source_sequence_claim,
        "stages": [
            {
                "stage": item.stage.name,
                "source_status": item.status.value,
                "source_refs": list(item.source_refs),
                "machine_stage_certified": False,
            }
            for item in evidence.stages
        ],
        "promotion_allowed": False,
        "performance_claim_allowed": False,
        "live_execution_authorized": False,
    }


def build_march_replay_bundle(
    ingestion_manifest: str | Path,
    *,
    examples_root: str | Path,
) -> dict[str, Any]:
    verified = load_verified_persisted_mt5_snapshot(ingestion_manifest)
    root = Path(examples_root).expanduser().resolve()
    if not root.is_dir():
        raise MarchReplayBundleError("examples_root is unavailable")

    bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
        verified.canonical_snapshot_path.read_bytes(),
        source_name=verified.snapshot.source_name,
        source_symbol=verified.snapshot.source_symbol,
        timeframe_seconds=verified.snapshot.timeframe_seconds,
        evaluation_time=verified.snapshot.coverage_end,
        source_file_name=verified.snapshot.source_file_name,
    )
    if reproduced != verified.snapshot:
        raise MarchReplayBundleError("verified snapshot changed when canonical bytes were reproduced")

    staging = verified.store_root / "research-bundles" / ".march-2023-staging"
    staging.mkdir(parents=True, exist_ok=True)
    episode_records: list[dict[str, Any]] = []

    for label, fixture_name, evidence_name in _EPISODES:
        fixture_path = root / fixture_name
        evidence_path = root / evidence_name
        fixture = load_source_fidelity_fixture(fixture_path)
        if fixture.timeframe_seconds != verified.snapshot.timeframe_seconds:
            raise MarchReplayBundleError(f"{label}: fixture timeframe does not match snapshot")

        source_result = evaluate_source_fidelity_fixture(
            bars=bars,
            fixture=fixture,
            timeframe_seconds=verified.snapshot.timeframe_seconds,
        )
        primitive_result = scan_primitive_replay_window(
            bars=bars,
            timeframe_seconds=verified.snapshot.timeframe_seconds,
            scan_start=fixture.window_start,
            scan_end=fixture.window_end,
            max_window_bars=20_000,
        )
        source_payload = _source_report(verified, source_result)
        primitive_payload = _primitive_report(verified, primitive_result)

        source_path = staging / f"{label}.source.json"
        primitive_path = staging / f"{label}.primitive.json"
        source_sha = _write_immutable_json(source_path, source_payload)
        primitive_sha = _write_immutable_json(primitive_path, primitive_payload)
        bridge = build_source_primitive_bridge(source_path, primitive_path)
        bridge_payload = _jsonable(asdict(bridge))
        bridge_sha = hashlib.sha256(_canonical_json_bytes(bridge_payload)).hexdigest()
        evidence_payload = _evidence_summary(evidence_path)
        evidence_sha = hashlib.sha256(evidence_path.read_bytes()).hexdigest()

        episode_records.append(
            {
                "label": label,
                "fixture_file": fixture_name,
                "fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
                "source_report": source_payload,
                "source_report_sha256": source_sha,
                "primitive_report": primitive_payload,
                "primitive_report_sha256": primitive_sha,
                "bridge_report": bridge_payload,
                "bridge_report_sha256": bridge_sha,
                "r143_source_evidence": evidence_payload,
                "r143_source_evidence_sha256": evidence_sha,
            }
        )

    identity = {
        "schema_version": "march_2023_replay_bundle_v1",
        "snapshot_id": verified.snapshot.snapshot_id,
        "normalized_sha256": verified.normalized_sha256,
        "source_sha256": verified.source_sha256,
        "broker_name": verified.snapshot.source_name,
        "broker_symbol": verified.snapshot.source_symbol,
        "timeframe_seconds": verified.snapshot.timeframe_seconds,
        "episodes": [
            {
                "label": item["label"],
                "fixture_sha256": item["fixture_sha256"],
                "source_report_sha256": item["source_report_sha256"],
                "primitive_report_sha256": item["primitive_report_sha256"],
                "bridge_report_sha256": item["bridge_report_sha256"],
                "r143_source_evidence_sha256": item["r143_source_evidence_sha256"],
            }
            for item in episode_records
        ],
        "reference_feed_required": "FOREXCOM:XAUUSD",
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "strategy_truth_changed": False,
        "live_execution_authorized": False,
    }
    bundle_sha = hashlib.sha256(_canonical_json_bytes(identity)).hexdigest()
    bundle_root = verified.store_root / "research-bundles" / "march-2023" / bundle_sha
    bundle_payload = dict(identity)
    bundle_payload.update(
        {
            "status": "MARCH_2023_REPLAY_BUNDLE_BUILT_NOT_CERTIFIED",
            "bundle_sha256": bundle_sha,
            "episodes_full": episode_records,
        }
    )
    manifest_path = bundle_root / "manifest.json"
    _write_immutable_json(manifest_path, bundle_payload)

    for item in episode_records:
        label = item["label"]
        episode_root = bundle_root / label
        _write_immutable_json(episode_root / "source_fidelity.json", item["source_report"])
        _write_immutable_json(episode_root / "primitive_scan.json", item["primitive_report"])
        _write_immutable_json(episode_root / "source_primitive_bridge.json", item["bridge_report"])
        _write_immutable_json(episode_root / "r143_source_evidence.json", item["r143_source_evidence"])

    return {
        "status": "MARCH_2023_REPLAY_BUNDLE_BUILT_NOT_CERTIFIED",
        "bundle_sha256": bundle_sha,
        "bundle_root": str(bundle_root),
        "manifest_path": str(manifest_path),
        "snapshot_id": verified.snapshot.snapshot_id,
        "normalized_sha256": verified.normalized_sha256,
        "episode_count": len(episode_records),
        "episodes": [
            {
                "label": item["label"],
                "source_status": item["source_report"]["status"],
                "matched_anchor_count": item["source_report"]["matched_anchor_count"],
                "anchor_count": item["source_report"]["anchor_count"],
                "basic_fu_candidate_count": item["primitive_report"]["basic_fu_candidate_count"],
                "source_style_hcs_candidate_count": item["primitive_report"]["source_style_hcs_candidate_count"],
                "exact_bar_basic_fu_correspondence_count": item["bridge_report"]["exact_bar_basic_fu_correspondence_count"],
                "exact_bar_hcs_candidate_correspondence_count": item["bridge_report"]["exact_bar_hcs_candidate_correspondence_count"],
            }
            for item in episode_records
        ],
        "reference_feed_required": "FOREXCOM:XAUUSD",
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "strategy_truth_changed": False,
        "live_execution_authorized": False,
    }
