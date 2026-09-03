from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from xauusd_v2 import agent06_locator_set_review_cli


class Agent06LocatorSetReviewCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.run_root = root / "run"
        self.datasets_dir = root / "datasets"
        self.run_root.mkdir()
        self.datasets_dir.mkdir()
        self.repo_commit = "a" * 40
        self.packet_sha = "b" * 64
        self.taxonomy_sha = "c" * 64

    @staticmethod
    def _write(path: Path, payload: object) -> None:
        path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    def _build_fixture(self) -> None:
        self._write(
            self.datasets_dir / "ground_truth_round_02.json",
            {
                "dataset": "fixture",
                "status": "candidate_not_verified",
                "source_episode": "fixture",
                "promotion_allowed": False,
                "test_vectors": [
                    {
                        "id": "GT-R02-001",
                        "source_locator": "same#image:1",
                        "expected_label": "A",
                        "expected_class": "valid",
                        "evidence": ["a"],
                        "forbidden_inference": "",
                    },
                    {
                        "id": "GT-R02-002",
                        "source_locator": "same#image:1",
                        "expected_label": "B",
                        "expected_class": "valid",
                        "evidence": ["b"],
                        "forbidden_inference": "",
                    },
                    {
                        "id": "GT-R02-003",
                        "source_locator": "other#image:2",
                        "expected_label": "C",
                        "expected_class": "edge_case",
                        "evidence": ["c"],
                        "forbidden_inference": "",
                    },
                ],
            },
        )
        self._write(
            self.run_root / "agent06_blind_predictions.json",
            {
                "version": 1,
                "run_id": "agent06-anthropic-fixture",
                "model_provider": "anthropic",
                "model_name": "claude-sonnet-5",
                "packet_sha256": self.packet_sha,
                "taxonomy_sha256": self.taxonomy_sha,
                "case_count": 3,
                "decisions": [
                    {
                        "vector_id": "GT-R02-001",
                        "source_locator": "same#image:1",
                        "predicted_label": "B",
                        "confidence": 0.9,
                        "evidence": ["supports B"],
                        "ambiguities": [],
                    },
                    {
                        "vector_id": "GT-R02-002",
                        "source_locator": "same#image:1",
                        "predicted_label": "B",
                        "confidence": 0.8,
                        "evidence": ["supports B"],
                        "ambiguities": [],
                    },
                    {
                        "vector_id": "GT-R02-003",
                        "source_locator": "other#image:2",
                        "predicted_label": None,
                        "confidence": 0.2,
                        "evidence": [],
                        "ambiguities": ["unclear"],
                    },
                ],
                "ground_truth_loaded_by_this_process": False,
                "comparison_performed_by_this_process": False,
                "promotion_allowed": False,
            },
        )
        self._write(
            self.run_root / "agent06_comparison.json",
            {
                "agree": 1,
                "disagree": 1,
                "ambiguous": 1,
                "total": 3,
                "outcomes": [
                    {
                        "vector_id": "GT-R02-001",
                        "result": "DISAGREE",
                        "expected_label": "A",
                        "predicted_label": "B",
                    },
                    {
                        "vector_id": "GT-R02-002",
                        "result": "AGREE",
                        "expected_label": "B",
                        "predicted_label": "B",
                    },
                    {
                        "vector_id": "GT-R02-003",
                        "result": "AMBIGUOUS",
                        "expected_label": "C",
                        "predicted_label": None,
                    },
                ],
            },
        )

    def test_same_locator_alternate_ground_truth_label_is_not_true_disagreement(self) -> None:
        self._build_fixture()
        with mock.patch.object(
            agent06_locator_set_review_cli,
            "audit_agent06_run",
            return_value={"status": "AUDIT_PASS"},
        ):
            report = agent06_locator_set_review_cli.build_locator_set_review(
                run_root=self.run_root,
                datasets_dir=self.datasets_dir,
                expected_case_count=3,
                expected_repo_commit=self.repo_commit,
                rounds=(2,),
            )
        self.assertEqual(report["exact_agree"], 1)
        self.assertEqual(report["locator_set_agree"], 1)
        self.assertEqual(report["unresolved_disagree"], 0)
        self.assertEqual(report["abstain"], 1)
        self.assertEqual(report["multi_label_locator_count"], 1)
        self.assertEqual(report["multi_label_case_count"], 2)
        collision = next(
            case for case in report["cases"] if case["vector_id"] == "GT-R02-001"
        )
        self.assertEqual(collision["adjusted_result"], "LOCATOR_SET_AGREE")
        self.assertEqual(collision["all_ground_truth_labels_for_locator"], ["A", "B"])
        self.assertFalse(report["promotion_allowed"])
        self.assertFalse(report["strategy_truth_changed"])

    def test_audit_fail_blocks_locator_set_review(self) -> None:
        self._build_fixture()
        with mock.patch.object(
            agent06_locator_set_review_cli,
            "audit_agent06_run",
            return_value={"status": "AUDIT_FAIL"},
        ):
            with self.assertRaisesRegex(ValueError, "must pass corrected artifact audit"):
                agent06_locator_set_review_cli.build_locator_set_review(
                    run_root=self.run_root,
                    datasets_dir=self.datasets_dir,
                    expected_case_count=3,
                    rounds=(2,),
                )


if __name__ == "__main__":
    unittest.main()
