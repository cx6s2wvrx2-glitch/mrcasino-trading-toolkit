from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2 import agent06_audit_cli


class Agent06AuditCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "run"
        self.root.mkdir(parents=True)
        self.run_id = "agent06-anthropic-test"
        self.repo_commit = "b" * 40
        self.packet_sha = "c" * 64
        self.taxonomy_sha = "d" * 64

    @staticmethod
    def _write(path: Path, payload: object) -> None:
        path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def _sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _build_valid_run(self) -> None:
        decisions = [
            {
                "vector_id": "GT-T-001",
                "source_locator": "source#image:1",
                "predicted_label": "A",
                "confidence": 0.9,
                "evidence": ["primary image evidence"],
                "ambiguities": [],
            },
            {
                "vector_id": "GT-T-002",
                "source_locator": "source#image:2",
                "predicted_label": None,
                "confidence": 0.4,
                "evidence": [],
                "ambiguities": ["unclear"],
            },
            {
                "vector_id": "GT-T-003",
                "source_locator": "source#text:3",
                "predicted_label": "B",
                "confidence": 0.8,
                "evidence": ["primary text evidence"],
                "ambiguities": [],
            },
        ]
        predictions = {
            "version": 1,
            "run_id": self.run_id,
            "model_provider": "anthropic",
            "model_name": "claude-sonnet-5",
            "packet_sha256": self.packet_sha,
            "taxonomy_sha256": self.taxonomy_sha,
            "case_count": 3,
            "decisions": decisions,
            "ground_truth_loaded_by_this_process": False,
            "comparison_performed_by_this_process": False,
            "promotion_allowed": False,
        }
        predictions_path = self.root / "agent06_blind_predictions.json"
        self._write(predictions_path, predictions)

        runtime_cases = [
            {
                "vector_id": "GT-T-001",
                "source_locator": "source#image:1",
                "source_text_sha256": None,
                "images": [{"mime_type": "image/png", "sha256": "1" * 64, "size_bytes": 10}],
                "predicted_label": "A",
                "abstained": False,
            },
            {
                "vector_id": "GT-T-002",
                "source_locator": "source#image:2",
                "source_text_sha256": None,
                "images": [{"mime_type": "image/png", "sha256": "2" * 64, "size_bytes": 20}],
                "predicted_label": None,
                "abstained": True,
            },
            {
                "vector_id": "GT-T-003",
                "source_locator": "source#text:3",
                "source_text_sha256": "3" * 64,
                "images": [],
                "predicted_label": "B",
                "abstained": False,
            },
        ]
        runtime = {
            "run_id": self.run_id,
            "model_provider": "anthropic",
            "model_name": "claude-sonnet-5",
            "packet_sha256": self.packet_sha,
            "taxonomy_sha256": self.taxonomy_sha,
            "case_count": 3,
            "completed_count": 3,
            "abstained_count": 1,
            "image_case_count": 2,
            "cases": runtime_cases,
            "promotion_allowed": False,
        }
        runtime_path = self.root / "agent06_runtime_manifest.json"
        self._write(runtime_path, runtime)

        predictions_sha = self._sha(predictions_path)
        runtime_sha = self._sha(runtime_path)
        frozen = {
            "version": 1,
            "run_id": self.run_id,
            "repo_commit": self.repo_commit,
            "provider": "anthropic",
            "model": "claude-sonnet-5",
            "bundle_sha256": agent06_audit_cli._EXPECTED_BUNDLE_SHA256,
            "primary_context_manifest_sha256": agent06_audit_cli._EXPECTED_MANIFEST_SHA256,
            "predictions_sha256": predictions_sha,
            "runtime_manifest_sha256": runtime_sha,
            "frozen_before_ground_truth_comparison": True,
            "promotion_allowed": False,
        }
        self._write(self.root / "agent06_frozen_output_hashes.json", frozen)

        readiness = {
            "total_cases": 3,
            "unique_locators": 3,
            "resolved_cases": 3,
            "missing_locators": [],
            "invalid_context_locators": [],
            "image_required_cases": 2,
            "image_missing_locators": [],
            "provider_configured": True,
            "model_configured": True,
            "multimodal_supported": True,
            "ready_to_run": True,
            "blockers": [],
            "status": "READY_TO_RUN",
        }
        self._write(self.root / "agent06_readiness.json", readiness)

        comparison = {
            "version": 1,
            "run_id": self.run_id,
            "model_provider": "anthropic",
            "model_name": "claude-sonnet-5",
            "packet_sha256": self.packet_sha,
            "predictions_sha256": predictions_sha,
            "outcomes": [{"result": "AGREE"}, {"result": "AMBIGUOUS"}, {"result": "AGREE"}],
            "agree": 2,
            "disagree": 0,
            "ambiguous": 1,
            "total": 3,
            "all_agree": False,
            "comparison_performed_after_blind_run": True,
            "promotion_allowed": False,
        }
        comparison_path = self.root / "agent06_comparison.json"
        self._write(comparison_path, comparison)

        summary = {
            "status": "LOCAL_AGENT06_PIPELINE_COMPLETE",
            "run_id": self.run_id,
            "repo_commit": self.repo_commit,
            "provider": "anthropic",
            "model": "claude-sonnet-5",
            "bundle_sha256": agent06_audit_cli._EXPECTED_BUNDLE_SHA256,
            "primary_context_manifest_sha256": agent06_audit_cli._EXPECTED_MANIFEST_SHA256,
            "predictions_sha256": predictions_sha,
            "runtime_manifest_sha256": runtime_sha,
            "run_root": str(self.root.resolve()),
            "comparison_path": str(comparison_path.resolve()),
            "api_key_written_to_disk": False,
            "blind_process_loaded_ground_truth": False,
            "promotion_allowed": False,
        }
        self._write(self.root / "agent06_local_pipeline_summary.json", summary)

    def test_complete_consistent_run_passes_without_promotion(self) -> None:
        self._build_valid_run()
        report = agent06_audit_cli.audit_agent06_run(
            run_root=self.root,
            expected_case_count=3,
            expected_repo_commit=self.repo_commit,
        )
        self.assertEqual(report["status"], "AUDIT_PASS")
        self.assertTrue(report["artifact_integrity_passed"])
        self.assertFalse(report["promotion_allowed"])
        self.assertFalse(report["independent_validation_auto_promoted"])
        self.assertEqual(report["runtime_abstained_count"], 1)
        self.assertEqual(report["runtime_image_case_count"], 2)
        self.assertEqual(report["ambiguous"], 1)
        self.assertEqual(report["blockers"], [])

    def test_tampered_predictions_are_detected_against_frozen_hash(self) -> None:
        self._build_valid_run()
        path = self.root / "agent06_blind_predictions.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["decisions"][0]["evidence"] = ["mutated after freeze"]
        self._write(path, payload)
        report = agent06_audit_cli.audit_agent06_run(run_root=self.root, expected_case_count=3)
        self.assertEqual(report["status"], "AUDIT_FAIL")
        self.assertTrue(any("predictions SHA-256" in blocker for blocker in report["blockers"]))

    def test_any_promotion_flag_true_is_rejected(self) -> None:
        self._build_valid_run()
        path = self.root / "agent06_comparison.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["promotion_allowed"] = True
        self._write(path, payload)
        report = agent06_audit_cli.audit_agent06_run(run_root=self.root, expected_case_count=3)
        self.assertEqual(report["status"], "AUDIT_FAIL")
        self.assertIn("comparison must keep promotion disabled", report["blockers"])

    def test_explicit_repo_commit_mismatch_is_rejected(self) -> None:
        self._build_valid_run()
        report = agent06_audit_cli.audit_agent06_run(
            run_root=self.root,
            expected_case_count=3,
            expected_repo_commit="a" * 40,
        )
        self.assertEqual(report["status"], "AUDIT_FAIL")
        self.assertIn("repo_commit does not match the explicitly expected commit", report["blockers"])

    def test_missing_required_artifact_fails_closed(self) -> None:
        self._build_valid_run()
        (self.root / "agent06_runtime_manifest.json").unlink()
        report = agent06_audit_cli.audit_agent06_run(run_root=self.root, expected_case_count=3)
        self.assertEqual(report["status"], "AUDIT_FAIL")
        self.assertIn("missing required artifact: agent06_runtime_manifest.json", report["blockers"])

    def test_runtime_abstained_count_must_match_frozen_predictions(self) -> None:
        self._build_valid_run()
        path = self.root / "agent06_runtime_manifest.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["abstained_count"] = 0
        self._write(path, payload)
        report = agent06_audit_cli.audit_agent06_run(run_root=self.root, expected_case_count=3)
        self.assertEqual(report["status"], "AUDIT_FAIL")
        self.assertIn(
            "runtime manifest abstained_count does not match frozen predictions",
            report["blockers"],
        )

    def test_runtime_image_count_must_match_per_case_evidence(self) -> None:
        self._build_valid_run()
        path = self.root / "agent06_runtime_manifest.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["image_case_count"] = 1
        self._write(path, payload)
        report = agent06_audit_cli.audit_agent06_run(run_root=self.root, expected_case_count=3)
        self.assertEqual(report["status"], "AUDIT_FAIL")
        self.assertIn(
            "runtime manifest image_case_count does not match per-case evidence metadata",
            report["blockers"],
        )

    def test_runtime_image_metadata_cannot_leak_local_path(self) -> None:
        self._build_valid_run()
        path = self.root / "agent06_runtime_manifest.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cases"][0]["images"][0]["local_path"] = "/private/source.png"
        self._write(path, payload)
        report = agent06_audit_cli.audit_agent06_run(run_root=self.root, expected_case_count=3)
        self.assertEqual(report["status"], "AUDIT_FAIL")
        self.assertTrue(
            any("leaks path-like fields" in blocker for blocker in report["blockers"])
        )

    def test_runtime_image_hash_and_size_are_validated(self) -> None:
        self._build_valid_run()
        path = self.root / "agent06_runtime_manifest.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cases"][0]["images"][0]["sha256"] = "not-a-hash"
        payload["cases"][0]["images"][0]["size_bytes"] = 0
        self._write(path, payload)
        report = agent06_audit_cli.audit_agent06_run(run_root=self.root, expected_case_count=3)
        self.assertEqual(report["status"], "AUDIT_FAIL")
        self.assertTrue(any("image SHA-256 is invalid" in blocker for blocker in report["blockers"]))
        self.assertTrue(any("image size is invalid" in blocker for blocker in report["blockers"]))


if __name__ == "__main__":
    unittest.main()
