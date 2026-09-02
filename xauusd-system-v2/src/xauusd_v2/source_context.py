from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class SourceLocatorKind(StrEnum):
    EXCALIDRAW_EMBEDDED = "excalidraw_embedded"
    EXCALIDRAW_TEXT = "excalidraw_text"
    TOPDOWN_SEQUENCE = "topdown_sequence"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class ParsedSourceLocator:
    raw: str
    asset_name: str
    kind: SourceLocatorKind
    locator_value: str


class PrimarySourceContextResolver(Protocol):
    """Runtime interface for retrieving actual primary source context.

    Implementations may use mounted conversation/library files, extracted archives or
    other approved storage, but must never substitute analyst summaries for unavailable
    primary content.
    """

    def resolve(self, locator: ParsedSourceLocator) -> str | None: ...


def parse_source_locator(raw: str) -> ParsedSourceLocator:
    value = raw.strip()
    if not value:
        raise ValueError("source locator is required")

    asset, sep, fragment = value.partition("#")
    asset = asset.strip()
    if not asset:
        raise ValueError("source locator asset name is required")

    if not sep or not fragment.strip():
        return ParsedSourceLocator(value, asset, SourceLocatorKind.OTHER, "")

    fragment = fragment.strip()
    if fragment.startswith("embedded:") and asset.lower().endswith(".excalidraw"):
        locator_value = fragment.removeprefix("embedded:").strip()
        kind = SourceLocatorKind.EXCALIDRAW_EMBEDDED
    elif fragment.startswith("text:") and asset.lower().endswith(".excalidraw"):
        locator_value = fragment.removeprefix("text:").strip()
        kind = SourceLocatorKind.EXCALIDRAW_TEXT
    elif fragment.startswith("sequence:"):
        locator_value = fragment.removeprefix("sequence:").strip()
        kind = SourceLocatorKind.TOPDOWN_SEQUENCE
    else:
        locator_value = fragment
        kind = SourceLocatorKind.OTHER

    if kind is not SourceLocatorKind.OTHER and not locator_value:
        raise ValueError("structured source locator value is required")

    return ParsedSourceLocator(value, asset, kind, locator_value)


def resolve_primary_context(
    raw_locator: str,
    resolver: PrimarySourceContextResolver,
) -> str:
    """Resolve actual primary context or fail closed.

    Empty/unavailable context is never replaced with notes, candidate labels or model
    memory because doing so would invalidate blind validation.
    """
    parsed = parse_source_locator(raw_locator)
    context = resolver.resolve(parsed)
    normalized = "" if context is None else context.strip()
    if not normalized:
        raise LookupError(f"primary source context unavailable for {raw_locator}")
    return normalized
