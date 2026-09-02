from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .agent06_local_cli import _EXPECTED_BUNDLE_SHA256, _EXPECTED_MANIFEST_SHA256
from .blind_validation_results_io import load_blind_predictions


_REQUIRED_FILES = {
    "summary": "agent06_local_pipeline_summary.json",
    "frozen": "agent06_frozen_output_hashes.json",
    "predictions": "agent06_blind_predictions.json",
    "runtime": "agent06_runtime_manifest.json",
    "readiness": "agent06_readiness.json",
    "comparison": "agent06_comparison.json",
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a completed local Agent-06 run after the blind provider stage and deterministic "
            "comparison. This command verifies artifact integrity and isolation metadata only; it "
            "never promotes strategy knowledge or rules."
        )
    )
    parser.add_argument("--run-root", required=True, help="Completed Agent-06 run directory.")
    parser.add_argument("--provider", default="anthropic", help="Expected provider metadata.")
    parser.add_argument("--model", default="claude-sonnet-5", help="Expected model metadata.")
    parser.add_argument("--case-count", type=int, default=173, help="Expected blind corpus size.")
    parser.add_argument(
        "--expected-repo-commit",
        default=None,
        help="Optional exact 40-character Git commit expected for the local run.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON audit report path. Existing files are never overwritten.",
    )
    return parser


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_object(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return raw


def _is_sha256(value: object) -> bool:
    text = str(value or "").strip().lower()
    return len(text) == 64 and all(ch in "0123456789abcdef" for ch in text)


def _is_git_commit(value: object) -> bool:
    text = str(value or "").strip().lower()
    return len(text) == 40 and all(ch in "0123456789abcdef" for ch in text)


def _same_path(value: object, expected: Path) -> bool:
    try:
        return Path(str(value)).expanduser().resolve() == expected.resolve()
    except (OSError, RuntimeError, ValueError):
        return False


def _append_if(blockers: list[str], condition: bool, message: str) -> None:
    if condition:
        blockers.append(message)


def audit_agent06_run(
    *,
    run_root: Path,
    expected_provider: str = "anthropic",
    expected_model: str = "claude-sonnet-5",
    expected_case_count: int = 173,
    expected_repo_commit: str | None = None,
) -> dict[str, Any]:
    run_root = run_root.expanduser().resolve()
    blockers: list[str] = []

    if expected_case_count <= 0:
        raise ValueError("expected_case_count must be positive")
    provider = expected_provider.strip()
    model = expected_model.strip()
    if not provider or not model:
        raise ValueError("expected provider and model are required")
    if expected_repo_commit is not None:
        expected_repo_commit = expected_repo_commit.strip().lower()
        if not _is_git_commit(expected_repo_commit):
            raise ValueError("expected_repo_commit must be a 40-character hexadecimal Git commit")

    if not run_root.is_dir():
        return {
            "status": "AUDIT_FAIL",
            "run_root": str(run_root),
            "blockers": ["run root does not exist or is not a directory"],
            "promotion_allowed": False,
        }

    paths = {name: run_root / filename for name, filename in _REQUIRED_FILES.items()}
    missing = [path.name for path in paths.values() if not path.is_file()]
    if missing:
        return {
            "status": "AUDIT_FAIL",
            "run_root": str(run_root),
            "blockers": [f"missing required artifact: {name}" for name in sorted(missing)],
            "promotion_allowed": False,
        }

    try:
        summary = _load_object(paths["summary"])
        frozen = _load_object(paths["frozen"])
        runtime = _load_object(paths["runtime"])
        readiness = _load_object(paths["readiness"])
        comparison = _load_object(paths["comparison"])
        predictions = load_blind_predictions(paths["predictions"])
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return {
            "status": "AUDIT_FAIL",
            "run_root": str(run_root),
            "blockers": [f"artifact parse/schema failure: {exc}"],
            "promotion_allowed": False,
        }

    predictions_sha256 = _sha256_file(paths["predictions"])
    runtime_sha256 = _sha256_file(paths["runtime"])

    run_id = str(summary.get("run_id", "")).strip()
    repo_commit = str(summary.get("repo_commit", "")).strip().lower()

    _append_if(blockers, summary.get("status") != "LOCAL_AGENT06_PIPELINE_COMPLETE", "local pipeline summary is not complete")
    _append_if(blockers, not run_id, "run_id is missing from local pipeline summary")
    _append_if(blockers, not _is_git_commit(repo_commit), "repo_commit is not a valid 40-character Git commit")
    if expected_repo_commit is not None:
        _append_if(blockers, repo_commit != expected_repo_commit, "repo_commit does not match the explicitly expected commit")
    _append_if(blockers, str(summary.get("provider", "")).strip() != provider, "summary provider metadata mismatch")
    _append_if(blockers, str(summary.get("model", "")).strip() != model, "summary model metadata mismatch")
    _append_if(blockers, summary.get("bundle_sha256") != _EXPECTED_BUNDLE_SHA256, "summary private bundle SHA-256 mismatch")
    _append_if(
        blockers,
        summary.get("primary_context_manifest_sha256") != _EXPECTED_MANIFEST_SHA256,
        "summary primary-context manifest SHA-256 mismatch",
    )
    _append_if(blockers, summary.get("predictions_sha256") != predictions_sha256, "summary predictions SHA-256 mismatch")
    _append_if(blockers, summary.get("runtime_manifest_sha256") != runtime_sha256, "summary runtime manifest SHA-256 mismatch")
    _append_if(blockers, summary.get("api_key_written_to_disk") is not False, "summary does not prove API key was kept off disk")
    _append_if(
        blockers,
        summary.get("blind_process_loaded_ground_truth") is not False,
        "summary indicates or fails to disprove ground-truth loading in the blind process",
    )
    _append_if(blockers, summary.get("promotion_allowed") is not False, "summary must keep promotion disabled")
    _append_if(blockers, not _same_path(summary.get("run_root"), run_root), "summary run_root does not match audited directory")
    _append_if(
        blockers,
        not _same_path(summary.get("comparison_path"), paths["comparison"]),
        "summary comparison_path does not match audited comparison artifact",
    )

    _append_if(blockers, frozen.get("version") != 1, "frozen output hash record version mismatch")
    _append_if(blockers, str(frozen.get("run_id", "")).strip() != run_id, "frozen hash record run_id mismatch")
    _append_if(blockers, str(frozen.get("repo_commit", "")).strip().lower() != repo_commit, "frozen hash record repo_commit mismatch")
    _append_if(blockers, str(frozen.get("provider", "")).strip() != provider, "frozen hash record provider mismatch")
    _append_if(blockers, str(frozen.get("model", "")).strip() != model, "frozen hash record model mismatch")
    _append_if(blockers, frozen.get("bundle_sha256") != _EXPECTED_BUNDLE_SHA256, "frozen hash record bundle SHA-256 mismatch")
    _append_if(
        blockers,
        frozen.get("primary_context_manifest_sha256") != _EXPECTED_MANIFEST_SHA256,
        "frozen hash record primary-context manifest SHA-256 mismatch",
    )
    _append_if(blockers, frozen.get("predictions_sha256") != predictions_sha256, "frozen predictions hash no longer matches file bytes")
    _append_if(blockers, frozen.get("runtime_manifest_sha256") != runtime_sha256, "frozen runtime-manifest hash no longer matches file bytes")
    _append_if(
        blockers,
        frozen.get("frozen_before_ground_truth_comparison") is not True,
        "blind outputs are not recorded as frozen before ground-truth comparison",
    )
    _append_if(blockers, frozen.get("promotion_allowed") is not False, "frozen hash record must keep promotion disabled")

    _append_if(blockers, predictions.run_id != run_id, "prediction run_id mismatch")
    _append_if(blockers, predictions.model_provider != provider, "prediction provider mismatch")
    _append_if(blockers, predictions.model_name != model, "prediction model mismatch")
    _append_if(blockers, predictions.case_count != expected_case_count, "prediction case count mismatch")

    runtime_cases = runtime.get("cases")
    if not isinstance(runtime_cases, list):
        blockers.append("runtime manifest cases must be a JSON array")
        runtime_cases = []
    _append_if(blockers, str(runtime.get("run_id", "")).strip() != run_id, "runtime manifest run_id mismatch")
    _append_if(blockers, str(runtime.get("model_provider", "")).strip() != provider, "runtime manifest provider mismatch")
    _append_if(blockers, str(runtime.get("model_name", "")).strip() != model, "runtime manifest model mismatch")
    _append_if(blockers, runtime.get("case_count") != expected_case_count, "runtime manifest case count mismatch")
    _append_if(blockers, runtime.get("completed_count") != expected_case_count, "runtime manifest does not show every case completed")
    _append_if(blockers, len(runtime_cases) != expected_case_count, "runtime manifest case-audit count mismatch")
    _append_if(blockers, runtime.get("promotion_allowed") is not False, "runtime manifest must keep promotion disabled")
    _append_if(blockers, runtime.get("packet_sha256") != predictions.packet_sha256, "runtime/prediction packet fingerprint mismatch")
    _append_if(blockers, runtime.get("taxonomy_sha256") != predictions.taxonomy_sha256, "runtime/prediction taxonomy fingerprint mismatch")

    decision_by_id = {decision.vector_id: decision for decision in predictions.batch.decisions}
    seen_runtime_ids: set[str] = set()
    for item in runtime_cases:
        if not isinstance(item, dict):
            blockers.append("runtime manifest contains a non-object case audit")
            continue
        vector_id = str(item.get("vector_id", "")).strip()
        if not vector_id:
            blockers.append("runtime manifest contains case audit without vector_id")
            continue
        if vector_id in seen_runtime_ids:
            blockers.append(f"runtime manifest contains duplicate vector_id: {vector_id}")
            continue
        seen_runtime_ids.add(vector_id)
        decision = decision_by_id.get(vector_id)
        if decision is None:
            blockers.append(f"runtime manifest contains unknown vector_id: {vector_id}")
            continue
        if str(item.get("source_locator", "")).strip() != decision.source_locator:
            blockers.append(f"runtime/prediction source locator mismatch for {vector_id}")
        if item.get("predicted_label") != decision.predicted_label:
            blockers.append(f"runtime/prediction label mismatch for {vector_id}")
        if item.get("abstained") is not decision.abstained:
            blockers.append(f"runtime/prediction abstention mismatch for {vector_id}")
    if runtime_cases and seen_runtime_ids != set(decision_by_id):
        blockers.append("runtime manifest vector IDs do not exactly match prediction vector IDs")

    _append_if(blockers, readiness.get("status") != "READY_TO_RUN", "readiness artifact is not READY_TO_RUN")
    _append_if(blockers, readiness.get("ready_to_run") is not True, "readiness artifact does not authorize blind-run start")
    _append_if(blockers, readiness.get("total_cases") != expected_case_count, "readiness total case count mismatch")
    _append_if(blockers, readiness.get("resolved_cases") != expected_case_count, "readiness did not resolve every case")
    _append_if(blockers, readiness.get("missing_locators") not in ([], ()), "readiness reports missing source locators")
    _append_if(blockers, readiness.get("invalid_context_locators") not in ([], ()), "readiness reports invalid source contexts")
    _append_if(blockers, readiness.get("image_missing_locators") not in ([], ()), "readiness reports missing primary images")
    _append_if(blockers, readiness.get("provider_configured") is not True, "readiness provider metadata was not configured")
    _append_if(blockers, readiness.get("model_configured") is not True, "readiness model metadata was not configured")
    image_required_cases = readiness.get("image_required_cases")
    if isinstance(image_required_cases, int) and image_required_cases > 0:
        _append_if(blockers, readiness.get("multimodal_supported") is not True, "readiness did not prove multimodal model support")

    _append_if(blockers, comparison.get("version") != 1, "comparison artifact version mismatch")
    _append_if(blockers, str(comparison.get("run_id", "")).strip() != run_id, "comparison run_id mismatch")
    _append_if(blockers, str(comparison.get("model_provider", "")).strip() != provider, "comparison provider mismatch")
    _append_if(blockers, str(comparison.get("model_name", "")).strip() != model, "comparison model mismatch")
    _append_if(blockers, comparison.get("packet_sha256") != predictions.packet_sha256, "comparison packet fingerprint mismatch")
    _append_if(blockers, comparison.get("predictions_sha256") != predictions_sha256, "comparison predictions SHA-256 mismatch")
    _append_if(
        blockers,
        comparison.get("comparison_performed_after_blind_run") is not True,
        "comparison is not recorded as a separate post-blind-run step",
    )
    _append_if(blockers, comparison.get("promotion_allowed") is not False, "comparison must keep promotion disabled")

    agree = comparison.get("agree")
    disagree = comparison.get("disagree")
    ambiguous = comparison.get("ambiguous")
    total = comparison.get("total")
    counts = (agree, disagree, ambiguous, total)
    if not all(isinstance(value, int) and value >= 0 for value in counts):
        blockers.append("comparison counts must be non-negative integers")
    else:
        _append_if(blockers, total != expected_case_count, "comparison total does not equal expected blind corpus size")
        _append_if(blockers, agree + disagree + ambiguous != total, "comparison agree/disagree/ambiguous counts do not sum to total")
        expected_all_agree = total > 0 and disagree == 0 and ambiguous == 0
        _append_if(blockers, comparison.get("all_agree") is not expected_all_agree, "comparison all_agree flag is inconsistent with counts")
    outcomes = comparison.get("outcomes")
    if not isinstance(outcomes, list):
        blockers.append("comparison outcomes must be a JSON array")
    elif isinstance(total, int) and len(outcomes) != total:
        blockers.append("comparison outcome count does not match declared total")

    for name, value in (
        ("predictions packet_sha256", predictions.packet_sha256),
        ("predictions taxonomy_sha256", predictions.taxonomy_sha256),
        ("actual predictions SHA-256", predictions_sha256),
        ("actual runtime manifest SHA-256", runtime_sha256),
    ):
        _append_if(blockers, not _is_sha256(value), f"{name} is not a valid SHA-256 digest")

    return {
        "status": "AUDIT_PASS" if not blockers else "AUDIT_FAIL",
        "run_id": run_id or None,
        "run_root": str(run_root),
        "repo_commit": repo_commit or None,
        "provider": provider,
        "model": model,
        "expected_case_count": expected_case_count,
        "predictions_sha256": predictions_sha256,
        "runtime_manifest_sha256": runtime_sha256,
        "agree": agree if isinstance(agree, int) else None,
        "disagree": disagree if isinstance(disagree, int) else None,
        "ambiguous": ambiguous if isinstance(ambiguous, int) else None,
        "all_agree": comparison.get("all_agree") if isinstance(comparison.get("all_agree"), bool) else None,
        "artifact_integrity_passed": not blockers,
        "independent_validation_auto_promoted": False,
        "promotion_allowed": False,
        "blockers": blockers,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = audit_agent06_run(
        run_root=Path(args.run_root),
        expected_provider=args.provider,
        expected_model=args.model,
        expected_case_count=args.case_count,
        expected_repo_commit=args.expected_repo_commit,
    )
    output = args.output
    if output:
        output_path = Path(output).expanduser().resolve()
        if output_path.exists():
            raise SystemExit("audit output already exists; refusing to overwrite")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "AUDIT_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
