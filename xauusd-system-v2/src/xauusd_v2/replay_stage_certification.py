from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .backtest_sequence import BacktestStage
from .component_replay import TimedStageConfirmation
from .data_snapshot import load_xauusd_csv_snapshot_bytes
from .mt5_snapshot_load import VerifiedPersistedMT5Snapshot
from .replay_candidate_registry import ReplayCandidate, ReplayCandidateState
from .source_chart_alignment import SourceChartAlignmentResult, SourceChartAlignmentState


class ReplayStageCertificationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class VerifiedReplayStageCertification:
    artifact_path: Path
    artifact_sha256: str
    candidate_id: str
    source_id: str
    source_locator: str
    snapshot_id: str
    normalized_sha256: str
    broker_name: str
    broker_symbol: str
    timeframe_seconds: int
    confirmations: tuple[TimedStageConfirmation, ...]
    stage_timestamps_certified: bool = True
    promotion_allowed: bool = False
    strategy_verified: bool = False
    performance_claim_allowed: bool = False
    schema_version: str = "r143_stage_timestamp_certification_v1"


_TOP_LEVEL_KEYS = {
    "schema_version",
    "candidate_id",
    "source_id",
    "source_locator",
    "snapshot_id",
    "normalized_sha256",
    "broker_name",
    "broker_symbol",
    "canonical_symbol",
    "timeframe_seconds",
    "stages",
    "promotion_allowed",
    "strategy_verified",
    "performance_claim_allowed",
}
_STAGE_KEYS = {
    "stage",
    "occurred_at",
    "available_at",
    "broker_bar_open",
    "source_ref",
    "evidence_kind",
}
_ALLOWED_EVIDENCE_KIND = "primary_source_label_aligned_to_closed_broker_bar"


def _require_exact_keys(value: object, expected: set[str], *, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReplayStageCertificationError(f"{field} must be an object")
    observed = set(value)
    if observed != expected:
        raise ReplayStageCertificationError(
            f"{field} schema mismatch; missing={sorted(expected - observed)}, extra={sorted(observed - expected)}"
        )
    return value


def _aware_datetime(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ReplayStageCertificationError(f"{field} must be an ISO-8601 timestamp")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ReplayStageCertificationError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ReplayStageCertificationError(f"{field} must be timezone-aware")
    return parsed


def _sha256_hex(value: object, *, field: str) -> str:
    text = str(value or "").strip().lower()
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise ReplayStageCertificationError(f"{field} must be a SHA-256 hex digest")
    return text


def _positive_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ReplayStageCertificationError(f"{field} must be a positive integer")
    return value


def _stage_from_name(value: object, *, field: str) -> BacktestStage:
    text = str(value or "").strip()
    try:
        return BacktestStage[text]
    except KeyError as exc:
        raise ReplayStageCertificationError(f"{field} is not a canonical R-143 stage") from exc


def load_verified_replay_stage_certification(
    path: str | Path,
    *,
    candidate: ReplayCandidate,
    snapshot: VerifiedPersistedMT5Snapshot,
    alignment: SourceChartAlignmentResult,
) -> VerifiedReplayStageCertification:
    """Verify a stage-timestamp evidence artifact against immutable broker data.

    The input file cannot assert ``certified=true``. Admissibility is derived here from
    exact candidate provenance, the already-verified content-addressed MT5 snapshot,
    closed broker bars, all six canonical R-143 stages, and lookahead-safe timestamps.

    This verifies the timestamp/evidence mapping contract only. It does not prove that
    an analyst's semantic stage label is strategy truth and never promotes a rule.
    """

    artifact_path = Path(path).expanduser().resolve()
    if not artifact_path.is_file():
        raise ReplayStageCertificationError("stage certification artifact is unavailable")
    try:
        raw_bytes = artifact_path.read_bytes()
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReplayStageCertificationError("stage certification artifact is not valid UTF-8 JSON") from exc

    item = _require_exact_keys(raw, _TOP_LEVEL_KEYS, field="artifact")
    if item["schema_version"] != "r143_stage_timestamp_certification_v1":
        raise ReplayStageCertificationError("unsupported stage certification schema_version")
    if candidate.state is ReplayCandidateState.CONTEXT_ONLY:
        raise ReplayStageCertificationError("context-only replay candidate cannot receive stage timestamp certification")
    if alignment.state is not SourceChartAlignmentState.ALIGNED_CANDIDATE or not alignment.aligned:
        raise ReplayStageCertificationError("stage certification requires an already-aligned source chart")
    if alignment.source_id != candidate.source_id or alignment.source_locator != candidate.locator:
        raise ReplayStageCertificationError("alignment provenance does not match replay candidate")
    if alignment.snapshot_id != snapshot.snapshot.snapshot_id:
        raise ReplayStageCertificationError("alignment snapshot identity does not match verified MT5 snapshot")

    candidate_id = str(item["candidate_id"]).strip()
    source_id = str(item["source_id"]).strip()
    source_locator = str(item["source_locator"]).strip()
    snapshot_id = str(item["snapshot_id"]).strip()
    normalized_sha = _sha256_hex(item["normalized_sha256"], field="normalized_sha256")
    broker_name = str(item["broker_name"]).strip()
    broker_symbol = str(item["broker_symbol"]).strip()
    canonical_symbol = str(item["canonical_symbol"]).strip().upper()
    timeframe_seconds = _positive_int(item["timeframe_seconds"], field="timeframe_seconds")

    if candidate_id != candidate.candidate_id:
        raise ReplayStageCertificationError("artifact candidate_id does not match replay candidate")
    if source_id != candidate.source_id or source_locator != candidate.locator:
        raise ReplayStageCertificationError("artifact source provenance does not match replay candidate")
    if snapshot_id != snapshot.snapshot.snapshot_id:
        raise ReplayStageCertificationError("artifact snapshot_id does not match verified MT5 snapshot")
    if normalized_sha != snapshot.normalized_sha256 or normalized_sha != snapshot.snapshot.sha256:
        raise ReplayStageCertificationError("artifact normalized SHA-256 does not match verified MT5 snapshot")
    if canonical_symbol != "XAUUSD":
        raise ReplayStageCertificationError("stage certification accepts canonical XAUUSD only")
    if not broker_name or broker_name.casefold() != snapshot.snapshot.source_name.casefold():
        raise ReplayStageCertificationError("artifact broker_name does not match verified MT5 snapshot")
    if not broker_symbol or broker_symbol.casefold() != snapshot.snapshot.source_symbol.casefold():
        raise ReplayStageCertificationError("artifact broker_symbol does not match verified MT5 snapshot")
    if timeframe_seconds != snapshot.snapshot.timeframe_seconds:
        raise ReplayStageCertificationError("artifact timeframe does not match verified MT5 snapshot")
    if not snapshot.snapshot.closed_only:
        raise ReplayStageCertificationError("stage certification requires a closed-only MT5 snapshot")

    if item["promotion_allowed"] is not False:
        raise ReplayStageCertificationError("stage certification must never allow promotion")
    if item["strategy_verified"] is not False:
        raise ReplayStageCertificationError("stage certification cannot claim strategy verification")
    if item["performance_claim_allowed"] is not False:
        raise ReplayStageCertificationError("stage certification cannot allow performance claims")

    # Reload the canonical bytes so every broker_bar_open can be tied to a real closed
    # bar in the exact content-addressed snapshot rather than to a timestamp asserted
    # by the certification file.
    try:
        bars, reproduced, _ = load_xauusd_csv_snapshot_bytes(
            snapshot.canonical_snapshot_path.read_bytes(),
            source_name=snapshot.snapshot.source_name,
            source_symbol=snapshot.snapshot.source_symbol,
            timeframe_seconds=snapshot.snapshot.timeframe_seconds,
            evaluation_time=snapshot.snapshot.coverage_end,
            source_file_name=snapshot.snapshot.source_file_name,
        )
    except (OSError, ValueError) as exc:
        raise ReplayStageCertificationError("verified MT5 snapshot could not be reproduced for stage certification") from exc
    if reproduced != snapshot.snapshot:
        raise ReplayStageCertificationError("reloaded MT5 snapshot metadata changed during stage certification")
    bars_by_open = {bar.timestamp: bar for bar in bars if bar.is_closed}

    stages_raw = item["stages"]
    if not isinstance(stages_raw, list):
        raise ReplayStageCertificationError("stages must be an array")
    expected_stages = tuple(BacktestStage)
    if len(stages_raw) != len(expected_stages):
        raise ReplayStageCertificationError("stage certification requires exactly all six R-143 stages")

    confirmations: list[TimedStageConfirmation] = []
    broker_opens: list[datetime] = []
    for index, raw_stage in enumerate(stages_raw):
        stage_item = _require_exact_keys(raw_stage, _STAGE_KEYS, field=f"stages[{index}]")
        stage = _stage_from_name(stage_item["stage"], field=f"stages[{index}].stage")
        expected_stage = expected_stages[index]
        if stage is not expected_stage:
            raise ReplayStageCertificationError(
                f"stages must appear exactly in canonical R-143 order; expected {expected_stage.name} at index {index}"
            )
        occurred_at = _aware_datetime(stage_item["occurred_at"], field=f"stages[{index}].occurred_at")
        available_at = _aware_datetime(stage_item["available_at"], field=f"stages[{index}].available_at")
        broker_bar_open = _aware_datetime(stage_item["broker_bar_open"], field=f"stages[{index}].broker_bar_open")
        source_ref = str(stage_item["source_ref"]).strip()
        evidence_kind = str(stage_item["evidence_kind"]).strip()
        if not source_ref:
            raise ReplayStageCertificationError(f"stages[{index}].source_ref is required")
        if evidence_kind != _ALLOWED_EVIDENCE_KIND:
            raise ReplayStageCertificationError(f"stages[{index}].evidence_kind is not admissible")

        bar = bars_by_open.get(broker_bar_open)
        if bar is None:
            raise ReplayStageCertificationError(
                f"stages[{index}].broker_bar_open does not identify a real closed bar in the verified snapshot"
            )
        bar_close = broker_bar_open + timedelta(seconds=timeframe_seconds)
        if occurred_at < broker_bar_open or occurred_at > bar_close:
            raise ReplayStageCertificationError(
                f"stages[{index}].occurred_at is outside the referenced broker bar"
            )
        if available_at < occurred_at:
            raise ReplayStageCertificationError(
                f"stages[{index}].available_at cannot precede occurred_at"
            )
        # Conservative historical rule: evidence anchored to a candle is not usable
        # before that exact broker candle has closed.
        if available_at < bar_close:
            raise ReplayStageCertificationError(
                f"stages[{index}].available_at precedes the referenced broker bar close"
            )
        if available_at > snapshot.snapshot.coverage_end:
            raise ReplayStageCertificationError(
                f"stages[{index}].available_at lies outside verified snapshot coverage"
            )

        confirmations.append(
            TimedStageConfirmation(
                stage=stage,
                occurred_at=occurred_at,
                available_at=available_at,
                source_ref=source_ref,
            )
        )
        broker_opens.append(broker_bar_open)

    for previous, current in zip(confirmations, confirmations[1:]):
        if current.occurred_at < previous.occurred_at:
            raise ReplayStageCertificationError("R-143 occurred_at timestamps are out of canonical stage order")
        if current.available_at < previous.available_at:
            raise ReplayStageCertificationError("R-143 available_at timestamps are out of canonical stage order")
    for previous, current in zip(broker_opens, broker_opens[1:]):
        if current < previous:
            raise ReplayStageCertificationError("R-143 broker bar references are out of canonical stage order")

    artifact_sha = hashlib.sha256(raw_bytes).hexdigest()
    return VerifiedReplayStageCertification(
        artifact_path=artifact_path,
        artifact_sha256=artifact_sha,
        candidate_id=candidate_id,
        source_id=source_id,
        source_locator=source_locator,
        snapshot_id=snapshot_id,
        normalized_sha256=normalized_sha,
        broker_name=broker_name,
        broker_symbol=broker_symbol,
        timeframe_seconds=timeframe_seconds,
        confirmations=tuple(confirmations),
    )
