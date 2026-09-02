from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .agent06_readiness import assess_agent06_readiness
from .agents.validation_agent import IndependentValidationAgent
from .blind_validation_multimodal_runtime import execute_multimodal_blind_validation_runtime
from .blind_validation_packet_io import load_blind_packet
from .primary_context_bundle import FileSystemPrimaryContextBundleResolver
from .structured_model_clients import CommandModelClientConfig, CommandStructuredModelClient


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


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.command:
        raise SystemExit("external model wrapper command is required")
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
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise SystemExit("output directory already exists; refusing to overwrite a blind run") from exc

    agent = IndependentValidationAgent(client)
    batch, manifest = execute_multimodal_blind_validation_runtime(
        run_id=args.run_id,
        model_provider=args.provider,
        model_name=args.model,
        packet=packet,
        agent=agent,
        source_context_resolver=resolver.resolve_payload,
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
        "case_count": manifest.case_count,
        "completed_count": manifest.completed_count,
        "abstained_count": manifest.abstained_count,
        "image_case_count": manifest.image_case_count,
        "packet_sha256": manifest.packet_sha256,
        "predictions_path": str(predictions_path),
        "manifest_path": str(manifest_path),
        "readiness_path": str(readiness_path),
        "comparison_performed": False,
        "promotion_allowed": False,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
