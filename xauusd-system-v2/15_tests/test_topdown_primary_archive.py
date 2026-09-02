from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from xauusd_v2.primary_context_bundle import FileSystemPrimaryContextBundleResolver
from xauusd_v2.topdown_primary_archive import (
    TOPDOWN_SOURCE_UUID,
    TopDownPrimaryArchiveError,
    stage_topdown_primary_archive,
)


JPEG_A = b"\xff\xd8\xff" + b"A" * 32
JPEG_B = b"\xff\xd8\xff" + b"B" * 32
JPEG_C = b"\xff\xd8\xff" + b"C" * 32


class TopDownPrimaryArchiveTests(unittest.TestCase):
    def make_zip(self, root: Path, members: dict[str, bytes]) -> Path:
        path = root / "top down analysis (1).zip"
        with ZipFile(path, "w") as zipped:
            for name, payload in members.items():
                zipped.writestr(name, payload)
        return path

    def loc(self, date: str, image: str | None = None) -> str:
        base = f"v2_sources:{TOPDOWN_SOURCE_UUID}#sequence:{date}"
        return base if image is None else f"{base}#image:{image}"

    def test_exact_image_locator_stages_only_original_requested_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.make_zip(
                root,
                {
                    "top down analysis/IMG_20231101_100000_001.jpg": JPEG_A,
                    "top down analysis/IMG_20231101_100001_002.jpg": JPEG_B,
                    "top down analysis/IMG_20231106_100000_003.jpg": JPEG_C,
                    "__MACOSX/top down analysis/._IMG_20231101_100000_001.jpg": b"metadata",
                },
            )
            locator = self.loc("2023-11-01", "IMG_20231101_100001_002.jpg")
            report = stage_topdown_primary_archive(
                archive_path=archive,
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
            self.assertEqual(Path(payload.images[0].path).read_bytes(), JPEG_B)

    def test_sequence_only_locator_stages_all_images_for_exact_filename_date(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.make_zip(
                root,
                {
                    "folder/IMG_20231101_100000_001.jpg": JPEG_A,
                    "folder/IMG_20231101_100001_002.jpg": JPEG_B,
                    "folder/IMG_20231106_100000_003.jpg": JPEG_C,
                },
            )
            locator = "top down analysis (1).zip#sequence:2023-11-01"
            report = stage_topdown_primary_archive(
                archive_path=archive,
                source_locators=(locator,),
                bundle_root=root / "bundle",
            )
            resolver = FileSystemPrimaryContextBundleResolver(
                bundle_root=report.bundle_root,
                manifest_path=report.manifest_path,
            )
            payload = resolver.resolve_payload(locator)
            self.assertEqual(len(payload.images), 2)
            self.assertEqual(report.staged_unique_images, 2)

    def test_unrelated_locators_are_ignored_not_reinterpreted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.make_zip(root, {"folder/IMG_20231101_100000_001.jpg": JPEG_A})
            locator = self.loc("2023-11-01", "IMG_20231101_100000_001.jpg")
            report = stage_topdown_primary_archive(
                archive_path=archive,
                source_locators=("casinonotes.excalidraw#embedded:abc", locator),
                bundle_root=root / "bundle",
            )
            self.assertEqual(report.requested_locators, 2)
            self.assertEqual(report.matched_locators, 1)

    def test_manifest_contains_source_locators_and_assets_but_no_answer_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.make_zip(root, {"folder/IMG_20231101_100000_001.jpg": JPEG_A})
            locator = self.loc("2023-11-01", "IMG_20231101_100000_001.jpg")
            report = stage_topdown_primary_archive(
                archive_path=archive,
                source_locators=(locator,),
                bundle_root=root / "bundle",
            )
            manifest = json.loads(report.manifest_path.read_text(encoding="utf-8"))
            encoded = json.dumps(manifest).lower()
            self.assertIn(locator.lower(), encoded)
            self.assertNotIn("expected_label", encoded)
            self.assertNotIn("expected_class", encoded)
            self.assertNotIn("forbidden_inference", encoded)
            self.assertNotIn("ground_truth_answer", encoded)
            self.assertNotIn("promotion_allowed", encoded)

    def test_sequence_image_date_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.make_zip(root, {"folder/IMG_20231101_100000_001.jpg": JPEG_A})
            with self.assertRaisesRegex(TopDownPrimaryArchiveError, "date mismatch"):
                stage_topdown_primary_archive(
                    archive_path=archive,
                    source_locators=(self.loc("2023-11-06", "IMG_20231101_100000_001.jpg"),),
                    bundle_root=root / "bundle",
                )

    def test_missing_referenced_image_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.make_zip(root, {"folder/IMG_20231101_100000_001.jpg": JPEG_A})
            with self.assertRaisesRegex(TopDownPrimaryArchiveError, "missing"):
                stage_topdown_primary_archive(
                    archive_path=archive,
                    source_locators=(self.loc("2023-11-01", "IMG_20231101_999999_999.jpg"),),
                    bundle_root=root / "bundle",
                )

    def test_duplicate_original_basenames_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "top down analysis (1).zip"
            with ZipFile(archive, "w") as zipped:
                zipped.writestr("a/IMG_20231101_100000_001.jpg", JPEG_A)
                zipped.writestr("b/IMG_20231101_100000_001.jpg", JPEG_B)
            with self.assertRaisesRegex(TopDownPrimaryArchiveError, "duplicate"):
                stage_topdown_primary_archive(
                    archive_path=archive,
                    source_locators=(self.loc("2023-11-01", "IMG_20231101_100000_001.jpg"),),
                    bundle_root=root / "bundle",
                )

    def test_extension_with_non_image_signature_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.make_zip(root, {"folder/IMG_20231101_100000_001.jpg": b"not-a-jpeg"})
            with self.assertRaisesRegex(TopDownPrimaryArchiveError, "does not match"):
                stage_topdown_primary_archive(
                    archive_path=archive,
                    source_locators=(self.loc("2023-11-01", "IMG_20231101_100000_001.jpg"),),
                    bundle_root=root / "bundle",
                )


if __name__ == "__main__":
    unittest.main()
