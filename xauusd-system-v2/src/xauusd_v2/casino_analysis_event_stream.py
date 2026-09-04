from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from .casino_directional_marker_semantics import CasinoMarkerDirection
from .casino_historical_event_runner import CasinoHistoricalEventRun
from .casino_source_hcs_candidate import SourceHCSMarkerProxyRun
from .casino_source_hcs_negation_context import SourceHCSPlusNegationProxyRun
from .casino_source_negation_candidate import SourceMarkerFUNegationProxyRun


class CasinoAnalysisEventKind(StrEnum):
    STRONG_FU = "strong_fu"
    ATTEMPTED_FU = "attempted_fu"
    BETA_HCS = "beta_hcs"
    SOURCE_HCS = "source_hcs_proxy"
    HCS_RETEST = "hcs_retest"
    BETA_NEGATION = "beta_negation"
    FU_NEGATION = "fu_negation_proxy"
    HCS_PLUS_NEGATION = "hcs_plus_negation_proxy"


class CasinoAnalysisEventProvenance(StrEnum):
    SUPPLIED_CASINO_HELPER = "supplied_casino_helper"
    SUPPLIED_BETA_STATE_MACHINE = "supplied_beta_state_machine"
    SOURCE_MARKER_PROXY = "source_marker_proxy"


@dataclass(frozen=True, slots=True)
class CasinoAnalysisEvent:
    kind: CasinoAnalysisEventKind
    direction: CasinoMarkerDirection
    provenance: CasinoAnalysisEventProvenance
    label: str
    relation: str | None = None
    detail: str | None = None
    candidate_only: bool = False
    strategy_semantics_certified: bool = False
    reference_feed_alignment_complete: bool = False


@dataclass(frozen=True, slots=True)
class CasinoAnalysisEventFrame:
    symbol: str
    timeframe: str
    bar_time_utc: datetime
    events: tuple[CasinoAnalysisEvent, ...]
    event_count: int
    strategy_semantics_certified: bool = False


@dataclass(frozen=True, slots=True)
class CasinoAnalysisEventStream:
    symbol: str
    timeframe: str
    frame_count: int
    event_count: int
    counts_by_kind: tuple[tuple[str, int], ...]
    frames: tuple[CasinoAnalysisEventFrame, ...]
    includes_supplied_helper_markers: bool = True
    includes_beta_hcs_state: bool = True
    includes_source_hcs_proxy: bool = True
    includes_source_fu_negation_proxy: bool = True
    includes_source_hcs_plus_negation_proxy: bool = True
    strategy_semantics_certified: bool = False
    reference_feed_alignment_complete: bool = False
    performance_claim_allowed: bool = False
    promotion_allowed: bool = False
    live_execution_authorized: bool = False


def build_casino_analysis_event_stream(
    *,
    supplied_run: CasinoHistoricalEventRun,
    source_hcs_run: SourceHCSMarkerProxyRun,
    source_negation_run: SourceMarkerFUNegationProxyRun,
    source_hcs_negation_run: SourceHCSPlusNegationProxyRun,
) -> CasinoAnalysisEventStream:
    """Merge implementation events and governed source proxies into one timeline.

    The stream is deliberately simple for downstream analysis while retaining strict
    provenance. Supplied-code events remain implementation evidence. Source-style HCS,
    FU-negation and HCS+negation events remain candidate-only proxies. Nothing in this
    adapter certifies strategy semantics, canonical FOREXCOM alignment, performance or
    execution readiness.
    """

    by_time: dict[datetime, list[CasinoAnalysisEvent]] = defaultdict(list)

    for frame in supplied_run.frames:
        timestamp = frame.bar_time_utc.astimezone(UTC)
        for event in frame.events:
            mapped = _map_supplied_event(event.kind.value)
            if mapped is None:
                continue
            provenance = (
                CasinoAnalysisEventProvenance.SUPPLIED_CASINO_HELPER
                if event.source.value == "supplied_casino_helper"
                else CasinoAnalysisEventProvenance.SUPPLIED_BETA_STATE_MACHINE
            )
            by_time[timestamp].append(
                CasinoAnalysisEvent(
                    kind=mapped,
                    direction=event.direction,
                    provenance=provenance,
                    label=event.marker_text or event.kind.value,
                    relation=event.relation_to_prior_event,
                    detail=None if event.hcs_count is None else f"hcs_count={event.hcs_count}",
                    candidate_only=False,
                )
            )

    for item in source_hcs_run.candidates:
        timestamp = item.second_bar_time_utc.astimezone(UTC)
        by_time[timestamp].append(
            CasinoAnalysisEvent(
                kind=CasinoAnalysisEventKind.SOURCE_HCS,
                direction=item.second_direction,
                provenance=CasinoAnalysisEventProvenance.SOURCE_MARKER_PROXY,
                label="HCS PROXY",
                relation="exact_retest_of_latest_visible_fu_family_wick",
                detail=(
                    f"{item.form.value}; {item.first_semantic_role}->{item.second_semantic_role}; "
                    f"{item.source_strength_label_proxy}"
                ),
                candidate_only=True,
            )
        )

    for item in source_negation_run.candidates:
        timestamp = item.negating_bar_time_utc.astimezone(UTC)
        by_time[timestamp].append(
            CasinoAnalysisEvent(
                kind=CasinoAnalysisEventKind.FU_NEGATION,
                direction=item.negating_direction,
                provenance=CasinoAnalysisEventProvenance.SOURCE_MARKER_PROXY,
                label="FU NEGATION PROXY",
                relation="opposes_latest_visible_manipulation_within_plus_1_or_2",
                detail=(
                    f"{item.original_helper_class.value}->{item.negating_helper_class.value}; "
                    f"offset=+{item.candle_offset}"
                ),
                candidate_only=True,
            )
        )

    for item in source_hcs_negation_run.candidates:
        timestamp = item.negating_bar_time_utc.astimezone(UTC)
        by_time[timestamp].append(
            CasinoAnalysisEvent(
                kind=CasinoAnalysisEventKind.HCS_PLUS_NEGATION,
                direction=item.negating_direction,
                provenance=CasinoAnalysisEventProvenance.SOURCE_MARKER_PROXY,
                label="HCS + NEGATION PROXY",
                relation="negates_source_hcs_second_node_within_plus_1_or_2",
                detail=f"{item.hcs_form.value}; offset=+{item.negation_candle_offset}",
                candidate_only=True,
            )
        )

    frames: list[CasinoAnalysisEventFrame] = []
    counts: Counter[str] = Counter()
    for timestamp in sorted(by_time):
        events = tuple(_dedupe_events(by_time[timestamp]))
        for event in events:
            counts[event.kind.value] += 1
        frames.append(
            CasinoAnalysisEventFrame(
                symbol=supplied_run.symbol,
                timeframe=supplied_run.timeframe,
                bar_time_utc=timestamp,
                events=events,
                event_count=len(events),
            )
        )

    return CasinoAnalysisEventStream(
        symbol=supplied_run.symbol,
        timeframe=supplied_run.timeframe,
        frame_count=len(frames),
        event_count=sum(frame.event_count for frame in frames),
        counts_by_kind=tuple(sorted(counts.items())),
        frames=tuple(frames),
    )


def _map_supplied_event(kind: str) -> CasinoAnalysisEventKind | None:
    mapping = {
        "strong_fu": CasinoAnalysisEventKind.STRONG_FU,
        "attempted_fu": CasinoAnalysisEventKind.ATTEMPTED_FU,
        "hcs": CasinoAnalysisEventKind.BETA_HCS,
        "hcs_retest": CasinoAnalysisEventKind.HCS_RETEST,
        "negation": CasinoAnalysisEventKind.BETA_NEGATION,
        "hcs_context_negation": CasinoAnalysisEventKind.BETA_NEGATION,
    }
    return mapping.get(kind)


def _dedupe_events(events: list[CasinoAnalysisEvent]) -> list[CasinoAnalysisEvent]:
    seen: set[tuple[str, str, str, str, str | None]] = set()
    result: list[CasinoAnalysisEvent] = []
    for event in events:
        key = (
            event.kind.value,
            event.direction.value,
            event.provenance.value,
            event.label,
            event.detail,
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(event)
    return result
