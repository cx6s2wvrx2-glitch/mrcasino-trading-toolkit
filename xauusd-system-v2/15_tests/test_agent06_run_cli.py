from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.agent06_run_cli import _parser, main
from xauusd_v2.agents.base import AgentContractError
from xauusd_v2.blind_validation_packet import BlindValidationCase, BlindValidationPacket
from xauusd_v2.blind_validation_packet_io import write_blind_packet


class Agent06RunCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / "bundle"
        self.bundle.mkdir()
        (self.bundle / "text").mkdir()
        (self.bundle / "text" / "a.txt").write_text("primary A", encoding="utf-8")
        (self.bundle / "text" / "b.txt").write_text("primary B", encoding="utf-8")
        self.packet_path = self.root / "packet.json"
        write_blind_packet(
            BlindValidationPacket(
                dataset_name="blind",
                taxonomy=("label_a", "label_b"),
                cases=(
                    BlindValidationCase(vector_id="GT-A", source_locator="source#a"),
                    BlindValidationCase(vector_id="GT-B", source_locator="source#b"),
                ),
            ),
            self.packet_path,
        )
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text(
            json.dumps({
                "version": 1,
                "entries": [
                    {"source_locator": "source#a", "text_path": "text/a.txt"},
                    {"source_locator": "source#b", "text_path": "text/b.txt"},
                ],
            }),
            encoding="utf-8",
        )
        self.wrapper = self.root / "wrapper.py"
        self.wrapper.write_text(
            "import json,sys\n"
            "request=json.load(sys.stdin)\n"
            "assert 'expected_label' not in json.dumps(request)\n"
            "json.dump({'predicted_label':'label_a','confidence':0.75,'evidence':['primary'],'ambiguities':[]},sys.stdout)\n",
            encoding="utf-8",
        )

    @staticmethod
    def _last_json_line(text: str) -> dict:
        lines = [line for line in text.splitlines() if line.strip()]
        return json.loads(lines[-1])

    def _base_args(self, *, output_dir: Path, wrapper: Path | None = None) -> list[str]:
        return [
            "--packet", str(self.packet_path),
            "--bundle-root", str(self.bundle),
            "--manifest", str(self.manifest),
            "--provider", "provider-x",
            "--model", "model-y",
            "--run-id", "run-1",
            "--output-dir", str(output_dir),
            "--command", sys.executable, str(wrapper or self.wrapper),
        ]

    def test_command_remainder_preserves_python_module_flags(self) -> None:
        args = _parser().parse_args([
            "--packet", "packet.json",
            "--bundle-root", "bundle",
            "--manifest", "manifest.json",
            "--provider", "anthropic",
            "--model", "claude-sonnet-5",
            "--run-id", "run-module",
            "--output-dir", "output",
            "--command", sys.executable, "-m", "xauusd_v2.anthropic_model_runner",
        ])
        self.assertEqual(
            args.command,
            [sys.executable, "-m", "xauusd_v2.anthropic_model_runner"],
        )

    def test_blind_run_writes_outputs_without_ground_truth_or_comparison(self) -> None:
        output_dir = self.root / "run"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(self._base_args(output_dir=output_dir))
        self.assertEqual(code, 0)
        summary = self._last_json_line(stdout.getvalue())
        self.assertEqual(summary["status"], "BLIND_RUN_COMPLETE")
        self.assertEqual(summary["resumed_count"], 0)
        self.assertFalse(summary["comparison_performed"])
        predictions = json.loads((output_dir / "agent06_blind_predictions.json").read_text(encoding="utf-8"))
        self.assertFalse(predictions["ground_truth_loaded_by_this_process"])
        self.assertFalse(predictions["comparison_performed_by_this_process"])
        self.assertFalse(predictions["promotion_allowed"])
        self.assertEqual(len(predictions["decisions"]), 2)
        self.assertNotIn("expected_label", json.dumps(predictions))
        checkpoint = json.loads((output_dir / "agent06_blind_checkpoint.json").read_text(encoding="utf-8"))
        self.assertEqual(checkpoint["completed_count"], 2)
        self.assertFalse(checkpoint["promotion_allowed"])

    def test_interrupted_run_resumes_without_recalling_completed_case(self) -> None:
        output_dir = self.root / "resume-run"
        calls = self.root / "calls.txt"
        fail_once = self.root / "fail-once.txt"
        wrapper = self.root / "resume_wrapper.py"
        wrapper.write_text(
            "import json,sys\n"
            "from pathlib import Path\n"
            f"calls=Path({str(calls)!r})\n"
            f"fail_once=Path({str(fail_once)!r})\n"
            "request=json.load(sys.stdin)\n"
            "user=request['user']\n"
            "vector='GT-A' if 'VECTOR ID: GT-A' in user else 'GT-B'\n"
            "with calls.open('a', encoding='utf-8') as h: h.write(vector+'\\n')\n"
            "if vector == 'GT-B' and not fail_once.exists():\n"
            "    fail_once.write_text('failed', encoding='utf-8')\n"
            "    print('model-runner-safe-error: TEST_PROVIDER_FAILURE', file=sys.stderr)\n"
            "    raise SystemExit(2)\n"
            "json.dump({'predicted_label':'label_a','confidence':0.75,'evidence':['primary'],'ambiguities':[]},sys.stdout)\n",
            encoding="utf-8",
        )
        args = self._base_args(output_dir=output_dir, wrapper=wrapper)
        with self.assertRaises(AgentContractError):
            main(args)
        checkpoint = json.loads((output_dir / "agent06_blind_checkpoint.json").read_text(encoding="utf-8"))
        self.assertEqual(checkpoint["completed_count"], 1)
        self.assertEqual([item["decision"]["vector_id"] for item in checkpoint["cases"]], ["GT-A"])
        self.assertFalse((output_dir / "agent06_blind_predictions.json").exists())

        stdout = io.StringIO()
        resume_args = args.copy()
        command_position = resume_args.index("--command")
        resume_args.insert(command_position, "--resume-existing")
        with contextlib.redirect_stdout(stdout):
            code = main(resume_args)
        self.assertEqual(code, 0)
        summary = self._last_json_line(stdout.getvalue())
        self.assertEqual(summary["resumed_count"], 1)
        self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), ["GT-A", "GT-B", "GT-B"])
        predictions = json.loads((output_dir / "agent06_blind_predictions.json").read_text(encoding="utf-8"))
        self.assertEqual(len(predictions["decisions"]), 2)

    def test_resume_rejects_packet_identity_mismatch(self) -> None:
        output_dir = self.root / "resume-mismatch"
        output_dir.mkdir()
        (output_dir / "agent06_blind_checkpoint.json").write_text(
            json.dumps({
                "version": 1,
                "run_id": "run-1",
                "model_provider": "provider-x",
                "model_name": "model-y",
                "packet_sha256": "0" * 64,
                "taxonomy_sha256": "0" * 64,
                "completed_count": 0,
                "cases": [],
                "ground_truth_loaded_by_this_process": False,
                "comparison_performed_by_this_process": False,
                "promotion_allowed": False,
            }),
            encoding="utf-8",
        )
        args = self._base_args(output_dir=output_dir)
        command_position = args.index("--command")
        args.insert(command_position, "--resume-existing")
        with self.assertRaisesRegex(SystemExit, "packet_sha256 mismatch"):
            main(args)

    def test_not_ready_returns_before_external_model_command(self) -> None:
        marker = self.root / "called.txt"
        wrapper = self.root / "should_not_run.py"
        wrapper.write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('called')\n",
            encoding="utf-8",
        )
        self.manifest.write_text(
            json.dumps({
                "version": 1,
                "entries": [{"source_locator": "source#a", "text_path": "text/a.txt"}],
            }),
            encoding="utf-8",
        )
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main([
                "--packet", str(self.packet_path),
                "--bundle-root", str(self.bundle),
                "--manifest", str(self.manifest),
                "--provider", "provider-x",
                "--model", "model-y",
                "--run-id", "run-2",
                "--output-dir", str(self.root / "run2"),
                "--command", sys.executable, str(wrapper),
            ])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "NOT_READY")
        self.assertFalse(marker.exists())

    def test_existing_output_directory_is_never_overwritten(self) -> None:
        output_dir = self.root / "existing"
        output_dir.mkdir()
        with self.assertRaisesRegex(SystemExit, "refusing to overwrite"):
            main(self._base_args(output_dir=output_dir))


if __name__ == "__main__":
    unittest.main()
