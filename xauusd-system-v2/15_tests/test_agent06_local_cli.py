from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from xauusd_v2 import agent06_local_cli


class Agent06LocalCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_safe_extract_rejects_path_traversal(self) -> None:
        bundle = self.root / "bad.zip"
        with zipfile.ZipFile(bundle, "w") as archive:
            archive.writestr("../escape.txt", "bad")
        destination = self.root / "out"
        with self.assertRaisesRegex(ValueError, "unsafe ZIP path"):
            agent06_local_cli._safe_extract_zip(bundle, destination)
        self.assertFalse(destination.exists())
        self.assertFalse((self.root.parent / "escape.txt").exists())

    def test_safe_extract_rejects_symbolic_links(self) -> None:
        bundle = self.root / "bad.zip"
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(bundle, "w") as archive:
            archive.writestr(info, "target")
        with self.assertRaisesRegex(ValueError, "symbolic links"):
            agent06_local_cli._safe_extract_zip(bundle, self.root / "out")

    def test_private_bundle_inside_public_repo_is_rejected(self) -> None:
        repo = self.root / "repo"
        (repo / "xauusd-system-v2" / "15_tests").mkdir(parents=True)
        bundle = repo / "private.zip"
        bundle.write_bytes(b"zip")
        with self.assertRaisesRegex(SystemExit, "must remain outside"):
            agent06_local_cli.main([
                "--bundle", str(bundle),
                "--model", "claude-sonnet-5",
                "--repo-root", str(repo),
                "--work-root", str(self.root / "work"),
            ])

    def test_secret_is_present_only_in_blind_provider_stage(self) -> None:
        repo = self.root / "repo"
        (repo / "xauusd-system-v2" / "15_tests").mkdir(parents=True)
        bundle = self.root / "private.zip"
        bundle.write_bytes(b"bundle")
        work = self.root / "private-work"
        stages: list[tuple[str, dict[str, str]]] = []

        def fake_extract(_source: Path, destination: Path) -> None:
            destination.mkdir(parents=True)
            (destination / "primary_context_bundle.json").write_text("{}", encoding="utf-8")

        def fake_hash(path: Path) -> str:
            if path == bundle:
                return agent06_local_cli._EXPECTED_BUNDLE_SHA256
            if path.name == "primary_context_bundle.json":
                return agent06_local_cli._EXPECTED_MANIFEST_SHA256
            return "a" * 64

        def has_module(command, module_name: str) -> bool:
            return any(str(part).endswith(module_name) for part in command)

        def fake_stage(command, *, cwd, environment, stage):
            stages.append((stage, dict(environment)))
            if has_module(command, "agent06_packet_cli"):
                output = Path(command[command.index("--output") + 1])
                output.write_text("{}", encoding="utf-8")
            elif has_module(command, "agent06_run_cli"):
                output_dir = Path(command[command.index("--output-dir") + 1])
                output_dir.mkdir(parents=True)
                (output_dir / "agent06_blind_predictions.json").write_text("{}", encoding="utf-8")
                (output_dir / "agent06_runtime_manifest.json").write_text("{}", encoding="utf-8")
            elif has_module(command, "agent06_compare_cli"):
                output = Path(command[command.index("--output") + 1])
                output.write_text("{}", encoding="utf-8")

        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "super-secret",
                "XAUUSD_AGENT06_ANTHROPIC_MODEL": "old-model",
            },
            clear=False,
        ), patch.object(agent06_local_cli, "_safe_extract_zip", side_effect=fake_extract), patch.object(
            agent06_local_cli, "_sha256_file", side_effect=fake_hash
        ), patch.object(agent06_local_cli, "_git_head", return_value="b" * 40), patch.object(
            agent06_local_cli, "_run_stage", side_effect=fake_stage
        ):
            code = agent06_local_cli.main([
                "--bundle", str(bundle),
                "--model", "claude-sonnet-5",
                "--repo-root", str(repo),
                "--work-root", str(work),
            ])

        self.assertEqual(code, 0)
        self.assertEqual(len(stages), 3)
        packet_env = stages[0][1]
        blind_env = stages[1][1]
        compare_env = stages[2][1]
        self.assertNotIn("ANTHROPIC_API_KEY", packet_env)
        self.assertNotIn("XAUUSD_AGENT06_ANTHROPIC_MODEL", packet_env)
        self.assertEqual(blind_env["ANTHROPIC_API_KEY"], "super-secret")
        self.assertEqual(blind_env["XAUUSD_AGENT06_ANTHROPIC_MODEL"], "claude-sonnet-5")
        self.assertNotIn("ANTHROPIC_API_KEY", compare_env)
        self.assertNotIn("XAUUSD_AGENT06_ANTHROPIC_MODEL", compare_env)
        summary_files = list((work / "runs").glob("*/agent06_local_pipeline_summary.json"))
        self.assertEqual(len(summary_files), 1)
        serialized = summary_files[0].read_text(encoding="utf-8")
        self.assertNotIn("super-secret", serialized)
        self.assertFalse(json.loads(serialized)["api_key_written_to_disk"])

    def test_one_command_resume_reuses_run_and_passes_resume_existing(self) -> None:
        repo = self.root / "repo"
        (repo / "xauusd-system-v2" / "15_tests").mkdir(parents=True)
        bundle = self.root / "private.zip"
        bundle.write_bytes(b"bundle")
        work = self.root / "private-work"
        run_id = "agent06-anthropic-20260902T200000Z"
        run_root = work / "runs" / run_id
        run_root.mkdir(parents=True)
        (run_root / "agent06_blind_checkpoint.json").write_text("{}", encoding="utf-8")
        seen_commands: list[list[str]] = []

        def fake_extract(_source: Path, destination: Path) -> None:
            destination.mkdir(parents=True)
            (destination / "primary_context_bundle.json").write_text("{}", encoding="utf-8")

        def fake_hash(path: Path) -> str:
            if path == bundle:
                return agent06_local_cli._EXPECTED_BUNDLE_SHA256
            if path.name == "primary_context_bundle.json":
                return agent06_local_cli._EXPECTED_MANIFEST_SHA256
            return "a" * 64

        def has_module(command, module_name: str) -> bool:
            return any(str(part).endswith(module_name) for part in command)

        def fake_stage(command, *, cwd, environment, stage):
            seen_commands.append(list(command))
            if has_module(command, "agent06_packet_cli"):
                output = Path(command[command.index("--output") + 1])
                output.write_text("{}", encoding="utf-8")
            elif has_module(command, "agent06_run_cli"):
                self.assertIn("--resume-existing", command)
                self.assertEqual(command[command.index("--run-id") + 1], run_id)
                self.assertEqual(Path(command[command.index("--output-dir") + 1]), run_root)
                (run_root / "agent06_blind_predictions.json").write_text("{}", encoding="utf-8")
                (run_root / "agent06_runtime_manifest.json").write_text("{}", encoding="utf-8")
            elif has_module(command, "agent06_compare_cli"):
                output = Path(command[command.index("--output") + 1])
                output.write_text("{}", encoding="utf-8")

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "super-secret"}, clear=False), patch.object(
            agent06_local_cli, "_safe_extract_zip", side_effect=fake_extract
        ), patch.object(agent06_local_cli, "_sha256_file", side_effect=fake_hash), patch.object(
            agent06_local_cli, "_git_head", return_value="b" * 40
        ), patch.object(agent06_local_cli, "_run_stage", side_effect=fake_stage):
            code = agent06_local_cli.main([
                "--bundle", str(bundle),
                "--model", "claude-sonnet-5",
                "--repo-root", str(repo),
                "--work-root", str(work),
                "--resume-run-id", run_id,
            ])

        self.assertEqual(code, 0)
        self.assertEqual(len(seen_commands), 3)
        self.assertEqual(list((work / "runs").iterdir()), [run_root])
        summary = json.loads((run_root / "agent06_local_pipeline_summary.json").read_text(encoding="utf-8"))
        self.assertTrue(summary["resumed"])
        self.assertEqual(summary["run_id"], run_id)
        self.assertFalse(summary["promotion_allowed"])

    def test_live_smoke_uses_three_cases_keeps_full_taxonomy_and_skips_comparison(self) -> None:
        repo = self.root / "repo"
        (repo / "xauusd-system-v2" / "15_tests").mkdir(parents=True)
        bundle = self.root / "private.zip"
        bundle.write_bytes(b"bundle")
        work = self.root / "private-work"
        seen_commands: list[list[str]] = []

        def fake_extract(_source: Path, destination: Path) -> None:
            destination.mkdir(parents=True)
            (destination / "primary_context_bundle.json").write_text("{}", encoding="utf-8")

        def fake_hash(path: Path) -> str:
            if path == bundle:
                return agent06_local_cli._EXPECTED_BUNDLE_SHA256
            if path.name == "primary_context_bundle.json":
                return agent06_local_cli._EXPECTED_MANIFEST_SHA256
            return "d" * 64

        def has_module(command, module_name: str) -> bool:
            return any(str(part).endswith(module_name) for part in command)

        def fake_stage(command, *, cwd, environment, stage):
            seen_commands.append(list(command))
            if has_module(command, "agent06_packet_cli"):
                output = Path(command[command.index("--output") + 1])
                output.write_text(
                    json.dumps(
                        {
                            "version": 1,
                            "dataset_name": "blind",
                            "taxonomy": [f"label_{index:03d}" for index in range(173)],
                            "cases": [
                                {"vector_id": f"GT-{index}", "source_locator": f"source-{index}"}
                                for index in range(10)
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
            elif has_module(command, "agent06_run_cli"):
                smoke_packet = Path(command[command.index("--packet") + 1])
                payload = json.loads(smoke_packet.read_text(encoding="utf-8"))
                self.assertEqual(len(payload["cases"]), 3)
                self.assertEqual(len(payload["taxonomy"]), 173)
                output_dir = Path(command[command.index("--output-dir") + 1])
                self.assertIn("smoke-runs", output_dir.parts)
                output_dir.mkdir(parents=True)
                (output_dir / "agent06_blind_predictions.json").write_text("{}", encoding="utf-8")
                (output_dir / "agent06_runtime_manifest.json").write_text("{}", encoding="utf-8")
            elif has_module(command, "agent06_compare_cli"):
                self.fail("smoke mode must never perform ground-truth comparison")

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "super-secret"}, clear=False), patch.object(
            agent06_local_cli, "_safe_extract_zip", side_effect=fake_extract
        ), patch.object(agent06_local_cli, "_sha256_file", side_effect=fake_hash), patch.object(
            agent06_local_cli, "_git_head", return_value="c" * 40
        ), patch.object(agent06_local_cli, "_run_stage", side_effect=fake_stage):
            code = agent06_local_cli.main([
                "--bundle", str(bundle),
                "--model", "claude-sonnet-5",
                "--repo-root", str(repo),
                "--work-root", str(work),
                "--smoke-cases", "3",
            ])

        self.assertEqual(code, 0)
        self.assertEqual(len(seen_commands), 2)
        smoke_summaries = list((work / "smoke-runs").glob("*/agent06_live_smoke_summary.json"))
        self.assertEqual(len(smoke_summaries), 1)
        summary = json.loads(smoke_summaries[0].read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "AGENT06_LIVE_SMOKE_PASS")
        self.assertEqual(summary["smoke_case_count"], 3)
        self.assertEqual(summary["taxonomy_count"], 173)
        self.assertFalse(summary["ground_truth_comparison_performed"])
        self.assertFalse(summary["promotion_allowed"])
        self.assertFalse(summary["api_key_written_to_disk"])

    def test_smoke_mode_cannot_be_combined_with_resume(self) -> None:
        with self.assertRaisesRegex(SystemExit, "cannot be combined"):
            agent06_local_cli.main([
                "--bundle", str(self.root / "unused.zip"),
                "--model", "claude-sonnet-5",
                "--resume-run-id", "agent06-anthropic-20260902T200000Z",
                "--smoke-cases", "3",
            ])


if __name__ == "__main__":
    unittest.main()
