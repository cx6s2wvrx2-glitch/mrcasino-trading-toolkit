from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from .agent06_readiness import assess_agent06_readiness
from .agents.validation_agent import IndependentValidationAgent, IndependentValidationDecision
from .blind_validation_multimodal_runtime import (
    MultimodalImageAudit,
    MultimodalRuntimeCaseAudit,
    ResumableBlindCase,
    execute_multimodal_blind_validation_runtime,
)
from .blind_validation_packet_io import load_blind_packet
from .blind_validation_runtime import blind_packet_sha256
from .primary_context_bundle import FileSystemPrimaryContextBundleResolver
from .structured_model_clients import CommandModelClientConfig, CommandStructuredModelClient


_CHECKPOINT_NAME = "agent06_blind_checkpoint.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute Agent-06 against an already-built answer-free blind packet. "
            "This command never loads ground-truth datasets and never performs comparison."
        )
    )
    parser.add_argument("--packet", required=True)
    parser.add_argument("--bundle-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--repo-commit",
        default="UNSPECIFIED",
        help="Git commit identity for reproducible checkpoint resume.",
    )
    parser.add_argument(
        "--resume-existing",
        action="store_true",
        help=(
            "Resume a previously interrupted blind run from its private checkpoint. "
            "Packet/taxonomy/provider/model/repo commit and primary evidence fingerprints must match exactly."
        ),
    )
    parser.add_argument(
        "--command",
        nargs=argparse.REMAINDER,
        required=True,
        help=(
            "External model wrapper command. This must be the final Agent-06 CLI option so wrapper "
            "arguments such as '-m' remain part of the command. Supply credentials only through "
            "environment/secrets."
        ),
    )
    return parser


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _atomic_write_json(path: Path, payload: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    _write_json(temporary, payload)
    temporary.replace(path)


def _taxonomy_sha256(taxonomy: tuple[str, ...]) -> str:
    encoded = json.dumps(
        list(taxonomy), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _checkpoint_payload(
    *,
    run_id: str,
    provider: str,
    model: str,
    repo_commit: str,
    packet_sha256: str,
    taxonomy_sha256: str,
    cases: dict[str, ResumableBlindCase],
    packet_order: tuple[str, ...],
) -> dict[str, object]:
    ordered = []
    for vector_id in packet_order:
        item = cases.get(vector_id)
        if item is None:
            continue
        ordered.append(
            {
                "decision": asdict(item.decision),
                "audit": asdict(item.audit),
            }
        )
    return {
        "version": 1,
        "run_id": run_id,
        "model_provider": provider,
        "model_name": model,
        "repo_commit": repo_commit,
        "packet_sha256": packet_sha256,
        "taxonomy_sha256": taxonomy_sha256,
        "completed_count": len(ordered),
        "cases": ordered,
        "ground_truth_loaded_by_this_process": False,
        "comparison_performed_by_this_process": False,
        "promotion_allowed": False,
    }


def _load_checkpoint(
    path: Path,
    *,
    run_id: str,
    provider: str,
    model: str,
    repo_commit: str,
    packet_sha256: str,
    taxonomy_sha256: str,
) -> dict[str, ResumableBlindCase]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit("existing Agent-06 checkpoint is unreadable") from exc
    if not isinstance(value, dict):
        raise SystemExit("existing Agent-06 checkpoint must be a JSON object")
    expected_identity = {
        "run_id": run_id,
        "model_provider": provider,
        "model_name": model,
        "repo_commit": repo_commit,
        "packet_sha256": packet_sha256,
        "taxonomy_sha256": taxonomy_sha256,
    }
    for key, expected in expected_identity.items():
        if value.get(key) != expected:
            raise SystemExit(f"existing Agent-06 checkpoint {key} mismatch")
    if value.get("ground_truth_loaded_by_this_process") is not False:
        raise SystemExit("resume checkpoint is not blind: ground-truth flag mismatch")
    if value.get("comparison_performed_by_this_process") is not False:
        raise SystemExit("resume checkpoint is not blind: comparison flag mismatch")
    if value.get("promotion_allowed") is not False:
        raise SystemExit("resume checkpoint cannot allow promotion")
    raw_cases = value.get("cases")
    if not isinstance(raw_cases, list):
        raise SystemExit("existing Agent-06 checkpoint cases are invalid")

    result: dict[str, ResumableBlindCase] = {}
    for raw in raw_cases:
        if not isinstance(raw, dict) or set(raw) != {"decision", "audit"}:
            raise SystemExit("existing Agent-06 checkpoint case is invalid")
        decision_raw = raw["decision"]
        audit_raw = raw["audit"]
        if not isinstance(decision_raw, dict) or not isinstance(audit_raw, dict):
            raise SystemExit("existing Agent-06 checkpoint case payload is invalid")
        try:
            decision = IndependentValidationDecision(
                vector_id=str(decision_raw["vector_id"]),
                source_locator=str(decision_raw["source_locator"]),
                predicted_label=(
                    None
                    if decision_raw["predicted_label"] is None
                    else str(decision_raw["predicted_label"])
                ),
                confidence=float(decision_raw["confidence"]),
                evidence=tuple(str(item) for item in decision_raw["evidence"]),
                ambiguities=tuple(str(item) for item in decision_raw["ambiguities"]),
            )
            images_raw = audit_raw["images"]
            if not isinstance(images_raw, list) or any(not isinstance(item, dict) for item in images_raw):
                raise TypeError("images")
            audit = MultimodalRuntimeCaseAudit(
                vector_id=str(audit_raw["vector_id"]),
                source_locator=str(audit_raw["source_locator"]),
                source_text_sha256=(
                    None
                    if audit_raw["source_text_sha256"] is None
                    else str(audit_raw["source_text_sha256"])
                ),
                images=tuple(
                    MultimodalImageAudit(
                        mime_type=str(item["mime_type"]),
                        sha256=str(item["sha256"]),
                        size_bytes=int(item["size_bytes"]),
                    )
                    for item in images_raw
                ),
                predicted_label=(
                    None
                    if audit_raw["predicted_label"] is None
                    else str(audit_raw["predicted_label"])
                ),
                abstained=bool(audit_raw["abstained"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise SystemExit("existing Agent-06 checkpoint case fields are invalid") from exc
        if decision.vector_id in result:
            raise SystemExit("existing Agent-06 checkpoint contains duplicate vector IDs")
        result[decision.vector_id] = ResumableBlindCase(decision=decision, audit=audit)
    if value.get("completed_count") != len(result):
        raise SystemExit("existing Agent-06 checkpoint completed_count mismatch")
    return result


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.command:
        raise SystemExit("external model wrapper command is required")
    repo_commit = args.repo_commit.strip() or "UNSPECIFIED"
    packet = load_blind_packet(args.packet)
    resolver = FileSystemPrimaryContextBundleResolver(
        bundle_root=args.bundle_root,
        manifest_path=args.manifest,
    )
    client = CommandStructuredModelClient(
        CommandModelClientConfig.from_command(tuple(args.command))
    )

    readiness = assess_agent06_readiness(
        packet=packet,
        resolver=resolver,
        model_client=client,
        model_provider=args.provider,
        model_name=args.model,
    )
    if not readiness.ready_to_run:
        output = asdict(readiness)
        output["blockers"] = list(readiness.blockers)
        output["status"] = "NOT_READY"
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 2

    output_dir = Path(args.output_dir)
    checkpoint_path = output_dir / _CHECKPOINT_NAME
    packet_hash = blind_packet_sha256(packet)
    taxonomy_hash = _taxonomy_sha256(packet.taxonomy)
    packet_order = tuple(case.vector_id for case in packet.cases)

    if args.resume_existing:
        if not output_dir.is_dir() or not checkpoint_path.is_file():
            raise SystemExit("resume requested but existing Agent-06 checkpoint is unavailable")
        if (output_dir / "agent06_blind_predictions.json").exists() or (
            output_dir / "agent06_runtime_manifest.json"
        ).exists():
            raise SystemExit("blind run already has final outputs; refusing resume")
        resume_cases = _load_checkpoint(
            checkpoint_path,
            run_id=args.run_id,
            provider=args.provider,
            model=args.model,
            repo_commit=repo_commit,
            packet_sha256=packet_hash,
            taxonomy_sha256=taxonomy_hash,
        )
        print(f"[resume] verified {len(resume_cases)}/{len(packet.cases)} completed blind cases", flush=True)
    else:
        try:
            output_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise SystemExit("output directory already exists; refusing to overwrite a blind run") from exc
        resume_cases = {}
        _atomic_write_json(
            checkpoint_path,
            _checkpoint_payload(
                run_id=args.run_id,
                provider=args.provider,
                model=args.model,
                repo_commit=repo_commit,
                packet_sha256=packet_hash,
                taxonomy_sha256=taxonomy_hash,
                cases=resume_cases,
                packet_order=packet_order,
            ),
        )

    agent = IndependentValidationAgent(client)
    checkpoint_cases = dict(resume_cases)

    def checkpoint_case(
        position: int,
        total: int,
        decision: IndependentValidationDecision,
        audit: MultimodalRuntimeCaseAudit,
    ) -> None:
        checkpoint_cases[decision.vector_id] = ResumableBlindCase(decision=decision, audit=audit)
        _atomic_write_json(
            checkpoint_path,
            _checkpoint_payload(
                run_id=args.run_id,
                provider=args.provider,
                model=args.model,
                repo_commit=repo_commit,
                packet_sha256=packet_hash,
                taxonomy_sha256=taxonomy_hash,
                cases=checkpoint_cases,
                packet_order=packet_order,
            ),
        )
        print(
            f"[case {position}/{total}] {decision.vector_id} "
            f"{'ABSTAIN' if decision.abstained else 'COMPLETE'}",
            flush=True,
        )

    batch, manifest = execute_multimodal_blind_validation_runtime(
        run_id=args.run_id,
        model_provider=args.provider,
        model_name=args.model,
        packet=packet,
        agent=agent,
        source_context_resolver=resolver.resolve_payload,
        resume_cases=resume_cases,
        on_case_completed=checkpoint_case,
    )

    decisions_payload = {
        "version": 1,
        "run_id": manifest.run_id,
        "model_provider": manifest.model_provider,
        "model_name": manifest.model_name,
        "packet_sha256": manifest.packet_sha256,
        "taxonomy_sha256": manifest.taxonomy_sha256,
        "case_count": manifest.case_count,
        "decisions": [asdict(decision) for decision in batch.decisions],
        "ground_truth_loaded_by_this_process": False,
        "comparison_performed_by_this_process": False,
        "promotion_allowed": False,
    }
    manifest_payload = asdict(manifest)
    readiness_payload = asdict(readiness)
    readiness_payload["blockers"] = list(readiness.blockers)
    readiness_payload["status"] = "READY_TO_RUN"

    predictions_path = output_dir / "agent06_blind_predictions.json"
    manifest_path = output_dir / "agent06_runtime_manifest.json"
    readiness_path = output_dir / "agent06_readiness.json"
    _write_json(predictions_path, decisions_payload)
    _write_json(manifest_path, manifest_payload)
    _write_json(readiness_path, readiness_payload)

    summary = {
        "status": "BLIND_RUN_COMPLETE",
        "run_id": manifest.run_id,
        "model_provider": manifest.model_provider,
        "model_name": manifest.model_name,
        "repo_commit": repo_commit,
        "case_count": manifest.case_count,
        "completed_count": manifest.completed_count,
        "resumed_count": len(resume_cases),
        "abstained_count": manifest.abstained_count,
        "image_case_count": manifest.image_case_count,
        "packet_sha256": manifest.packet_sha256,
        "predictions_path": str(predictions_path),
        "manifest_path": str(manifest_path),
        "readiness_path": str(readiness_path),
        "checkpoint_path": str(checkpoint_path),
        "comparison_performed": False,
        "promotion_allowed": False,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
