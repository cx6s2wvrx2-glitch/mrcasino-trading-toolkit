from __future__ import annotations

from dataclasses import dataclass


CANONICAL_REFERENCE_FEED = "FOREXCOM:XAUUSD"
BROKER_RESEARCH_FEED = "Exclusive Markets Ltd.:XAUUSD!"


@dataclass(frozen=True, slots=True)
class TimeframeRegistryEntry:
    code: str
    minutes: int
    evidence_class: str
    roles: tuple[str, ...]
    beta_configured: bool
    beta_category: str | None
    broker_validation_status: str
    reference_anchor_status: str
    blocker: str | None = None
    source_note: str | None = None


_BETA_MINUTES = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 35, 40, 45, 50, 55, 60, 90, 100)


def _beta_category(minutes: int) -> str:
    if 1 <= minutes <= 5:
        return "ENTRY"
    if 6 <= minutes <= 20:
        return "SCALP"
    if 30 <= minutes <= 100:
        return "INTRA"
    raise ValueError("beta minute outside configured category ranges")


def _code(minutes: int) -> str:
    if minutes == 60:
        return "H1"
    return f"M{minutes}"


def _broker_status(code: str) -> str:
    if code == "M1":
        return "IMMUTABLE_SOURCE_M1"
    if code in {"H1", "H4", "H8", "D1"}:
        return "BROKER_NATIVE_OHLC_VALIDATED"
    return "NOT_NATIVE_VALIDATED"


def _reference_anchor_status(code: str) -> str:
    if code == "H11":
        return "BLOCKED"
    return "UNVERIFIED"


def _build_registry() -> tuple[TimeframeRegistryEntry, ...]:
    items: dict[int, TimeframeRegistryEntry] = {}

    for minutes in _BETA_MINUTES:
        code = _code(minutes)
        items[minutes] = TimeframeRegistryEntry(
            code=code,
            minutes=minutes,
            evidence_class="IMPLEMENTATION_HELPER",
            roles=("multi_confirmation",),
            beta_configured=True,
            beta_category=_beta_category(minutes),
            broker_validation_status=_broker_status(code),
            reference_anchor_status=_reference_anchor_status(code),
            source_note="Exact BETA 1 + LAOL configured timeframe.",
        )

    # Primary-source higher-timeframe zone/refinement sequence. 15h/14h is
    # preserved as an alternative notation in the source, not silently turned
    # into a rule requiring both layers.
    primary_htf = {
        180: ("H3", ("zone", "tfs", "swing"), "Primary HTF descent / swing TFS."),
        240: ("H4", ("zone", "context"), "Primary HTF descent; broker-native validated."),
        300: ("H5", ("zone", "tfs", "swing"), "Primary HTF descent / swing TFS."),
        420: ("H7", ("zone", "tfs", "swing"), "Primary HTF descent / swing TFS."),
        480: ("H8", ("context",), "Broker-native validation layer; not asserted as a mandatory primary sequence step."),
        660: ("H11", ("zone", "tfs", "swing"), "Primary HTF descent / swing TFS; anchor unresolved."),
        720: ("H12", ("zone", "context"), "Primary HTF descent."),
        840: ("H14", ("zone", "context"), "Primary source writes 15/14h as an alternative slot."),
        900: ("H15", ("zone", "context"), "Primary source writes 15/14h as an alternative slot."),
        1080: ("H18", ("zone", "context"), "Primary HTF descent start/refinement layer."),
        1440: ("D1", ("zone", "context"), "Primary HTF descent; broker-native validated."),
        5760: ("D4", ("zone", "context", "long_term"), "Primary HTF descent upper layer."),
    }

    for minutes, (code, roles, note) in primary_htf.items():
        existing = items.get(minutes)
        blocker = "B-07" if code == "H11" else None
        if existing is None:
            items[minutes] = TimeframeRegistryEntry(
                code=code,
                minutes=minutes,
                evidence_class="PRIMARY_SOURCE",
                roles=roles,
                beta_configured=False,
                beta_category=None,
                broker_validation_status=_broker_status(code),
                reference_anchor_status=_reference_anchor_status(code),
                blocker=blocker,
                source_note=note,
            )
        else:
            items[minutes] = TimeframeRegistryEntry(
                code=code,
                minutes=minutes,
                evidence_class="PRIMARY_SOURCE+IMPLEMENTATION_HELPER",
                roles=tuple(dict.fromkeys(existing.roles + roles)),
                beta_configured=existing.beta_configured,
                beta_category=existing.beta_category,
                broker_validation_status=_broker_status(code),
                reference_anchor_status=_reference_anchor_status(code),
                blocker=blocker,
                source_note=note,
            )

    return tuple(items[key] for key in sorted(items))


TIMEFRAME_REGISTRY = _build_registry()
TIMEFRAME_BY_CODE = {item.code: item for item in TIMEFRAME_REGISTRY}
TIMEFRAME_BY_MINUTES = {item.minutes: item for item in TIMEFRAME_REGISTRY}


def get_timeframe(code: str) -> TimeframeRegistryEntry:
    normalized = code.strip().upper()
    try:
        return TIMEFRAME_BY_CODE[normalized]
    except KeyError as exc:
        raise KeyError(f"unregistered timeframe: {normalized}") from exc


def reference_anchor_certified(code: str) -> bool:
    """Fail closed until FOREXCOM/reference candle anchors are explicitly certified."""
    return get_timeframe(code).reference_anchor_status == "CERTIFIED"
