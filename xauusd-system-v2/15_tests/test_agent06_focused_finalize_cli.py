from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from xauusd_v2.agent06_focused_finalize_cli import audit_and_finalize
from xauusd_v2.agent06_local_cli import _EXPECTED_BUNDLE_SHA256, _EXPECTED_MANIFEST_SHA256
from xauusd_v2.agent06_run_cli import _taxonomy_sha256
from xauusd_v2.focused_validation_packet import (
    FocusedValidationCase,
    FocusedValidationPacket,
    focused_packet_sha256,
)


class Agent06FocusedFinalizeTests(unittest.TestCase):
    def _write_json(self, path: Path, value: object) -> None:
        path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    def _fixture(self, root: Path) -> tuple[Path, Path, FocusedValidationPacket, dict[str, object]]:
        run_id = "agent06-focus-anthropic-20260903T084504Z"
        run_root = root / run_id
        run_root.mkdir()
        review_path = root / "review.json"
        packet = FocusedValidationPacket(
            dataset_name="fixture",
            cases=(
                FocusedValidationCase("GT-A", "source#a", "claim_a"),
                FocusedValidationCase("GT-B", "source#b", "claim_b"),
            ),
        )
        review: dict[str, object] = {
            "status": "AGENT06_LOCATOR_SET_REVIEW_READY",
            "audit_status": "AUDIT_PASS",
            "run_id": "agent06-anthropic-source",
            "total_cases": 5,
            "exact_agree": 2,
            "locator_set_agree": 1,
            "unresolved_disagree": 1,
            "abstain": 1,
            "promotion_allowed": False,
            "strategy_truth_changed": False,
            "cases": [
                {"vector_id": "GT-C", "adjusted_result": "LOCATOR_SET_AGREE"},
                {"vector_id": "GT-A", "adjusted_result": "UNRESOLVED_DISAGREE"},
                {"vector_id": "GT-B", "adjusted_result": "ABSTAIN"},
            ],
        }
        self._write_json(review_path, review)

        packet_sha = focused_packet_sha256(packet)
        taxonomy_sha = _taxonomy_sha256(packet.verdict_taxonomy)
        decisions = [
            {
                "vector_id": "GT-A",
                "source_locator": "source#a",
                "predicted_label": "SUPPORTED",
                "confidence": 0.9,
                "evidence": ["direct annotation"],
                "ambiguities": [],
            },
            {
                "vector_id": "GT-B",
                "source_locator": "source#b",
                "predicted_label": "INSUFFICIENT",
                "confidence": 0.6,
                "evidence": ["partial annotation"],
                "ambiguities": ["exact relation not explicit"],
            },
        ]
        predictions = {
            "version": 1,
            "protocol": "agent06_focused_claim_adjudication_v2",
            "run_id": run_id,
            "model_provider": "anthropic",
            "model_name": "claude-sonnet-5",
            "packet_sha256": packet_sha,
            "taxonomy_sha256": taxonomy_sha,
            "case_count": 2,
            "decisions": decisions,
            "candidate_claim_visible_to_provider": True,
            "expected_verdict_loaded_by_this_process": False,
            "ground_truth_dataset_loaded_by_this_process": False,
            "comparison_performed_by_this_process": False,
            "promotion_allowed": False,
        }
        runtime_cases = [
            {
                "vector_id": "GT-A",
                "source_locator": "source#a",
                "source_text_sha256": "b" * 64,
                "images": [{"mime_type": "image/png", "sha256": "a" * 64, "size_bytes": 100}],
                "predicted_label": "SUPPORTED",
                "abstained": False,
            },
            {
                "vector_id": "GT-B",
                "source_locator": "source#b",
                "source_text_sha256": None,
                "images": [{"mime_type": "image/jpeg", "sha256": "c" * 64, "size_bytes": 200}],
                "predicted_label": "INSUFFICIENT",
                "abstained": False,
            },
        ]
        runtime = {
            "protocol": "agent06_focused_claim_adjudication_v2",
            "run_id": run_id,
            "model_provider": "anthropic",
            "model_name": "claude-sonnet-5",
            "packet_sha256": packet_sha,
            "taxonomy_sha256": taxonomy_sha,
            "case_count": 2,
            "completed_count": 2,
            "abstained_count": 0,
            "image_case_count": 2,
            "cases": runtime_cases,
            "promotion_allowed": False,
        }
        readiness = {
            "status": "FOCUSED_READY_TO_RUN",
            "ready_to_run": True,
            "blockers": [],
            "total_cases": 2,
            "resolved_cases": 2,
            "provider_configured": True,
            "model_configured": True,
            "multimodal_supported": True,
        }
        checkpoint = {
            "version": 1,
            "run_id": run_id,
            "model_provider": "anthropic",
            "model_name": "claude-sonnet-5",
            "repo_commit": "d" * 40,
            "packet_sha256": packet_sha,
            "taxonomy_sha256": taxonomy_sha,
            "completed_count": 2,
            "cases": [
                {"decision": decisions[0], "audit": runtime_cases[0]},
                {"decision": decisions[1], "audit": runtime_cases[1]},
            ],
            "ground_truth_loaded_by_this_process": False,
            "comparison_performed_by_this_process": False,
            "promotion_allowed": False,
        }
        self._write_json(run_root / "agent06_focused_predictions.json", predictions)
        self._write_json(run_root / "agent06_focused_runtime_manifest.json", runtime)
        self._write_json(run_root / "agent06_focused_readiness.json", readiness)
        self._write_json(run_root / "agent06_focused_checkpoint.json", checkpoint)

        import hashlib
        predictions_sha = hashlib.sha256((run_root / "agent06_focused_predictions.json").read_bytes()).hexdigest()
        runtime_sha = hashlib.sha256((run_root / "agent06_focused_runtime_manifest.json").read_bytes()).hexdigest()
        review_sha = hashlib.sha256(review_path.read_bytes()).hexdigest()
        summary = {
            "status": "AGENT06_FOCUSED_ADJUDICATION_COMPLETE",
            "run_id": run_id,
            "repo_commit": "d" * 40,
            "provider": "anthropic",
            "model": "claude-sonnet-5",
            "case_count": 2,
            "full_target_case_count": 2,
            "verdict_counts": {"SUPPORTED": 1, "CONTRADICTED": 0, "INSUFFICIENT": 1},
            "provider_abstain_count": 0,
            "bundle_sha256": _EXPECTED_BUNDLE_SHA256,
            "primary_context_manifest_sha256": _EXPECTED_MANIFEST_SHA256,
            "source_review_sha256": review_sha,
            "predictions_sha256": predictions_sha,
            "runtime_manifest_sha256": runtime_sha,
            "candidate_claim_visible_to_provider": True,
            "expected_verdict_supplied_to_provider": False,
            "ground_truth_evidence_supplied_to_provider": False,
            "ground_truth_expected_class_supplied_to_provider": False,
            "ground_truth_forbidden_inference_supplied_to_provider": False,
            "provider_execution_process_loaded_ground_truth_dataset": False,
            "api_key_written_to_disk": False,
            "promotion_allowed": False,
        }
        self._write_json(run_root / "agent06_focused_adjudication_summary.json", summary)
        return run_root, review_path, packet, review

    def test_consistent_focused_run_finalizes_without_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run_root, review_path, packet, review = self._fixture(root)
            with patch(
                "xauusd_v2.agent06_focused_finalize_cli.build_targeted_packet",
                return_value=(packet, {"UNRESOLVED_DISAGREE": 1, "ABSTAIN": 1}, review),
            ):
                report = audit_and_finalize(
                    run_root=run_root,
                    review_path=review_path,
                    datasets_dir=root,
                    expected_provider="anthropic",
                    expected_model="claude-sonnet-5",
                    expected_case_count=2,
                    expected_repo_commit="d" * 40,
                )
            self.assertEqual(report["status"], "AGENT06_FOCUSED_FINALIZE_PASS")
            self.assertEqual(report["v1_exact_agree"], 2)
            self.assertEqual(report["v1_locator_collision_neutral"], 1)
            self.assertEqual(report["v2_focused_supported"], 1)
            self.assertEqual(report["v2_focused_insufficient"], 1)
            self.assertEqual(report["v2_focused_contradicted"], 0)
            self.assertFalse(report["provider_calls_performed_by_finalizer"])
            self.assertFalse(report["promotion_allowed"])
            self.assertFalse(report["strategy_truth_changed"])

    def test_tampered_predictions_fail_finalization(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run_root, review_path, packet, review = self._fixture(root)
            predictions_path = run_root / "agent06_focused_predictions.json"
            predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
            predictions["decisions"][0]["predicted_label"] = "CONTRADICTED"
            self._write_json(predictions_path, predictions)
            with patch(
                "xauusd_v2.agent06_focused_finalize_cli.build_targeted_packet",
                return_value=(packet, {"UNRESOLVED_DISAGREE": 1, "ABSTAIN": 1}, review),
            ):
                report = audit_and_finalize(
                    run_root=run_root,
                    review_path=review_path,
                    datasets_dir=root,
                    expected_provider="anthropic",
                    expected_model="claude-sonnet-5",
                    expected_case_count=2,
                    expected_repo_commit="d" * 40,
                )
            self.assertEqual(report["status"], "AGENT06_FOCUSED_FINALIZE_FAIL")
            self.assertFalse(report["artifact_integrity_passed"])
            self.assertTrue(any("predictions hash mismatch" in item for item in report["blockers"]))


if __name__ == "__main__":
    unittest.main()
