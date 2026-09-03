from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


class SourcePrimitiveBridgeError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class AnchorPrimitiveCorrespondence:
    anchor_id: str
    source_ref: str
    source_level: str
    source_predicate: str
    broker_anchor_matched: bool
    matched_at: datetime | None
    primitive_window_covers_anchor: bool | None
    basic_fu_candidate_at_exact_bar: bool | None
    basic_fu_directions: tuple[str, ...]
    basic_fu_event_ids: tuple[str, ...]
    source_style_hcs_candidate_at_exact_bar: bool | None
    hcs_candidate_forms: tuple[str, ...]
    hcs_first_event_ids: tuple[str, ...]
    raw_correspondence_only: bool = True
    semantic_stage_certified: bool = False


@dataclass(frozen=True, slots=True)
class SourcePrimitiveBridgeResult:
    episode_id: str
    snapshot_id: str
    normalized_sha256: str
    broker_name: str
    broker_symbol: str
    timeframe_seconds: int
    source_report_sha256: str
    primitive_report_sha256: str
    source_window_start: datetime
    source_window_end: datetime
    primitive_scan_start: datetime
    primitive_scan_end: datetime
    anchors: tuple[AnchorPrimitiveCorrespondence, ...]
    matched_anchor_count: int
    covered_matched_anchor_count: int
    exact_bar_basic_fu_correspondence_count: int
    exact_bar_hcs_candidate_correspondence_count: int
    semantic_stage_certification: bool = False
    performance_claim_allowed: bool = False
    strategy_truth_changed: bool = False
    promotion_allowed: bool = False
    live_execution_authorized: bool = False


_SOURCE_REQUIRED_KEYS = {
    "schema_version",
    "status",
    "episode_id",
    "source_locator",
    "snapshot_id",
    "normalized_sha256",
    "broker_name",
    "broker_symbol",
    "timeframe_seconds",
    "window_start",
    "window_end",
    "anchors",
    "semantic_stage_certification",
    "performance_claim_allowed",
    "promotion_allowed",
    "strategy_truth_changed",
    "live_execution_authorized",
    "reference_feed_alignment_complete",
    "reference_feed_required",
}

_PRIMITIVE_REQUIRED_KEYS = {
    "schema_version",
    "status",
    "snapshot_id",
    "normalized_sha256",
    "broker_name",
    "broker_symbol",
    "timeframe_seconds",
    "scan_start",
    "scan_end",
    "fu_candidates",
    "wick_interactions",
    "certified_fu_count",
    "certified_hcs_count",
    "strategy_truth_changed",
    "promotion_allowed",
    "live_execution_authorized",
}

_ANCHOR_REQUIRED_KEYS = {
    "anchor_id",
    "level",
    "predicate",
    "source_ref",
    "matched",
    "matched_at",
}

_FU_REQUIRED_KEYS = {"event_id", "bar_open", "direction", "certified_fu"}
_HCS_REQUIRED_KEYS = {
    "first_event_id",
    "interaction_bar_open",
    "hcs_candidate_form",
    "source_style_hcs_candidate",
    "certified_hcs",
}


def _load_json(path: str | Path, *, label: str) -> tuple[dict[str, Any], str]:
    file_path = Path(path).expanduser().resolve()
    if not file_path.is_file():
        raise SourcePrimitiveBridgeError(f"{label} file is unavailable")
    try:
        raw_bytes = file_path.read_bytes()
        value = json.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SourcePrimitiveBridgeError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise SourcePrimitiveBridgeError(f"{label} must be a JSON object")
    return value, hashlib.sha256(raw_bytes).hexdigest()


def _require_keys(value: dict[str, Any], required: set[str], *, label: str) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise SourcePrimitiveBridgeError(f"{label} is missing required fields: {missing}")


def _text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SourcePrimitiveBridgeError(f"{field} must be non-empty text")
    return value.strip()


def _aware_time(value: object, *, field: str, allow_none: bool = False) -> datetime | None:
    if value is None and allow_none:
        return None
    text = _text(value, field=field)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise SourcePrimitiveBridgeError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SourcePrimitiveBridgeError(f"{field} must be timezone-aware")
    return parsed


def _false_flag(mapping: dict[str, Any], key: str, *, label: str) -> None:
    if mapping.get(key) is not False:
        raise SourcePrimitiveBridgeError(f"{label}.{key} must be false")


def _nonnegative_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SourcePrimitiveBridgeError(f"{field} must be a non-negative integer")
    return value


def build_source_primitive_bridge(
    source_fidelity_report: str | Path,
    primitive_scan_report: str | Path,
) -> SourcePrimitiveBridgeResult:
    """Join source-labelled broker anchors to raw primitive observations by exact bar time.

    This bridge is intentionally narrow. It never decides that an FU/HCS or any R-143
    stage is strategy-certified. It answers only whether the exact closed broker bar
    that satisfied a source-labelled price anchor was also labelled by the raw primitive
    scanner as a basic-FU candidate and/or an HCS-style candidate interaction.

    There is no price tolerance, nearest-event matching or after-the-fact time search.
    If an anchor lies outside the primitive scan window, primitive correspondence is
    returned as unknown (None), not false.
    """

    source, source_sha = _load_json(source_fidelity_report, label="source fidelity report")
    primitive, primitive_sha = _load_json(primitive_scan_report, label="primitive scan report")
    _require_keys(source, _SOURCE_REQUIRED_KEYS, label="source fidelity report")
    _require_keys(primitive, _PRIMITIVE_REQUIRED_KEYS, label="primitive scan report")

    if source["schema_version"] != "source_fidelity_replay_report_v1":
        raise SourcePrimitiveBridgeError("unsupported source fidelity report schema_version")
    if primitive["schema_version"] != "primitive_replay_scan_report_v1":
        raise SourcePrimitiveBridgeError("unsupported primitive scan report schema_version")
    if source["status"] not in {"SOURCE_FIDELITY_REPLAY_PASS", "SOURCE_FIDELITY_REPLAY_INCOMPLETE"}:
        raise SourcePrimitiveBridgeError("source fidelity report status is not bridge-admissible")
    if primitive["status"] != "PRIMITIVE_REPLAY_SCAN_COMPLETE_NOT_CERTIFIED":
        raise SourcePrimitiveBridgeError("primitive scan report status is not bridge-admissible")

    for key in (
        "semantic_stage_certification",
        "performance_claim_allowed",
        "promotion_allowed",
        "strategy_truth_changed",
        "live_execution_authorized",
    ):
        _false_flag(source, key, label="source fidelity report")
    for key in ("strategy_truth_changed", "promotion_allowed", "live_execution_authorized"):
        _false_flag(primitive, key, label="primitive scan report")

    if _nonnegative_int(primitive["certified_fu_count"], field="certified_fu_count") != 0:
        raise SourcePrimitiveBridgeError("primitive scan cannot claim certified FU evidence")
    if _nonnegative_int(primitive["certified_hcs_count"], field="certified_hcs_count") != 0:
        raise SourcePrimitiveBridgeError("primitive scan cannot claim certified HCS evidence")

    identity_fields = (
        "snapshot_id",
        "normalized_sha256",
        "broker_name",
        "broker_symbol",
        "timeframe_seconds",
    )
    for key in identity_fields:
        if source[key] != primitive[key]:
            raise SourcePrimitiveBridgeError(f"source/primitive identity mismatch: {key}")

    timeframe_seconds = primitive["timeframe_seconds"]
    if isinstance(timeframe_seconds, bool) or not isinstance(timeframe_seconds, int) or timeframe_seconds <= 0:
        raise SourcePrimitiveBridgeError("timeframe_seconds must be a positive integer")

    source_start = _aware_time(source["window_start"], field="source.window_start")
    source_end = _aware_time(source["window_end"], field="source.window_end")
    primitive_start = _aware_time(primitive["scan_start"], field="primitive.scan_start")
    primitive_end = _aware_time(primitive["scan_end"], field="primitive.scan_end")
    assert source_start is not None and source_end is not None
    assert primitive_start is not None and primitive_end is not None
    if source_end <= source_start or primitive_end <= primitive_start:
        raise SourcePrimitiveBridgeError("report windows must have positive duration")

    raw_fu = primitive["fu_candidates"]
    raw_hcs = primitive["wick_interactions"]
    if not isinstance(raw_fu, list) or not isinstance(raw_hcs, list):
        raise SourcePrimitiveBridgeError("primitive candidate arrays are invalid")

    fu_by_time: dict[datetime, list[dict[str, Any]]] = {}
    seen_event_ids: set[str] = set()
    for index, item in enumerate(raw_fu):
        if not isinstance(item, dict):
            raise SourcePrimitiveBridgeError(f"fu_candidates[{index}] must be an object")
        _require_keys(item, _FU_REQUIRED_KEYS, label=f"fu_candidates[{index}]")
        event_id = _text(item["event_id"], field=f"fu_candidates[{index}].event_id")
        if event_id in seen_event_ids:
            raise SourcePrimitiveBridgeError(f"duplicate primitive FU event_id: {event_id}")
        seen_event_ids.add(event_id)
        if item["certified_fu"] is not False:
            raise SourcePrimitiveBridgeError("primitive FU event cannot claim certification")
        bar_open = _aware_time(item["bar_open"], field=f"fu_candidates[{index}].bar_open")
        assert bar_open is not None
        fu_by_time.setdefault(bar_open, []).append(item)

    hcs_by_time: dict[datetime, list[dict[str, Any]]] = {}
    for index, item in enumerate(raw_hcs):
        if not isinstance(item, dict):
            raise SourcePrimitiveBridgeError(f"wick_interactions[{index}] must be an object")
        _require_keys(item, _HCS_REQUIRED_KEYS, label=f"wick_interactions[{index}]")
        if item["certified_hcs"] is not False:
            raise SourcePrimitiveBridgeError("primitive HCS interaction cannot claim certification")
        if item["source_style_hcs_candidate"] is not True:
            continue
        bar_open = _aware_time(
            item["interaction_bar_open"],
            field=f"wick_interactions[{index}].interaction_bar_open",
        )
        assert bar_open is not None
        hcs_by_time.setdefault(bar_open, []).append(item)

    raw_anchors = source["anchors"]
    if not isinstance(raw_anchors, list):
        raise SourcePrimitiveBridgeError("source anchors must be an array")

    observations: list[AnchorPrimitiveCorrespondence] = []
    seen_anchor_ids: set[str] = set()
    for index, item in enumerate(raw_anchors):
        if not isinstance(item, dict):
            raise SourcePrimitiveBridgeError(f"anchors[{index}] must be an object")
        _require_keys(item, _ANCHOR_REQUIRED_KEYS, label=f"anchors[{index}]")
        anchor_id = _text(item["anchor_id"], field=f"anchors[{index}].anchor_id")
        if anchor_id in seen_anchor_ids:
            raise SourcePrimitiveBridgeError(f"duplicate source anchor_id: {anchor_id}")
        seen_anchor_ids.add(anchor_id)
        matched = item["matched"]
        if not isinstance(matched, bool):
            raise SourcePrimitiveBridgeError(f"anchors[{index}].matched must be boolean")
        matched_at = _aware_time(
            item["matched_at"],
            field=f"anchors[{index}].matched_at",
            allow_none=True,
        )
        if matched != (matched_at is not None):
            raise SourcePrimitiveBridgeError(f"anchors[{index}] matched/matched_at are inconsistent")

        if matched_at is None:
            covered: bool | None = None
            fu_match: bool | None = None
            hcs_match: bool | None = None
            directions: tuple[str, ...] = ()
            event_ids: tuple[str, ...] = ()
            forms: tuple[str, ...] = ()
            first_ids: tuple[str, ...] = ()
        else:
            covered = primitive_start <= matched_at < primitive_end
            if not covered:
                fu_match = None
                hcs_match = None
                directions = ()
                event_ids = ()
                forms = ()
                first_ids = ()
            else:
                fu_items = fu_by_time.get(matched_at, [])
                hcs_items = hcs_by_time.get(matched_at, [])
                fu_match = bool(fu_items)
                hcs_match = bool(hcs_items)
                directions = tuple(sorted({_text(entry["direction"], field="direction") for entry in fu_items}))
                event_ids = tuple(sorted(_text(entry["event_id"], field="event_id") for entry in fu_items))
                forms = tuple(
                    sorted(
                        {
                            _text(entry["hcs_candidate_form"], field="hcs_candidate_form")
                            for entry in hcs_items
                            if entry.get("hcs_candidate_form") is not None
                        }
                    )
                )
                first_ids = tuple(
                    sorted(_text(entry["first_event_id"], field="first_event_id") for entry in hcs_items)
                )

        observations.append(
            AnchorPrimitiveCorrespondence(
                anchor_id=anchor_id,
                source_ref=_text(item["source_ref"], field=f"anchors[{index}].source_ref"),
                source_level=str(item["level"]),
                source_predicate=_text(item["predicate"], field=f"anchors[{index}].predicate"),
                broker_anchor_matched=matched,
                matched_at=matched_at,
                primitive_window_covers_anchor=covered,
                basic_fu_candidate_at_exact_bar=fu_match,
                basic_fu_directions=directions,
                basic_fu_event_ids=event_ids,
                source_style_hcs_candidate_at_exact_bar=hcs_match,
                hcs_candidate_forms=forms,
                hcs_first_event_ids=first_ids,
            )
        )

    matched_count = sum(1 for item in observations if item.broker_anchor_matched)
    covered_count = sum(
        1
        for item in observations
        if item.broker_anchor_matched and item.primitive_window_covers_anchor is True
    )
    fu_count = sum(1 for item in observations if item.basic_fu_candidate_at_exact_bar is True)
    hcs_count = sum(1 for item in observations if item.source_style_hcs_candidate_at_exact_bar is True)

    return SourcePrimitiveBridgeResult(
        episode_id=_text(source["episode_id"], field="episode_id"),
        snapshot_id=_text(source["snapshot_id"], field="snapshot_id"),
        normalized_sha256=_text(source["normalized_sha256"], field="normalized_sha256"),
        broker_name=_text(source["broker_name"], field="broker_name"),
        broker_symbol=_text(source["broker_symbol"], field="broker_symbol"),
        timeframe_seconds=timeframe_seconds,
        source_report_sha256=source_sha,
        primitive_report_sha256=primitive_sha,
        source_window_start=source_start,
        source_window_end=source_end,
        primitive_scan_start=primitive_start,
        primitive_scan_end=primitive_end,
        anchors=tuple(observations),
        matched_anchor_count=matched_count,
        covered_matched_anchor_count=covered_count,
        exact_bar_basic_fu_correspondence_count=fu_count,
        exact_bar_hcs_candidate_correspondence_count=hcs_count,
    )
