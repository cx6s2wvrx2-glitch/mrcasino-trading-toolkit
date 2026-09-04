from __future__ import annotations

import unittest

from xauusd_v2.casino_history_report_cli import build_summary_text


class CasinoHistoryReportCLITests(unittest.TestCase):
    def test_summary_surfaces_beta_vs_source_proxy_and_marker_rows(self) -> None:
        report = {
            "status": "SUPPLIED_INDICATOR_HISTORY_REPLAY_COMPLETE_NOT_CERTIFIED",
            "snapshot_id": "sha256:test",
            "normalized_sha256": "test",
            "broker_name": "broker",
            "broker_symbol": "XAUUSD!",
            "broker_timezone": "Europe/Athens",
            "timeframe": "M15",
            "window_start_utc": "2023-03-30T00:00:00Z",
            "window_end_utc": "2023-04-01T00:00:00Z",
            "replay_bar_count_before_window_clip": 10,
            "window_evaluated_bar_count": 8,
            "window_event_frame_count": 3,
            "window_event_count": 3,
            "source_hcs_marker_proxy_candidate_count": 1,
            "window_gap_affected_derived_bar_count": 0,
            "events_on_gap_affected_derived_bars": 0,
            "reference_feed_alignment_complete": False,
            "strategy_semantics_certified": False,
            "event_counts_by_kind": {"hcs": 1, "strong_fu": 2},
            "event_counts_by_direction": {"bullish": 2, "bearish": 1},
            "source_hcs_marker_proxy_counts_by_form": {"strong_attempted": 1},
            "hcs_implementation_vs_source_marker_proxy": {
                "beta_hcs_event_bar_count": 1,
                "source_marker_proxy_bar_count": 1,
                "overlap_bar_count": 0,
                "beta_only_bar_count": 1,
                "source_proxy_only_bar_count": 1,
            },
            "events": [
                {
                    "bar_time_utc": "2023-03-30T12:00:00Z",
                    "kind": "hcs",
                    "direction": "bullish",
                    "marker_text": "HCS X1",
                    "hcs_count": 1,
                    "derived_bar_gap_affected": False,
                },
                {
                    "bar_time_utc": "2023-03-30T12:15:00Z",
                    "kind": "strong_fu",
                    "direction": "bullish",
                    "visual_cue": "bright_green",
                    "derived_bar_gap_affected": False,
                },
            ],
            "source_hcs_marker_proxy_candidates": [
                {
                    "first_bar_time_utc": "2023-03-30T12:15:00Z",
                    "second_bar_time_utc": "2023-03-30T12:30:00Z",
                    "first_direction": "bullish",
                    "second_direction": "bearish",
                    "form": "strong_attempted",
                    "source_strength_label_proxy": "L2_PROXY",
                    "same_direction": False,
                    "latest_prior_marker_node_count": 1,
                    "derived_bar_gap_affected": False,
                }
            ],
        }

        text = build_summary_text(report, marker_limit=1)
        self.assertIn("HCS IMPLEMENTATION vs SOURCE-MARKER PROXY", text)
        self.assertIn("BETA HCS EVENTS: 1", text)
        self.assertIn("SOURCE-STYLE HCS MARKER PROXY CANDIDATES: 1", text)
        self.assertIn("L2_PROXY", text)
        self.assertIn("FIRST 1 STRONG/ATT EVENTS", text)
        self.assertIn("bright_green", text)

    def test_negative_marker_limit_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_summary_text({}, marker_limit=-1)


if __name__ == "__main__":
    unittest.main()
