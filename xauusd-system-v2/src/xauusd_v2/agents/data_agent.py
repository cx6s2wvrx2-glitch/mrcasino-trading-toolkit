from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import isfinite

from ..models import AgentRunResult
from .base import AgentContractError


@dataclass(frozen=True, slots=True)
class MarketBar:
    """One broker/source bar. timestamp is the BAR OPEN time and must be timezone-aware."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    is_closed: bool
    source_name: str
    source_symbol: str


@dataclass(frozen=True, slots=True)
class MarketDataValidationReport:
    canonical_symbol: str
    timeframe_seconds: int
    total_bars: int
    closed_bars: int
    provisional_bars: int
    first_timestamp: datetime
    last_timestamp: datetime
    source_names: tuple[str, ...]
    source_symbols: tuple[str, ...]
    warnings: tuple[str, ...]


class XAUUSDDataAgent:
    """Deterministic market-data gate; no LLM and no strategy authority."""

    name = "xauusd_data_agent_03"
    version = "0.1.0"

    def validate_batch(
        self,
        *,
        bars: tuple[MarketBar, ...],
        timeframe_seconds: int,
        evaluation_time: datetime,
        canonical_symbol: str = "XAUUSD",
    ) -> tuple[MarketDataValidationReport, AgentRunResult]:
        if canonical_symbol.upper().strip() != "XAUUSD":
            raise AgentContractError("V2 market-data agent accepts canonical XAUUSD only")
        if timeframe_seconds <= 0:
            raise AgentContractError("timeframe_seconds must be positive")
        if evaluation_time.tzinfo is None or evaluation_time.utcoffset() is None:
            raise AgentContractError("evaluation_time must be timezone-aware")
        if not bars:
            raise AgentContractError("market-data batch is empty")

        previous_timestamp: datetime | None = None
        provisional_count = 0
        warnings: list[str] = []
        source_names: set[str] = set()
        source_symbols: set[str] = set()

        for index, bar in enumerate(bars):
            if bar.timestamp.tzinfo is None or bar.timestamp.utcoffset() is None:
                raise AgentContractError(f"bar {index} timestamp must be timezone-aware")
            if bar.timestamp > evaluation_time:
                raise AgentContractError(f"bar {index} starts in the future")
            if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
                raise AgentContractError("bars must be strictly increasing with no duplicate timestamps")
            previous_timestamp = bar.timestamp

            prices = (bar.open, bar.high, bar.low, bar.close)
            if not all(isfinite(value) for value in prices):
                raise AgentContractError(f"bar {index} contains non-finite price")
            if bar.low > min(bar.open, bar.close) or bar.high < max(bar.open, bar.close) or bar.low > bar.high:
                raise AgentContractError(f"bar {index} has invalid OHLC geometry")

            if not bar.source_name.strip() or not bar.source_symbol.strip():
                raise AgentContractError(f"bar {index} is missing source provenance")
            source_names.add(bar.source_name.strip())
            source_symbols.add(bar.source_symbol.strip())

            close_time = bar.timestamp + timedelta(seconds=timeframe_seconds)
            if bar.is_closed and close_time > evaluation_time:
                raise AgentContractError(f"bar {index} is marked closed before its close time")
            if not bar.is_closed:
                provisional_count += 1
                if index != len(bars) - 1:
                    raise AgentContractError("only the final bar may be provisional/unclosed")
                if close_time <= evaluation_time:
                    raise AgentContractError("final bar is marked provisional even though its close time has passed")

        if provisional_count:
            warnings.append("Final bar is provisional and must never satisfy confirmed-only strategy conditions.")
        if len(source_names) > 1:
            warnings.append("Batch contains multiple market-data sources; do not merge price geometry silently.")
        if len(source_symbols) > 1:
            warnings.append("Batch contains multiple broker symbol aliases; canonicalization must remain explicit.")

        report = MarketDataValidationReport(
            canonical_symbol="XAUUSD",
            timeframe_seconds=timeframe_seconds,
            total_bars=len(bars),
            closed_bars=len(bars) - provisional_count,
            provisional_bars=provisional_count,
            first_timestamp=bars[0].timestamp,
            last_timestamp=bars[-1].timestamp,
            source_names=tuple(sorted(source_names)),
            source_symbols=tuple(sorted(source_symbols)),
            warnings=tuple(warnings),
        )
        run = AgentRunResult(
            agent_name=self.name,
            agent_version=self.version,
            input_refs=tuple(sorted(source_names | source_symbols)),
            payload={
                "canonical_symbol": report.canonical_symbol,
                "timeframe_seconds": timeframe_seconds,
                "total_bars": report.total_bars,
                "closed_bars": report.closed_bars,
                "provisional_bars": report.provisional_bars,
                "warnings": list(report.warnings),
            },
            needs_review=bool(report.warnings),
        )
        return report, run
