from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.agent06_readiness_cli import main


class Agent06ReadinessCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.datasets = self.root / "datasets"
        self.bundle = self.root / "bundle"
        self.datasets.mkdir()
        self.bundle.mkdir()
        (self.bundle / "text").mkdir()
        (self.bundle / "images").mkdir()
        (self.bundle / "text" / "a.txt").write_text("primary text", encoding="utf-8")
        (self.bundle / "images" / "b.png").write_bytes(b"primary image")
        dataset = {
            "dataset": "test",
            "status": "candidate_not_verified",
            "source_episode": "primary",
            "promotion_allowed": False,
            "test_vectors": [
                {
                    "id": "GT-A",
                    "source_locator": "source#text:a",
                    "expected_label": "label_a",
                    "expected_class": "valid",
                    "evidence": ["primary"],
                    "forbidden_inference": "",
                },
                {
                    "id": "GT-B",
                    "source_locator": "source#image:b.png",
                    "expected_label": "label_b",
                    "expected_class": "edge_case",
                    "evidence": ["primary"],
                    "forbidden_inference": "",
                },
            ],
        }
        (self.datasets / "ground_truth_round_02.json").write_text(json.dumps(dataset), encoding="utf-8")

    def run_cli(self, manifest_payload):
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps(manifest_payload), encoding="utf-8")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main([
                "--bundle-root", str(self.bundle),
                "--manifest", str(manifest),
                "--datasets-dir", str(self.datasets),
                "--provider", "provider-x",
                "--model", "model-y",
                "--rounds", "2",
                "--command", sys.executable,
            ])
        return code, json.loads(stdout.getvalue())

    def test_ready_bundle_returns_zero_and_ready_status(self) -> None:
        code, output = self.run_cli({
            "version": 1,
            "entries": [
                {"source_locator": "source#text:a", "text_path": "text/a.txt"},
                {"source_locator": "source#image:b.png", "images": [{"path": "images/b.png", "mime_type": "image/png"}]},
            ],
        })
        self.assertEqual(code, 0)
        self.assertEqual(output["status"], "READY_TO_RUN")
        self.assertTrue(output["ready_to_run"])

    def test_incomplete_bundle_returns_two_and_blockers(self) -> None:
        code, output = self.run_cli({
            "version": 1,
            "entries": [
                {"source_locator": "source#text:a", "text_path": "text/a.txt"},
            ],
        })
        self.assertEqual(code, 2)
        self.assertEqual(output["status"], "NOT_READY")
        self.assertFalse(output["ready_to_run"])
        self.assertEqual(output["missing_locators"], ["source#image:b.png"])


if __name__ == "__main__":
    unittest.main()
