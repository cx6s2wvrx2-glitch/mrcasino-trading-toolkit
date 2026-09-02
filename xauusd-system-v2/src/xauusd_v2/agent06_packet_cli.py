from __future__ import annotations

import argparse
import json
from pathlib import Path

from .blind_validation_packet import build_blind_packet_multi
from .blind_validation_packet_io import write_blind_packet
from .blind_validation_runtime import blind_packet_sha256
from .validation import load_ground_truth


_DEFAULT_ROUNDS = tuple(range(2, 14))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build an answer-free Agent-06 blind packet before any external model process is started."
        )
    )
    parser.add_argument("--datasets-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--rounds",
        nargs="*",
        type=int,
        default=list(_DEFAULT_ROUNDS),
        help="Ground-truth round numbers. Defaults to 2..13.",
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
    write_blind_packet(packet, args.output)
    summary = {
        "status": "BLIND_PACKET_WRITTEN",
        "output": str(Path(args.output)),
        "case_count": len(packet.cases),
        "taxonomy_count": len(packet.taxonomy),
        "packet_sha256": blind_packet_sha256(packet),
        "contains_per_case_expected_answers": False,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
