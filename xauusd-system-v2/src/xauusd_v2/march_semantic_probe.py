from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .agents.data_agent import MarketBar
from .data_snapshot import load_xauusd_csv_snapshot_bytes
from .fu_basic_candidate import BasicFUCandidateState, classify_basic_fu_candidate
from .mt5_snapshot_load import load_verified_persisted_mt5_snapshot
from .primitive_replay_scan import PrimitiveReplayScanResult, scan_primitive_replay_window


class MarchSemanticProbeError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class MarchSemanticProbeSpec:
    probe_id: str
    episode_id: str
    source_ref: str
    source_role: str
    primitive_family: str
    level: Decimal
    timeframe_seconds: int
    window_start: datetime
    window_end: datetime
    note: str


_GOVERNED_START = datetime(2023, 3, 30, tzinfo=UTC)
_GOVERNED_END = datetime(2023, 4, 1, tzinfo=UTC)
_FIXTURE_SCHEMA = "march_source_semantic_probes_v1"
_TOP_LEVEL_FIELDS = {
    "schema_version",
    "probes",
    "source_occurrence_timestamps_certified",
    "semantic_stage_certification",
    "performance_claim_allowed",
    "promotion_allowed",
    "live_execution_authorized",
}
_PROBE_FIELDS = {
    "probe_id",
    "episode_id",
    "source_ref",
    "source_role",
    "primitive_family",
    "level",
    "timeframe_seconds",
    "window_start",
    "window_end",
    "note",
}


def _canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_immutable(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise MarchSemanticProbeError(f"refusing to overwrite differing immutable artifact: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _parse_aware_timestamp(raw: Any, *, field: str) -> datetime:
    if not isinstance(raw, str) or not raw.strip():
        raise MarchSemanticProbeError(f"{field} must be a non-empty timezone-aware timestamp")
    text = raw.strip()
    iso_text = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(iso_text)
    except ValueError as exc:
        raise MarchSemanticProbeError(f"{field} must be valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MarchSemanticProbeError(f"{field} must be timezone-aware")
    return parsed.astimezone(UTC)


def _parse_level(raw: Any, *, probe_id: str) -> Decimal:
    if not isinstance(raw, str) or not raw.strip():
        raise MarchSemanticProbeError(f"{probe_id}: level must be an exact decimal string")
    try:
        value = Decimal(raw.strip())
    except InvalidOperation as exc:
        raise MarchSemanticProbeError(f"{probe_id}: invalid level") from exc
    if not value.is_finite() or value <= 0:
        raise MarchSemanticProbeError(f"{probe_id}: level must be finite and positive")
    return value


def load_march_semantic_probe_specs(path: str | Path) -> tuple[MarchSemanticProbeSpec, ...]:
    fixture_path = Path(path).expanduser().resolve()
    if not fixture_path.is_file():
        raise MarchSemanticProbeError("semantic probe fixture is unavailable")
    try:
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MarchSemanticProbeError("semantic probe fixture is not valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise MarchSemanticProbeError("semantic probe fixture root must be an object")
    extra = set(payload) - _TOP_LEVEL_FIELDS
    missing = _TOP_LEVEL_FIELDS - set(payload)
    if extra or missing:
        raise MarchSemanticProbeError(
            f"semantic probe fixture fields mismatch; missing={sorted(missing)} extra={sorted(extra)}"
        )
    if payload["schema_version"] != _FIXTURE_SCHEMA:
        raise MarchSemanticProbeError("unsupported semantic probe fixture schema")
    for flag in (
        "source_occurrence_timestamps_certified",
        "semantic_stage_certification",
        "performance_claim_allowed",
        "promotion_allowed",
        "live_execution_authorized",
    ):
        if payload[flag] is not False:
            raise MarchSemanticProbeError(f"{flag} must remain false")

    raw_probes = payload["probes"]
    if not isinstance(raw_probes, list) or not raw_probes:
        raise MarchSemanticProbeError("semantic probe fixture requires at least one probe")

    specs: list[MarchSemanticProbeSpec] = []
    seen: set[str] = set()
    for index, raw_probe in enumerate(raw_probes):
        if not isinstance(raw_probe, dict):
            raise MarchSemanticProbeError(f"probe {index}: expected object")
        extra_probe = set(raw_probe) - _PROBE_FIELDS
        missing_probe = _PROBE_FIELDS - set(raw_probe)
        if extra_probe or missing_probe:
            raise MarchSemanticProbeError(
                f"probe {index}: fields mismatch; missing={sorted(missing_probe)} extra={sorted(extra_probe)}"
            )
        probe_id = raw_probe["probe_id"]
        if not isinstance(probe_id, str) or not probe_id.strip():
            raise MarchSemanticProbeError(f"probe {index}: probe_id is required")
        if probe_id in seen:
            raise MarchSemanticProbeError(f"duplicate probe_id: {probe_id}")
        seen.add(probe_id)
        for field in ("episode_id", "source_ref", "source_role", "note"):
            if not isinstance(raw_probe[field], str) or not raw_probe[field].strip():
                raise MarchSemanticProbeError(f"{probe_id}: {field} is required")
        family = raw_probe["primitive_family"]
        if family not in {"FU", "HCS"}:
            raise MarchSemanticProbeError(f"{probe_id}: primitive_family must be FU or HCS")
        timeframe = raw_probe["timeframe_seconds"]
        if type(timeframe) is not int or timeframe != 60:
            raise MarchSemanticProbeError(f"{probe_id}: only governed M1/60-second probes are allowed")
        start = _parse_aware_timestamp(raw_probe["window_start"], field=f"{probe_id}.window_start")
        end = _parse_aware_timestamp(raw_probe["window_end"], field=f"{probe_id}.window_end")
        if end <= start:
            raise MarchSemanticProbeError(f"{probe_id}: window_end must be later than window_start")
        if start < _GOVERNED_START or end > _GOVERNED_END:
            raise MarchSemanticProbeError(f"{probe_id}: probe window escapes the governed March interval")
        specs.append(
            MarchSemanticProbeSpec(
                probe_id=probe_id,
                episode_id=raw_probe["episode_id"].strip(),
                source_ref=raw_probe["source_ref"].strip(),
                source_role=raw_probe["source_role"].strip(),
                primitive_family=family,
                level=_parse_level(raw_probe["level"], probe_id=probe_id),
                timeframe_seconds=timeframe,
                window_start=start,
                window_end=end,
                note=raw_probe["note"].strip(),
            )
        )
    return tuple(specs)


def _decimal_price(value: float) -> Decimal:
    return Decimal(str(value))


def _basic_fu_observation(
    bars: tuple[MarketBar, ...],
    index: int,
    *,
    timeframe_seconds: int,
) -> dict[str, Any]:
    current = bars[index]
    if index == 0:
        return {
            "state": "UNAVAILABLE_WINDOW_BOUNDARY",
            "direction": None,
            "reason": "previous closed bar is outside the explicit probe window",
        }
    previous = bars[index - 1]
    if current.timestamp - previous.timestamp != timedelta(seconds=timeframe_seconds):
        return {
            "state": "UNAVAILABLE_DATA_GAP",
            "direction": None,
            "reason": "previous closed bar is not contiguous; adjacency is not inferred across a data gap",
        }
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
    return {
        "state": result.state.value,
        "direction": direction,
        "reason": result.reason,
        "swept_previous_high": result.swept_previous_high,
        "swept_previous_low": result.swept_previous_low,
        "previous_high": str(_decimal_price(previous.high)),
        "previous_low": str(_decimal_price(previous.low)),
    }


def _probe_one(
    bars: tuple[MarketBar, ...],
    primitive: PrimitiveReplayScanResult,
    spec: MarchSemanticProbeSpec,
) -> dict[str, Any]:
    selected = tuple(
        bar for bar in bars if spec.window_start <= bar.timestamp < spec.window_end and bar.is_closed
    )
    if len(selected) < 2:
        raise MarchSemanticProbeError(f"{spec.probe_id}: fewer than two closed bars in probe window")

    fu_times = {item.bar_open for item in primitive.fu_candidates}
    interactions_by_time: dict[datetime, list[Any]] = {}
    for item in primitive.wick_interactions:
        interactions_by_time.setdefault(item.interaction_bar_open, []).append(item)

    touched: list[dict[str, Any]] = []
    raw_match_count = 0
    for index, bar in enumerate(selected):
        level = spec.level
        if not (_decimal_price(bar.low) <= level <= _decimal_price(bar.high)):
            continue
        basic = _basic_fu_observation(selected, index, timeframe_seconds=spec.timeframe_seconds)
        interactions = interactions_by_time.get(bar.timestamp, [])
        hcs_candidates = [item for item in interactions if item.source_style_hcs_candidate]
        forms = sorted(
            {
                item.hcs_candidate_form.value
                for item in hcs_candidates
                if item.hcs_candidate_form is not None
            }
        )
        raw_family_match = (
            bar.timestamp in fu_times if spec.primitive_family == "FU" else bool(hcs_candidates)
        )
        raw_match_count += int(raw_family_match)
        touched.append(
            {
                "bar_open": bar.timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z"),
                "open": str(_decimal_price(bar.open)),
                "high": str(_decimal_price(bar.high)),
                "low": str(_decimal_price(bar.low)),
                "close": str(_decimal_price(bar.close)),
                "level_touched_exactly_by_range": True,
                "basic_fu": basic,
                "wick_interaction_count": len(interactions),
                "source_style_hcs_candidate_count": len(hcs_candidates),
                "source_style_hcs_candidate_forms": forms,
                "raw_requested_family_match": raw_family_match,
                "certified_fu": False,
                "certified_hcs": False,
            }
        )

    if not touched:
        diagnostic = "SOURCE_LEVEL_NOT_TOUCHED_ON_BROKER_FEED"
    elif spec.primitive_family == "FU" and raw_match_count:
        diagnostic = "RAW_FU_CANDIDATE_PRESENT_ON_SOURCE_LEVEL_TOUCH"
    elif spec.primitive_family == "FU":
        diagnostic = "NO_RAW_FU_CANDIDATE_ON_SOURCE_LEVEL_TOUCH"
    elif raw_match_count:
        diagnostic = "RAW_HCS_CANDIDATE_PRESENT_ON_SOURCE_LEVEL_TOUCH"
    else:
        diagnostic = "NO_RAW_HCS_CANDIDATE_ON_SOURCE_LEVEL_TOUCH"

    return {
        "probe_id": spec.probe_id,
        "episode_id": spec.episode_id,
        "source_ref": spec.source_ref,
        "source_role": spec.source_role,
        "primitive_family": spec.primitive_family,
        "level": str(spec.level),
        "timeframe_seconds": spec.timeframe_seconds,
        "window_start": spec.window_start.isoformat().replace("+00:00", "Z"),
        "window_end": spec.window_end.isoformat().replace("+00:00", "Z"),
        "source_note": spec.note,
        "source_occurrence_timestamp_certified": False,
        "occurrence_timestamp_inferred": False,
        "nearest_bar_substitution_allowed": False,
        "price_tolerance_applied": False,
        "level_touch_bar_count": len(touched),
        "raw_requested_family_match_bar_count": raw_match_count,
        "diagnostic": diagnostic,
        "touch_observations": touched,
        "certified_fu_count": 0,
        "certified_hcs_count": 0,
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }


def build_march_semantic_probe_report(
    ingestion_manifest: str | Path,
    *,
    probe_fixture: str | Path,
) -> dict[str, Any]:
    specs = load_march_semantic_probe_specs(probe_fixture)
    fixture_path = Path(probe_fixture).expanduser().resolve()
    verified = load_verified_persisted_mt5_snapshot(ingestion_manifest)
    if verified.snapshot.timeframe_seconds != 60:
        raise MarchSemanticProbeError("March semantic probes require the verified M1 snapshot")
    bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
        verified.canonical_snapshot_path.read_bytes(),
        source_name=verified.snapshot.source_name,
        source_symbol=verified.snapshot.source_symbol,
        timeframe_seconds=verified.snapshot.timeframe_seconds,
        evaluation_time=verified.snapshot.coverage_end,
        source_file_name=verified.snapshot.source_file_name,
    )
    if reproduced != verified.snapshot:
        raise MarchSemanticProbeError("verified snapshot changed when canonical bytes were reproduced")

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
        records.append(_probe_one(bars, scans[key], spec))

    payload = {
        "schema_version": "march_source_semantic_probe_report_v1",
        "status": "MARCH_SOURCE_SEMANTIC_PROBE_COMPLETE_NOT_CERTIFIED",
        "snapshot_id": verified.snapshot.snapshot_id,
        "normalized_sha256": verified.normalized_sha256,
        "broker_name": verified.snapshot.source_name,
        "broker_symbol": verified.snapshot.source_symbol,
        "probe_fixture": fixture_path.name,
        "probe_fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
        "probe_count": len(records),
        "probes": records,
        "interpretation_boundary": (
            "These probes test only whether the current narrow raw FU/HCS primitive grammar appears on closed M1 bars "
            "whose price range contains an explicitly source-labelled FU/HCS level. The source does not provide exact "
            "occurrence timestamps for these labels, so no individual broker bar is promoted to source event identity."
        ),
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
    report_root = verified.store_root / "research-bundles" / "march-2023-semantic-probes" / report_sha
    _write_immutable(report_root / "report.json", raw)
    return {
        "status": payload["status"],
        "report_sha256": report_sha,
        "report_root": str(report_root),
        "snapshot_id": payload["snapshot_id"],
        "normalized_sha256": payload["normalized_sha256"],
        "probe_count": len(records),
        "probes": [
            {
                "probe_id": item["probe_id"],
                "source_role": item["source_role"],
                "primitive_family": item["primitive_family"],
                "level": item["level"],
                "level_touch_bar_count": item["level_touch_bar_count"],
                "raw_requested_family_match_bar_count": item["raw_requested_family_match_bar_count"],
                "diagnostic": item["diagnostic"],
            }
            for item in records
        ],
        "reference_feed_alignment_complete": False,
        "source_occurrence_timestamps_certified": False,
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
    }
