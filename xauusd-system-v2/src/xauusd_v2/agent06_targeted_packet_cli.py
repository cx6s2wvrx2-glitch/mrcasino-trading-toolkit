from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .blind_validation_packet import BlindValidationCase, BlindValidationPacket
from .blind_validation_packet_io import write_blind_packet
from .blind_validation_runtime import blind_packet_sha256
from .validation import GroundTruthVector, load_ground_truth


_DEFAULT_ROUNDS = tuple(range(2, 14))
_TARGET_RESULTS = {"UNRESOLVED_DISAGREE", "ABSTAIN"}
_VERDICT_TAXONOMY = ("SUPPORTED", "CONTRADICTED", "INSUFFICIENT")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a focused Agent-06 adjudication packet only for cases left unresolved by the "
            "collision-aware locator-set review. The candidate claim is visible because it is the "
            "question being adjudicated; the expected verdict, ground-truth evidence/class and "
            "forbidden-inference notes remain excluded."
        )
    )
    parser.add_argument("--review", required=True, help="agent06_locator_review.json")
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


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_review(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit("locator-set review is unreadable") from exc
    if not isinstance(value, dict):
        raise SystemExit("locator-set review must be one JSON object")
    if value.get("status") != "AGENT06_LOCATOR_SET_REVIEW_READY":
        raise SystemExit("locator-set review status is not ready")
    if value.get("audit_status") != "AUDIT_PASS":
        raise SystemExit("targeted adjudication requires an audited source run")
    if value.get("promotion_allowed") is not False:
        raise SystemExit("locator-set review cannot allow promotion")
    if value.get("strategy_truth_changed") is not False:
        raise SystemExit("locator-set review must not mutate strategy truth")
    return value


def _load_vectors(datasets_dir: Path, rounds: tuple[int, ...]) -> dict[str, GroundTruthVector]:
    result: dict[str, GroundTruthVector] = {}
    for round_no in rounds:
        dataset = load_ground_truth(datasets_dir / f"ground_truth_round_{round_no:02d}.json")
        for vector in dataset.vectors:
            if vector.id in result:
                raise SystemExit(f"duplicate vector id across selected datasets: {vector.id}")
            result[vector.id] = vector
    return result


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    rounds = tuple(args.rounds)
    if not rounds or len(set(rounds)) != len(rounds):
        raise SystemExit("rounds must be a non-empty unique list")

    review_path = Path(args.review).expanduser().resolve()
    datasets_dir = Path(args.datasets_dir).expanduser().resolve()
    review = _load_review(review_path)
    vectors = _load_vectors(datasets_dir, rounds)

    raw_cases = review.get("cases")
    if not isinstance(raw_cases, list):
        raise SystemExit("locator-set review cases are invalid")

    selected: list[BlindValidationCase] = []
    counts = {key: 0 for key in sorted(_TARGET_RESULTS)}
    seen_ids: set[str] = set()
    for raw in raw_cases:
        if not isinstance(raw, dict):
            raise SystemExit("locator-set review contains an invalid case")
        adjusted_result = str(raw.get("adjusted_result", "")).strip()
        if adjusted_result not in _TARGET_RESULTS:
            continue
        vector_id = str(raw.get("vector_id", "")).strip()
        source_locator = str(raw.get("source_locator", "")).strip()
        if not vector_id or vector_id in seen_ids:
            raise SystemExit("locator-set review contains duplicate/empty target vector id")
        vector = vectors.get(vector_id)
        if vector is None:
            raise SystemExit(f"target vector is missing from selected ground truth datasets: {vector_id}")
        if vector.source_locator != source_locator:
            raise SystemExit(f"target vector source locator changed since locator-set review: {vector_id}")
        # The candidate label is intentionally exposed as the question under review.
        # Its expected adjudication is NOT exposed. Evidence, expected class and
        # forbidden-inference metadata are also excluded from the provider packet.
        selected.append(
            BlindValidationCase(
                vector_id=vector.id,
                source_locator=vector.source_locator,
                focus=vector.expected_label,
            )
        )
        seen_ids.add(vector_id)
        counts[adjusted_result] += 1

    if not selected:
        raise SystemExit("locator-set review contains no unresolved/abstained cases")

    expected_total = int(review.get("unresolved_disagree", -1)) + int(review.get("abstain", -1))
    if expected_total != len(selected):
        raise SystemExit("locator-set review unresolved counts do not match selected target cases")

    packet = BlindValidationPacket(
        dataset_name=(
            f"XAUUSD V2 Agent-06 Focused Claim Adjudication from {str(review.get('run_id', '')).strip()}"
        ),
        taxonomy=_VERDICT_TAXONOMY,
        cases=tuple(selected),
    )
    write_blind_packet(packet, args.output)

    summary = {
        "status": "AGENT06_TARGETED_PACKET_WRITTEN",
        "output": str(Path(args.output)),
        "source_review": str(review_path),
        "source_review_sha256": _sha256_file(review_path),
        "source_run_id": str(review.get("run_id", "")),
        "case_count": len(packet.cases),
        "selected_from": counts,
        "verdict_taxonomy": list(packet.taxonomy),
        "packet_sha256": blind_packet_sha256(packet),
        "candidate_claim_visible": True,
        "contains_expected_verdicts": False,
        "contains_ground_truth_evidence": False,
        "contains_expected_class": False,
        "contains_forbidden_inference": False,
        "promotion_allowed": False,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
