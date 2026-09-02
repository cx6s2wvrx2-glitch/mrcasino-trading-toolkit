from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath


_EXPECTED_BUNDLE_SHA256 = "6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf"
_EXPECTED_MANIFEST_SHA256 = "e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37"
_MANIFEST_NAME = "primary_context_bundle.json"
_RUN_ID_RE = re.compile(r"agent06-anthropic-\d{8}T\d{6}Z")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the complete local XAUUSD Agent-06 independent-validation pipeline while keeping "
            "the private source bundle and Anthropic credential outside the public repository."
        )
    )
    parser.add_argument("--bundle", required=True, help="Private Agent-06 source ZIP.")
    parser.add_argument("--model", required=True, help="Explicit Anthropic model ID, e.g. claude-sonnet-5.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Checkout root containing xauusd-system-v2/. Defaults to the current directory.",
    )
    parser.add_argument(
        "--work-root",
        default=str(Path.home() / ".xauusd-agent06"),
        help="Private working directory outside the Git repository.",
    )
    parser.add_argument(
        "--resume-run-id",
        default="",
        help=(
            "Resume one interrupted run from its private per-case checkpoint. The current Git commit, "
            "packet, taxonomy, provider/model and primary evidence must match the checkpoint exactly."
        ),
    )
    return parser


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _safe_extract_zip(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    destination_resolved = destination.resolve()
    try:
        with zipfile.ZipFile(source) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise ValueError("private bundle contains duplicate ZIP member names")
            for info in infos:
                member = PurePosixPath(info.filename)
                if member.is_absolute() or ".." in member.parts:
                    raise ValueError("private bundle contains unsafe ZIP path")
                unix_mode = (info.external_attr >> 16) & 0xFFFF
                if unix_mode and stat.S_ISLNK(unix_mode):
                    raise ValueError("private bundle contains symbolic links")
                target = (destination / Path(*member.parts)).resolve()
                if not _is_relative_to(target, destination_resolved):
                    raise ValueError("private bundle member escapes extraction directory")
            archive.extractall(destination)
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def _sanitized_environment() -> dict[str, str]:
    environment = dict(os.environ)
    environment.pop("ANTHROPIC_API_KEY", None)
    environment.pop("XAUUSD_AGENT06_ANTHROPIC_MODEL", None)
    return environment


def _run_stage(command: list[str], *, cwd: Path, environment: dict[str, str], stage: str) -> None:
    print(f"[{stage}]", flush=True)
    completed = subprocess.run(command, cwd=cwd, env=environment, check=False)
    if completed.returncode != 0:
        raise SystemExit(f"{stage} failed with exit code {completed.returncode}")


def _git_head(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit("could not resolve Git commit for the supplied repository")
    value = completed.stdout.strip()
    if len(value) != 40:
        raise SystemExit("unexpected Git commit identifier")
    return value


def _load_api_key() -> str:
    existing = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if existing:
        return existing
    value = getpass.getpass("Anthropic API key (hidden; never written to disk): ").strip()
    if not value:
        raise SystemExit("Anthropic API key is required")
    return value


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    bundle = Path(args.bundle).expanduser().resolve()
    repo_root = Path(args.repo_root).expanduser().resolve()
    work_root = Path(args.work_root).expanduser().resolve()
    model = args.model.strip()
    resume_run_id = args.resume_run_id.strip()

    if not model:
        raise SystemExit("explicit Anthropic model is required")
    if not bundle.is_file():
        raise SystemExit("private Agent-06 bundle does not exist")
    project_root = repo_root / "xauusd-system-v2"
    datasets_dir = project_root / "15_tests"
    if not datasets_dir.is_dir():
        raise SystemExit("repo-root must contain xauusd-system-v2/15_tests")
    if _is_relative_to(bundle, repo_root):
        raise SystemExit("private source bundle must remain outside the public Git repository")
    if _is_relative_to(work_root, repo_root):
        raise SystemExit("private work-root must remain outside the public Git repository")

    bundle_sha256 = _sha256_file(bundle)
    if bundle_sha256 != _EXPECTED_BUNDLE_SHA256:
        raise SystemExit(
            f"private bundle SHA-256 mismatch: expected {_EXPECTED_BUNDLE_SHA256}, got {bundle_sha256}"
        )

    repo_commit = _git_head(repo_root)
    if resume_run_id:
        if _RUN_ID_RE.fullmatch(resume_run_id) is None:
            raise SystemExit("resume-run-id has invalid Agent-06 run identifier format")
        run_id = resume_run_id
    else:
        run_id = f"agent06-anthropic-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"

    run_root = work_root / "runs" / run_id
    staging_root = work_root / "staging" / run_id
    evidence_root = staging_root / "evidence"
    packet_path = staging_root / "blind_packet.json"
    work_root.mkdir(parents=True, exist_ok=True)

    if resume_run_id:
        if not run_root.is_dir() or not (run_root / "agent06_blind_checkpoint.json").is_file():
            raise SystemExit("resume-run-id does not contain a resumable private checkpoint")
        if staging_root.exists():
            raise SystemExit("resume staging directory already exists; refusing ambiguous resume")
    else:
        if run_root.exists() or staging_root.exists():
            raise SystemExit("generated run ID already exists; refusing to overwrite")
    staging_root.mkdir(parents=True, exist_ok=False)

    try:
        _safe_extract_zip(bundle, evidence_root)
        manifest = evidence_root / _MANIFEST_NAME
        if not manifest.is_file():
            raise SystemExit("private bundle is missing primary_context_bundle.json")
        manifest_sha256 = _sha256_file(manifest)
        if manifest_sha256 != _EXPECTED_MANIFEST_SHA256:
            raise SystemExit(
                f"primary context manifest SHA-256 mismatch: expected {_EXPECTED_MANIFEST_SHA256}, "
                f"got {manifest_sha256}"
            )

        sanitized_env = _sanitized_environment()
        python = sys.executable
        _run_stage(
            [
                python,
                "-m",
                "xauusd_v2.agent06_packet_cli",
                "--datasets-dir",
                str(datasets_dir),
                "--output",
                str(packet_path),
            ],
            cwd=staging_root,
            environment=sanitized_env,
            stage="1/4 build frozen answer-free packet",
        )

        api_key = _load_api_key()
        blind_env = dict(sanitized_env)
        blind_env["ANTHROPIC_API_KEY"] = api_key
        blind_env["XAUUSD_AGENT06_ANTHROPIC_MODEL"] = model
        blind_command = [
            python,
            "-m",
            "xauusd_v2.agent06_run_cli",
            "--packet",
            str(packet_path),
            "--bundle-root",
            str(evidence_root),
            "--manifest",
            str(manifest),
            "--provider",
            "anthropic",
            "--model",
            model,
            "--run-id",
            run_id,
            "--output-dir",
            str(run_root),
            "--repo-commit",
            repo_commit,
        ]
        if resume_run_id:
            blind_command.append("--resume-existing")
        blind_command.extend(
            [
                "--command",
                python,
                "-m",
                "xauusd_v2.anthropic_model_runner",
            ]
        )
        _run_stage(
            blind_command,
            cwd=staging_root,
            environment=blind_env,
            stage="2/4 execute 173-case isolated blind provider run",
        )
        del api_key
        blind_env.pop("ANTHROPIC_API_KEY", None)
        blind_env.pop("XAUUSD_AGENT06_ANTHROPIC_MODEL", None)

        predictions = run_root / "agent06_blind_predictions.json"
        runtime_manifest = run_root / "agent06_runtime_manifest.json"
        if not predictions.is_file() or not runtime_manifest.is_file():
            raise SystemExit("blind run completed without required frozen outputs")
        predictions_sha256 = _sha256_file(predictions)
        runtime_manifest_sha256 = _sha256_file(runtime_manifest)
        frozen_hashes_path = run_root / "agent06_frozen_output_hashes.json"
        frozen_hashes_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "run_id": run_id,
                    "repo_commit": repo_commit,
                    "provider": "anthropic",
                    "model": model,
                    "bundle_sha256": bundle_sha256,
                    "primary_context_manifest_sha256": manifest_sha256,
                    "predictions_sha256": predictions_sha256,
                    "runtime_manifest_sha256": runtime_manifest_sha256,
                    "frozen_before_ground_truth_comparison": True,
                    "promotion_allowed": False,
                },
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print("[3/4 freeze and hash blind outputs]", flush=True)

        comparison_path = run_root / "agent06_comparison.json"
        _run_stage(
            [
                python,
                "-m",
                "xauusd_v2.agent06_compare_cli",
                "--packet",
                str(packet_path),
                "--predictions",
                str(predictions),
                "--datasets-dir",
                str(datasets_dir),
                "--output",
                str(comparison_path),
            ],
            cwd=staging_root,
            environment=sanitized_env,
            stage="4/4 deterministic post-run ground-truth comparison",
        )

        final_summary = {
            "status": "LOCAL_AGENT06_PIPELINE_COMPLETE",
            "run_id": run_id,
            "resumed": bool(resume_run_id),
            "repo_commit": repo_commit,
            "provider": "anthropic",
            "model": model,
            "bundle_sha256": bundle_sha256,
            "primary_context_manifest_sha256": manifest_sha256,
            "predictions_sha256": predictions_sha256,
            "runtime_manifest_sha256": runtime_manifest_sha256,
            "run_root": str(run_root),
            "comparison_path": str(comparison_path),
            "api_key_written_to_disk": False,
            "blind_process_loaded_ground_truth": False,
            "promotion_allowed": False,
        }
        (run_root / "agent06_local_pipeline_summary.json").write_text(
            json.dumps(final_summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(final_summary, ensure_ascii=False, sort_keys=True))
        return 0
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
