from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .agents.data_agent import MarketDataValidationReport
from .agents.quant_agent import QuantitativeResearchAgent, ResearchDesignReport, ResearchExperimentSpec
from .data_snapshot import DataSnapshotManifest


class ResearchRuntimeStatus(StrEnum):
    BLOCKED = "BLOCKED"
    DATA_READY = "DATA_READY"
    BACKTEST_READY = "BACKTEST_READY"


@dataclass(frozen=True, slots=True)
class ResearchRuntimeReport:
    experiment_id: str
    status: ResearchRuntimeStatus
    snapshot_id: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    data_ready: bool
    strategy_certification_ready: bool


def prepare_research_runtime(
    *,
    spec: ResearchExperimentSpec,
    snapshot: DataSnapshotManifest,
    data_report: MarketDataValidationReport,
    strategy_certification_ready: bool,
    quant_agent: QuantitativeResearchAgent | None = None,
) -> tuple[ResearchRuntimeReport, ResearchDesignReport]:
    agent = quant_agent or QuantitativeResearchAgent()
    design, _ = agent.validate_experiment(spec=spec)

    blockers = list(design.blockers)
    warnings = list(design.warnings)

    if spec.data_snapshot_ref.strip() != snapshot.snapshot_id:
        blockers.append("experiment data_snapshot_ref does not match immutable snapshot id")
    if snapshot.canonical_symbol != "XAUUSD" or data_report.canonical_symbol != "XAUUSD":
        blockers.append("data runtime accepts canonical XAUUSD only")
    if spec.timeframe_seconds != snapshot.timeframe_seconds:
        blockers.append("experiment timeframe does not match data snapshot timeframe")
    if data_report.timeframe_seconds != snapshot.timeframe_seconds:
        blockers.append("data validation report timeframe does not match snapshot")
    if snapshot.bar_count != data_report.total_bars:
        blockers.append("snapshot bar count does not match validated data report")
    if not snapshot.closed_only or data_report.provisional_bars:
        blockers.append("performance research requires a closed-only historical snapshot")

    if snapshot.first_timestamp > spec.train.start:
        blockers.append("data snapshot does not cover the start of the train window")
    if snapshot.coverage_end < spec.test.end:
        blockers.append("data snapshot does not cover the end of the locked test window")

    data_ready = not blockers
    if blockers:
        status = ResearchRuntimeStatus.BLOCKED
    elif strategy_certification_ready:
        status = ResearchRuntimeStatus.BACKTEST_READY
    else:
        status = ResearchRuntimeStatus.DATA_READY
        warnings.append(
            "Data/research design is ready, but strategy certification is not ready; performance backtest remains gated."
        )

    report = ResearchRuntimeReport(
        experiment_id=spec.experiment_id.strip(),
        status=status,
        snapshot_id=snapshot.snapshot_id,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        data_ready=data_ready,
        strategy_certification_ready=strategy_certification_ready,
    )
    return report, design
