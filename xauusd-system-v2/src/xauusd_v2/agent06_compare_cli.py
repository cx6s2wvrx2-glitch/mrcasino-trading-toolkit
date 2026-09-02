from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from .blind_validation_compare import compare_blind_multi_batch
from .blind_validation_packet_io import load_blind_packet
from .blind_validation_results_io import load_blind_predictions
from .blind_validation_runtime import blind_packet_sha256
from .validation import load_ground_truth


_DEFAULT_ROUNDS = tuple(range(2, 14))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare an already-completed blind Agent-06 run against ground truth. "
            "This is intentionally a separate post-run process."
        )
    )
    parser.add_argument("--packet", required=True)
    parser.add_argument("--predictions", required=True)
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

    packet = load_blind_packet(args.packet)
    prediction_file = load_blind_predictions(args.predictions)
    packet_digest = blind_packet_sha256(packet)
    if prediction_file.packet_sha256 != packet_digest:
        raise SystemExit("prediction packet fingerprint does not match supplied blind packet")
    if prediction_file.case_count != len(packet.cases):
        raise SystemExit("prediction case count does not match supplied blind packet")

    packet_by_id = {case.vector_id: case.source_locator for case in packet.cases}
    decisions = prediction_file.batch.decisions
    if set(packet_by_id) != {decision.vector_id for decision in decisions}:
        raise SystemExit("prediction vector ids do not exactly match supplied blind packet")
    for decision in decisions:
        if packet_by_id[decision.vector_id] != decision.source_locator:
            raise SystemExit(f"prediction locator mismatch for {decision.vector_id}")
        if decision.predicted_label is not None and decision.predicted_label not in packet.taxonomy:
            raise SystemExit(f"prediction label is outside packet taxonomy for {decision.vector_id}")

    datasets_dir = Path(args.datasets_dir)
    datasets = tuple(
        load_ground_truth(datasets_dir / f"ground_truth_round_{round_no:02d}.json")
        for round_no in rounds
    )
    report = compare_blind_multi_batch(datasets=datasets, batch=prediction_file.batch)

    report_payload = asdict(report)
    report_payload.update(
        {
            "version": 1,
            "run_id": prediction_file.run_id,
            "model_provider": prediction_file.model_provider,
            "model_name": prediction_file.model_name,
            "packet_sha256": packet_digest,
            "predictions_sha256": hashlib.sha256(
                Path(args.predictions).read_bytes()
            ).hexdigest(),
            "comparison_performed_after_blind_run": True,
            "promotion_allowed": False,
        }
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise SystemExit("comparison output already exists; refusing to overwrite")
    output_path.write_text(
        json.dumps(report_payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    summary = {
        "status": "COMPARISON_COMPLETE",
        "run_id": prediction_file.run_id,
        "model_provider": prediction_file.model_provider,
        "model_name": prediction_file.model_name,
        "agree": report.agree,
        "disagree": report.disagree,
        "ambiguous": report.ambiguous,
        "total": report.total,
        "all_agree": report.all_agree,
        "promotion_allowed": False,
        "output": str(output_path),
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
