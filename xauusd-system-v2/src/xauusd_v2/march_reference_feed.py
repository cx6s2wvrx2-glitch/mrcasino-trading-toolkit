from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .agents.data_agent import MarketBar
from .data_snapshot import DataSnapshotError, load_xauusd_csv_snapshot_bytes
from .mt5_snapshot_load import load_verified_persisted_mt5_snapshot
from .primitive_replay_scan import PrimitiveReplayScanResult, scan_primitive_replay_window
from .source_fidelity_replay import (
    SourceFidelityReplayResult,
    evaluate_source_fidelity_fixture,
    load_source_fidelity_fixture,
)


class MarchReferenceFeedError(ValueError):
    pass


_REFERENCE_SOURCE_NAME = "FOREXCOM"
_REFERENCE_SOURCE_SYMBOL = "XAUUSD"
_REFERENCE_FEED_ID = "FOREXCOM:XAUUSD"
_MARCH_START = datetime(2023, 3, 30, tzinfo=UTC)
_MARCH_END = datetime(2023, 4, 1, tzinfo=UTC)
_EPISODES = (
    ("2023-03-30-buy", "SOURCE_FIDELITY_2023_03_30_BUY.json"),
    ("2023-03-31-sell", "SOURCE_FIDELITY_2023_03_31_SELL.json"),
)


def _canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_immutable(path: Path, data: bytes) -> str:
    digest = hashlib.sha256(data).hexdigest()
    if path.exists():
        if path.read_bytes() != data:
            raise MarchReferenceFeedError(f"refusing to overwrite differing immutable artifact: {path}")
        return digest
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return digest


def _parse_reference_timestamp(raw: str, *, row_number: int) -> datetime:
    text = raw.strip()
    if not text:
        raise MarchReferenceFeedError(f"row {row_number}: reference timestamp is required")

    # Unix epoch values are timezone-unambiguous and common in chart exports.
    try:
        if text.lstrip("-").isdigit():
            value = int(text)
            if abs(value) >= 10_000_000_000:
                value /= 1000
            return datetime.fromtimestamp(value, tz=UTC)
    except (OverflowError, OSError, ValueError) as exc:
        raise MarchReferenceFeedError(f"row {row_number}: invalid Unix reference timestamp") from exc

    iso_text = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(iso_text)
    except ValueError as exc:
        raise MarchReferenceFeedError(
            f"row {row_number}: timestamp must be timezone-aware ISO-8601 or Unix epoch"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MarchReferenceFeedError(
            f"row {row_number}: naive timestamp rejected; reference-feed timezone must be explicit"
        )
    return parsed.astimezone(UTC)


def _price(raw: str, *, field: str, row_number: int) -> Decimal:
    try:
        value = Decimal(raw.strip())
    except Exception as exc:
        raise MarchReferenceFeedError(f"row {row_number}: invalid {field}") from exc
    if not value.is_finite() or value <= 0:
        raise MarchReferenceFeedError(f"row {row_number}: {field} must be finite and positive")
    return value


def _reference_columns(fieldnames: list[str] | None) -> dict[str, str]:
    if not fieldnames:
        raise MarchReferenceFeedError("reference CSV has no header")
    by_lower: dict[str, str] = {}
    for field in fieldnames:
        key = field.strip().lower()
        if key in by_lower:
            raise MarchReferenceFeedError(f"reference CSV has duplicate case-insensitive column: {key}")
        by_lower[key] = field

    timestamp_candidates = [name for name in ("timestamp", "time") if name in by_lower]
    if len(timestamp_candidates) != 1:
        raise MarchReferenceFeedError("reference CSV requires exactly one timestamp/time column")
    required = {name: by_lower.get(name) for name in ("open", "high", "low", "close")}
    missing = [name for name, value in required.items() if value is None]
    if missing:
        raise MarchReferenceFeedError(f"reference CSV missing fields: {', '.join(missing)}")
    return {
        "timestamp": by_lower[timestamp_candidates[0]],
        "open": required["open"] or "",
        "high": required["high"] or "",
        "low": required["low"] or "",
        "close": required["close"] or "",
    }


def _normalize_reference_csv(raw_bytes: bytes) -> tuple[bytes, str, int]:
    if not raw_bytes:
        raise MarchReferenceFeedError("reference CSV is empty")
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise MarchReferenceFeedError("reference CSV must be UTF-8") from exc

    reader = csv.DictReader(io.StringIO(text))
    columns = _reference_columns(reader.fieldnames)
    selected: list[tuple[datetime, Decimal, Decimal, Decimal, Decimal]] = []
    previous: datetime | None = None
    for row_number, row in enumerate(reader, start=2):
        timestamp = _parse_reference_timestamp(row[columns["timestamp"]], row_number=row_number)
        if previous is not None and timestamp <= previous:
            raise MarchReferenceFeedError(
                f"row {row_number}: reference timestamps must be strictly increasing with no duplicates"
            )
        previous = timestamp
        open_value = _price(row[columns["open"]], field="open", row_number=row_number)
        high_value = _price(row[columns["high"]], field="high", row_number=row_number)
        low_value = _price(row[columns["low"]], field="low", row_number=row_number)
        close_value = _price(row[columns["close"]], field="close", row_number=row_number)
        if high_value < max(open_value, close_value) or low_value > min(open_value, close_value) or low_value > high_value:
            raise MarchReferenceFeedError(f"row {row_number}: invalid OHLC geometry")
        if _MARCH_START <= timestamp < _MARCH_END:
            selected.append((timestamp, open_value, high_value, low_value, close_value))

    if len(selected) < 2:
        raise MarchReferenceFeedError("reference CSV contains fewer than two M1 bars in the governed March window")

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("timestamp", "open", "high", "low", "close"))
    for timestamp, open_value, high_value, low_value, close_value in selected:
        writer.writerow(
            (
                timestamp.isoformat().replace("+00:00", "Z"),
                str(open_value),
                str(high_value),
                str(low_value),
                str(close_value),
            )
        )
    normalized = output.getvalue().encode("utf-8")
    return normalized, hashlib.sha256(raw_bytes).hexdigest(), len(selected)


def _bar_map(bars: tuple[MarketBar, ...], *, start: datetime, end: datetime) -> dict[datetime, MarketBar]:
    return {bar.timestamp.astimezone(UTC): bar for bar in bars if start <= bar.timestamp.astimezone(UTC) < end and bar.is_closed}


def _decimal_price(value: float) -> Decimal:
    return Decimal(str(value))


def _feed_geometry(reference: tuple[MarketBar, ...], broker: tuple[MarketBar, ...], *, start: datetime, end: datetime) -> dict[str, Any]:
    ref = _bar_map(reference, start=start, end=end)
    bro = _bar_map(broker, start=start, end=end)
    ref_times = set(ref)
    bro_times = set(bro)
    common = sorted(ref_times & bro_times)
    stats: dict[str, dict[str, Any]] = {}
    for field in ("open", "high", "low", "close"):
        deltas = [
            _decimal_price(getattr(ref[timestamp], field)) - _decimal_price(getattr(bro[timestamp], field))
            for timestamp in common
        ]
        nonzero = [value for value in deltas if value != 0]
        stats[field] = {
            "nonzero_delta_count": len(nonzero),
            "max_abs_delta": str(max((abs(value) for value in deltas), default=Decimal("0"))),
        }
    exact_ohlc = sum(
        1
        for timestamp in common
        if all(
            _decimal_price(getattr(ref[timestamp], field)) == _decimal_price(getattr(bro[timestamp], field))
            for field in ("open", "high", "low", "close")
        )
    )
    return {
        "reference_bar_count": len(ref),
        "broker_bar_count": len(bro),
        "exact_timestamp_intersection_count": len(common),
        "reference_only_timestamp_count": len(ref_times - bro_times),
        "broker_only_timestamp_count": len(bro_times - ref_times),
        "exact_ohlc_match_count": exact_ohlc,
        "ohlc_delta_stats": stats,
        "nearest_bar_substitution_allowed": False,
        "price_tolerance_applied": False,
    }


def _anchor_rows(result: SourceFidelityReplayResult) -> list[dict[str, Any]]:
    return [
        {
            "anchor_id": item.anchor_id,
            "level": str(item.level),
            "predicate": item.predicate.value,
            "matched": item.matched,
            "matched_at": item.matched_at.astimezone(UTC).isoformat().replace("+00:00", "Z") if item.matched_at else None,
            "open": str(item.open) if item.open is not None else None,
            "high": str(item.high) if item.high is not None else None,
            "low": str(item.low) if item.low is not None else None,
            "close": str(item.close) if item.close is not None else None,
        }
        for item in result.anchor_matches
    ]


def _primitive_correspondence(source: SourceFidelityReplayResult, primitive: PrimitiveReplayScanResult) -> dict[str, Any]:
    fu_times = {item.bar_open.astimezone(UTC) for item in primitive.fu_candidates}
    hcs_times = {
        item.interaction_bar_open.astimezone(UTC)
        for item in primitive.wick_interactions
        if item.source_style_hcs_candidate
    }
    observations: list[dict[str, Any]] = []
    for anchor in source.anchor_matches:
        matched_at = anchor.matched_at.astimezone(UTC) if anchor.matched_at is not None else None
        observations.append(
            {
                "anchor_id": anchor.anchor_id,
                "matched_at": matched_at.isoformat().replace("+00:00", "Z") if matched_at else None,
                "basic_fu_candidate_at_exact_bar": matched_at in fu_times if matched_at is not None else None,
                "source_style_hcs_candidate_at_exact_bar": matched_at in hcs_times if matched_at is not None else None,
            }
        )
    return {
        "basic_fu_candidate_count": len(primitive.fu_candidates),
        "source_style_hcs_candidate_count": primitive.source_style_hcs_candidates,
        "exact_bar_basic_fu_correspondence_count": sum(item["basic_fu_candidate_at_exact_bar"] is True for item in observations),
        "exact_bar_hcs_candidate_correspondence_count": sum(item["source_style_hcs_candidate_at_exact_bar"] is True for item in observations),
        "anchor_observations": observations,
        "certified_fu_count": 0,
        "certified_hcs_count": 0,
    }


def _source_summary(result: SourceFidelityReplayResult) -> dict[str, Any]:
    passed = result.all_anchors_matched and result.expansion_probe_matched
    return {
        "status": "SOURCE_FIDELITY_REPLAY_PASS" if passed else "SOURCE_FIDELITY_REPLAY_INCOMPLETE",
        "anchor_count": len(result.anchor_matches),
        "matched_anchor_count": sum(item.matched for item in result.anchor_matches),
        "all_anchors_matched": result.all_anchors_matched,
        "expansion_probe_matched": result.expansion_probe_matched,
        "anchors": _anchor_rows(result),
    }


def _anchor_comparison(reference: SourceFidelityReplayResult, broker: SourceFidelityReplayResult) -> list[dict[str, Any]]:
    broker_by_id = {item.anchor_id: item for item in broker.anchor_matches}
    rows: list[dict[str, Any]] = []
    for ref_item in reference.anchor_matches:
        bro_item = broker_by_id[ref_item.anchor_id]
        ref_time = ref_item.matched_at.astimezone(UTC) if ref_item.matched_at else None
        bro_time = bro_item.matched_at.astimezone(UTC) if bro_item.matched_at else None
        rows.append(
            {
                "anchor_id": ref_item.anchor_id,
                "reference_matched": ref_item.matched,
                "broker_matched": bro_item.matched,
                "reference_matched_at": ref_time.isoformat().replace("+00:00", "Z") if ref_time else None,
                "broker_matched_at": bro_time.isoformat().replace("+00:00", "Z") if bro_time else None,
                "same_exact_matched_timestamp": ref_time == bro_time if ref_time is not None and bro_time is not None else None,
            }
        )
    return rows


def build_march_reference_feed_comparison(
    reference_csv: str | Path,
    ingestion_manifest: str | Path,
    *,
    examples_root: str | Path,
) -> dict[str, Any]:
    reference_path = Path(reference_csv).expanduser().resolve()
    if not reference_path.is_file():
        raise MarchReferenceFeedError("reference CSV is unavailable")
    examples = Path(examples_root).expanduser().resolve()
    if not examples.is_dir():
        raise MarchReferenceFeedError("examples_root is unavailable")

    normalized_bytes, raw_sha256, selected_count = _normalize_reference_csv(reference_path.read_bytes())
    try:
        reference_bars, reference_manifest, _ = load_xauusd_csv_snapshot_bytes(
            normalized_bytes,
            source_name=_REFERENCE_SOURCE_NAME,
            source_symbol=_REFERENCE_SOURCE_SYMBOL,
            timeframe_seconds=60,
            evaluation_time=_MARCH_END,
            source_file_name=reference_path.name,
        )
    except DataSnapshotError as exc:
        raise MarchReferenceFeedError(str(exc)) from exc
    if not reference_manifest.closed_only:
        raise MarchReferenceFeedError("governed March reference sample must contain closed bars only")
    if reference_manifest.bar_count != selected_count:
        raise MarchReferenceFeedError("reference normalization bar count mismatch")

    verified = load_verified_persisted_mt5_snapshot(ingestion_manifest)
    if verified.snapshot.timeframe_seconds != 60:
        raise MarchReferenceFeedError("broker comparison requires the verified M1 snapshot")
    broker_bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
        verified.canonical_snapshot_path.read_bytes(),
        source_name=verified.snapshot.source_name,
        source_symbol=verified.snapshot.source_symbol,
        timeframe_seconds=verified.snapshot.timeframe_seconds,
        evaluation_time=verified.snapshot.coverage_end,
        source_file_name=verified.snapshot.source_file_name,
    )
    if reproduced != verified.snapshot:
        raise MarchReferenceFeedError("verified broker snapshot changed when canonical bytes were reproduced")

    episodes: list[dict[str, Any]] = []
    for label, fixture_name in _EPISODES:
        fixture_path = examples / fixture_name
        fixture = load_source_fidelity_fixture(fixture_path)
        reference_source = evaluate_source_fidelity_fixture(
            bars=reference_bars,
            fixture=fixture,
            timeframe_seconds=60,
        )
        broker_source = evaluate_source_fidelity_fixture(
            bars=broker_bars,
            fixture=fixture,
            timeframe_seconds=60,
        )
        reference_primitive = scan_primitive_replay_window(
            bars=reference_bars,
            timeframe_seconds=60,
            scan_start=fixture.window_start,
            scan_end=fixture.window_end,
            max_window_bars=20_000,
        )
        broker_primitive = scan_primitive_replay_window(
            bars=broker_bars,
            timeframe_seconds=60,
            scan_start=fixture.window_start,
            scan_end=fixture.window_end,
            max_window_bars=20_000,
        )
        episodes.append(
            {
                "label": label,
                "fixture_file": fixture_name,
                "fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
                "window_start": fixture.window_start.astimezone(UTC).isoformat().replace("+00:00", "Z"),
                "window_end": fixture.window_end.astimezone(UTC).isoformat().replace("+00:00", "Z"),
                "reference_source": _source_summary(reference_source),
                "broker_source": _source_summary(broker_source),
                "reference_primitives": _primitive_correspondence(reference_source, reference_primitive),
                "broker_primitives": _primitive_correspondence(broker_source, broker_primitive),
                "anchor_comparison": _anchor_comparison(reference_source, broker_source),
                "feed_geometry": _feed_geometry(
                    reference_bars,
                    broker_bars,
                    start=fixture.window_start,
                    end=fixture.window_end,
                ),
            }
        )

    reference_correspondence = sum(
        episode["reference_primitives"]["exact_bar_basic_fu_correspondence_count"]
        + episode["reference_primitives"]["exact_bar_hcs_candidate_correspondence_count"]
        for episode in episodes
    )
    broker_correspondence = sum(
        episode["broker_primitives"]["exact_bar_basic_fu_correspondence_count"]
        + episode["broker_primitives"]["exact_bar_hcs_candidate_correspondence_count"]
        for episode in episodes
    )
    reference_all_source_pass = all(
        episode["reference_source"]["status"] == "SOURCE_FIDELITY_REPLAY_PASS" for episode in episodes
    )
    if reference_correspondence > broker_correspondence:
        diagnostic = "REFERENCE_FEED_CHANGES_PRIMITIVE_CORRESPONDENCE"
    elif reference_all_source_pass and reference_correspondence == 0:
        diagnostic = "REFERENCE_FEED_DOES_NOT_RESOLVE_PRIMITIVE_CORRESPONDENCE"
    elif not reference_all_source_pass:
        diagnostic = "REFERENCE_FEED_GEOMETRY_DIFFERS_AT_SOURCE_ANCHORS"
    else:
        diagnostic = "REFERENCE_FEED_COMPARISON_INCONCLUSIVE_NOT_CERTIFIED"

    identity = {
        "schema_version": "march_reference_feed_comparison_v1",
        "reference_feed_id": _REFERENCE_FEED_ID,
        "reference_raw_sha256": raw_sha256,
        "reference_normalized_sha256": reference_manifest.sha256,
        "broker_snapshot_id": verified.snapshot.snapshot_id,
        "broker_normalized_sha256": verified.normalized_sha256,
        "timeframe_seconds": 60,
        "window_start": _MARCH_START.isoformat().replace("+00:00", "Z"),
        "window_end": _MARCH_END.isoformat().replace("+00:00", "Z"),
        "fixture_sha256": [episode["fixture_sha256"] for episode in episodes],
    }
    comparison_sha256 = hashlib.sha256(_canonical_json_bytes(identity)).hexdigest()
    root = verified.store_root / "reference-feed-comparisons" / "march-2023" / comparison_sha256
    canonical_path = root / "forexcom_xauusd_m1.csv"
    _write_immutable(canonical_path, normalized_bytes)

    manifest = {
        **identity,
        "status": "MARCH_REFERENCE_FEED_COMPARISON_BUILT_NOT_CERTIFIED",
        "comparison_sha256": comparison_sha256,
        "diagnostic": diagnostic,
        "episodes": episodes,
        "reference_input_file": reference_path.name,
        "reference_bar_count": reference_manifest.bar_count,
        "reference_canonical_path": str(canonical_path),
        "broker_name": verified.snapshot.source_name,
        "broker_symbol": verified.snapshot.source_symbol,
        "candidate_only_output": True,
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "strategy_truth_changed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
        "price_tolerance_applied": False,
        "nearest_bar_substitution_allowed": False,
    }
    manifest_path = root / "manifest.json"
    _write_immutable(manifest_path, _canonical_json_bytes(manifest))

    return {
        "status": manifest["status"],
        "comparison_sha256": comparison_sha256,
        "comparison_root": str(root),
        "manifest_path": str(manifest_path),
        "reference_feed_id": _REFERENCE_FEED_ID,
        "reference_raw_sha256": raw_sha256,
        "reference_normalized_sha256": reference_manifest.sha256,
        "reference_bar_count": reference_manifest.bar_count,
        "broker_snapshot_id": verified.snapshot.snapshot_id,
        "broker_normalized_sha256": verified.normalized_sha256,
        "diagnostic": diagnostic,
        "episodes": [
            {
                "label": episode["label"],
                "reference_source_status": episode["reference_source"]["status"],
                "reference_matched_anchor_count": episode["reference_source"]["matched_anchor_count"],
                "reference_anchor_count": episode["reference_source"]["anchor_count"],
                "reference_basic_fu_candidate_count": episode["reference_primitives"]["basic_fu_candidate_count"],
                "reference_source_style_hcs_candidate_count": episode["reference_primitives"]["source_style_hcs_candidate_count"],
                "reference_exact_bar_basic_fu_correspondence_count": episode["reference_primitives"]["exact_bar_basic_fu_correspondence_count"],
                "reference_exact_bar_hcs_candidate_correspondence_count": episode["reference_primitives"]["exact_bar_hcs_candidate_correspondence_count"],
                "broker_exact_bar_basic_fu_correspondence_count": episode["broker_primitives"]["exact_bar_basic_fu_correspondence_count"],
                "broker_exact_bar_hcs_candidate_correspondence_count": episode["broker_primitives"]["exact_bar_hcs_candidate_correspondence_count"],
                "feed_geometry": episode["feed_geometry"],
            }
            for episode in episodes
        ],
        "candidate_only_output": True,
        "semantic_stage_certification": False,
        "performance_claim_allowed": False,
        "strategy_truth_changed": False,
        "promotion_allowed": False,
        "live_execution_authorized": False,
        "price_tolerance_applied": False,
        "nearest_bar_substitution_allowed": False,
    }
