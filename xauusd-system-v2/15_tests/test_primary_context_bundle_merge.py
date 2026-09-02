from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.primary_context_bundle import load_primary_context_bundle
from xauusd_v2.primary_context_bundle_merge import (
    PrimaryContextBundleMergeError,
    merge_primary_context_manifests,
)


class PrimaryContextBundleMergeTests(unittest.TestCase):
    def write(self, path: Path, entries: list[dict[str, object]]) -> Path:
        path.write_text(json.dumps({"version": 1, "entries": entries}), encoding="utf-8")
        return path

    def test_merges_distinct_entries_and_output_loads(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            one = self.write(root / "one.json", [{"source_locator": "a", "text_path": "a.txt"}])
            two = self.write(
                root / "two.json",
                [{"source_locator": "b", "images": [{"path": "b.png", "mime_type": "image/png"}]}],
            )
            output = root / "merged.json"
            report = merge_primary_context_manifests(
                manifest_paths=(one, two),
                output_manifest=output,
            )
            self.assertEqual(report.input_manifests, 2)
            self.assertEqual(report.merged_entries, 2)
            self.assertEqual(len(load_primary_context_bundle(output).entries), 2)

    def test_identical_duplicate_entry_is_deduplicated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            entry = {"source_locator": "same", "text_path": "a.txt"}
            one = self.write(root / "one.json", [entry])
            two = self.write(root / "two.json", [entry])
            report = merge_primary_context_manifests(
                manifest_paths=(one, two),
                output_manifest=root / "merged.json",
            )
            self.assertEqual(report.merged_entries, 1)

    def test_conflicting_duplicate_entry_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            one = self.write(root / "one.json", [{"source_locator": "same", "text_path": "a.txt"}])
            two = self.write(root / "two.json", [{"source_locator": "same", "text_path": "b.txt"}])
            with self.assertRaisesRegex(PrimaryContextBundleMergeError, "conflicting"):
                merge_primary_context_manifests(
                    manifest_paths=(one, two),
                    output_manifest=root / "merged.json",
                )

    def test_forbidden_answer_fields_in_input_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "bad.json"
            path.write_text(
                json.dumps({
                    "version": 1,
                    "entries": [{
                        "source_locator": "a",
                        "text_path": "a.txt",
                        "expected_label": "secret",
                    }],
                }),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "forbidden answer field"):
                merge_primary_context_manifests(
                    manifest_paths=(path,),
                    output_manifest=root / "merged.json",
                )

    def test_existing_different_output_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            one = self.write(root / "one.json", [{"source_locator": "a", "text_path": "a.txt"}])
            output = root / "merged.json"
            output.write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(PrimaryContextBundleMergeError, "collision"):
                merge_primary_context_manifests(
                    manifest_paths=(one,),
                    output_manifest=output,
                )
            self.assertEqual(output.read_text(encoding="utf-8"), "tampered")


if __name__ == "__main__":
    unittest.main()
