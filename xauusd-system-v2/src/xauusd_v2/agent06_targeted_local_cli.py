from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

from .agent06_local_cli import (
    _EXPECTED_BUNDLE_SHA256,
    _EXPECTED_MANIFEST_SHA256,
    _MANIFEST_NAME,
    _git_head,
    _is_relative_to,
    _load_api_key,
    _run_stage,
    _safe_extract_zip,
    _sanitized_environment,
    _sha256_file,
    _write_smoke_packet,
)
from .blind_validation_packet_io import load_blind_packet


_RUN_ID_RE = re.compile(r"agent06-focus-anthropic-\d{8}T\d{6}Z")
_MAX_SMOKE_CASES = 5
_VERDICTS = {"SUPPORTED", "CONTRADICTED", "INSUFFICIENT"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run low-cost focused Agent-06 adjudication only for unresolved/abstained cases from an "
            "audited locator-set review. This is not a replacement accuracy score for the original "
            "single-label run and never auto-promotes strategy truth."
        )
    )
    parser.add_argument("--bundle", required=True, help="Private Agent-06 source ZIP.")
    parser.add_argument("--review", required=True, help="agent06_locator_review.json from the audited source run.")
    parser.add_argument("--model", required=True, help="Explicit Anthropic model ID, e.g. claude-sonnet-5.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--work-root",
        default=str(Path.home() / ".xauusd-agent06"),
        help="Private Agent-06 working directory outside the Git repository.",
    )
    parser.add_argument(
        "--resume-run-id",
        default="",
        help="Resume an interrupted focused adjudication from its private per-case checkpoint.",
    )
    parser.add_argument(
        "--smoke-cases",
        type=int,
        default=0,
        help="Run only the first N focused cases (1-5) as a live provider smoke test.",
    )
    return parser


def _decision_counts(predictions_path: Path) -> tuple[int, dict[str, int], int]:
    try:
        payload = json.loads(predictions_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit("focused predictions output is unreadable") from exc
    decisions = payload.get("decisions") if isinstance(payload, dict) else None
    if not isinstance(decisions, list):
        raise SystemExit("focused predictions output has invalid decisions")
    counts = {verdict: 0 for verdict in sorted(_VERDICTS)}
    abstain = 0
    for raw in decisions:
        if not isinstance(raw, dict):
            raise SystemExit("focused predictions contain invalid decision")
        verdict = raw.get("predicted_label")
        if verdict is None:
            abstain += 1
        elif str(verdict) in _VERDICTS:
            counts[str(verdict)] += 1
        else:
            raise SystemExit("focused predictions contain verdict outside frozen taxonomy")
    return len(decisions), counts, abstain


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    bundle = Path(args.bundle).expanduser().resolve()
    review = Path(args.review).expanduser().resolve()
    repo_root = Path(args.repo_root).expanduser().resolve()
    work_root = Path(args.work_root).expanduser().resolve()
    model = args.model.strip()
    resume_run_id = args.resume_run_id.strip()
    smoke_cases = int(args.smoke_cases)

    if not model:
        raise SystemExit("explicit Anthropic model is required")
    if smoke_cases < 0 or smoke_cases > _MAX_SMOKE_CASES:
        raise SystemExit(f"smoke-cases must be between 0 and {_MAX_SMOKE_CASES}")
    if resume_run_id and smoke_cases:
        raise SystemExit("smoke mode cannot be combined with resume-run-id")
    if not bundle.is_file():
        raise SystemExit("private Agent-06 bundle does not exist")
    if not review.is_file():
        raise SystemExit("locator-set review file does not exist")

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
    review_sha256 = _sha256_file(review)
    repo_commit = _git_head(repo_root)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    if resume_run_id:
        if _RUN_ID_RE.fullmatch(resume_run_id) is None:
            raise SystemExit("resume-run-id has invalid focused Agent-06 identifier format")
        run_id = resume_run_id
    else:
        run_id = f"agent06-focus-anthropic-{timestamp}"

    if smoke_cases:
        run_root = work_root / "focused-smoke-runs" / run_id
    else:
        run_root = work_root / "focused-runs" / run_id
    staging_root = work_root / "staging" / run_id
    evidence_root = staging_root / "evidence"
    packet_path = staging_root / "focused_packet.json"
    smoke_packet_path = staging_root / "focused_packet_smoke.json"
    work_root.mkdir(parents=True, exist_ok=True)

    if resume_run_id:
        if not run_root.is_dir() or not (run_root / "agent06_blind_checkpoint.json").is_file():
            raise SystemExit("resume-run-id does not contain a resumable focused checkpoint")
        if staging_root.exists():
            raise SystemExit("resume staging directory already exists; refusing ambiguous resume")
    else:
        if run_root.exists() or staging_root.exists():
            raise SystemExit("generated focused run ID already exists; refusing to overwrite")
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
                "xauusd_v2.agent06_targeted_packet_cli",
                "--review",
                str(review),
                "--datasets-dir",
                str(datasets_dir),
                "--output",
                str(packet_path),
            ],
            cwd=staging_root,
            environment=sanitized_env,
            stage="1/2 build focused unresolved-case packet",
        )

        full_packet = load_blind_packet(packet_path)
        full_case_count = len(full_packet.cases)
        taxonomy_count = len(full_packet.taxonomy)
        if tuple(full_packet.taxonomy) != ("SUPPORTED", "CONTRADICTED", "INSUFFICIENT"):
            raise SystemExit("focused packet verdict taxonomy mismatch")

        provider_packet_path = packet_path
        if smoke_cases:
            _write_smoke_packet(packet_path, smoke_packet_path, smoke_cases)
            provider_packet_path = smoke_packet_path
            print(
                f"[smoke] selected {smoke_cases}/{full_case_count} focused cases; verdict taxonomy remains {taxonomy_count}",
                flush=True,
            )

        api_key = _load_api_key()
        provider_env = dict(sanitized_env)
        provider_env["ANTHROPIC_API_KEY"] = api_key
        provider_env["XAUUSD_AGENT06_ANTHROPIC_MODEL"] = model
        command = [
            python,
            "-m",
            "xauusd_v2.agent06_run_cli",
            "--packet",
            str(provider_packet_path),
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
            command.append("--resume-existing")
        command.extend(
            [
                "--command",
                python,
                "-m",
                "xauusd_v2.anthropic_model_runner",
            ]
        )
        _run_stage(
            command,
            cwd=staging_root,
            environment=provider_env,
            stage=(
                f"2/2 execute {smoke_cases}-case focused live smoke"
                if smoke_cases
                else f"2/2 execute {full_case_count}-case focused provider adjudication"
            ),
        )
        del api_key
        provider_env.pop("ANTHROPIC_API_KEY", None)
        provider_env.pop("XAUUSD_AGENT06_ANTHROPIC_MODEL", None)

        predictions = run_root / "agent06_blind_predictions.json"
        runtime_manifest = run_root / "agent06_runtime_manifest.json"
        if not predictions.is_file() or not runtime_manifest.is_file():
            raise SystemExit("focused run completed without required frozen outputs")
        completed_count, verdict_counts, abstain_count = _decision_counts(predictions)
        expected_completed = smoke_cases if smoke_cases else full_case_count
        if completed_count != expected_completed:
            raise SystemExit("focused run completed-count mismatch")

        summary = {
            "status": (
                "AGENT06_FOCUSED_SMOKE_PASS"
                if smoke_cases
                else "AGENT06_FOCUSED_ADJUDICATION_COMPLETE"
            ),
            "run_id": run_id,
            "resumed": bool(resume_run_id),
            "repo_commit": repo_commit,
            "provider": "anthropic",
            "model": model,
            "case_count": completed_count,
            "full_target_case_count": full_case_count,
            "verdict_counts": verdict_counts,
            "provider_abstain_count": abstain_count,
            "bundle_sha256": bundle_sha256,
            "primary_context_manifest_sha256": manifest_sha256,
            "source_review_sha256": review_sha256,
            "predictions_sha256": _sha256_file(predictions),
            "runtime_manifest_sha256": _sha256_file(runtime_manifest),
            "run_root": str(run_root),
            "candidate_claim_visible_to_provider": True,
            "expected_verdict_supplied_to_provider": False,
            "ground_truth_evidence_supplied_to_provider": False,
            "ground_truth_expected_class_supplied_to_provider": False,
            "ground_truth_forbidden_inference_supplied_to_provider": False,
            "provider_execution_process_loaded_ground_truth_dataset": False,
            "api_key_written_to_disk": False,
            "promotion_allowed": False,
        }
        summary_name = (
            "agent06_focused_smoke_summary.json"
            if smoke_cases
            else "agent06_focused_adjudication_summary.json"
        )
        (run_root / summary_name).write_text(
            json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
