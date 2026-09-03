from __future__ import annotations

import json
import unittest

from test_agent06_audit_cli import Agent06AuditCliTests
from xauusd_v2 import agent06_audit_cli, agent06_audit_v2_cli


class Agent06AuditV2CliTests(unittest.TestCase):
    def _fixture(self) -> Agent06AuditCliTests:
        helper = Agent06AuditCliTests(methodName="test_complete_consistent_run_passes_without_promotion")
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        helper._build_valid_run()
        return helper

    @staticmethod
    def _rewrite_runtime_hashes(helper: Agent06AuditCliTests) -> None:
        runtime_path = helper.root / "agent06_runtime_manifest.json"
        runtime_sha = helper._sha(runtime_path)

        frozen_path = helper.root / "agent06_frozen_output_hashes.json"
        frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
        frozen["runtime_manifest_sha256"] = runtime_sha
        helper._write(frozen_path, frozen)

        summary_path = helper.root / "agent06_local_pipeline_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["runtime_manifest_sha256"] = runtime_sha
        helper._write(summary_path, summary)

    def test_extra_resolved_image_case_is_not_confused_with_explicit_image_requirement(self) -> None:
        helper = self._fixture()
        runtime_path = helper.root / "agent06_runtime_manifest.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime["cases"][2]["images"] = [
            {"mime_type": "image/png", "sha256": "4" * 64, "size_bytes": 30}
        ]
        runtime["image_case_count"] = 3
        helper._write(runtime_path, runtime)
        self._rewrite_runtime_hashes(helper)

        legacy = agent06_audit_cli.audit_agent06_run(
            run_root=helper.root,
            expected_case_count=3,
            expected_repo_commit=helper.repo_commit,
        )
        self.assertEqual(legacy["status"], "AUDIT_FAIL")
        self.assertEqual(
            legacy["blockers"],
            ["readiness image-required count does not match runtime image-evidence count"],
        )

        fixed = agent06_audit_v2_cli.audit_agent06_run(
            run_root=helper.root,
            expected_case_count=3,
            expected_repo_commit=helper.repo_commit,
        )
        self.assertEqual(fixed["status"], "AUDIT_PASS")
        self.assertTrue(fixed["artifact_integrity_passed"])
        self.assertEqual(fixed["blockers"], [])
        self.assertEqual(fixed["image_audit_semantics"], "locator-required-subset-v2")
        self.assertFalse(fixed["promotion_allowed"])

    def test_explicit_image_required_case_without_image_still_fails_closed(self) -> None:
        helper = self._fixture()
        runtime_path = helper.root / "agent06_runtime_manifest.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime["cases"][1]["images"] = []
        runtime["cases"][1]["source_text_sha256"] = "5" * 64
        runtime["image_case_count"] = 1
        helper._write(runtime_path, runtime)
        self._rewrite_runtime_hashes(helper)

        fixed = agent06_audit_v2_cli.audit_agent06_run(
            run_root=helper.root,
            expected_case_count=3,
            expected_repo_commit=helper.repo_commit,
        )
        self.assertEqual(fixed["status"], "AUDIT_FAIL")
        self.assertFalse(fixed["artifact_integrity_passed"])
        self.assertTrue(
            any("explicit image-required locator has no runtime image evidence" in item for item in fixed["blockers"])
        )
        self.assertFalse(fixed["promotion_allowed"])

    def test_unrelated_legacy_integrity_failure_is_never_cleared(self) -> None:
        helper = self._fixture()
        comparison_path = helper.root / "agent06_comparison.json"
        comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
        comparison["promotion_allowed"] = True
        helper._write(comparison_path, comparison)

        fixed = agent06_audit_v2_cli.audit_agent06_run(
            run_root=helper.root,
            expected_case_count=3,
        )
        self.assertEqual(fixed["status"], "AUDIT_FAIL")
        self.assertIn("comparison must keep promotion disabled", fixed["blockers"])
        self.assertFalse(fixed["promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
