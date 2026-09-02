from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.agent06_compare_cli import main
from xauusd_v2.blind_validation_packet import BlindValidationCase, BlindValidationPacket
from xauusd_v2.blind_validation_packet_io import write_blind_packet
from xauusd_v2.blind_validation_runtime import blind_packet_sha256


class Agent06CompareCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.datasets = self.root / "datasets"
        self.datasets.mkdir()
        dataset = {
            "dataset": "test",
            "status": "candidate_not_verified",
            "source_episode": "primary",
            "promotion_allowed": False,
            "test_vectors": [
                {
                    "id": "GT-A",
                    "source_locator": "source#a",
                    "expected_label": "label_a",
                    "expected_class": "valid",
                    "evidence": ["primary"],
                    "forbidden_inference": "",
                },
                {
                    "id": "GT-B",
                    "source_locator": "source#b",
                    "expected_label": "label_b",
                    "expected_class": "invalid",
                    "evidence": ["primary"],
                    "forbidden_inference": "",
                },
            ],
        }
        (self.datasets / "ground_truth_round_02.json").write_text(json.dumps(dataset), encoding="utf-8")
        self.packet = BlindValidationPacket(
            dataset_name="blind",
            taxonomy=("label_a", "label_b"),
            cases=(
                BlindValidationCase(vector_id="GT-A", source_locator="source#a"),
                BlindValidationCase(vector_id="GT-B", source_locator="source#b"),
            ),
        )
        self.packet_path = self.root / "packet.json"
        write_blind_packet(self.packet, self.packet_path)
        self.predictions = self.root / "predictions.json"
        self.predictions.write_text(
            json.dumps({
                "version": 1,
                "run_id": "run-1",
                "model_provider": "provider-x",
                "model_name": "model-y",
                "packet_sha256": blind_packet_sha256(self.packet),
                "taxonomy_sha256": "0" * 64,
                "case_count": 2,
                "decisions": [
                    {
                        "vector_id": "GT-A",
                        "source_locator": "source#a",
                        "predicted_label": "label_a",
                        "confidence": 0.9,
                        "evidence": ["source"],
                        "ambiguities": [],
                    },
                    {
                        "vector_id": "GT-B",
                        "source_locator": "source#b",
                        "predicted_label": None,
                        "confidence": 0.3,
                        "evidence": [],
                        "ambiguities": ["unclear"],
                    },
                ],
                "ground_truth_loaded_by_this_process": False,
                "comparison_performed_by_this_process": False,
                "promotion_allowed": False,
            }),
            encoding="utf-8",
        )

    def test_post_run_comparison_is_separate_and_never_promotes(self) -> None:
        output = self.root / "comparison.json"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main([
                "--packet", str(self.packet_path),
                "--predictions", str(self.predictions),
                "--datasets-dir", str(self.datasets),
                "--output", str(output),
                "--rounds", "2",
            ])
        self.assertEqual(code, 0)
        summary = json.loads(stdout.getvalue())
        self.assertEqual(summary["agree"], 1)
        self.assertEqual(summary["ambiguous"], 1)
        self.assertEqual(summary["disagree"], 0)
        self.assertFalse(summary["promotion_allowed"])
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertTrue(report["comparison_performed_after_blind_run"])
        self.assertFalse(report["promotion_allowed"])

    def test_mismatched_packet_fingerprint_fails_before_comparison(self) -> None:
        raw = json.loads(self.predictions.read_text(encoding="utf-8"))
        raw["packet_sha256"] = "f" * 64
        self.predictions.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "fingerprint"):
            main([
                "--packet", str(self.packet_path),
                "--predictions", str(self.predictions),
                "--datasets-dir", str(self.datasets),
                "--output", str(self.root / "comparison.json"),
                "--rounds", "2",
            ])

    def test_prediction_locator_mismatch_is_rejected(self) -> None:
        raw = json.loads(self.predictions.read_text(encoding="utf-8"))
        raw["decisions"][0]["source_locator"] = "source#wrong"
        self.predictions.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "locator mismatch"):
            main([
                "--packet", str(self.packet_path),
                "--predictions", str(self.predictions),
                "--datasets-dir", str(self.datasets),
                "--output", str(self.root / "comparison.json"),
                "--rounds", "2",
            ])


if __name__ == "__main__":
    unittest.main()
