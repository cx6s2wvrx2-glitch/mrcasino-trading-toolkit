from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .agent06_local_cli import _EXPECTED_BUNDLE_SHA256, _EXPECTED_MANIFEST_SHA256
from .agent06_run_cli import _taxonomy_sha256
from .agent06_targeted_packet_cli import build_targeted_packet
from .focused_validation_packet import FOCUSED_VERDICT_TAXONOMY, focused_packet_sha256


_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_FILES = (
    "agent06_focused_checkpoint.json",
    "agent06_focused_predictions.json",
    "agent06_focused_runtime_manifest.json",
    "agent06_focused_readiness.json",
    "agent06_focused_adjudication_summary.json",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministically audit and close a completed focused Agent-06 adjudication. "
            "This command performs no provider calls, never auto-promotes strategy truth, and "
            "preserves the documented V1 single-label protocol caveat."
        )
    )
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--review", required=True, help="Audited agent06_locator_review.json used to build the focused packet.")
    parser.add_argument("--datasets-dir", default="./xauusd-system-v2/15_tests")
    parser.add_argument("--provider", default="anthropic")
    parser.add_argument("--model", default="claude-sonnet-5")
    parser.add_argument("--case-count", type=int, default=23)
    parser.add_argument("--expected-repo-commit", required=True)
    parser.add_argument("--output", default=None)
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
        raise ValueError(f"{path.name} must contain one JSON object")
    return raw


def _block(blockers: list[str], condition: bool, message: str) -> None:
    if not condition:
        blockers.append(message)


def _is_nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _review_counts(review: dict[str, Any]) -> tuple[int, int, int, int]:
    exact = review.get("exact_agree")
    locator = review.get("locator_set_agree")
    unresolved = review.get("unresolved_disagree")
    abstain = review.get("abstain")
    values = (exact, locator, unresolved, abstain)
    if not all(_is_nonnegative_int(value) for value in values):
        raise ValueError("locator review summary counts are invalid")
    return int(exact), int(locator), int(unresolved), int(abstain)


def audit_and_finalize(
    *,
    run_root: Path,
    review_path: Path,
    datasets_dir: Path,
    expected_provider: str,
    expected_model: str,
    expected_case_count: int,
    expected_repo_commit: str,
) -> dict[str, Any]:
    root = run_root.expanduser().resolve()
    review_path = review_path.expanduser().resolve()
    datasets_dir = datasets_dir.expanduser().resolve()
    blockers: list[str] = []

    if expected_case_count <= 0:
        return {
            "status": "AGENT06_FOCUSED_FINALIZE_FAIL",
            "blockers": ["expected case count must be positive"],
            "promotion_allowed": False,
            "strategy_truth_changed": False,
        }

    missing = [name for name in _REQUIRED_FILES if not (root / name).is_file()]
    if missing:
        return {
            "status": "AGENT06_FOCUSED_FINALIZE_FAIL",
            "run_root": str(root),
            "blockers": [f"missing required focused artifacts: {', '.join(missing)}"],
            "promotion_allowed": False,
            "strategy_truth_changed": False,
        }

    try:
        review = _load_object(review_path)
        packet, selected_from, rebuilt_review = build_targeted_packet(
            review_path=review_path,
            datasets_dir=datasets_dir,
        )
        predictions = _load_object(root / "agent06_focused_predictions.json")
        runtime = _load_object(root / "agent06_focused_runtime_manifest.json")
        readiness = _load_object(root / "agent06_focused_readiness.json")
        checkpoint = _load_object(root / "agent06_focused_checkpoint.json")
        summary = _load_object(root / "agent06_focused_adjudication_summary.json")
        exact_agree, locator_set_agree, original_unresolved, original_abstain = _review_counts(review)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError, SystemExit) as exc:
        return {
            "status": "AGENT06_FOCUSED_FINALIZE_FAIL",
            "run_root": str(root),
            "blockers": [f"focused audit could not reconstruct/read artifacts: {exc}"],
            "promotion_allowed": False,
            "strategy_truth_changed": False,
        }

    packet_sha = focused_packet_sha256(packet)
    taxonomy_sha = _taxonomy_sha256(packet.verdict_taxonomy)
    review_sha = _sha256_file(review_path)
    predictions_sha = _sha256_file(root / "agent06_focused_predictions.json")
    runtime_sha = _sha256_file(root / "agent06_focused_runtime_manifest.json")
    packet_cases = list(packet.cases)
    packet_ids = [case.vector_id for case in packet_cases]

    _block(blockers, rebuilt_review == review, "targeted packet builder did not return the same review object")
    _block(blockers, len(packet_cases) == expected_case_count, "rebuilt focused packet case count mismatch")
    _block(blockers, tuple(packet.verdict_taxonomy) == FOCUSED_VERDICT_TAXONOMY, "focused verdict taxonomy mismatch")
    _block(blockers, original_unresolved + original_abstain == expected_case_count, "source review target count mismatch")
    _block(blockers, selected_from.get("UNRESOLVED_DISAGREE") == original_unresolved, "rebuilt unresolved selection count mismatch")
    _block(blockers, selected_from.get("ABSTAIN") == original_abstain, "rebuilt abstain selection count mismatch")

    run_id = str(summary.get("run_id", "")).strip()
    _block(blockers, bool(run_id), "focused summary run_id is missing")
    _block(blockers, root.name == run_id, "focused run directory name does not match run_id")
    _block(blockers, summary.get("status") == "AGENT06_FOCUSED_ADJUDICATION_COMPLETE", "focused summary status mismatch")
    _block(blockers, summary.get("provider") == expected_provider, "focused summary provider mismatch")
    _block(blockers, summary.get("model") == expected_model, "focused summary model mismatch")
    _block(blockers, summary.get("repo_commit") == expected_repo_commit, "focused summary repo commit mismatch")
    _block(blockers, summary.get("case_count") == expected_case_count, "focused summary case count mismatch")
    _block(blockers, summary.get("full_target_case_count") == expected_case_count, "focused summary target count mismatch")
    _block(blockers, summary.get("bundle_sha256") == _EXPECTED_BUNDLE_SHA256, "focused summary bundle hash mismatch")
    _block(blockers, summary.get("primary_context_manifest_sha256") == _EXPECTED_MANIFEST_SHA256, "focused summary primary manifest hash mismatch")
    _block(blockers, summary.get("source_review_sha256") == review_sha, "focused summary source review hash mismatch")
    _block(blockers, summary.get("predictions_sha256") == predictions_sha, "focused summary predictions hash mismatch")
    _block(blockers, summary.get("runtime_manifest_sha256") == runtime_sha, "focused summary runtime manifest hash mismatch")
    _block(blockers, summary.get("candidate_claim_visible_to_provider") is True, "candidate claim visibility flag mismatch")
    _block(blockers, summary.get("expected_verdict_supplied_to_provider") is False, "expected verdict leakage flag mismatch")
    _block(blockers, summary.get("ground_truth_evidence_supplied_to_provider") is False, "ground-truth evidence leakage flag mismatch")
    _block(blockers, summary.get("ground_truth_expected_class_supplied_to_provider") is False, "ground-truth expected-class leakage flag mismatch")
    _block(blockers, summary.get("ground_truth_forbidden_inference_supplied_to_provider") is False, "ground-truth forbidden-inference leakage flag mismatch")
    _block(blockers, summary.get("provider_execution_process_loaded_ground_truth_dataset") is False, "provider process ground-truth isolation flag mismatch")
    _block(blockers, summary.get("api_key_written_to_disk") is False, "API key persistence flag mismatch")
    _block(blockers, summary.get("promotion_allowed") is False, "focused summary cannot allow promotion")

    _block(blockers, predictions.get("protocol") == "agent06_focused_claim_adjudication_v2", "focused predictions protocol mismatch")
    _block(blockers, predictions.get("run_id") == run_id, "focused predictions run_id mismatch")
    _block(blockers, predictions.get("model_provider") == expected_provider, "focused predictions provider mismatch")
    _block(blockers, predictions.get("model_name") == expected_model, "focused predictions model mismatch")
    _block(blockers, predictions.get("packet_sha256") == packet_sha, "focused predictions packet hash mismatch")
    _block(blockers, predictions.get("taxonomy_sha256") == taxonomy_sha, "focused predictions taxonomy hash mismatch")
    _block(blockers, predictions.get("case_count") == expected_case_count, "focused predictions case count mismatch")
    _block(blockers, predictions.get("candidate_claim_visible_to_provider") is True, "focused predictions claim visibility mismatch")
    _block(blockers, predictions.get("expected_verdict_loaded_by_this_process") is False, "focused predictions expected-verdict isolation mismatch")
    _block(blockers, predictions.get("ground_truth_dataset_loaded_by_this_process") is False, "focused predictions ground-truth isolation mismatch")
    _block(blockers, predictions.get("comparison_performed_by_this_process") is False, "focused provider process comparison flag mismatch")
    _block(blockers, predictions.get("promotion_allowed") is False, "focused predictions cannot allow promotion")

    raw_decisions = predictions.get("decisions")
    if not isinstance(raw_decisions, list):
        blockers.append("focused predictions decisions array is invalid")
        raw_decisions = []
    _block(blockers, len(raw_decisions) == expected_case_count, "focused decisions count mismatch")

    verdict_counts = {verdict: 0 for verdict in FOCUSED_VERDICT_TAXONOMY}
    provider_abstain_count = 0
    decision_by_id: dict[str, dict[str, Any]] = {}
    focused_cases: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_decisions):
        if not isinstance(raw, dict):
            blockers.append(f"focused decision at index {index} is not an object")
            continue
        vector_id = str(raw.get("vector_id", "")).strip()
        source_locator = str(raw.get("source_locator", "")).strip()
        if not vector_id or vector_id in decision_by_id:
            blockers.append(f"focused decision has duplicate/empty vector id at index {index}")
            continue
        decision_by_id[vector_id] = raw
        if index >= len(packet_cases):
            blockers.append(f"focused decision {vector_id} is outside rebuilt packet order")
            continue
        case = packet_cases[index]
        _block(blockers, vector_id == case.vector_id, f"focused decision order/vector mismatch for {vector_id}")
        _block(blockers, source_locator == case.source_locator, f"focused decision locator mismatch for {vector_id}")
        verdict = raw.get("predicted_label")
        if verdict is None:
            provider_abstain_count += 1
        elif verdict in FOCUSED_VERDICT_TAXONOMY:
            verdict_counts[str(verdict)] += 1
        else:
            blockers.append(f"focused decision verdict is outside frozen taxonomy for {vector_id}")
        confidence = raw.get("confidence")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
            blockers.append(f"focused decision confidence is invalid for {vector_id}")
        evidence = raw.get("evidence")
        ambiguities = raw.get("ambiguities")
        if not isinstance(evidence, list) or any(not isinstance(item, str) for item in evidence):
            blockers.append(f"focused decision evidence is invalid for {vector_id}")
            evidence = []
        if not isinstance(ambiguities, list) or any(not isinstance(item, str) for item in ambiguities):
            blockers.append(f"focused decision ambiguities are invalid for {vector_id}")
            ambiguities = []
        focused_cases.append(
            {
                "vector_id": vector_id,
                "candidate_claim": case.candidate_claim,
                "source_locator": source_locator,
                "verdict": verdict,
                "confidence": confidence,
                "evidence": evidence,
                "ambiguities": ambiguities,
            }
        )

    _block(blockers, list(decision_by_id) == packet_ids, "focused decisions do not exactly match rebuilt packet IDs/order")
    _block(blockers, summary.get("verdict_counts") == verdict_counts, "focused summary verdict counts mismatch")
    _block(blockers, summary.get("provider_abstain_count") == provider_abstain_count, "focused summary provider abstain count mismatch")

    _block(blockers, runtime.get("protocol") == "agent06_focused_claim_adjudication_v2", "focused runtime protocol mismatch")
    _block(blockers, runtime.get("run_id") == run_id, "focused runtime run_id mismatch")
    _block(blockers, runtime.get("model_provider") == expected_provider, "focused runtime provider mismatch")
    _block(blockers, runtime.get("model_name") == expected_model, "focused runtime model mismatch")
    _block(blockers, runtime.get("packet_sha256") == packet_sha, "focused runtime packet hash mismatch")
    _block(blockers, runtime.get("taxonomy_sha256") == taxonomy_sha, "focused runtime taxonomy hash mismatch")
    _block(blockers, runtime.get("case_count") == expected_case_count, "focused runtime case count mismatch")
    _block(blockers, runtime.get("completed_count") == expected_case_count, "focused runtime completed count mismatch")
    _block(blockers, runtime.get("abstained_count") == provider_abstain_count, "focused runtime abstain count mismatch")
    _block(blockers, runtime.get("promotion_allowed") is False, "focused runtime cannot allow promotion")

    runtime_cases = runtime.get("cases")
    if not isinstance(runtime_cases, list):
        blockers.append("focused runtime cases array is invalid")
        runtime_cases = []
    _block(blockers, len(runtime_cases) == expected_case_count, "focused runtime cases count mismatch")
    observed_image_case_count = 0
    for index, raw in enumerate(runtime_cases):
        if not isinstance(raw, dict):
            blockers.append(f"focused runtime case at index {index} is not an object")
            continue
        if index >= len(packet_cases):
            blockers.append(f"focused runtime case at index {index} is outside packet order")
            continue
        case = packet_cases[index]
        decision = decision_by_id.get(case.vector_id)
        _block(blockers, raw.get("vector_id") == case.vector_id, f"focused runtime vector mismatch for {case.vector_id}")
        _block(blockers, raw.get("source_locator") == case.source_locator, f"focused runtime locator mismatch for {case.vector_id}")
        if decision is not None:
            _block(blockers, raw.get("predicted_label") == decision.get("predicted_label"), f"focused runtime verdict mismatch for {case.vector_id}")
            _block(blockers, raw.get("abstained") is (decision.get("predicted_label") is None), f"focused runtime abstain flag mismatch for {case.vector_id}")
        text_sha = raw.get("source_text_sha256")
        if text_sha is not None and (not isinstance(text_sha, str) or _HEX64_RE.fullmatch(text_sha) is None):
            blockers.append(f"focused runtime text hash is invalid for {case.vector_id}")
        images = raw.get("images")
        if not isinstance(images, list):
            blockers.append(f"focused runtime images are invalid for {case.vector_id}")
            continue
        if images:
            observed_image_case_count += 1
        for image in images:
            if not isinstance(image, dict):
                blockers.append(f"focused runtime image metadata is invalid for {case.vector_id}")
                continue
            sha = image.get("sha256")
            size = image.get("size_bytes")
            mime = image.get("mime_type")
            if not isinstance(sha, str) or _HEX64_RE.fullmatch(sha) is None:
                blockers.append(f"focused runtime image hash is invalid for {case.vector_id}")
            if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
                blockers.append(f"focused runtime image size is invalid for {case.vector_id}")
            if not isinstance(mime, str) or not mime.startswith("image/"):
                blockers.append(f"focused runtime image mime is invalid for {case.vector_id}")
    _block(blockers, runtime.get("image_case_count") == observed_image_case_count, "focused runtime image case count mismatch")

    _block(blockers, readiness.get("status") == "FOCUSED_READY_TO_RUN", "focused readiness status mismatch")
    _block(blockers, readiness.get("ready_to_run") is True, "focused readiness is not ready")
    _block(blockers, readiness.get("blockers") == [], "focused readiness blockers are not empty")
    _block(blockers, readiness.get("total_cases") == expected_case_count, "focused readiness total case count mismatch")
    _block(blockers, readiness.get("resolved_cases") == expected_case_count, "focused readiness resolved case count mismatch")
    _block(blockers, readiness.get("provider_configured") is True, "focused readiness provider flag mismatch")
    _block(blockers, readiness.get("model_configured") is True, "focused readiness model flag mismatch")
    _block(blockers, readiness.get("multimodal_supported") is True, "focused readiness multimodal flag mismatch")

    _block(blockers, checkpoint.get("run_id") == run_id, "focused checkpoint run_id mismatch")
    _block(blockers, checkpoint.get("model_provider") == expected_provider, "focused checkpoint provider mismatch")
    _block(blockers, checkpoint.get("model_name") == expected_model, "focused checkpoint model mismatch")
    _block(blockers, checkpoint.get("repo_commit") == expected_repo_commit, "focused checkpoint repo commit mismatch")
    _block(blockers, checkpoint.get("packet_sha256") == packet_sha, "focused checkpoint packet hash mismatch")
    _block(blockers, checkpoint.get("taxonomy_sha256") == taxonomy_sha, "focused checkpoint taxonomy hash mismatch")
    _block(blockers, checkpoint.get("completed_count") == expected_case_count, "focused checkpoint completed count mismatch")
    _block(blockers, checkpoint.get("ground_truth_loaded_by_this_process") is False, "focused checkpoint ground-truth isolation mismatch")
    _block(blockers, checkpoint.get("comparison_performed_by_this_process") is False, "focused checkpoint comparison flag mismatch")
    _block(blockers, checkpoint.get("promotion_allowed") is False, "focused checkpoint cannot allow promotion")
    checkpoint_cases = checkpoint.get("cases")
    if not isinstance(checkpoint_cases, list):
        blockers.append("focused checkpoint cases array is invalid")
        checkpoint_cases = []
    _block(blockers, len(checkpoint_cases) == expected_case_count, "focused checkpoint cases count mismatch")
    for index, item in enumerate(checkpoint_cases):
        if not isinstance(item, dict) or not isinstance(item.get("decision"), dict):
            blockers.append(f"focused checkpoint case at index {index} is invalid")
            continue
        if index >= len(raw_decisions):
            blockers.append(f"focused checkpoint case at index {index} exceeds final decisions")
            continue
        _block(blockers, item.get("decision") == raw_decisions[index], f"focused checkpoint/final decision mismatch at index {index}")

    supported_ids = [case["vector_id"] for case in focused_cases if case.get("verdict") == "SUPPORTED"]
    contradicted_ids = [case["vector_id"] for case in focused_cases if case.get("verdict") == "CONTRADICTED"]
    insufficient_ids = [case["vector_id"] for case in focused_cases if case.get("verdict") == "INSUFFICIENT" or case.get("verdict") is None]

    locator_collision_ids: list[str] = []
    raw_review_cases = review.get("cases")
    if isinstance(raw_review_cases, list):
        for raw in raw_review_cases:
            if isinstance(raw, dict) and raw.get("adjusted_result") == "LOCATOR_SET_AGREE":
                vector_id = str(raw.get("vector_id", "")).strip()
                if vector_id:
                    locator_collision_ids.append(vector_id)
    _block(blockers, len(locator_collision_ids) == locator_set_agree, "locator collision case count does not match review summary")

    total_cases = review.get("total_cases")
    _block(blockers, total_cases == exact_agree + locator_set_agree + expected_case_count, "final 173-case accounting mismatch")

    if blockers:
        return {
            "status": "AGENT06_FOCUSED_FINALIZE_FAIL",
            "run_id": run_id,
            "run_root": str(root),
            "blockers": blockers,
            "artifact_integrity_passed": False,
            "promotion_allowed": False,
            "strategy_truth_changed": False,
            "provider_calls_performed_by_finalizer": False,
        }

    final_status = (
        "AGENT06_EXTERNAL_VALIDATION_CLOSED_WITH_CONTRADICTIONS"
        if contradicted_ids
        else "AGENT06_EXTERNAL_VALIDATION_CLOSED_WITH_UNRESOLVED_EVIDENCE"
        if insufficient_ids
        else "AGENT06_EXTERNAL_VALIDATION_CLOSED_NO_CONTRADICTIONS"
    )
    return {
        "status": "AGENT06_FOCUSED_FINALIZE_PASS",
        "closure_status": final_status,
        "run_id": run_id,
        "source_run_id": str(review.get("run_id", "")),
        "run_root": str(root),
        "repo_commit": expected_repo_commit,
        "provider": expected_provider,
        "model": expected_model,
        "artifact_integrity_passed": True,
        "all_cases_accounted_for": True,
        "total_cases": total_cases,
        "v1_exact_agree": exact_agree,
        "v1_locator_collision_neutral": locator_set_agree,
        "v2_focused_supported": len(supported_ids),
        "v2_focused_contradicted": len(contradicted_ids),
        "v2_focused_insufficient": len(insufficient_ids),
        "focused_provider_abstain_count": provider_abstain_count,
        "focused_verdict_counts": verdict_counts,
        "focused_supported_case_ids": supported_ids,
        "focused_contradicted_case_ids": contradicted_ids,
        "focused_insufficient_case_ids": insufficient_ids,
        "locator_collision_case_ids": locator_collision_ids,
        "focused_cases": focused_cases,
        "packet_sha256": packet_sha,
        "predictions_sha256": predictions_sha,
        "runtime_manifest_sha256": runtime_sha,
        "source_review_sha256": review_sha,
        "bundle_sha256": _EXPECTED_BUNDLE_SHA256,
        "primary_context_manifest_sha256": _EXPECTED_MANIFEST_SHA256,
        "v1_protocol_caveat": (
            "V1 exact agreement is preserved as evidence from the original under-specified single-label protocol; "
            "it is not relabeled as V2 focused claim adjudication. LOCATOR_SET_AGREE remains a documented "
            "benchmark-collision-neutral result, not case-specific external support."
        ),
        "provider_calls_performed_by_finalizer": False,
        "paid_provider_work_complete": True,
        "no_further_provider_calls_required_for_agent06_closure": True,
        "strategy_truth_changed": False,
        "promotion_allowed": False,
        "independent_validation_auto_promoted": False,
        "live_execution_authorized": False,
        "blockers": [],
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = audit_and_finalize(
        run_root=Path(args.run_root),
        review_path=Path(args.review),
        datasets_dir=Path(args.datasets_dir),
        expected_provider=args.provider.strip(),
        expected_model=args.model.strip(),
        expected_case_count=args.case_count,
        expected_repo_commit=args.expected_repo_commit.strip(),
    )
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        if output_path.exists():
            raise SystemExit("final Agent-06 closure output already exists; refusing overwrite")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report.get("status") == "AGENT06_FOCUSED_FINALIZE_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
