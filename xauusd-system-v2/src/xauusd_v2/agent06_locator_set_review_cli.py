from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from .agent06_audit_v2_cli import audit_agent06_run
from .blind_validation_results_io import load_blind_predictions
from .validation import load_ground_truth


_DEFAULT_ROUNDS = tuple(range(2, 14))
_ROUND_RE = re.compile(r"GT-R(\d{2})-")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Re-evaluate an audited Agent-06 run against the set of all ground-truth labels attached "
            "to each exact source locator. This detects false single-label disagreements when one "
            "image/locator has multiple legitimate ground-truth concepts. It never changes frozen "
            "predictions, comparison artifacts, strategy truth, or promotion state."
        )
    )
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--datasets-dir", required=True)
    parser.add_argument("--provider", default="anthropic")
    parser.add_argument("--model", default="claude-sonnet-5")
    parser.add_argument("--case-count", type=int, default=173)
    parser.add_argument("--expected-repo-commit", default=None)
    parser.add_argument("--rounds", nargs="*", type=int, default=list(_DEFAULT_ROUNDS))
    parser.add_argument("--output", default=None)
    return parser


def _load_comparison(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("comparison must contain a JSON object")
    return payload


def _round_from_vector_id(vector_id: str) -> str:
    match = _ROUND_RE.match(vector_id)
    return f"R{match.group(1)}" if match else "UNKNOWN"


def build_locator_set_review(
    *,
    run_root: Path,
    datasets_dir: Path,
    expected_provider: str = "anthropic",
    expected_model: str = "claude-sonnet-5",
    expected_case_count: int = 173,
    expected_repo_commit: str | None = None,
    rounds: tuple[int, ...] = _DEFAULT_ROUNDS,
) -> dict[str, Any]:
    resolved_root = run_root.expanduser().resolve()
    audit = audit_agent06_run(
        run_root=resolved_root,
        expected_provider=expected_provider,
        expected_model=expected_model,
        expected_case_count=expected_case_count,
        expected_repo_commit=expected_repo_commit,
    )
    if audit.get("status") != "AUDIT_PASS":
        raise ValueError("Agent-06 run must pass corrected artifact audit before locator-set review")

    if not rounds or len(set(rounds)) != len(rounds):
        raise ValueError("rounds must be a non-empty unique sequence")
    datasets_path = datasets_dir.expanduser().resolve()
    datasets = tuple(
        load_ground_truth(datasets_path / f"ground_truth_round_{round_no:02d}.json")
        for round_no in rounds
    )

    vectors_by_id = {}
    labels_by_locator: dict[str, set[str]] = defaultdict(set)
    ids_by_locator: dict[str, list[str]] = defaultdict(list)
    for dataset in datasets:
        for vector in dataset.vectors:
            if vector.id in vectors_by_id:
                raise ValueError(f"duplicate ground-truth vector id: {vector.id}")
            vectors_by_id[vector.id] = vector
            labels_by_locator[vector.source_locator].add(vector.expected_label)
            ids_by_locator[vector.source_locator].append(vector.id)

    predictions = load_blind_predictions(resolved_root / "agent06_blind_predictions.json")
    comparison = _load_comparison(resolved_root / "agent06_comparison.json")
    if predictions.case_count != expected_case_count or len(vectors_by_id) != expected_case_count:
        raise ValueError("prediction/ground-truth case count does not match expected case count")
    if set(vectors_by_id) != {decision.vector_id for decision in predictions.batch.decisions}:
        raise ValueError("prediction ids do not exactly match ground-truth ids")

    original_outcomes = comparison.get("outcomes")
    if not isinstance(original_outcomes, list) or len(original_outcomes) != expected_case_count:
        raise ValueError("comparison outcomes are missing or inconsistent")
    original_result_by_id = {}
    for outcome in original_outcomes:
        if not isinstance(outcome, dict):
            raise ValueError("comparison outcome is not an object")
        vector_id = str(outcome.get("vector_id", "")).strip()
        result = str(outcome.get("result", "")).strip()
        if not vector_id or vector_id in original_result_by_id:
            raise ValueError("comparison outcome vector ids are missing or duplicated")
        original_result_by_id[vector_id] = result

    exact_agree = 0
    locator_set_agree = 0
    unresolved_disagree = 0
    abstain = 0
    cases: list[dict[str, Any]] = []
    by_round: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for decision in predictions.batch.decisions:
        vector = vectors_by_id[decision.vector_id]
        if decision.source_locator != vector.source_locator:
            raise ValueError(f"prediction locator mismatch for {decision.vector_id}")
        locator_labels = tuple(sorted(labels_by_locator[vector.source_locator]))
        predicted = decision.predicted_label

        if predicted is None:
            adjusted = "ABSTAIN"
            abstain += 1
        elif predicted == vector.expected_label:
            adjusted = "EXACT_AGREE"
            exact_agree += 1
        elif predicted in labels_by_locator[vector.source_locator]:
            adjusted = "LOCATOR_SET_AGREE"
            locator_set_agree += 1
        else:
            adjusted = "UNRESOLVED_DISAGREE"
            unresolved_disagree += 1

        round_name = _round_from_vector_id(decision.vector_id)
        by_round[round_name][adjusted] += 1
        if adjusted != "EXACT_AGREE":
            cases.append(
                {
                    "vector_id": decision.vector_id,
                    "round": round_name,
                    "source_locator": vector.source_locator,
                    "expected_label": vector.expected_label,
                    "predicted_label": predicted,
                    "all_ground_truth_labels_for_locator": list(locator_labels),
                    "same_locator_vector_ids": sorted(ids_by_locator[vector.source_locator]),
                    "original_result": original_result_by_id.get(decision.vector_id),
                    "adjusted_result": adjusted,
                    "confidence": decision.confidence,
                    "provider_evidence": list(decision.evidence),
                    "provider_ambiguities": list(decision.ambiguities),
                }
            )

    multi_label_locators = {
        locator: tuple(sorted(labels))
        for locator, labels in labels_by_locator.items()
        if len(labels) > 1
    }
    multi_label_case_count = sum(
        len(ids_by_locator[locator]) for locator in multi_label_locators
    )

    return {
        "status": "AGENT06_LOCATOR_SET_REVIEW_READY",
        "run_id": predictions.run_id,
        "provider": predictions.model_provider,
        "model": predictions.model_name,
        "audit_status": audit.get("status"),
        "total_cases": expected_case_count,
        "original_agree": comparison.get("agree"),
        "original_disagree": comparison.get("disagree"),
        "original_ambiguous": comparison.get("ambiguous"),
        "exact_agree": exact_agree,
        "locator_set_agree": locator_set_agree,
        "unresolved_disagree": unresolved_disagree,
        "abstain": abstain,
        "single_label_adjusted_supported": exact_agree + locator_set_agree,
        "multi_label_locator_count": len(multi_label_locators),
        "multi_label_case_count": multi_label_case_count,
        "multi_label_locators": [
            {
                "source_locator": locator,
                "ground_truth_labels": list(labels),
                "vector_ids": sorted(ids_by_locator[locator]),
            }
            for locator, labels in sorted(multi_label_locators.items())
        ],
        "by_round": {
            round_name: dict(sorted(counts.items()))
            for round_name, counts in sorted(by_round.items())
        },
        "cases": cases,
        "interpretation": (
            "LOCATOR_SET_AGREE means the model selected a different label that the benchmark itself "
            "also assigns to the exact same source locator. Such a result is a single-label benchmark "
            "collision, not evidence that the model contradicted the source."
        ),
        "review_is_deterministic_only": True,
        "strategy_truth_changed": False,
        "promotion_allowed": False,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = build_locator_set_review(
        run_root=Path(args.run_root),
        datasets_dir=Path(args.datasets_dir),
        expected_provider=args.provider,
        expected_model=args.model,
        expected_case_count=args.case_count,
        expected_repo_commit=args.expected_repo_commit,
        rounds=tuple(args.rounds),
    )
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        if output_path.exists():
            raise SystemExit("review output already exists; refusing to overwrite")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
