from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .agent06_audit_cli import audit_agent06_run as _legacy_audit_agent06_run
from .agent06_readiness import locator_requires_primary_image


_FALSE_POSITIVE_BLOCKER = "readiness image-required count does not match runtime image-evidence count"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a completed local Agent-06 run with corrected readiness-vs-runtime image semantics. "
            "All legacy integrity/isolation checks remain mandatory; only the known image-count "
            "false-positive can be re-evaluated. This command never promotes strategy knowledge or rules."
        )
    )
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--provider", default="anthropic")
    parser.add_argument("--model", default="claude-sonnet-5")
    parser.add_argument("--case-count", type=int, default=173)
    parser.add_argument("--expected-repo-commit", default=None)
    parser.add_argument("--output", default=None)
    return parser


def _load_object(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return raw


def _corrected_image_semantics_blockers(run_root: Path) -> list[str]:
    blockers: list[str] = []
    runtime_path = run_root / "agent06_runtime_manifest.json"
    readiness_path = run_root / "agent06_readiness.json"
    try:
        runtime = _load_object(runtime_path)
        readiness = _load_object(readiness_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return [f"corrected image-semantics audit could not read artifacts: {exc}"]

    runtime_cases = runtime.get("cases")
    if not isinstance(runtime_cases, list):
        return ["corrected image-semantics audit requires runtime cases array"]

    syntactically_required_count = 0
    observed_image_case_count = 0
    for index, item in enumerate(runtime_cases):
        if not isinstance(item, dict):
            blockers.append(f"corrected image-semantics audit found non-object runtime case at index {index}")
            continue
        vector_id = str(item.get("vector_id", "")).strip() or f"index-{index}"
        locator = str(item.get("source_locator", "")).strip()
        images = item.get("images")
        if not isinstance(images, list):
            blockers.append(f"corrected image-semantics audit found invalid images array for {vector_id}")
            continue

        has_image = bool(images)
        if has_image:
            observed_image_case_count += 1

        if locator_requires_primary_image(locator):
            syntactically_required_count += 1
            if not has_image:
                blockers.append(f"explicit image-required locator has no runtime image evidence for {vector_id}")

    readiness_required = readiness.get("image_required_cases")
    if isinstance(readiness_required, bool) or not isinstance(readiness_required, int) or readiness_required < 0:
        blockers.append("readiness image_required_cases is invalid")
    elif readiness_required != syntactically_required_count:
        blockers.append(
            "readiness image-required count does not match syntactically image-required runtime locators"
        )

    declared_runtime_image_count = runtime.get("image_case_count")
    if (
        isinstance(declared_runtime_image_count, bool)
        or not isinstance(declared_runtime_image_count, int)
        or declared_runtime_image_count < 0
    ):
        blockers.append("runtime image_case_count is invalid")
    elif declared_runtime_image_count != observed_image_case_count:
        blockers.append("runtime image_case_count does not match actual per-case image evidence")

    return blockers


def audit_agent06_run(
    *,
    run_root: Path,
    expected_provider: str = "anthropic",
    expected_model: str = "claude-sonnet-5",
    expected_case_count: int = 173,
    expected_repo_commit: str | None = None,
) -> dict[str, Any]:
    resolved_root = run_root.expanduser().resolve()
    report = _legacy_audit_agent06_run(
        run_root=resolved_root,
        expected_provider=expected_provider,
        expected_model=expected_model,
        expected_case_count=expected_case_count,
        expected_repo_commit=expected_repo_commit,
    )

    blockers = report.get("blockers")
    if report.get("status") == "AUDIT_PASS":
        result = dict(report)
        result["image_audit_semantics"] = "locator-required-subset-v2"
        return result
    if blockers != [_FALSE_POSITIVE_BLOCKER]:
        return report

    corrected_blockers = _corrected_image_semantics_blockers(resolved_root)
    if corrected_blockers:
        result = dict(report)
        result["blockers"] = corrected_blockers
        result["image_audit_semantics"] = "locator-required-subset-v2"
        result["artifact_integrity_passed"] = False
        result["status"] = "AUDIT_FAIL"
        result["promotion_allowed"] = False
        result["independent_validation_auto_promoted"] = False
        return result

    result = dict(report)
    result["blockers"] = []
    result["image_audit_semantics"] = "locator-required-subset-v2"
    result["artifact_integrity_passed"] = True
    result["status"] = "AUDIT_PASS"
    result["promotion_allowed"] = False
    result["independent_validation_auto_promoted"] = False
    return result


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = audit_agent06_run(
        run_root=Path(args.run_root),
        expected_provider=args.provider,
        expected_model=args.model,
        expected_case_count=args.case_count,
        expected_repo_commit=args.expected_repo_commit,
    )
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        if output_path.exists():
            raise SystemExit("audit output already exists; refusing to overwrite")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report.get("status") == "AUDIT_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
