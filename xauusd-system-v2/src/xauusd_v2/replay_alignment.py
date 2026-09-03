from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


class ReplayAlignmentError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class VerifiedReplaySlice:
    manifest_path: Path
    csv_path: Path
    episode_id: str
    source_locator: str
    slice_sha256: str
    bar_count: int
    low_min: Decimal
    high_max: Decimal


@dataclass(frozen=True, slots=True)
class SourcePriceAnchor:
    anchor_id: str
    price: Decimal
    evidence_class: str
    source_image: str
    source_claim: str
    source_note: str
    role: str


@dataclass(frozen=True, slots=True)
class AnchorProbeResult:
    anchor_id: str
    price: str
    role: str
    evidence_class: str
    source_image: str
    source_claim: str
    source_note: str
    within_slice_price_range: bool
    touched: bool
    touch_bar_count: int
    first_touch_timestamp_utc: str | None
    last_touch_timestamp_utc: str | None
    closest_distance: str
    closest_timestamp_utc: str
    closest_bar_low: str
    closest_bar_high: str


def _decimal(value: object, *, field: str) -> Decimal:
    try:
        text = str(value).strip()
        if not text:
            raise InvalidOperation
        parsed = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise ReplayAlignmentError(f"{field} must be a decimal") from exc
    if not parsed.is_finite():
        raise ReplayAlignmentError(f"{field} must be finite")
    return parsed


def _positive_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ReplayAlignmentError(f"{field} must be a positive integer")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_timestamp(value: str, *, field: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ReplayAlignmentError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ReplayAlignmentError(f"{field} must be timezone-aware")
    return parsed.astimezone(UTC)


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def load_verified_replay_slice(manifest_path: str | Path) -> VerifiedReplaySlice:
    path = Path(manifest_path).expanduser().resolve()
    if not path.is_file():
        raise ReplayAlignmentError("replay slice manifest is unavailable")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReplayAlignmentError("replay slice manifest is not valid UTF-8 JSON") from exc

    if not isinstance(raw, dict):
        raise ReplayAlignmentError("replay slice manifest must be an object")
    if raw.get("schema_version") != "historical_replay_slice_v1":
        raise ReplayAlignmentError("unsupported replay slice schema")
    if raw.get("status") != "REPLAY_MARKET_SLICE_BUILT":
        raise ReplayAlignmentError("replay slice is not in built state")
    if raw.get("promotion_allowed") is not False or raw.get("live_execution_authorized") is not False:
        raise ReplayAlignmentError("replay slice governance flags are unsafe")

    episode_id = str(raw.get("episode_id", "")).strip()
    source_locator = str(raw.get("source_locator", "")).strip()
    slice_sha = str(raw.get("slice_sha256", "")).strip().lower()
    csv_path = Path(str(raw.get("csv_path", ""))).expanduser().resolve()
    if not episode_id or not source_locator:
        raise ReplayAlignmentError("replay slice provenance is incomplete")
    if len(slice_sha) != 64 or any(ch not in "0123456789abcdef" for ch in slice_sha):
        raise ReplayAlignmentError("replay slice SHA-256 is invalid")
    if not csv_path.is_file():
        raise ReplayAlignmentError("replay slice CSV is unavailable")
    if _sha256_file(csv_path) != slice_sha:
        raise ReplayAlignmentError("replay slice CSV SHA-256 mismatch")

    return VerifiedReplaySlice(
        manifest_path=path,
        csv_path=csv_path,
        episode_id=episode_id,
        source_locator=source_locator,
        slice_sha256=slice_sha,
        bar_count=_positive_int(raw.get("bar_count"), field="bar_count"),
        low_min=_decimal(raw.get("low_min"), field="low_min"),
        high_max=_decimal(raw.get("high_max"), field="high_max"),
    )


def load_source_price_anchors(anchor_path: str | Path) -> tuple[str, str, tuple[SourcePriceAnchor, ...]]:
    path = Path(anchor_path).expanduser().resolve()
    if not path.is_file():
        raise ReplayAlignmentError("source anchor file is unavailable")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReplayAlignmentError("source anchor file is not valid UTF-8 JSON") from exc
    if not isinstance(raw, dict) or raw.get("schema_version") != "source_price_anchor_set_v1":
        raise ReplayAlignmentError("unsupported source anchor schema")
    if raw.get("promotion_allowed") is not False or raw.get("live_execution_authorized") is not False:
        raise ReplayAlignmentError("source anchor governance flags are unsafe")
    episode_id = str(raw.get("episode_id", "")).strip()
    source_locator = str(raw.get("source_locator", "")).strip()
    anchors_raw = raw.get("anchors")
    if not episode_id or not source_locator or not isinstance(anchors_raw, list) or not anchors_raw:
        raise ReplayAlignmentError("source anchor provenance or anchors are incomplete")

    anchors: list[SourcePriceAnchor] = []
    seen: set[str] = set()
    for index, item in enumerate(anchors_raw):
        if not isinstance(item, dict):
            raise ReplayAlignmentError(f"anchor {index} must be an object")
        anchor_id = str(item.get("anchor_id", "")).strip()
        if not anchor_id or anchor_id in seen:
            raise ReplayAlignmentError("anchor_id must be non-empty and unique")
        seen.add(anchor_id)
        fields = {
            name: str(item.get(name, "")).strip()
            for name in ("evidence_class", "source_image", "source_claim", "source_note", "role")
        }
        if any(not value for value in fields.values()):
            raise ReplayAlignmentError(f"anchor {anchor_id} has incomplete provenance")
        anchors.append(
            SourcePriceAnchor(
                anchor_id=anchor_id,
                price=_decimal(item.get("price"), field=f"anchor {anchor_id} price"),
                evidence_class=fields["evidence_class"],
                source_image=fields["source_image"],
                source_claim=fields["source_claim"],
                source_note=fields["source_note"],
                role=fields["role"],
            )
        )
    return episode_id, source_locator, tuple(anchors)


def probe_replay_anchors(
    replay: VerifiedReplaySlice,
    anchors: tuple[SourcePriceAnchor, ...],
) -> tuple[AnchorProbeResult, ...]:
    states: dict[str, dict[str, Any]] = {
        anchor.anchor_id: {
            "touch_count": 0,
            "first_touch": None,
            "last_touch": None,
            "closest_distance": None,
            "closest_timestamp": None,
            "closest_low": None,
            "closest_high": None,
        }
        for anchor in anchors
    }

    with replay.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"timestamp", "open", "high", "low", "close"}
        missing = sorted(required - set(reader.fieldnames or ()))
        if missing:
            raise ReplayAlignmentError(f"replay CSV missing fields: {', '.join(missing)}")
        rows = 0
        for row_no, row in enumerate(reader, start=2):
            timestamp = _parse_timestamp(row["timestamp"], field=f"row {row_no} timestamp")
            low = _decimal(row["low"], field=f"row {row_no} low")
            high = _decimal(row["high"], field=f"row {row_no} high")
            if low > high:
                raise ReplayAlignmentError(f"row {row_no} has invalid low/high geometry")
            rows += 1
            for anchor in anchors:
                state = states[anchor.anchor_id]
                if low <= anchor.price <= high:
                    distance = Decimal("0")
                    state["touch_count"] += 1
                    if state["first_touch"] is None:
                        state["first_touch"] = timestamp
                    state["last_touch"] = timestamp
                elif anchor.price < low:
                    distance = low - anchor.price
                else:
                    distance = anchor.price - high

                current = state["closest_distance"]
                if current is None or distance < current:
                    state["closest_distance"] = distance
                    state["closest_timestamp"] = timestamp
                    state["closest_low"] = low
                    state["closest_high"] = high
        if rows != replay.bar_count:
            raise ReplayAlignmentError(
                f"replay CSV row count changed: manifest={replay.bar_count}, observed={rows}"
            )

    results: list[AnchorProbeResult] = []
    for anchor in anchors:
        state = states[anchor.anchor_id]
        if state["closest_distance"] is None or state["closest_timestamp"] is None:
            raise ReplayAlignmentError("anchor probe did not observe any replay bars")
        results.append(
            AnchorProbeResult(
                anchor_id=anchor.anchor_id,
                price=str(anchor.price),
                role=anchor.role,
                evidence_class=anchor.evidence_class,
                source_image=anchor.source_image,
                source_claim=anchor.source_claim,
                source_note=anchor.source_note,
                within_slice_price_range=replay.low_min <= anchor.price <= replay.high_max,
                touched=state["touch_count"] > 0,
                touch_bar_count=state["touch_count"],
                first_touch_timestamp_utc=(
                    _iso(state["first_touch"]) if state["first_touch"] is not None else None
                ),
                last_touch_timestamp_utc=(
                    _iso(state["last_touch"]) if state["last_touch"] is not None else None
                ),
                closest_distance=str(state["closest_distance"]),
                closest_timestamp_utc=_iso(state["closest_timestamp"]),
                closest_bar_low=str(state["closest_low"]),
                closest_bar_high=str(state["closest_high"]),
            )
        )
    return tuple(results)
