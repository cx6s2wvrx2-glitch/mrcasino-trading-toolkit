from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.source_primitive_bridge import SourcePrimitiveBridgeError, build_source_primitive_bridge


class SourcePrimitiveBridgeTests(unittest.TestCase):
    def write(self, payload: dict[str, object]) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(payload, handle)
        handle.close()
        path = Path(handle.name)
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        return path

    def source_report(self) -> dict[str, object]:
        return {
            "schema_version": "source_fidelity_replay_report_v1",
            "status": "SOURCE_FIDELITY_REPLAY_PASS",
            "episode_id": "march-buy",
            "source_locator": "primary:march-buy",
            "snapshot_id": "sha256:" + "a" * 64,
            "normalized_sha256": "a" * 64,
            "broker_name": "Exclusive Markets Ltd.",
            "broker_symbol": "XAUUSD!",
            "timeframe_seconds": 60,
            "window_start": "2023-03-30T15:50:00+00:00",
            "window_end": "2023-03-30T17:00:00+00:00",
            "anchor_count": 2,
            "matched_anchor_count": 2,
            "all_anchors_matched": True,
            "anchors": [
                {
                    "anchor_id": "A-1973",
                    "level": "1973",
                    "predicate": "range_touch",
                    "source_ref": "primary:strongest-1m-fu-1973",
                    "matched": True,
                    "matched_at": "2023-03-30T15:53:00+00:00",
                    "open": "1972.8",
                    "high": "1973.6",
                    "low": "1972.7",
                    "close": "1973.47",
                    "reason": "fixture"
                },
                {
                    "anchor_id": "A-1975",
                    "level": "1975",
                    "predicate": "range_touch",
                    "source_ref": "primary:hcs-1975",
                    "matched": True,
                    "matched_at": "2023-03-30T15:58:00+00:00",
                    "open": "1974.6",
                    "high": "1975.19",
                    "low": "1974.4",
                    "close": "1975.0",
                    "reason": "fixture"
                }
            ],
            "expansion_probe": None,
            "expansion_probe_matched": True,
            "expansion_finishes_before_first_anchor": None,
            "semantic_stage_certification": False,
            "performance_claim_allowed": False,
            "promotion_allowed": False,
            "strategy_truth_changed": False,
            "live_execution_authorized": False,
            "reference_feed_alignment_complete": False,
            "reference_feed_required": "FOREXCOM:XAUUSD"
        }

    def primitive_report(self) -> dict[str, object]:
        return {
            "schema_version": "primitive_replay_scan_report_v1",
            "status": "PRIMITIVE_REPLAY_SCAN_COMPLETE_NOT_CERTIFIED",
            "snapshot_id": "sha256:" + "a" * 64,
            "normalized_sha256": "a" * 64,
            "broker_name": "Exclusive Markets Ltd.",
            "broker_symbol": "XAUUSD!",
            "timeframe_seconds": 60,
            "scan_start": "2023-03-30T15:50:00+00:00",
            "scan_end": "2023-03-30T16:10:00+00:00",
            "bar_count": 20,
            "basic_fu_candidate_count": 2,
            "ambiguous_basic_fu_bar_count": 0,
            "adjacency_gap_pairs_skipped": 0,
            "wick_interaction_count_total": 1,
            "source_style_hcs_candidate_count": 1,
            "candidate_only_output": False,
            "fu_candidates": [
                {
                    "event_id": "basic-fu:1973",
                    "bar_open": "2023-03-30T15:53:00+00:00",
                    "available_at": "2023-03-30T15:54:00+00:00",
                    "direction": "bullish",
                    "certified_fu": False
                },
                {
                    "event_id": "basic-fu:1975",
                    "bar_open": "2023-03-30T15:58:00+00:00",
                    "available_at": "2023-03-30T15:59:00+00:00",
                    "direction": "bullish",
                    "certified_fu": False
                }
            ],
            "wick_interactions": [
                {
                    "first_event_id": "basic-fu:1973",
                    "interaction_bar_open": "2023-03-30T15:58:00+00:00",
                    "interaction_available_at": "2023-03-30T15:59:00+00:00",
                    "hcs_candidate_form": "continuation",
                    "source_style_hcs_candidate": True,
                    "certified_hcs": False
                }
            ],
            "certified_fu_count": 0,
            "certified_hcs_count": 0,
            "blockers_preserved": ["B-01", "B-02", "B-03", "B-05"],
            "strategy_truth_changed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False
        }

    def test_exact_bar_correspondence_is_measured_without_certification(self) -> None:
        result = build_source_primitive_bridge(self.write(self.source_report()), self.write(self.primitive_report()))
        self.assertEqual(result.matched_anchor_count, 2)
        self.assertEqual(result.covered_matched_anchor_count, 2)
        self.assertEqual(result.exact_bar_basic_fu_correspondence_count, 2)
        self.assertEqual(result.exact_bar_hcs_candidate_correspondence_count, 1)
        first, second = result.anchors
        self.assertTrue(first.basic_fu_candidate_at_exact_bar)
        self.assertFalse(first.source_style_hcs_candidate_at_exact_bar)
        self.assertTrue(second.basic_fu_candidate_at_exact_bar)
        self.assertTrue(second.source_style_hcs_candidate_at_exact_bar)
        self.assertEqual(second.hcs_candidate_forms, ("continuation",))
        self.assertFalse(result.semantic_stage_certification)
        self.assertFalse(result.promotion_allowed)

    def test_anchor_outside_primitive_window_is_unknown_not_false(self) -> None:
        primitive = self.primitive_report()
        primitive["scan_end"] = "2023-03-30T15:56:00+00:00"
        result = build_source_primitive_bridge(self.write(self.source_report()), self.write(primitive))
        second = result.anchors[1]
        self.assertFalse(second.primitive_window_covers_anchor)
        self.assertIsNone(second.basic_fu_candidate_at_exact_bar)
        self.assertIsNone(second.source_style_hcs_candidate_at_exact_bar)

    def test_covered_anchor_without_candidate_is_explicit_false(self) -> None:
        primitive = self.primitive_report()
        primitive["fu_candidates"] = [primitive["fu_candidates"][0]]
        primitive["wick_interactions"] = []
        result = build_source_primitive_bridge(self.write(self.source_report()), self.write(primitive))
        second = result.anchors[1]
        self.assertTrue(second.primitive_window_covers_anchor)
        self.assertFalse(second.basic_fu_candidate_at_exact_bar)
        self.assertFalse(second.source_style_hcs_candidate_at_exact_bar)

    def test_snapshot_mismatch_fails_closed(self) -> None:
        primitive = self.primitive_report()
        primitive["snapshot_id"] = "sha256:" + "b" * 64
        with self.assertRaisesRegex(SourcePrimitiveBridgeError, "snapshot_id"):
            build_source_primitive_bridge(self.write(self.source_report()), self.write(primitive))

    def test_source_promotion_claim_fails_closed(self) -> None:
        source = self.source_report()
        source["promotion_allowed"] = True
        with self.assertRaisesRegex(SourcePrimitiveBridgeError, "promotion_allowed"):
            build_source_primitive_bridge(self.write(source), self.write(self.primitive_report()))

    def test_primitive_certification_claim_fails_closed(self) -> None:
        primitive = self.primitive_report()
        primitive["certified_fu_count"] = 1
        with self.assertRaisesRegex(SourcePrimitiveBridgeError, "certified FU"):
            build_source_primitive_bridge(self.write(self.source_report()), self.write(primitive))

    def test_unmatched_source_anchor_has_no_primitive_verdict(self) -> None:
        source = self.source_report()
        anchor = source["anchors"][1]
        anchor["matched"] = False
        anchor["matched_at"] = None
        result = build_source_primitive_bridge(self.write(source), self.write(self.primitive_report()))
        second = result.anchors[1]
        self.assertFalse(second.broker_anchor_matched)
        self.assertIsNone(second.primitive_window_covers_anchor)
        self.assertIsNone(second.basic_fu_candidate_at_exact_bar)


if __name__ == "__main__":
    unittest.main()
