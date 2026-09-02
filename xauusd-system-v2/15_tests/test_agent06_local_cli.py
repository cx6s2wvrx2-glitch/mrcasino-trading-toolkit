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

        def fake_stage(command, *, cwd, environment, stage):
            stages.append((stage, dict(environment)))
            if "agent06_packet_cli" in command:
                output = Path(command[command.index("--output") + 1])
                output.write_text("{}", encoding="utf-8")
            elif "agent06_run_cli" in command:
                output_dir = Path(command[command.index("--output-dir") + 1])
                output_dir.mkdir(parents=True)
                (output_dir / "agent06_blind_predictions.json").write_text("{}", encoding="utf-8")
                (output_dir / "agent06_runtime_manifest.json").write_text("{}", encoding="utf-8")
            elif "agent06_compare_cli" in command:
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


if __name__ == "__main__":
    unittest.main()
