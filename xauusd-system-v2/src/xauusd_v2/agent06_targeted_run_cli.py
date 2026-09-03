from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .agent06_readiness import assess_agent06_readiness
from .agent06_run_cli import (
    _atomic_write_json,
    _checkpoint_payload,
    _load_checkpoint,
    _taxonomy_sha256,
    _write_json,
)
from .agents.validation_agent import IndependentValidationAgent, IndependentValidationDecision
from .blind_validation_multimodal_runtime import (
    MultimodalRuntimeCaseAudit,
    ResumableBlindCase,
)
from .blind_validation_packet import BlindValidationCase, BlindValidationPacket
from .focused_validation_packet import focused_packet_sha256
from .focused_validation_packet_io import load_focused_packet
from .focused_validation_runtime import execute_focused_validation_runtime
from .primary_context_bundle import FileSystemPrimaryContextBundleResolver
from .structured_model_clients import CommandModelClientConfig, CommandStructuredModelClient


_CHECKPOINT_NAME = "agent06_focused_checkpoint.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute Agent-06 focused claim adjudication against a pre-built focused packet. "
            "This process never loads ground-truth datasets, expected verdicts or comparison data."
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
        help="Git commit identity for reproducible focused checkpoint resume.",
    )
    parser.add_argument(
        "--resume-existing",
        action="store_true",
        help=(
            "Resume a focused run from its private checkpoint. Packet (including each candidate claim), "
            "verdict taxonomy, provider, model, repo commit and primary evidence must match exactly."
        ),
    )
    parser.add_argument(
        "--command",
        nargs=argparse.REMAINDER,
        required=True,
        help="External model wrapper command; must be the final option.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.command:
        raise SystemExit("external model wrapper command is required")

    repo_commit = args.repo_commit.strip() or "UNSPECIFIED"
    packet = load_focused_packet(args.packet)
    resolver = FileSystemPrimaryContextBundleResolver(
        bundle_root=args.bundle_root,
        manifest_path=args.manifest,
    )
    client = CommandStructuredModelClient(
        CommandModelClientConfig.from_command(tuple(args.command))
    )

    # Reuse the proven primary-evidence readiness gate without altering its legacy
    # packet contract. This adapter contains no expected answer and is never persisted.
    readiness_packet = BlindValidationPacket(
        dataset_name=packet.dataset_name,
        taxonomy=packet.verdict_taxonomy,
        cases=tuple(
            BlindValidationCase(
                vector_id=case.vector_id,
                source_locator=case.source_locator,
            )
            for case in packet.cases
        ),
    )
    readiness = assess_agent06_readiness(
        packet=readiness_packet,
        resolver=resolver,
        model_client=client,
        model_provider=args.provider,
        model_name=args.model,
    )
    if not readiness.ready_to_run:
        output = asdict(readiness)
        output["blockers"] = list(readiness.blockers)
        output["status"] = "FOCUSED_NOT_READY"
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 2

    output_dir = Path(args.output_dir)
    checkpoint_path = output_dir / _CHECKPOINT_NAME
    packet_hash = focused_packet_sha256(packet)
    taxonomy_hash = _taxonomy_sha256(packet.verdict_taxonomy)
    packet_order = tuple(case.vector_id for case in packet.cases)

    predictions_path = output_dir / "agent06_focused_predictions.json"
    manifest_path = output_dir / "agent06_focused_runtime_manifest.json"
    readiness_path = output_dir / "agent06_focused_readiness.json"

    if args.resume_existing:
        if not output_dir.is_dir() or not checkpoint_path.is_file():
            raise SystemExit("resume requested but existing focused checkpoint is unavailable")
        if predictions_path.exists() or manifest_path.exists():
            raise SystemExit("focused run already has final outputs; refusing resume")
        resume_cases = _load_checkpoint(
            checkpoint_path,
            run_id=args.run_id,
            provider=args.provider,
            model=args.model,
            repo_commit=repo_commit,
            packet_sha256=packet_hash,
            taxonomy_sha256=taxonomy_hash,
        )
        print(
            f"[resume] verified {len(resume_cases)}/{len(packet.cases)} completed focused cases",
            flush=True,
        )
    else:
        try:
            output_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise SystemExit("focused output directory already exists; refusing overwrite") from exc
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
        verdict = "ABSTAIN" if decision.abstained else str(decision.predicted_label)
        print(f"[case {position}/{total}] {decision.vector_id} {verdict}", flush=True)

    batch, manifest = execute_focused_validation_runtime(
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
        "protocol": "agent06_focused_claim_adjudication_v2",
        "run_id": manifest.run_id,
        "model_provider": manifest.model_provider,
        "model_name": manifest.model_name,
        "packet_sha256": manifest.packet_sha256,
        "taxonomy_sha256": manifest.taxonomy_sha256,
        "case_count": manifest.case_count,
        "decisions": [asdict(decision) for decision in batch.decisions],
        "candidate_claim_visible_to_provider": True,
        "expected_verdict_loaded_by_this_process": False,
        "ground_truth_dataset_loaded_by_this_process": False,
        "comparison_performed_by_this_process": False,
        "promotion_allowed": False,
    }
    manifest_payload = asdict(manifest)
    manifest_payload["protocol"] = "agent06_focused_claim_adjudication_v2"
    readiness_payload = asdict(readiness)
    readiness_payload["blockers"] = list(readiness.blockers)
    readiness_payload["status"] = "FOCUSED_READY_TO_RUN"

    _write_json(predictions_path, decisions_payload)
    _write_json(manifest_path, manifest_payload)
    _write_json(readiness_path, readiness_payload)

    summary = {
        "status": "FOCUSED_RUN_COMPLETE",
        "run_id": manifest.run_id,
        "model_provider": manifest.model_provider,
        "model_name": manifest.model_name,
        "repo_commit": repo_commit,
        "case_count": manifest.case_count,
        "completed_count": manifest.completed_count,
        "resumed_count": len(resume_cases),
        "provider_abstained_count": manifest.abstained_count,
        "image_case_count": manifest.image_case_count,
        "packet_sha256": manifest.packet_sha256,
        "predictions_path": str(predictions_path),
        "manifest_path": str(manifest_path),
        "readiness_path": str(readiness_path),
        "checkpoint_path": str(checkpoint_path),
        "expected_verdict_loaded": False,
        "ground_truth_dataset_loaded": False,
        "comparison_performed": False,
        "promotion_allowed": False,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
