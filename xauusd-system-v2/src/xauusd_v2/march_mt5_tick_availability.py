from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol
from uuid import uuid4

from .mt5_snapshot_load import load_verified_persisted_mt5_snapshot


class MarchMT5TickAvailabilityError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class TickWindow:
    window_id: str
    parent_bar_open: datetime
    source_role: str

    @property
    def end(self) -> datetime:
        return self.parent_bar_open + timedelta(minutes=1)


MARCH_HCS_TICK_WINDOWS = (
    TickWindow(
        window_id="buy_1975_hcs_candidate_2023_03_30_1231",
        parent_bar_open=datetime(2023, 3, 30, 12, 31, tzinfo=UTC),
        source_role="easy_1m_hcs_reentry_1975",
    ),
    TickWindow(
        window_id="sell_1986_hcs_control_2023_03_31_1236",
        parent_bar_open=datetime(2023, 3, 31, 12, 36, tzinfo=UTC),
        source_role="clearest_1m_hcs_sell_entry_1986_control",
    ),
)


class MT5TickProvider(Protocol):
    COPY_TICKS_ALL: int

    def initialize(self) -> bool: ...
    def shutdown(self) -> Any: ...
    def last_error(self) -> Any: ...
    def symbol_info(self, symbol: str) -> Any: ...
    def terminal_info(self) -> Any: ...
    def account_info(self) -> Any: ...
    def copy_ticks_range(self, symbol: str, date_from: datetime, date_to: datetime, flags: int) -> Any: ...


def _canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _immutable_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not path.is_file() or path.read_bytes() != payload:
            raise MarchMT5TickAvailabilityError(f"immutable tick artifact collision or tampering detected: {path}")
        return

    temp = path.parent / f".{path.name}.{uuid4().hex}.tmp"
    try:
        with temp.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp, path)
        except FileExistsError:
            if not path.is_file() or path.read_bytes() != payload:
                raise MarchMT5TickAvailabilityError(
                    f"immutable tick artifact collision or tampering detected: {path}"
                )
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _value(item: Any, name: str) -> Any:
    if isinstance(item, Mapping):
        return item[name]
    try:
        return item[name]
    except (IndexError, KeyError, TypeError):
        return getattr(item, name)


def _field_names(ticks: Any) -> tuple[str, ...]:
    dtype = getattr(ticks, "dtype", None)
    names = getattr(dtype, "names", None)
    if names:
        return tuple(str(name) for name in names)
    if isinstance(ticks, list) and ticks and isinstance(ticks[0], Mapping):
        return tuple(str(name) for name in ticks[0].keys())
    return ()


def _normalize_tick_rows(
    ticks: Iterable[Any],
    *,
    field_names: tuple[str, ...],
    start: datetime,
    end: datetime,
) -> tuple[dict[str, object], ...]:
    if start.tzinfo is None or start.utcoffset() is None or end.tzinfo is None or end.utcoffset() is None:
        raise MarchMT5TickAvailabilityError("tick window timestamps must be timezone-aware")
    if start >= end:
        raise MarchMT5TickAvailabilityError("tick window must have positive duration")
    if "time_msc" not in field_names:
        raise MarchMT5TickAvailabilityError("MT5 tick payload must expose time_msc for sub-second ordering")

    required = {"bid", "ask", "last", "flags"}
    missing = sorted(required - set(field_names))
    if missing:
        raise MarchMT5TickAvailabilityError(f"MT5 tick payload missing required fields: {missing}")

    start_ms = int(start.astimezone(UTC).timestamp() * 1000)
    end_ms = int(end.astimezone(UTC).timestamp() * 1000)
    normalized: list[dict[str, object]] = []
    previous_msc: int | None = None

    for source_index, item in enumerate(ticks):
        time_msc = int(_value(item, "time_msc"))
        if time_msc < start_ms or time_msc >= end_ms:
            continue
        if previous_msc is not None and time_msc < previous_msc:
            raise MarchMT5TickAvailabilityError("MT5 ticks are not ordered by time_msc")
        previous_msc = time_msc

        row: dict[str, object] = {
            "sequence": len(normalized),
            "source_index": source_index,
            "time_msc": time_msc,
            "timestamp_utc": datetime.fromtimestamp(time_msc / 1000, tz=UTC).isoformat().replace("+00:00", "Z"),
            "bid": float(_value(item, "bid")),
            "ask": float(_value(item, "ask")),
            "last": float(_value(item, "last")),
            "flags": int(_value(item, "flags")),
        }
        if "volume" in field_names:
            row["volume"] = int(_value(item, "volume"))
        if "volume_real" in field_names:
            row["volume_real"] = float(_value(item, "volume_real"))
        normalized.append(row)

    return tuple(normalized)


def _tick_bytes(rows: tuple[dict[str, object], ...]) -> bytes:
    return b"".join(_canonical_json_bytes(row) for row in rows)


def _safe_attr(value: Any, name: str) -> object | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value.get(name)
    return getattr(value, name, None)


def acquire_march_mt5_tick_availability(
    ingestion_manifest: str | Path,
    *,
    provider: MT5TickProvider,
) -> dict[str, Any]:
    verified = load_verified_persisted_mt5_snapshot(ingestion_manifest)
    if verified.snapshot.timeframe_seconds != 60:
        raise MarchMT5TickAvailabilityError("March tick availability probe requires the governed M1 snapshot")

    broker_name = verified.snapshot.source_name
    broker_symbol = verified.snapshot.source_symbol
    if not broker_name.strip() or not broker_symbol.strip():
        raise MarchMT5TickAvailabilityError("verified MT5 snapshot provenance is incomplete")

    if not provider.initialize():
        return {
            "status": "MT5_TICK_API_INITIALIZE_FAILED_NOT_CERTIFIED",
            "broker_name": broker_name,
            "broker_symbol": broker_symbol,
            "normalized_sha256": verified.normalized_sha256,
            "snapshot_id": verified.snapshot.snapshot_id,
            "mt5_last_error": repr(provider.last_error()),
            "tick_windows": [],
            "tick_path_evidence_available": False,
            "marked_liquidity_reference_certified": False,
            "fu_criteria_certified": False,
            "semantic_stage_certification": False,
            "strategy_truth_changed": False,
            "performance_claim_allowed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
        }

    try:
        symbol_info = provider.symbol_info(broker_symbol)
        if symbol_info is None:
            raise MarchMT5TickAvailabilityError(
                f"verified broker symbol is unavailable in the connected MT5 terminal: {broker_symbol}"
            )

        terminal = provider.terminal_info()
        account = provider.account_info()
        windows: list[dict[str, Any]] = []

        for spec in MARCH_HCS_TICK_WINDOWS:
            raw_ticks = provider.copy_ticks_range(
                broker_symbol,
                spec.parent_bar_open,
                spec.end,
                provider.COPY_TICKS_ALL,
            )
            if raw_ticks is None:
                windows.append(
                    {
                        "window_id": spec.window_id,
                        "source_role": spec.source_role,
                        "start_utc": spec.parent_bar_open.isoformat().replace("+00:00", "Z"),
                        "end_utc_exclusive": spec.end.isoformat().replace("+00:00", "Z"),
                        "status": "MT5_TICK_RANGE_REQUEST_FAILED",
                        "mt5_last_error": repr(provider.last_error()),
                        "tick_count": 0,
                        "first_tick_utc": None,
                        "last_tick_utc": None,
                        "ticks_sha256": None,
                        "ticks_bytes": None,
                    }
                )
                continue

            if len(raw_ticks) == 0:
                windows.append(
                    {
                        "window_id": spec.window_id,
                        "source_role": spec.source_role,
                        "start_utc": spec.parent_bar_open.isoformat().replace("+00:00", "Z"),
                        "end_utc_exclusive": spec.end.isoformat().replace("+00:00", "Z"),
                        "status": "MT5_TICKS_UNAVAILABLE_FOR_RANGE",
                        "mt5_last_error": repr(provider.last_error()),
                        "tick_count": 0,
                        "first_tick_utc": None,
                        "last_tick_utc": None,
                        "ticks_sha256": None,
                        "ticks_bytes": None,
                    }
                )
                continue

            names = _field_names(raw_ticks)
            rows = _normalize_tick_rows(
                raw_ticks,
                field_names=names,
                start=spec.parent_bar_open,
                end=spec.end,
            )
            if not rows:
                windows.append(
                    {
                        "window_id": spec.window_id,
                        "source_role": spec.source_role,
                        "start_utc": spec.parent_bar_open.isoformat().replace("+00:00", "Z"),
                        "end_utc_exclusive": spec.end.isoformat().replace("+00:00", "Z"),
                        "status": "MT5_RETURNED_NO_TICKS_INSIDE_HALF_OPEN_RANGE",
                        "mt5_last_error": repr(provider.last_error()),
                        "tick_count": 0,
                        "first_tick_utc": None,
                        "last_tick_utc": None,
                        "ticks_sha256": None,
                        "ticks_bytes": None,
                    }
                )
                continue

            payload = _tick_bytes(rows)
            digest = hashlib.sha256(payload).hexdigest()
            windows.append(
                {
                    "window_id": spec.window_id,
                    "source_role": spec.source_role,
                    "start_utc": spec.parent_bar_open.isoformat().replace("+00:00", "Z"),
                    "end_utc_exclusive": spec.end.isoformat().replace("+00:00", "Z"),
                    "status": "MT5_TICKS_AVAILABLE",
                    "mt5_last_error": None,
                    "tick_count": len(rows),
                    "first_tick_utc": rows[0]["timestamp_utc"],
                    "last_tick_utc": rows[-1]["timestamp_utc"],
                    "ticks_sha256": digest,
                    "ticks_bytes": payload,
                }
            )

        available_count = sum(item["status"] == "MT5_TICKS_AVAILABLE" for item in windows)
        return {
            "status": (
                "MARCH_MT5_TICKS_AVAILABLE_NOT_CERTIFIED"
                if available_count == len(MARCH_HCS_TICK_WINDOWS)
                else "MARCH_MT5_TICK_AVAILABILITY_PARTIAL_OR_UNAVAILABLE_NOT_CERTIFIED"
            ),
            "broker_name": broker_name,
            "broker_symbol": broker_symbol,
            "canonical_symbol": "XAUUSD",
            "normalized_sha256": verified.normalized_sha256,
            "snapshot_id": verified.snapshot.snapshot_id,
            "terminal_name": _safe_attr(terminal, "name"),
            "terminal_company": _safe_attr(terminal, "company"),
            "account_server": _safe_attr(account, "server"),
            "requested_window_count": len(MARCH_HCS_TICK_WINDOWS),
            "available_window_count": available_count,
            "tick_path_evidence_available": available_count > 0,
            "tick_windows": windows,
            "marked_liquidity_reference_certified": False,
            "fu_criteria_certified": False,
            "semantic_stage_certification": False,
            "strategy_truth_changed": False,
            "performance_claim_allowed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
        }
    finally:
        provider.shutdown()


def persist_march_mt5_tick_availability(
    report: dict[str, Any],
    *,
    store_root: str | Path,
) -> dict[str, Any]:
    root = Path(store_root).expanduser()
    persisted_windows: list[dict[str, Any]] = []

    for item in report["tick_windows"]:
        clean = dict(item)
        payload = clean.pop("ticks_bytes", None)
        digest = clean.get("ticks_sha256")
        if payload is not None:
            if not isinstance(payload, bytes) or not digest:
                raise MarchMT5TickAvailabilityError("tick bytes/digest invariant violated")
            if hashlib.sha256(payload).hexdigest() != digest:
                raise MarchMT5TickAvailabilityError("tick payload hash mismatch before persistence")
            tick_path = root / "ticks" / digest / "ticks.jsonl"
            _immutable_write(tick_path, payload)
            clean["ticks_path"] = str(tick_path)
        else:
            clean["ticks_path"] = None
        persisted_windows.append(clean)

    clean_report = {key: value for key, value in report.items() if key != "tick_windows"}
    clean_report["tick_windows"] = persisted_windows
    report_bytes = _canonical_json_bytes(clean_report)
    report_sha = hashlib.sha256(report_bytes).hexdigest()
    report_root = root / "research-bundles" / "march-2023-mt5-tick-availability" / report_sha
    report_path = report_root / "report.json"
    _immutable_write(report_path, report_bytes)

    result = dict(clean_report)
    result["report_sha256"] = report_sha
    result["report_root"] = str(report_root)
    result["report_path"] = str(report_path)
    return result
