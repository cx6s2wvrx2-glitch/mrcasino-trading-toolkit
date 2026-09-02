from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .backtest_sequence import BacktestStage
from .component_replay import ComponentReplayResult, TimedStageConfirmation, replay_r143_at


_STAGE_NAMES: dict[str, BacktestStage] = {
    "HCS_ZONE_REACTION": BacktestStage.HCS_ZONE_REACTION,
    "TFS": BacktestStage.TFS,
    "LAOL_MET": BacktestStage.LAOL_MET,
    "TRUE_STOP_RESPECTED": BacktestStage.TRUE_STOP_RESPECTED,
    "TEN_MIN_TRUE_STOP_ESTABLISHED": BacktestStage.TEN_MIN_TRUE_STOP_ESTABLISHED,
    "TARGETS_AND_TIMING": BacktestStage.TARGETS_AND_TIMING,
}
_DATASET_KEYS = {"dataset", "status", "promotion_allowed", "sessions"}
_SESSION_KEYS = {"session_id", "source_ref", "evaluation_time", "confirmations"}
_CONFIRMATION_KEYS = {"stage", "occurred_at", "available_at", "source_ref"}


@dataclass(frozen=True, slots=True)
class HistoricalReplaySession:
    session_id: str
    source_ref: str
    evaluation_time: datetime
    confirmations: tuple[TimedStageConfirmation, ...]

    def replay(self) -> ComponentReplayResult:
        return replay_r143_at(self.confirmations, evaluation_time=self.evaluation_time)


@dataclass(frozen=True, slots=True)
class HistoricalReplayDataset:
    name: str
    status: str
    promotion_allowed: bool
    sessions: tuple[HistoricalReplaySession, ...]


def _require_exact_keys(mapping: object, expected: set[str], *, field: str) -> dict[str, object]:
    if not isinstance(mapping, dict):
        raise ValueError(f"{field} must be a JSON object")
    observed = set(mapping)
    if observed != expected:
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        raise ValueError(f"{field} schema mismatch; missing={missing}, extra={extra}")
    return mapping


def load_historical_replay_dataset(path: str | Path) -> HistoricalReplayDataset:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    root = _require_exact_keys(payload, _DATASET_KEYS, field="historical replay dataset")

    name = _required_text(root, "dataset")
    status = _required_text(root, "status")
    promotion_allowed = root.get("promotion_allowed")
    if not isinstance(promotion_allowed, bool):
        raise ValueError("promotion_allowed must be boolean")
    if promotion_allowed:
        raise ValueError("historical replay datasets must keep promotion_allowed=false")

    raw_sessions = root.get("sessions")
    if not isinstance(raw_sessions, list) or not raw_sessions:
        raise ValueError("historical replay dataset must contain at least one session")

    sessions: list[HistoricalReplaySession] = []
    seen_session_ids: set[str] = set()
    for raw_session in raw_sessions:
        raw = _require_exact_keys(raw_session, _SESSION_KEYS, field="replay session")
        session_id = _required_text(raw, "session_id")
        if session_id in seen_session_ids:
            raise ValueError(f"duplicate session_id: {session_id}")
        seen_session_ids.add(session_id)

        source_ref = _required_text(raw, "source_ref")
        evaluation_time = _parse_time(_required_text(raw, "evaluation_time"), "evaluation_time")

        raw_confirmations = raw.get("confirmations")
        if not isinstance(raw_confirmations, list):
            raise ValueError(f"session {session_id} confirmations must be a list")

        confirmations: list[TimedStageConfirmation] = []
        seen_stages: set[BacktestStage] = set()
        for raw_event in raw_confirmations:
            event = _require_exact_keys(
                raw_event,
                _CONFIRMATION_KEYS,
                field=f"session {session_id} confirmation",
            )
            stage_name = _required_text(event, "stage")
            try:
                stage = _STAGE_NAMES[stage_name]
            except KeyError as exc:
                raise ValueError(f"unknown R-143 stage: {stage_name}") from exc
            if stage in seen_stages:
                raise ValueError(f"session {session_id} duplicates stage {stage_name}")
            seen_stages.add(stage)

            confirmation = TimedStageConfirmation(
                stage=stage,
                occurred_at=_parse_time(_required_text(event, "occurred_at"), "occurred_at"),
                available_at=_parse_time(_required_text(event, "available_at"), "available_at"),
                source_ref=_required_text(event, "source_ref"),
            )
            confirmations.append(confirmation)

        sessions.append(
            HistoricalReplaySession(
                session_id=session_id,
                source_ref=source_ref,
                evaluation_time=evaluation_time,
                confirmations=tuple(confirmations),
            )
        )

    return HistoricalReplayDataset(
        name=name,
        status=status,
        promotion_allowed=False,
        sessions=tuple(sessions),
    )


def replay_dataset(dataset: HistoricalReplayDataset) -> tuple[ComponentReplayResult, ...]:
    return tuple(session.replay() for session in dataset.sessions)


def _required_text(mapping: dict[str, object], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required and must be non-empty text")
    return value.strip()


def _parse_time(value: str, field: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"invalid ISO timestamp for {field}: {value}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return parsed
