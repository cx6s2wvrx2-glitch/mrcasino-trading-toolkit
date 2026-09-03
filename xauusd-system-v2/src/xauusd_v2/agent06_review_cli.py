from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .agent06_audit_v2_cli import audit_agent06_run
from .blind_validation_results_io import load_blind_predictions


_ROUND_RE = re.compile(r"^GT-R([0-9]{2})-[0-9]+$")
_ALLOWED_RESULTS = {"AGREE", "DISAGREE", "AMBIGUOUS"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic review report for the non-agree cases from an already completed "
            "and audited Agent-06 run. This command performs no provider calls and never promotes rules."
        )
    )
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--expected-repo-commit", required=True)
    parser.add_argument("--provider", default="anthropic")
    parser.add_argument("--model", default="claude-sonnet-5")
    parser.add_argument("--case-count", type=int, default=173)
    parser.add_argument("--output", default=None)
    return parser


def _load_object(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return raw


def _round_from_vector_id(vector_id: str) -> int | None:
    match = _ROUND_RE.fullmatch(vector_id)
    if match is None:
        return None
    return int(match.group(1))


def _review_priority(*, result: str, confidence: float) -> str:
    if result == "AMBIGUOUS":
        return "ABSTENTION_REVIEW"
    if confidence >= 0.80:
        return "HIGH_CONFIDENCE_DISAGREEMENT"
    return "DISAGREEMENT_REVIEW"


def build_review_report(
    *,
    run_root: Path,
    expected_repo_commit: str,
    expected_provider: str = "anthropic",
    expected_model: str = "claude-sonnet-5",
    expected_case_count: int = 173,
) -> dict[str, Any]:
    root = run_root.expanduser().resolve()
    audit = audit_agent06_run(
        run_root=root,
        expected_provider=expected_provider,
        expected_model=expected_model,
        expected_case_count=expected_case_count,
        expected_repo_commit=expected_repo_commit,
    )
    if audit.get("status") != "AUDIT_PASS":
        raise ValueError("Agent-06 review requires AUDIT_PASS before non-agreement analysis")

    comparison = _load_object(root / "agent06_comparison.json")
    predictions = load_blind_predictions(root / "agent06_blind_predictions.json")
    outcomes = comparison.get("outcomes")
    if not isinstance(outcomes, list):
        raise ValueError("comparison outcomes must be a JSON array")
    if len(outcomes) != expected_case_count:
        raise ValueError("comparison outcome count does not match expected case count")

    decisions = {decision.vector_id: decision for decision in predictions.batch.decisions}
    if len(decisions) != expected_case_count:
        raise ValueError("prediction decision count does not match expected case count")

    cases: list[dict[str, Any]] = []
    by_round: dict[str, dict[str, int]] = {}
    high_confidence_disagreements = 0
    observed_counts = {"AGREE": 0, "DISAGREE": 0, "AMBIGUOUS": 0}
    seen_ids: set[str] = set()

    for raw in outcomes:
        if not isinstance(raw, dict):
            raise ValueError("comparison contains non-object outcome")
        vector_id = str(raw.get("vector_id", "")).strip()
        result = str(raw.get("result", "")).strip()
        expected_label = str(raw.get("expected_label", "")).strip()
        predicted_raw = raw.get("predicted_label")
        predicted_label = None if predicted_raw is None else str(predicted_raw).strip() or None

        if not vector_id or vector_id in seen_ids:
            raise ValueError("comparison contains duplicate or empty vector_id")
        seen_ids.add(vector_id)
        if result not in _ALLOWED_RESULTS:
            raise ValueError(f"unsupported comparison result for {vector_id}: {result}")
        if not expected_label:
            raise ValueError(f"comparison expected label is missing for {vector_id}")
        decision = decisions.get(vector_id)
        if decision is None:
            raise ValueError(f"comparison vector is missing from frozen predictions: {vector_id}")
        if decision.predicted_label != predicted_label:
            raise ValueError(f"comparison/prediction label mismatch for {vector_id}")

        observed_counts[result] += 1
        if result == "AGREE":
            continue

        round_number = _round_from_vector_id(vector_id)
        round_key = f"R{round_number:02d}" if round_number is not None else "UNKNOWN"
        round_counts = by_round.setdefault(round_key, {"DISAGREE": 0, "AMBIGUOUS": 0, "total": 0})
        round_counts[result] += 1
        round_counts["total"] += 1

        priority = _review_priority(result=result, confidence=decision.confidence)
        if priority == "HIGH_CONFIDENCE_DISAGREEMENT":
            high_confidence_disagreements += 1

        cases.append(
            {
                "vector_id": vector_id,
                "round": round_number,
                "result": result,
                "review_priority": priority,
                "expected_label": expected_label,
                "predicted_label": predicted_label,
                "confidence": decision.confidence,
                "source_locator": decision.source_locator,
                "provider_evidence": list(decision.evidence),
                "provider_ambiguities": list(decision.ambiguities),
            }
        )

    declared_counts = {
        "AGREE": comparison.get("agree"),
        "DISAGREE": comparison.get("disagree"),
        "AMBIGUOUS": comparison.get("ambiguous"),
    }
    if declared_counts != observed_counts:
        raise ValueError("comparison declared counts do not match per-case outcomes")

    cases.sort(key=lambda item: (item["round"] if item["round"] is not None else 999, item["vector_id"]))
    by_round = dict(sorted(by_round.items()))

    return {
        "status": "AGENT06_REVIEW_REPORT_READY",
        "run_id": predictions.run_id,
        "run_repo_commit": expected_repo_commit,
        "provider": predictions.model_provider,
        "model": predictions.model_name,
        "audit_status": "AUDIT_PASS",
        "total_cases": expected_case_count,
        "agree": observed_counts["AGREE"],
        "disagree": observed_counts["DISAGREE"],
        "ambiguous": observed_counts["AMBIGUOUS"],
        "non_agree_total": len(cases),
        "high_confidence_disagreement_count": high_confidence_disagreements,
        "by_round": by_round,
        "cases": cases,
        "review_is_deterministic_only": True,
        "strategy_truth_changed": False,
        "promotion_allowed": False,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = build_review_report(
            run_root=Path(args.run_root),
            expected_repo_commit=args.expected_repo_commit,
            expected_provider=args.provider,
            expected_model=args.model,
            expected_case_count=args.case_count,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

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
