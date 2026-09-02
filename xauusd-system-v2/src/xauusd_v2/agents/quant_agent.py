from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..models import AgentRunResult
from .base import AgentContractError


@dataclass(frozen=True, slots=True)
class ResearchWindow:
    name: str
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.start.utcoffset() is None:
            raise AgentContractError(f"{self.name} start must be timezone-aware")
        if self.end.tzinfo is None or self.end.utcoffset() is None:
            raise AgentContractError(f"{self.name} end must be timezone-aware")
        if self.start >= self.end:
            raise AgentContractError(f"{self.name} window must have start < end")


@dataclass(frozen=True, slots=True)
class ResearchExperimentSpec:
    experiment_id: str
    strategy_version: str
    strategy_commit_sha: str
    data_snapshot_ref: str
    parameter_set_ref: str
    cost_model_ref: str
    symbol: str
    timeframe_seconds: int
    train: ResearchWindow
    validation: ResearchWindow
    test: ResearchWindow
    confirmed_bars_only: bool = True
    test_locked_until_final_evaluation: bool = True


@dataclass(frozen=True, slots=True)
class ResearchDesignReport:
    experiment_id: str
    ready_for_research: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    train_window: tuple[datetime, datetime]
    validation_window: tuple[datetime, datetime]
    test_window: tuple[datetime, datetime]


def _is_hex(value: str, length: int) -> bool:
    text = value.strip().lower()
    return len(text) == length and all(ch in "0123456789abcdef" for ch in text)


def _is_sha256_ref(value: str) -> bool:
    text = value.strip().lower()
    if not text.startswith("sha256:"):
        return False
    return _is_hex(text.removeprefix("sha256:"), 64)


class QuantitativeResearchAgent:
    """Deterministic research-design gate.

    It does not modify strategy rules, select production risk, or authorize trades.
    Its job is to reject non-reproducible / leakage-prone experiment designs before
    a backtest or statistical study is treated as evidence.
    """

    name = "quant_research_agent_05"
    version = "0.2.0"

    def validate_experiment(
        self,
        *,
        spec: ResearchExperimentSpec,
    ) -> tuple[ResearchDesignReport, AgentRunResult]:
        blockers: list[str] = []
        warnings: list[str] = []

        required_text = {
            "experiment_id": spec.experiment_id,
            "strategy_version": spec.strategy_version,
            "strategy_commit_sha": spec.strategy_commit_sha,
            "data_snapshot_ref": spec.data_snapshot_ref,
            "parameter_set_ref": spec.parameter_set_ref,
            "cost_model_ref": spec.cost_model_ref,
        }
        for field_name, value in required_text.items():
            if not value.strip():
                blockers.append(f"{field_name} is required for reproducibility")

        if spec.strategy_commit_sha.strip() and not _is_hex(spec.strategy_commit_sha, 40):
            blockers.append("strategy_commit_sha must be an exact 40-character Git commit SHA")

        content_addressed_refs = {
            "data_snapshot_ref": spec.data_snapshot_ref,
            "parameter_set_ref": spec.parameter_set_ref,
            "cost_model_ref": spec.cost_model_ref,
        }
        for field_name, value in content_addressed_refs.items():
            if value.strip() and not _is_sha256_ref(value):
                blockers.append(f"{field_name} must be a content-addressed sha256:<64-hex> reference")

        if spec.symbol.upper().strip() != "XAUUSD":
            blockers.append("research scope is canonical XAUUSD only")
        if spec.timeframe_seconds <= 0:
            blockers.append("timeframe_seconds must be positive")
        if not spec.confirmed_bars_only:
            blockers.append("research may use confirmed bars only")
        if not spec.test_locked_until_final_evaluation:
            blockers.append("test set must remain locked until final evaluation")

        windows = (spec.train, spec.validation, spec.test)
        expected_names = ("train", "validation", "test")
        for window, expected_name in zip(windows, expected_names, strict=True):
            if window.name.strip().lower() != expected_name:
                blockers.append(f"expected {expected_name} window, got {window.name!r}")

        if spec.train.end > spec.validation.start:
            blockers.append("train and validation windows overlap")
        if spec.validation.end > spec.test.start:
            blockers.append("validation and test windows overlap")

        if spec.train.end == spec.validation.start:
            warnings.append("train and validation windows are contiguous with no purge gap")
        if spec.validation.end == spec.test.start:
            warnings.append("validation and test windows are contiguous with no purge gap")

        ready = not blockers
        report = ResearchDesignReport(
            experiment_id=spec.experiment_id.strip(),
            ready_for_research=ready,
            blockers=tuple(blockers),
            warnings=tuple(warnings),
            train_window=(spec.train.start, spec.train.end),
            validation_window=(spec.validation.start, spec.validation.end),
            test_window=(spec.test.start, spec.test.end),
        )
        run = AgentRunResult(
            agent_name=self.name,
            agent_version=self.version,
            input_refs=tuple(
                value.strip()
                for value in (
                    spec.experiment_id,
                    spec.strategy_version,
                    spec.strategy_commit_sha,
                    spec.data_snapshot_ref,
                    spec.parameter_set_ref,
                    spec.cost_model_ref,
                )
                if value.strip()
            ),
            payload={
                "ready_for_research": report.ready_for_research,
                "blockers": list(report.blockers),
                "warnings": list(report.warnings),
                "symbol": "XAUUSD",
                "timeframe_seconds": spec.timeframe_seconds,
                "content_addressed_inputs_required": True,
                "authority": {
                    "may_modify_strategy": False,
                    "may_select_live_risk": False,
                    "may_authorize_trade": False,
                },
            },
            needs_review=True,
        )
        return report, run
