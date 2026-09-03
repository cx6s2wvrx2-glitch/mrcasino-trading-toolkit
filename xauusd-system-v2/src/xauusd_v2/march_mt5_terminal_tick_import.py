from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import uuid4

from .march_mt5_tick_availability import MARCH_HCS_TICK_WINDOWS
from .mt5_snapshot_load import load_verified_persisted_mt5_snapshot


class MarchMT5TerminalTickImportError(ValueError):
    pass


_SCHEMA_VERSION = "xauusd_v2_mt5_terminal_tick_export_v1"
_EXPECTED_HEADER = (
    "schema_version",
    "record_type",
    "window_id",
    "broker_symbol",
    "start_msc",
    "end_msc_inclusive",
    "copy_result",
    "last_error",
    "source_index",
    "time_msc",
    "bid",
    "ask",
    "last",
    "volume",
    "flags",
    "volume_real",
)


@dataclass(frozen=True, slots=True)
class _WindowContract:
    window_id: str
    source_role: str
    start_msc: int
    end_msc_inclusive: int


_WINDOW_CONTRACTS = tuple(
    _WindowContract(
        window_id=spec.window_id,
        source_role=spec.source_role,
        start_msc=int(spec.parent_bar_open.astimezone(UTC).timestamp() * 1000),
        end_msc_inclusive=int(spec.end.astimezone(UTC).timestamp() * 1000) - 1,
    )
    for spec in MARCH_HCS_TICK_WINDOWS
)
_WINDOW_BY_ID = {item.window_id: item for item in _WINDOW_CONTRACTS}


def _canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _immutable_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not path.is_file() or path.read_bytes() != payload:
            raise MarchMT5TerminalTickImportError(
                f"immutable terminal tick artifact collision or tampering detected: {path}"
            )
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
                raise MarchMT5TerminalTickImportError(
                    f"immutable terminal tick artifact collision or tampering detected: {path}"
                )
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _int_field(value: str | None, *, field: str, row_number: int, allow_negative_one: bool = False) -> int:
    text = "" if value is None else value.strip()
    if not text:
        raise MarchMT5TerminalTickImportError(f"row {row_number}: {field} is required")
    try:
        parsed = int(text)
    except ValueError as exc:
        raise MarchMT5TerminalTickImportError(f"row {row_number}: invalid {field}") from exc
    minimum = -1 if allow_negative_one else 0
    if parsed < minimum:
        raise MarchMT5TerminalTickImportError(f"row {row_number}: {field} is below allowed minimum")
    return parsed


def _decimal_text(value: str | None, *, field: str, row_number: int) -> str:
    text = "" if value is None else value.strip()
    if not text:
        raise MarchMT5TerminalTickImportError(f"row {row_number}: {field} is required")
    try:
        parsed = Decimal(text)
    except InvalidOperation as exc:
        raise MarchMT5TerminalTickImportError(f"row {row_number}: invalid {field}") from exc
    if not parsed.is_finite() or parsed < 0:
        raise MarchMT5TerminalTickImportError(f"row {row_number}: {field} must be finite and non-negative")
    return text


def _timestamp_utc(time_msc: int) -> str:
    seconds, milliseconds = divmod(time_msc, 1000)
    base = datetime.fromtimestamp(seconds, tz=UTC)
    return f"{base:%Y-%m-%dT%H:%M:%S}.{milliseconds:03d}Z"


def _tick_bytes(rows: list[dict[str, object]]) -> bytes:
    return b"".join(_canonical_json_bytes(row) for row in rows)


def _blank_only(row: dict[str, str | None], fields: tuple[str, ...], *, row_number: int) -> None:
    nonblank = [field for field in fields if (row.get(field) or "").strip()]
    if nonblank:
        raise MarchMT5TerminalTickImportError(
            f"row {row_number}: fields must be blank for this record type: {nonblank}"
        )


def build_march_mt5_terminal_tick_import_report(
    raw_export_bytes: bytes,
    *,
    broker_name: str,
    broker_symbol: str,
    normalized_sha256: str,
    snapshot_id: str,
) -> dict[str, Any]:
    if not raw_export_bytes:
        raise MarchMT5TerminalTickImportError("MT5 terminal tick export is empty")
    try:
        text = raw_export_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise MarchMT5TerminalTickImportError("MT5 terminal tick export must be UTF-8/ASCII CSV") from exc

    reader = csv.DictReader(io.StringIO(text), delimiter=",")
    header = tuple(reader.fieldnames or ())
    if header != _EXPECTED_HEADER:
        raise MarchMT5TerminalTickImportError(
            f"MT5 terminal tick export header mismatch; observed={header}"
        )

    statuses: dict[str, dict[str, int]] = {}
    ticks_by_window: dict[str, list[dict[str, object]]] = {
        contract.window_id: [] for contract in _WINDOW_CONTRACTS
    }

    for row_number, row in enumerate(reader, start=2):
        if row.get("schema_version") != _SCHEMA_VERSION:
            raise MarchMT5TerminalTickImportError(f"row {row_number}: unsupported schema_version")

        window_id = (row.get("window_id") or "").strip()
        contract = _WINDOW_BY_ID.get(window_id)
        if contract is None:
            raise MarchMT5TerminalTickImportError(f"row {row_number}: unexpected window_id {window_id!r}")
        if (row.get("broker_symbol") or "").strip() != broker_symbol:
            raise MarchMT5TerminalTickImportError(
                f"row {row_number}: broker_symbol disagrees with verified MT5 snapshot"
            )

        start_msc = _int_field(row.get("start_msc"), field="start_msc", row_number=row_number)
        end_msc = _int_field(
            row.get("end_msc_inclusive"), field="end_msc_inclusive", row_number=row_number
        )
        if start_msc != contract.start_msc or end_msc != contract.end_msc_inclusive:
            raise MarchMT5TerminalTickImportError(
                f"row {row_number}: tick window bounds disagree with governed March contract"
            )

        record_type = (row.get("record_type") or "").strip()
        if record_type == "status":
            if window_id in statuses:
                raise MarchMT5TerminalTickImportError(
                    f"row {row_number}: duplicate status record for {window_id}"
                )
            copied = _int_field(
                row.get("copy_result"),
                field="copy_result",
                row_number=row_number,
                allow_negative_one=True,
            )
            last_error = _int_field(row.get("last_error"), field="last_error", row_number=row_number)
            _blank_only(
                row,
                ("source_index", "time_msc", "bid", "ask", "last", "volume", "flags", "volume_real"),
                row_number=row_number,
            )
            statuses[window_id] = {"copy_result": copied, "last_error": last_error}
            continue

        if record_type != "tick":
            raise MarchMT5TerminalTickImportError(f"row {row_number}: unexpected record_type")
        if window_id not in statuses:
            raise MarchMT5TerminalTickImportError(
                f"row {row_number}: tick record appeared before its status record"
            )
        _blank_only(row, ("copy_result", "last_error"), row_number=row_number)

        source_index = _int_field(row.get("source_index"), field="source_index", row_number=row_number)
        expected_index = len(ticks_by_window[window_id])
        if source_index != expected_index:
            raise MarchMT5TerminalTickImportError(
                f"row {row_number}: source_index must be contiguous from zero"
            )
        time_msc = _int_field(row.get("time_msc"), field="time_msc", row_number=row_number)
        if time_msc < contract.start_msc or time_msc > contract.end_msc_inclusive:
            raise MarchMT5TerminalTickImportError(f"row {row_number}: tick falls outside governed window")
        if ticks_by_window[window_id] and time_msc < int(ticks_by_window[window_id][-1]["time_msc"]):
            raise MarchMT5TerminalTickImportError(
                f"row {row_number}: tick timestamps are not ordered by time_msc"
            )

        bid = _decimal_text(row.get("bid"), field="bid", row_number=row_number)
        ask = _decimal_text(row.get("ask"), field="ask", row_number=row_number)
        last = _decimal_text(row.get("last"), field="last", row_number=row_number)
        volume = _int_field(row.get("volume"), field="volume", row_number=row_number)
        flags = _int_field(row.get("flags"), field="flags", row_number=row_number)
        volume_real = _decimal_text(row.get("volume_real"), field="volume_real", row_number=row_number)

        ticks_by_window[window_id].append(
            {
                "sequence": source_index,
                "source_index": source_index,
                "time_msc": time_msc,
                "timestamp_utc": _timestamp_utc(time_msc),
                "bid": bid,
                "ask": ask,
                "last": last,
                "volume": volume,
                "flags": flags,
                "volume_real": volume_real,
            }
        )

    expected_ids = set(_WINDOW_BY_ID)
    if set(statuses) != expected_ids:
        missing = sorted(expected_ids - set(statuses))
        raise MarchMT5TerminalTickImportError(
            f"MT5 terminal tick export is missing governed status records: {missing}"
        )

    windows: list[dict[str, Any]] = []
    available_count = 0
    for contract in _WINDOW_CONTRACTS:
        status = statuses[contract.window_id]
        rows = ticks_by_window[contract.window_id]
        copied = status["copy_result"]
        if copied > 0 and len(rows) != copied:
            raise MarchMT5TerminalTickImportError(
                f"{contract.window_id}: copy_result={copied} but tick rows={len(rows)}"
            )
        if copied <= 0 and rows:
            raise MarchMT5TerminalTickImportError(
                f"{contract.window_id}: tick rows exist despite non-positive copy_result"
            )

        payload = _tick_bytes(rows)
        digest = hashlib.sha256(payload).hexdigest() if rows else None
        if copied == -1:
            window_status = "MT5_TERMINAL_TICK_RANGE_REQUEST_FAILED"
        elif copied == 0:
            window_status = "MT5_TERMINAL_TICKS_UNAVAILABLE_FOR_RANGE"
        else:
            window_status = "MT5_TERMINAL_TICKS_AVAILABLE"
            available_count += 1

        windows.append(
            {
                "window_id": contract.window_id,
                "source_role": contract.source_role,
                "start_msc": contract.start_msc,
                "end_msc_inclusive": contract.end_msc_inclusive,
                "status": window_status,
                "copy_result": copied,
                "mt5_last_error": status["last_error"],
                "tick_count": len(rows),
                "first_tick_utc": rows[0]["timestamp_utc"] if rows else None,
                "last_tick_utc": rows[-1]["timestamp_utc"] if rows else None,
                "ticks_sha256": digest,
                "ticks_bytes": payload if rows else None,
            }
        )

    return {
        "status": (
            "MARCH_MT5_TERMINAL_TICKS_IMPORTED_NOT_CERTIFIED"
            if available_count == len(_WINDOW_CONTRACTS)
            else "MARCH_MT5_TERMINAL_TICK_IMPORT_PARTIAL_OR_UNAVAILABLE_NOT_CERTIFIED"
        ),
        "source_kind": "MT5_TERMINAL_NATIVE_COPYTICKSRANGE",
        "broker_name": broker_name,
        "broker_symbol": broker_symbol,
        "canonical_symbol": "XAUUSD",
        "normalized_sha256": normalized_sha256,
        "snapshot_id": snapshot_id,
        "raw_export_sha256": hashlib.sha256(raw_export_bytes).hexdigest(),
        "requested_window_count": len(_WINDOW_CONTRACTS),
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


def persist_march_mt5_terminal_tick_import(
    report: dict[str, Any],
    *,
    raw_export_bytes: bytes,
    store_root: str | Path,
) -> dict[str, Any]:
    root = Path(store_root).expanduser()
    observed_raw_sha = hashlib.sha256(raw_export_bytes).hexdigest()
    if observed_raw_sha != report.get("raw_export_sha256"):
        raise MarchMT5TerminalTickImportError("raw terminal export hash disagrees with report")

    raw_path = root / "raw-terminal-tick-exports" / observed_raw_sha / "xauusd_v2_march_hcs_ticks.csv"
    _immutable_write(raw_path, raw_export_bytes)

    persisted_windows: list[dict[str, Any]] = []
    for item in report["tick_windows"]:
        clean = dict(item)
        payload = clean.pop("ticks_bytes", None)
        digest = clean.get("ticks_sha256")
        if payload is not None:
            if not isinstance(payload, bytes) or not digest:
                raise MarchMT5TerminalTickImportError("tick bytes/digest invariant violated")
            if hashlib.sha256(payload).hexdigest() != digest:
                raise MarchMT5TerminalTickImportError("normalized tick payload hash mismatch")
            tick_path = root / "ticks" / str(digest) / "ticks.jsonl"
            _immutable_write(tick_path, payload)
            clean["ticks_path"] = str(tick_path)
        else:
            clean["ticks_path"] = None
        persisted_windows.append(clean)

    clean_report = {key: value for key, value in report.items() if key != "tick_windows"}
    clean_report["raw_export_path"] = str(raw_path)
    clean_report["tick_windows"] = persisted_windows
    report_bytes = _canonical_json_bytes(clean_report)
    report_sha = hashlib.sha256(report_bytes).hexdigest()
    report_root = root / "research-bundles" / "march-2023-mt5-terminal-tick-import" / report_sha
    report_path = report_root / "report.json"
    _immutable_write(report_path, report_bytes)

    clean_report["report_sha256"] = report_sha
    clean_report["report_root"] = str(report_root)
    clean_report["report_path"] = str(report_path)
    return clean_report


def import_march_mt5_terminal_tick_export(
    ingestion_manifest: str | Path,
    terminal_export: str | Path,
    *,
    store_root: str | Path,
) -> dict[str, Any]:
    verified = load_verified_persisted_mt5_snapshot(ingestion_manifest)
    if verified.snapshot.timeframe_seconds != 60:
        raise MarchMT5TerminalTickImportError("terminal tick import requires governed M1 snapshot")

    export_path = Path(terminal_export).expanduser()
    try:
        raw_export = export_path.read_bytes()
    except OSError as exc:
        raise MarchMT5TerminalTickImportError("MT5 terminal tick export file is unavailable") from exc

    report = build_march_mt5_terminal_tick_import_report(
        raw_export,
        broker_name=verified.snapshot.source_name,
        broker_symbol=verified.snapshot.source_symbol,
        normalized_sha256=verified.normalized_sha256,
        snapshot_id=verified.snapshot.snapshot_id,
    )
    return persist_march_mt5_terminal_tick_import(
        report,
        raw_export_bytes=raw_export,
        store_root=store_root,
    )
