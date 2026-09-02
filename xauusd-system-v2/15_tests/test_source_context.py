from __future__ import annotations

import unittest

from xauusd_v2.source_context import (
    ParsedSourceLocator,
    SourceLocatorKind,
    parse_source_locator,
    resolve_primary_context,
)


class FakeResolver:
    def __init__(self, mapping: dict[str, str | None]) -> None:
        self.mapping = mapping
        self.seen: list[ParsedSourceLocator] = []

    def resolve(self, locator: ParsedSourceLocator) -> str | None:
        self.seen.append(locator)
        return self.mapping.get(locator.raw)


class SourceContextTests(unittest.TestCase):
    def test_excalidraw_embedded_locator_is_parsed(self) -> None:
        parsed = parse_source_locator("casinonotes.excalidraw#embedded:abc123")
        self.assertEqual(parsed.kind, SourceLocatorKind.EXCALIDRAW_EMBEDDED)
        self.assertEqual(parsed.asset_name, "casinonotes.excalidraw")
        self.assertEqual(parsed.locator_value, "abc123")

    def test_excalidraw_text_locator_is_parsed(self) -> None:
        parsed = parse_source_locator("casinonotes.excalidraw#text:node42")
        self.assertEqual(parsed.kind, SourceLocatorKind.EXCALIDRAW_TEXT)
        self.assertEqual(parsed.locator_value, "node42")

    def test_topdown_sequence_locator_is_parsed(self) -> None:
        parsed = parse_source_locator("top down analysis (1).zip#sequence:2023-11-01")
        self.assertEqual(parsed.kind, SourceLocatorKind.TOPDOWN_SEQUENCE)
        self.assertEqual(parsed.locator_value, "2023-11-01")

    def test_v2_source_page_visual_locator_is_first_class(self) -> None:
        raw = "v2_sources:47c7d97d-a873-43f9-b4fc-b0fabbd47ba2#page:2#visual:h1"
        parsed = parse_source_locator(raw)
        self.assertEqual(parsed.kind, SourceLocatorKind.V2_SOURCE)
        self.assertEqual(parsed.asset_name, "v2_sources:47c7d97d-a873-43f9-b4fc-b0fabbd47ba2")
        self.assertEqual(parsed.locator_value, "page:2#visual:h1")

    def test_invalid_v2_source_uuid_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_source_locator("v2_sources:not-a-uuid#page:2")

    def test_v2_source_requires_fragment(self) -> None:
        with self.assertRaises(ValueError):
            parse_source_locator("v2_sources:47c7d97d-a873-43f9-b4fc-b0fabbd47ba2")

    def test_unknown_fragment_is_preserved_as_other(self) -> None:
        parsed = parse_source_locator("source.pdf#page:3")
        self.assertEqual(parsed.kind, SourceLocatorKind.OTHER)
        self.assertEqual(parsed.locator_value, "page:3")

    def test_empty_locator_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_source_locator("   ")

    def test_missing_structured_value_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_source_locator("casinonotes.excalidraw#embedded:")

    def test_real_context_is_returned(self) -> None:
        raw = "casinonotes.excalidraw#text:node42"
        resolver = FakeResolver({raw: " primary casino text "})
        self.assertEqual(resolve_primary_context(raw, resolver), "primary casino text")

    def test_v2_source_real_context_is_returned(self) -> None:
        raw = "v2_sources:47c7d97d-a873-43f9-b4fc-b0fabbd47ba2#page:2#visual:h1"
        resolver = FakeResolver({raw: " primary approved visual context "})
        self.assertEqual(resolve_primary_context(raw, resolver), "primary approved visual context")
        self.assertEqual(resolver.seen[0].kind, SourceLocatorKind.V2_SOURCE)

    def test_unavailable_context_fails_closed(self) -> None:
        raw = "casinonotes.excalidraw#embedded:missing"
        resolver = FakeResolver({raw: None})
        with self.assertRaises(LookupError):
            resolve_primary_context(raw, resolver)

    def test_empty_context_fails_closed(self) -> None:
        raw = "top down analysis (1).zip#sequence:2023-11-01"
        resolver = FakeResolver({raw: "   "})
        with self.assertRaises(LookupError):
            resolve_primary_context(raw, resolver)


if __name__ == "__main__":
    unittest.main()
