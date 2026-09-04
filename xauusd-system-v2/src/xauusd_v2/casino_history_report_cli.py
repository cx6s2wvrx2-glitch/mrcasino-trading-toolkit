from __future__ import annotations

import argparse
import json
from datetime import datetime

from .casino_history_report import build_verified_indicator_history_report


def _datetime(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError("timestamp must be timezone-aware")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay supplied Casino/BETA indicator events from a verified persisted XAUUSD MT5 snapshot."
    )
    parser.add_argument("ingestion_manifest")
    parser.add_argument("--timeframe", default="M15", help="M1, M5, M10, M15, M30, H1, H4, H8 or D1")
    parser.add_argument("--start", required=True, type=_datetime)
    parser.add_argument("--end", required=True, type=_datetime)
    args = parser.parse_args()

    report = build_verified_indicator_history_report(
        args.ingestion_manifest,
        timeframe_code=args.timeframe,
        start_utc=args.start,
        end_utc=args.end,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
