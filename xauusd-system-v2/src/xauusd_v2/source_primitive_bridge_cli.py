from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from .source_primitive_bridge import SourcePrimitiveBridgeError, build_source_primitive_bridge


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xauusd-v2-source-primitive-bridge",
        description=(
            "Join a source-fidelity replay report to a primitive replay scan by exact closed-bar timestamp. "
            "The output measures raw correspondence only and never certifies FU, HCS, R-143 stages, strategy truth or performance."
        ),
    )
    parser.add_argument("source_fidelity_report", type=Path)
    parser.add_argument("primitive_scan_report", type=Path)
    return parser


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = build_source_primitive_bridge(
            args.source_fidelity_report,
            args.primitive_scan_report,
        )
        payload = {
            "schema_version": "source_primitive_bridge_report_v1",
            "status": "SOURCE_PRIMITIVE_BRIDGE_COMPLETE_NOT_CERTIFIED",
            **asdict(result),
            "interpretation": (
                "Exact-bar source-to-raw correspondence only. False means the covered exact anchor bar was not a raw candidate; "
                "null means the primitive scan did not cover that anchor. Neither state is a strategy verdict."
            ),
            "reference_feed_alignment_complete": False,
            "reference_feed_required": "FOREXCOM:XAUUSD",
        }
        print(json.dumps(_jsonable(payload), sort_keys=True, indent=2))
        return 0
    except (SourcePrimitiveBridgeError, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
