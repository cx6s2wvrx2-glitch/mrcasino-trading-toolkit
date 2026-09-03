from __future__ import annotations

import unittest
from datetime import UTC, datetime
from types import SimpleNamespace

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.march_reference_feed import (
    MarchReferenceFeedError,
    _feed_geometry,
    _normalize_reference_csv,
    _primitive_correspondence,
)
from xauusd_v2.march_reference_feed_cli import build_parser


class MarchReferenceFeedTests(unittest.TestCase):
    def bar(self, minute: int, *, close: float = 100.0, source: str = "FOREXCOM") -> MarketBar:
        return MarketBar(
            timestamp=datetime(2023, 3, 30, 12, minute, tzinfo=UTC),
            open=100.0,
            high=max(100.5, close),
            low=min(99.5, close),
            close=close,
            is_closed=True,
            source_name=source,
            source_symbol="XAUUSD" if source == "FOREXCOM" else "XAUUSD!",
        )

    def test_cli_requires_explicit_forexcom_reference_identity(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["reference.csv", "manifest.json"])
        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "reference.csv",
                    "manifest.json",
                    "--reference-feed-id",
                    "SOMEOTHER:XAUUSD",
                ]
            )
        args = parser.parse_args(
            [
                "reference.csv",
                "manifest.json",
                "--reference-feed-id",
                "FOREXCOM:XAUUSD",
            ]
        )
        self.assertEqual(args.reference_feed_id, "FOREXCOM:XAUUSD")

    def test_reference_normalization_accepts_time_alias_and_preserves_exact_prices(self) -> None:
        raw = (
            "time,open,high,low,close,Volume\n"
            "2023-03-30T00:00:00Z,1970.10,1971.20,1969.90,1970.80,10\n"
            "2023-03-30T00:01:00+00:00,1970.80,1971.00,1970.20,1970.30,11\n"
        ).encode()
        normalized, _, count = _normalize_reference_csv(raw)
        self.assertEqual(count, 2)
        text = normalized.decode()
        self.assertIn("timestamp,open,high,low,close\n", text)
        self.assertIn("2023-03-30T00:00:00Z,1970.10,1971.20,1969.90,1970.80\n", text)
        self.assertNotIn("Volume", text)

    def test_naive_reference_timestamp_fails_closed(self) -> None:
        raw = (
            "time,open,high,low,close\n"
            "2023-03-30 00:00:00,1970,1971,1969,1970.5\n"
            "2023-03-30 00:01:00,1970.5,1971,1970,1970.2\n"
        ).encode()
        with self.assertRaisesRegex(MarchReferenceFeedError, "naive timestamp rejected"):
            _normalize_reference_csv(raw)

    def test_duplicate_or_out_of_order_timestamp_fails_closed(self) -> None:
        duplicate = (
            "timestamp,open,high,low,close\n"
            "2023-03-30T00:00:00Z,1970,1971,1969,1970.5\n"
            "2023-03-30T00:00:00Z,1970.5,1971,1970,1970.2\n"
        ).encode()
        with self.assertRaisesRegex(MarchReferenceFeedError, "strictly increasing"):
            _normalize_reference_csv(duplicate)

    def test_out_of_window_future_rows_cannot_change_bounded_normalized_sample(self) -> None:
        base = (
            "timestamp,open,high,low,close\n"
            "2023-03-30T00:00:00Z,1970,1971,1969,1970.5\n"
            "2023-03-30T00:01:00Z,1970.5,1971,1970,1970.2\n"
        ).encode()
        extended = base + b"2023-04-01T00:00:00Z,9999,10000,9998,9999.5\n"
        base_normalized, base_raw_sha, base_count = _normalize_reference_csv(base)
        extended_normalized, extended_raw_sha, extended_count = _normalize_reference_csv(extended)
        self.assertEqual(base_normalized, extended_normalized)
        self.assertEqual(base_count, extended_count)
        self.assertNotEqual(base_raw_sha, extended_raw_sha)

    def test_feed_geometry_uses_exact_timestamp_intersection_and_zero_tolerance(self) -> None:
        reference = (
            self.bar(0, close=100.001),
            self.bar(2, close=101.0),
        )
        broker = (
            self.bar(0, close=100.0, source="Exclusive Markets Ltd."),
            self.bar(1, close=101.0, source="Exclusive Markets Ltd."),
        )
        report = _feed_geometry(
            reference,
            broker,
            start=datetime(2023, 3, 30, 12, 0, tzinfo=UTC),
            end=datetime(2023, 3, 30, 12, 3, tzinfo=UTC),
        )
        self.assertEqual(report["exact_timestamp_intersection_count"], 1)
        self.assertEqual(report["reference_only_timestamp_count"], 1)
        self.assertEqual(report["broker_only_timestamp_count"], 1)
        self.assertEqual(report["exact_ohlc_match_count"], 0)
        self.assertEqual(report["ohlc_delta_stats"]["close"]["nonzero_delta_count"], 1)
        self.assertEqual(report["ohlc_delta_stats"]["close"]["max_abs_delta"], "0.001")
        self.assertFalse(report["nearest_bar_substitution_allowed"])
        self.assertFalse(report["price_tolerance_applied"])

    def test_primitive_correspondence_is_exact_bar_only_not_nearest_bar(self) -> None:
        anchor_time = datetime(2023, 3, 30, 12, 1, tzinfo=UTC)
        source = SimpleNamespace(
            anchor_matches=(SimpleNamespace(anchor_id="a1", matched_at=anchor_time),)
        )
        nearest_only = SimpleNamespace(
            fu_candidates=(SimpleNamespace(bar_open=datetime(2023, 3, 30, 12, 2, tzinfo=UTC)),),
            wick_interactions=(
                SimpleNamespace(
                    interaction_bar_open=datetime(2023, 3, 30, 12, 2, tzinfo=UTC),
                    source_style_hcs_candidate=True,
                ),
            ),
            source_style_hcs_candidates=1,
        )
        nearest_report = _primitive_correspondence(source, nearest_only)
        self.assertEqual(nearest_report["exact_bar_basic_fu_correspondence_count"], 0)
        self.assertEqual(nearest_report["exact_bar_hcs_candidate_correspondence_count"], 0)

        exact = SimpleNamespace(
            fu_candidates=(SimpleNamespace(bar_open=anchor_time),),
            wick_interactions=(
                SimpleNamespace(
                    interaction_bar_open=anchor_time,
                    source_style_hcs_candidate=True,
                ),
            ),
            source_style_hcs_candidates=1,
        )
        exact_report = _primitive_correspondence(source, exact)
        self.assertEqual(exact_report["exact_bar_basic_fu_correspondence_count"], 1)
        self.assertEqual(exact_report["exact_bar_hcs_candidate_correspondence_count"], 1)
        self.assertEqual(exact_report["certified_fu_count"], 0)
        self.assertEqual(exact_report["certified_hcs_count"], 0)


if __name__ == "__main__":
    unittest.main()
