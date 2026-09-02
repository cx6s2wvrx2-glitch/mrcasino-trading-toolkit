from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.excalidraw_primary_context import (
    ExcalidrawPrimaryContextError,
    stage_excalidraw_primary_context,
)
from xauusd_v2.primary_context_bundle import FileSystemPrimaryContextBundleResolver


PNG = b"\x89PNG\r\n\x1a\n" + b"A" * 32
FILE_ID = "95b7205bc49506c7f397e0678a45f07556ce105b"
TEXT_ID = "OMwY9lMSC1oWmpOAW7S7p"


class ExcalidrawPrimaryContextTests(unittest.TestCase):
    def make_source(
        self,
        root: Path,
        *,
        payload: bytes = PNG,
        mime_type: str = "image/png",
        image_deleted: bool = False,
        text_deleted: bool = False,
    ) -> Path:
        data_url = f"data:{mime_type};base64," + base64.b64encode(payload).decode("ascii")
        document = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": [
                {
                    "id": "image-element",
                    "type": "image",
                    "fileId": FILE_ID,
                    "isDeleted": image_deleted,
                },
                {
                    "id": TEXT_ID,
                    "type": "text",
                    "text": "LAOL must be inside a POI near a true stop",
                    "isDeleted": text_deleted,
                },
            ],
            "files": {
                FILE_ID: {
                    "mimeType": mime_type,
                    "id": FILE_ID,
                    "dataURL": data_url,
                }
            },
        }
        path = root / "casinonotes.excalidraw"
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def test_exact_embedded_id_stages_original_image_and_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            locator = f"casinonotes.excalidraw#embedded:{FILE_ID}"
            report = stage_excalidraw_primary_context(
                excalidraw_path=source,
                source_locators=(locator,),
                bundle_root=root / "bundle",
            )
            self.assertEqual(report.matched_locators, 1)
            self.assertEqual(report.staged_unique_images, 1)
            resolver = FileSystemPrimaryContextBundleResolver(
                bundle_root=report.bundle_root,
                manifest_path=report.manifest_path,
            )
            payload = resolver.resolve_payload(locator)
            self.assertEqual(len(payload.images), 1)
            self.assertEqual(Path(payload.images[0].path).read_bytes(), PNG)

    def test_exact_text_element_stages_original_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            locator = f"casinonotes.excalidraw#text:{TEXT_ID}"
            report = stage_excalidraw_primary_context(
                excalidraw_path=source,
                source_locators=(locator,),
                bundle_root=root / "bundle",
            )
            self.assertEqual(report.staged_unique_texts, 1)
            resolver = FileSystemPrimaryContextBundleResolver(
                bundle_root=report.bundle_root,
                manifest_path=report.manifest_path,
            )
            payload = resolver.resolve_payload(locator)
            self.assertEqual(payload.text, "LAOL must be inside a POI near a true stop")
            self.assertEqual(payload.images, ())

    def test_missing_embedded_id_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            with self.assertRaisesRegex(ExcalidrawPrimaryContextError, "no live image element"):
                stage_excalidraw_primary_context(
                    excalidraw_path=source,
                    source_locators=("casinonotes.excalidraw#embedded:missing",),
                    bundle_root=root / "bundle",
                )

    def test_deleted_image_element_cannot_authorize_embedded_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root, image_deleted=True)
            with self.assertRaisesRegex(ExcalidrawPrimaryContextError, "no live image element"):
                stage_excalidraw_primary_context(
                    excalidraw_path=source,
                    source_locators=(f"casinonotes.excalidraw#embedded:{FILE_ID}",),
                    bundle_root=root / "bundle",
                )

    def test_deleted_text_element_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root, text_deleted=True)
            with self.assertRaisesRegex(ExcalidrawPrimaryContextError, "missing live text element"):
                stage_excalidraw_primary_context(
                    excalidraw_path=source,
                    source_locators=(f"casinonotes.excalidraw#text:{TEXT_ID}",),
                    bundle_root=root / "bundle",
                )

    def test_mime_signature_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root, payload=b"not-a-png")
            with self.assertRaisesRegex(ExcalidrawPrimaryContextError, "does not match"):
                stage_excalidraw_primary_context(
                    excalidraw_path=source,
                    source_locators=(f"casinonotes.excalidraw#embedded:{FILE_ID}",),
                    bundle_root=root / "bundle",
                )

    def test_manifest_contains_no_ground_truth_answer_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            locators = (
                f"casinonotes.excalidraw#embedded:{FILE_ID}",
                f"casinonotes.excalidraw#text:{TEXT_ID}",
            )
            report = stage_excalidraw_primary_context(
                excalidraw_path=source,
                source_locators=locators,
                bundle_root=root / "bundle",
            )
            encoded = report.manifest_path.read_text(encoding="utf-8").lower()
            for forbidden in (
                "expected_label",
                "expected_class",
                "forbidden_inference",
                "ground_truth_answer",
                "promotion_allowed",
            ):
                self.assertNotIn(forbidden, encoded)

    def test_unrelated_locator_is_ignored_but_excalidraw_match_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            locator = f"casinonotes.excalidraw#embedded:{FILE_ID}"
            report = stage_excalidraw_primary_context(
                excalidraw_path=source,
                source_locators=("other-source#page:1", locator),
                bundle_root=root / "bundle",
            )
            self.assertEqual(report.requested_locators, 2)
            self.assertEqual(report.matched_locators, 1)


if __name__ == "__main__":
    unittest.main()
