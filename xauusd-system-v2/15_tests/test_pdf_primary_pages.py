from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.pdf_primary_pages import PDFPrimaryPageStageError, stage_pdf_primary_pages
from xauusd_v2.primary_context_bundle import FileSystemPrimaryContextBundleResolver


SOURCE_A = "a338728f-1796-4665-b678-774ea9f9f031"
SOURCE_B = "47c7d97d-a873-43f9-b4fc-b0fabbd47ba2"
PNG_A = b"\x89PNG\r\n\x1a\n" + b"A" * 32
PNG_B = b"\x89PNG\r\n\x1a\n" + b"B" * 32


class PDFPrimaryPageStageTests(unittest.TestCase):
    def test_fragment_locators_stage_one_full_page_and_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            page = root / "page-4.png"
            page.write_bytes(PNG_A)
            locators = (
                f"v2_sources:{SOURCE_A}#page:4#visual:weekly",
                f"v2_sources:{SOURCE_A}#page:4#text:source-note",
            )
            report = stage_pdf_primary_pages(
                rendered_pages={SOURCE_A: {4: page}},
                source_locators=locators,
                bundle_root=root / "bundle",
            )
            self.assertEqual(report.matched_locators, 2)
            self.assertEqual(report.staged_unique_pages, 1)
            resolver = FileSystemPrimaryContextBundleResolver(
                bundle_root=report.bundle_root,
                manifest_path=report.manifest_path,
            )
            for locator in locators:
                self.assertEqual(len(resolver.resolve_payload(locator).images), 1)

    def test_unrelated_sources_are_ignored_not_reinterpreted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            page = root / "page-4.png"
            page.write_bytes(PNG_A)
            report = stage_pdf_primary_pages(
                rendered_pages={SOURCE_A: {4: page}},
                source_locators=(
                    f"v2_sources:{SOURCE_A}#page:4#visual:weekly",
                    f"v2_sources:{SOURCE_B}#page:2#visual:h1",
                    "casinonotes.excalidraw#embedded:abc",
                ),
                bundle_root=root / "bundle",
            )
            self.assertEqual(report.requested_locators, 3)
            self.assertEqual(report.matched_locators, 1)

    def test_missing_rendered_page_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(PDFPrimaryPageStageError, "missing rendered"):
                stage_pdf_primary_pages(
                    rendered_pages={SOURCE_A: {}},
                    source_locators=(f"v2_sources:{SOURCE_A}#page:4#visual:weekly",),
                    bundle_root=root / "bundle",
                )

    def test_non_image_page_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            page = root / "page-4.png"
            page.write_bytes(b"not-a-png")
            with self.assertRaisesRegex(PDFPrimaryPageStageError, "does not match"):
                stage_pdf_primary_pages(
                    rendered_pages={SOURCE_A: {4: page}},
                    source_locators=(f"v2_sources:{SOURCE_A}#page:4",),
                    bundle_root=root / "bundle",
                )

    def test_manifest_contains_only_canonical_pages_not_case_answers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            page_a = root / "page-4.png"
            page_b = root / "page-2.png"
            page_a.write_bytes(PNG_A)
            page_b.write_bytes(PNG_B)
            report = stage_pdf_primary_pages(
                rendered_pages={SOURCE_A: {4: page_a}, SOURCE_B: {2: page_b}},
                source_locators=(
                    f"v2_sources:{SOURCE_A}#page:4#visual:weekly",
                    f"v2_sources:{SOURCE_B}#page:2#visual:h1",
                ),
                bundle_root=root / "bundle",
            )
            manifest = json.loads(report.manifest_path.read_text(encoding="utf-8"))
            encoded = json.dumps(manifest).lower()
            self.assertIn(f"v2_sources:{SOURCE_A}#page:4", encoded)
            self.assertIn(f"v2_sources:{SOURCE_B}#page:2", encoded)
            self.assertNotIn("expected_label", encoded)
            self.assertNotIn("expected_class", encoded)
            self.assertNotIn("ground_truth_answer", encoded)
            self.assertNotIn("promotion_allowed", encoded)

    def test_no_matching_pdf_locators_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            page = root / "page-4.png"
            page.write_bytes(PNG_A)
            with self.assertRaisesRegex(PDFPrimaryPageStageError, "no PDF page"):
                stage_pdf_primary_pages(
                    rendered_pages={SOURCE_A: {4: page}},
                    source_locators=("casinonotes.excalidraw#embedded:abc",),
                    bundle_root=root / "bundle",
                )


if __name__ == "__main__":
    unittest.main()
