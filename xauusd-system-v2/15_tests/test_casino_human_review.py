from __future__ import annotations

import unittest

from xauusd_v2.casino_human_review import build_greek_human_review


class CasinoHumanReviewTests(unittest.TestCase):
    def test_review_keeps_supplied_markers_proxies_and_compound_frames_readable(self) -> None:
        report = {
            "broker_name": "Exclusive Markets",
            "broker_symbol": "XAUUSD!",
            "timeframe": "M15",
            "window_start_utc": "2023-03-30T00:00:00Z",
            "window_end_utc": "2023-04-01T00:00:00Z",
            "reference_feed_alignment_complete": False,
            "events": [
                {"kind": "strong_fu", "direction": "bullish"},
                {"kind": "strong_fu", "direction": "bearish"},
                {"kind": "attempted_fu", "direction": "bearish"},
            ],
            "source_hcs_marker_proxy_candidates": [
                {"form": "strong_attempted", "same_direction": False},
                {"form": "attempted_attempted", "same_direction": True},
            ],
            "source_marker_fu_negation_proxy_candidates": [{"id": 1}],
            "source_hcs_plus_negation_proxy_candidates": [{"id": 1}],
            "hcs_implementation_vs_source_marker_proxy": {
                "beta_hcs_event_bar_count": 8,
                "source_marker_proxy_bar_count": 14,
                "overlap_bar_count": 1,
                "beta_only_bar_count": 7,
                "source_proxy_only_bar_count": 13,
            },
            "analysis_event_stream_frames": [
                {
                    "bar_time_utc": "2023-03-30T12:30:00Z",
                    "events": [
                        {
                            "kind": "strong_fu",
                            "direction": "bearish",
                            "candidate_only": False,
                        },
                        {
                            "kind": "source_hcs_proxy",
                            "direction": "bearish",
                            "candidate_only": True,
                        },
                    ],
                }
            ],
        }

        text = build_greek_human_review(report)
        self.assertIn("Strong FU bullish: 1", text)
        self.assertIn("Attempted FU bearish: 1", text)
        self.assertIn("BETA HCS bars: 8", text)
        self.assertIn("Source-style HCS candidate bars: 14", text)
        self.assertIn("Κοινά bars: 1", text)
        self.assertIn("strong_attempted: 1", text)
        self.assertIn("HCS με ίδια κατεύθυνση: 1", text)
        self.assertIn("HCS με αντίθετη κατεύθυνση: 1", text)
        self.assertIn("FU Negation candidates: 1", text)
        self.assertIn("HCS + Negation candidates: 1", text)
        self.assertIn("Strong FU bearish + HCS bearish [candidate]", text)
        self.assertIn("δεν χρειάζεται να ξανα-ανακαλύπτει τα A/F markers", text)
        self.assertIn("Δεν αποτελεί backtest απόδοσης", text)

    def test_negative_compound_limit_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_greek_human_review({}, compound_limit=-1)


if __name__ == "__main__":
    unittest.main()
