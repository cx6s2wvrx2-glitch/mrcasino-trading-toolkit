from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.march_replay_bundle import (
    MarchReplayBundleError,
    _EPISODES,
    _canonical_json_bytes,
    _primitive_report,
    _source_report,
    _write_immutable_json,
)
from xauusd_v2.primitive_replay_scan import scan_primitive_replay_window
from xauusd_v2.r143_source_evidence import load_r143_source_evidence_map
from xauusd_v2.source_fidelity_replay import evaluate_source_fidelity_fixture, load_source_fidelity_fixture
from xauusd_v2.source_primitive_bridge import SourcePrimitiveBridgeError, build_source_primitive_bridge


UTC = timezone.utc


class MarchReplayBundleTests(unittest.TestCase):
    @property
    def examples_root(self) -> Path:
        return Path(__file__).resolve().parents[1] / "06_examples"

    def verified_stub(self) -> SimpleNamespace:
        return SimpleNamespace(
            normalized_sha256="b" * 64,
            snapshot=SimpleNamespace(
                snapshot_id="sha256:" + "b" * 64,
                source_name="Exclusive Markets Ltd.",
                source_symbol="XAUUSD!",
            ),
        )

    def bar(
        self,
        minute: int,
        open_: float,
        high: float,
        low: float,
        close: float,
        *,
        is_closed: bool = True,
    ) -> MarketBar:
        return MarketBar(
            timestamp=datetime(2023, 3, 30, 12, minute, tzinfo=UTC),
            open=open_,
            high=high,
            low=low,
            close=close,
            is_closed=is_closed,
            source_name="Exclusive Markets Ltd.",
            source_symbol="XAUUSD!",
        )

    def write_json(self, directory: str, name: str, payload: dict[str, object]) -> Path:
        path = Path(directory) / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_bundle_episode_registry_is_exactly_march_buy_and_sell(self) -> None:
        self.assertEqual(
            _EPISODES,
            (
                (
                    "2023-03-30-buy",
                    "SOURCE_FIDELITY_2023_03_30_BUY.json",
                    "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
                ),
                (
                    "2023-03-31-sell",
                    "SOURCE_FIDELITY_2023_03_31_SELL.json",
                    "R143_SOURCE_EVIDENCE_2023_03_31_SELL.json",
                ),
            ),
        )

    def test_governed_march_fixtures_and_evidence_maps_load(self) -> None:
        for _, fixture_name, evidence_name in _EPISODES:
            fixture = load_source_fidelity_fixture(self.examples_root / fixture_name)
            evidence = load_r143_source_evidence_map(self.examples_root / evidence_name)
            self.assertEqual(fixture.timeframe_seconds, 60)
            self.assertLess(fixture.window_start, fixture.window_end)
            self.assertFalse(fixture.promotion_allowed)
            self.assertFalse(evidence.promotion_allowed)
            self.assertFalse(evidence.performance_claim_allowed)
            self.assertFalse(evidence.live_execution_authorized)
            self.assertTrue(all(not stage.machine_stage_certified for stage in evidence.stages))

    def test_canonical_json_is_order_independent(self) -> None:
        left = _canonical_json_bytes({"b": 2, "a": 1})
        right = _canonical_json_bytes({"a": 1, "b": 2})
        self.assertEqual(left, right)
        self.assertEqual(json.loads(left), {"a": 1, "b": 2})

    def test_immutable_writer_is_idempotent_and_refuses_differing_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            first = _write_immutable_json(path, {"status": "A", "promotion_allowed": False})
            second = _write_immutable_json(path, {"promotion_allowed": False, "status": "A"})
            self.assertEqual(first, second)
            with self.assertRaisesRegex(MarchReplayBundleError, "refusing to overwrite"):
                _write_immutable_json(path, {"status": "B", "promotion_allowed": False})

    def test_primitive_bundle_report_is_candidate_only_and_never_promotes(self) -> None:
        result = scan_primitive_replay_window(
            bars=(
                self.bar(0, 100.0, 100.5, 99.5, 100.2),
                self.bar(1, 100.2, 100.4, 99.4, 100.3),
            ),
            timeframe_seconds=60,
            scan_start=datetime(2023, 3, 30, 12, 0, tzinfo=UTC),
            scan_end=datetime(2023, 3, 30, 12, 2, tzinfo=UTC),
        )
        report = _primitive_report(self.verified_stub(), result)
        self.assertTrue(report["candidate_only_output"])
        self.assertEqual(report["certified_fu_count"], 0)
        self.assertEqual(report["certified_hcs_count"], 0)
        self.assertFalse(report["semantic_stage_certification"])
        self.assertFalse(report["performance_claim_allowed"])
        self.assertFalse(report["promotion_allowed"])
        self.assertFalse(report["strategy_truth_changed"])
        self.assertFalse(report["live_execution_authorized"])

    def test_data_gap_is_preserved_in_bundle_report_and_never_classified_as_adjacent(self) -> None:
        result = scan_primitive_replay_window(
            bars=(
                self.bar(0, 100.0, 101.0, 99.0, 100.5),
                self.bar(2, 100.5, 101.5, 98.5, 99.5),
            ),
            timeframe_seconds=60,
            scan_start=datetime(2023, 3, 30, 12, 0, tzinfo=UTC),
            scan_end=datetime(2023, 3, 30, 12, 3, tzinfo=UTC),
        )
        report = _primitive_report(self.verified_stub(), result)
        self.assertEqual(report["adjacency_gap_pairs_skipped"], 1)
        self.assertEqual(report["basic_fu_candidate_count"], 0)
        self.assertEqual(report["certified_fu_count"], 0)

    def test_out_of_window_future_bar_cannot_change_bundle_primitive_report(self) -> None:
        base = (
            self.bar(0, 100.0, 100.5, 99.5, 100.2),
            self.bar(1, 100.2, 100.4, 99.4, 100.3),
        )
        future = self.bar(2, 100.3, 110.0, 90.0, 109.0)
        scan_start = datetime(2023, 3, 30, 12, 0, tzinfo=UTC)
        scan_end = datetime(2023, 3, 30, 12, 2, tzinfo=UTC)
        without_future = scan_primitive_replay_window(
            bars=base,
            timeframe_seconds=60,
            scan_start=scan_start,
            scan_end=scan_end,
        )
        with_future = scan_primitive_replay_window(
            bars=base + (future,),
            timeframe_seconds=60,
            scan_start=scan_start,
            scan_end=scan_end,
        )
        left = _canonical_json_bytes(_primitive_report(self.verified_stub(), without_future))
        right = _canonical_json_bytes(_primitive_report(self.verified_stub(), with_future))
        self.assertEqual(left, right)

    def test_ordered_anchor_safety_survives_bundle_report_composition(self) -> None:
        payload = {
            "schema_version": "source_fidelity_fixture_v1",
            "episode_id": "ordered-anchor-test",
            "source_locator": "primary:ordered-anchor-test",
            "timeframe_seconds": 60,
            "window_start": "2023-03-30T12:00:00Z",
            "window_end": "2023-03-30T12:01:00Z",
            "anchors": [
                {
                    "anchor_id": "a1",
                    "level": "100.00",
                    "predicate": "low_equals",
                    "source_ref": "primary:a1",
                },
                {
                    "anchor_id": "a2",
                    "level": "101.00",
                    "predicate": "range_touch",
                    "source_ref": "primary:a2",
                },
            ],
            "expansion_probe": None,
            "promotion_allowed": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            fixture = load_source_fidelity_fixture(self.write_json(directory, "fixture.json", payload))
            result = evaluate_source_fidelity_fixture(
                bars=(self.bar(0, 101.0, 101.2, 100.0, 100.8),),
                fixture=fixture,
                timeframe_seconds=60,
            )
        report = _source_report(self.verified_stub(), result)
        self.assertEqual(report["status"], "SOURCE_FIDELITY_REPLAY_INCOMPLETE")
        self.assertEqual(report["matched_anchor_count"], 1)
        self.assertTrue(report["anchors"][0]["matched"])
        self.assertFalse(report["anchors"][1]["matched"])
        self.assertFalse(report["semantic_stage_certification"])
        self.assertFalse(report["performance_claim_allowed"])
        self.assertFalse(report["promotion_allowed"])
        self.assertFalse(report["live_execution_authorized"])

    def test_source_primitive_identity_mismatch_fails_closed_inside_bundle_bridge(self) -> None:
        source = {
            "schema_version": "source_fidelity_replay_report_v1",
            "status": "SOURCE_FIDELITY_REPLAY_PASS",
            "episode_id": "episode",
            "source_locator": "primary:episode",
            "snapshot_id": "sha256:" + "a" * 64,
            "normalized_sha256": "a" * 64,
            "broker_name": "Exclusive Markets Ltd.",
            "broker_symbol": "XAUUSD!",
            "timeframe_seconds": 60,
            "window_start": "2023-03-30T12:00:00Z",
            "window_end": "2023-03-30T12:10:00Z",
            "anchors": [],
            "semantic_stage_certification": False,
            "performance_claim_allowed": False,
            "promotion_allowed": False,
            "strategy_truth_changed": False,
            "live_execution_authorized": False,
            "reference_feed_alignment_complete": False,
            "reference_feed_required": "FOREXCOM:XAUUSD",
        }
        primitive = {
            "schema_version": "primitive_replay_scan_report_v1",
            "status": "PRIMITIVE_REPLAY_SCAN_COMPLETE_NOT_CERTIFIED",
            "snapshot_id": "sha256:" + "a" * 64,
            "normalized_sha256": "c" * 64,
            "broker_name": "Exclusive Markets Ltd.",
            "broker_symbol": "XAUUSD!",
            "timeframe_seconds": 60,
            "scan_start": "2023-03-30T12:00:00Z",
            "scan_end": "2023-03-30T12:10:00Z",
            "fu_candidates": [],
            "wick_interactions": [],
            "certified_fu_count": 0,
            "certified_hcs_count": 0,
            "strategy_truth_changed": False,
            "promotion_allowed": False,
            "live_execution_authorized": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            source_path = self.write_json(directory, "source.json", source)
            primitive_path = self.write_json(directory, "primitive.json", primitive)
            with self.assertRaisesRegex(SourcePrimitiveBridgeError, "identity mismatch: normalized_sha256"):
                build_source_primitive_bridge(source_path, primitive_path)


if __name__ == "__main__":
    unittest.main()
