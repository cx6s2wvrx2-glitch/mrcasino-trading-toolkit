from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.primary_context_bundle import FileSystemPrimaryContextBundleResolver, load_primary_context_bundle


SOURCE_UUID = "a338728f-1796-4665-b678-774ea9f9f031"


class PrimaryContextBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "text").mkdir()
        (self.root / "images").mkdir()
        (self.root / "text" / "a.txt").write_text("original primary words", encoding="utf-8")
        (self.root / "images" / "a.png").write_bytes(b"primary-chart")

    def write_manifest(self, payload) -> Path:
        path = self.root / "manifest.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_resolves_original_text_and_image_from_relative_paths(self) -> None:
        manifest = self.write_manifest({
            "version": 1,
            "entries": [{
                "source_locator": "source#image:a",
                "text_path": "text/a.txt",
                "images": [{"path": "images/a.png", "mime_type": "image/png"}],
            }],
        })
        resolver = FileSystemPrimaryContextBundleResolver(bundle_root=self.root, manifest_path=manifest)
        payload = resolver.resolve_payload("source#image:a")
        self.assertEqual(payload.text, "original primary words")
        self.assertEqual(len(payload.images), 1)
        self.assertEqual(payload.images[0].mime_type, "image/png")

    def test_pdf_fragment_locator_can_resolve_full_original_page(self) -> None:
        page_locator = f"v2_sources:{SOURCE_UUID}#page:4"
        manifest = self.write_manifest({
            "version": 1,
            "entries": [{
                "source_locator": page_locator,
                "images": [{"path": "images/a.png", "mime_type": "image/png"}],
            }],
        })
        resolver = FileSystemPrimaryContextBundleResolver(bundle_root=self.root, manifest_path=manifest)
        payload = resolver.resolve_payload(page_locator + "#visual:weekly")
        self.assertEqual(len(payload.images), 1)

    def test_exact_fragment_entry_takes_precedence_over_page_fallback(self) -> None:
        page_locator = f"v2_sources:{SOURCE_UUID}#page:4"
        fragment_locator = page_locator + "#visual:weekly"
        (self.root / "images" / "fragment.png").write_bytes(b"fragment-chart")
        manifest = self.write_manifest({
            "version": 1,
            "entries": [
                {
                    "source_locator": page_locator,
                    "images": [{"path": "images/a.png", "mime_type": "image/png"}],
                },
                {
                    "source_locator": fragment_locator,
                    "images": [{"path": "images/fragment.png", "mime_type": "image/png"}],
                },
            ],
        })
        resolver = FileSystemPrimaryContextBundleResolver(bundle_root=self.root, manifest_path=manifest)
        payload = resolver.resolve_payload(fragment_locator)
        self.assertEqual(Path(payload.images[0].path).read_bytes(), b"fragment-chart")

    def test_non_page_locator_never_uses_fallback(self) -> None:
        manifest = self.write_manifest({
            "version": 1,
            "entries": [{"source_locator": "casinonotes.excalidraw", "text_path": "text/a.txt"}],
        })
        resolver = FileSystemPrimaryContextBundleResolver(bundle_root=self.root, manifest_path=manifest)
        with self.assertRaises(LookupError):
            resolver.resolve_payload("casinonotes.excalidraw#embedded:abc")

    def test_duplicate_locator_is_rejected(self) -> None:
        entry = {"source_locator": "same", "text_path": "text/a.txt"}
        manifest = self.write_manifest({"version": 1, "entries": [entry, entry]})
        with self.assertRaisesRegex(ValueError, "duplicate"):
            load_primary_context_bundle(manifest)

    def test_answer_leakage_fields_are_rejected(self) -> None:
        manifest = self.write_manifest({
            "version": 1,
            "entries": [{
                "source_locator": "source#one",
                "text_path": "text/a.txt",
                "expected_label": "secret-answer",
            }],
        })
        with self.assertRaisesRegex(ValueError, "forbidden answer field"):
            load_primary_context_bundle(manifest)

    def test_path_traversal_is_rejected(self) -> None:
        outside = self.root.parent / "outside-primary.txt"
        outside.write_text("outside", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        manifest = self.write_manifest({
            "version": 1,
            "entries": [{"source_locator": "source#one", "text_path": "../outside-primary.txt"}],
        })
        resolver = FileSystemPrimaryContextBundleResolver(bundle_root=self.root, manifest_path=manifest)
        with self.assertRaisesRegex(ValueError, "escapes bundle root"):
            resolver.resolve_payload("source#one")

    def test_unknown_locator_fails_closed(self) -> None:
        manifest = self.write_manifest({
            "version": 1,
            "entries": [{"source_locator": "source#one", "text_path": "text/a.txt"}],
        })
        resolver = FileSystemPrimaryContextBundleResolver(bundle_root=self.root, manifest_path=manifest)
        with self.assertRaises(LookupError):
            resolver.resolve_payload("source#missing")


if __name__ == "__main__":
    unittest.main()
