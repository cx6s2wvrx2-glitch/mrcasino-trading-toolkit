from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.agent06_run_cli import _parser, main
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
            code = main([
                "--packet", str(self.packet_path),
                "--bundle-root", str(self.bundle),
                "--manifest", str(self.manifest),
                "--provider", "provider-x",
                "--model", "model-y",
                "--run-id", "run-1",
                "--output-dir", str(output_dir),
                "--command", sys.executable, str(self.wrapper),
            ])
        self.assertEqual(code, 0)
        summary = json.loads(stdout.getvalue())
        self.assertEqual(summary["status"], "BLIND_RUN_COMPLETE")
        self.assertFalse(summary["comparison_performed"])
        predictions = json.loads((output_dir / "agent06_blind_predictions.json").read_text(encoding="utf-8"))
        self.assertFalse(predictions["ground_truth_loaded_by_this_process"])
        self.assertFalse(predictions["comparison_performed_by_this_process"])
        self.assertFalse(predictions["promotion_allowed"])
        self.assertEqual(len(predictions["decisions"]), 2)
        self.assertNotIn("expected_label", json.dumps(predictions))

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
            main([
                "--packet", str(self.packet_path),
                "--bundle-root", str(self.bundle),
                "--manifest", str(self.manifest),
                "--provider", "provider-x",
                "--model", "model-y",
                "--run-id", "run-3",
                "--output-dir", str(output_dir),
                "--command", sys.executable, str(self.wrapper),
            ])


if __name__ == "__main__":
    unittest.main()
