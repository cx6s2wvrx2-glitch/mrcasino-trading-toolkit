from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .agent06_readiness import assess_agent06_readiness
from .blind_validation_packet import build_blind_packet_multi
from .primary_context_bundle import FileSystemPrimaryContextBundleResolver
from .structured_model_clients import CommandModelClientConfig, CommandStructuredModelClient
from .validation import load_ground_truth


_DEFAULT_ROUNDS = tuple(range(2, 14))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fail-closed readiness check for a real XAUUSD V2 Agent-06 blind validation run."
    )
    parser.add_argument("--bundle-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--datasets-dir", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument(
        "--rounds",
        nargs="*",
        type=int,
        default=list(_DEFAULT_ROUNDS),
        help="Ground-truth round numbers. Defaults to 2..13.",
    )
    parser.add_argument(
        "--command",
        nargs="+",
        required=True,
        help="External model wrapper command. Credentials must be supplied through environment/secrets, never here.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    rounds = tuple(args.rounds)
    if not rounds:
        raise SystemExit("at least one round is required")
    if len(set(rounds)) != len(rounds):
        raise SystemExit("duplicate round numbers are not allowed")

    datasets_dir = Path(args.datasets_dir)
    datasets = tuple(
        load_ground_truth(datasets_dir / f"ground_truth_round_{round_no:02d}.json")
        for round_no in rounds
    )
    packet = build_blind_packet_multi(
        datasets,
        dataset_name=f"XAUUSD V2 Blind Validation Rounds {min(rounds):02d}-{max(rounds):02d}",
    )
    resolver = FileSystemPrimaryContextBundleResolver(
        bundle_root=args.bundle_root,
        manifest_path=args.manifest,
    )
    client = CommandStructuredModelClient(
        CommandModelClientConfig.from_command(tuple(args.command))
    )
    report = assess_agent06_readiness(
        packet=packet,
        resolver=resolver,
        model_client=client,
        model_provider=args.provider,
        model_name=args.model,
    )
    output = asdict(report)
    output["blockers"] = list(report.blockers)
    output["status"] = "READY_TO_RUN" if report.ready_to_run else "NOT_READY"
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0 if report.ready_to_run else 2


if __name__ == "__main__":
    raise SystemExit(main())
