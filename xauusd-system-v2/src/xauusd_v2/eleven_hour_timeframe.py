from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


ELEVEN_HOUR_MINUTES = 660


class ElevenHourState(StrEnum):
    NATIVE_SERIES_USABLE = "native_series_usable"
    SYNTHESIS_CANDIDATE = "synthesis_candidate"
    SYNTHESIS_BLOCKED = "synthesis_blocked"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class ElevenHourResult:
    state: ElevenHourState
    usable_for_context: bool
    synthetic_construction_allowed: bool
    reason: str


def evaluate_eleven_hour_series(
    *,
    timeframe_minutes: int,
    already_formed_series: bool | None,
    source_name: str | None,
    synthesis_requested: bool = False,
    anchor_definition_certified: bool = False,
) -> ElevenHourResult:
    """Gate use and construction of the Reflection 11h custom timeframe.

    The approved Reflection corpus repeatedly uses 11h as a real swing/zone
    timeframe, but R-118 explicitly leaves its candle/session construction
    unresolved. V2 may therefore consume an already-formed 11h series with
    provenance, but must not aggregate lower-timeframe bars into 11h candles
    until the anchor/session origin is separately certified.
    """
    if timeframe_minutes != ELEVEN_HOUR_MINUTES:
        return ElevenHourResult(
            ElevenHourState.NOT_CERTIFIED,
            False,
            False,
            "this boundary applies only to the 11h / 660-minute timeframe",
        )

    if already_formed_series is None:
        return ElevenHourResult(
            ElevenHourState.NOT_CERTIFIED,
            False,
            False,
            "whether the 11h series is already formed is unknown",
        )

    clean_source = (source_name or "").strip()

    if synthesis_requested:
        if not anchor_definition_certified:
            return ElevenHourResult(
                ElevenHourState.SYNTHESIS_BLOCKED,
                False,
                False,
                "R-118 does not define the 11h candle anchor/session origin; lower-TF aggregation is blocked",
            )
        if not clean_source:
            return ElevenHourResult(
                ElevenHourState.NOT_CERTIFIED,
                False,
                False,
                "timeframe construction requires explicit source/broker provenance",
            )
        return ElevenHourResult(
            ElevenHourState.SYNTHESIS_CANDIDATE,
            True,
            True,
            "11h anchor construction has separate certified evidence; normal data/replay certification still applies",
        )

    if already_formed_series and clean_source:
        return ElevenHourResult(
            ElevenHourState.NATIVE_SERIES_USABLE,
            True,
            False,
            "approved sources establish 11h as a strategy timeframe; an already-formed provenance-bearing series may be consumed without inventing its anchor",
        )

    return ElevenHourResult(
        ElevenHourState.NOT_CERTIFIED,
        False,
        False,
        "11h context requires an already-formed series with explicit source/broker provenance",
    )
