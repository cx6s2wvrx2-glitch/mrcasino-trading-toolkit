from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from xauusd_v2 import agent06_review_cli


class Agent06ReviewCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "run"
        self.root.mkdir(parents=True)
        self.commit = "5" * 40

        predictions = {
            "version": 1,
            "run_id": "agent06-anthropic-test",
            "model_provider": "anthropic",
            "model_name": "claude-sonnet-5",
            "packet_sha256": "a" * 64,
            "taxonomy_sha256": "b" * 64,
            "case_count": 3,
            "decisions": [
                {
                    "vector_id": "GT-R02-001",
                    "source_locator": "source#image:1",
                    "predicted_label": "A",
                    "confidence": 0.95,
                    "evidence": ["e1"],
                    "ambiguities": [],
                },
                {
                    "vector_id": "GT-R10-005",
                    "source_locator": "source#visual:5",
                    "predicted_label": "WRONG",
                    "confidence": 0.91,
                    "evidence": ["e2"],
                    "ambiguities": ["a2"],
                },
                {
                    "vector_id": "GT-R13-026",
                    "source_locator": "source#image:26",
                    "predicted_label": None,
                    "confidence": 0.40,
                    "evidence": [],
                    "ambiguities": ["unclear"],
                },
            ],
            "ground_truth_loaded_by_this_process": False,
            "comparison_performed_by_this_process": False,
            "promotion_allowed": False,
        }
        (self.root / "agent06_blind_predictions.json").write_text(
            json.dumps(predictions), encoding="utf-8"
        )
        comparison = {
            "outcomes": [
                {
                    "vector_id": "GT-R02-001",
                    "result": "AGREE",
                    "expected_label": "A",
                    "predicted_label": "A",
                },
                {
                    "vector_id": "GT-R10-005",
                    "result": "DISAGREE",
                    "expected_label": "B",
                    "predicted_label": "WRONG",
                },
                {
                    "vector_id": "GT-R13-026",
                    "result": "AMBIGUOUS",
                    "expected_label": "C",
                    "predicted_label": None,
                },
            ],
            "agree": 1,
            "disagree": 1,
            "ambiguous": 1,
            "total": 3,
        }
        (self.root / "agent06_comparison.json").write_text(
            json.dumps(comparison), encoding="utf-8"
        )

    @patch("xauusd_v2.agent06_review_cli.audit_agent06_run")
    def test_report_contains_only_non_agree_cases_and_review_priorities(self, audit_mock) -> None:
        audit_mock.return_value = {"status": "AUDIT_PASS"}
        report = agent06_review_cli.build_review_report(
            run_root=self.root,
            expected_repo_commit=self.commit,
            expected_case_count=3,
        )
        self.assertEqual(report["status"], "AGENT06_REVIEW_REPORT_READY")
        self.assertEqual(report["agree"], 1)
        self.assertEqual(report["disagree"], 1)
        self.assertEqual(report["ambiguous"], 1)
        self.assertEqual(report["non_agree_total"], 2)
        self.assertEqual(report["high_confidence_disagreement_count"], 1)
        self.assertEqual(report["by_round"]["R10"]["DISAGREE"], 1)
        self.assertEqual(report["by_round"]["R13"]["AMBIGUOUS"], 1)
        self.assertEqual(report["cases"][0]["vector_id"], "GT-R10-005")
        self.assertEqual(
            report["cases"][0]["review_priority"],
            "HIGH_CONFIDENCE_DISAGREEMENT",
        )
        self.assertEqual(report["cases"][1]["review_priority"], "ABSTENTION_REVIEW")
        self.assertFalse(report["strategy_truth_changed"])
        self.assertFalse(report["promotion_allowed"])

    @patch("xauusd_v2.agent06_review_cli.audit_agent06_run")
    def test_audit_fail_blocks_review(self, audit_mock) -> None:
        audit_mock.return_value = {"status": "AUDIT_FAIL", "blockers": ["x"]}
        with self.assertRaisesRegex(ValueError, "requires AUDIT_PASS"):
            agent06_review_cli.build_review_report(
                run_root=self.root,
                expected_repo_commit=self.commit,
                expected_case_count=3,
            )

    @patch("xauusd_v2.agent06_review_cli.audit_agent06_run")
    def test_comparison_prediction_mismatch_is_rejected(self, audit_mock) -> None:
        audit_mock.return_value = {"status": "AUDIT_PASS"}
        path = self.root / "agent06_comparison.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["outcomes"][1]["predicted_label"] = "DIFFERENT"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "comparison/prediction label mismatch"):
            agent06_review_cli.build_review_report(
                run_root=self.root,
                expected_repo_commit=self.commit,
                expected_case_count=3,
            )


if __name__ == "__main__":
    unittest.main()
