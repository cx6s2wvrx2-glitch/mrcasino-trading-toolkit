from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.source_fidelity_replay import (
    AnchorPredicate,
    SourceFidelityReplayError,
    evaluate_source_fidelity_fixture,
    load_source_fidelity_fixture,
)


UTC = timezone.utc


class SourceFidelityReplayTests(unittest.TestCase):
    def write_fixture(self, payload: dict[str, object]) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(payload, handle)
        handle.close()
        path = Path(handle.name)
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        return path

    def fixture_payload(self) -> dict[str, object]:
        return {
            "schema_version": "source_fidelity_fixture_v1",
            "episode_id": "episode-1",
            "source_locator": "primary:episode-1",
            "timeframe_seconds": 60,
            "window_start": "2023-03-30T12:00:00Z",
            "window_end": "2023-03-30T13:00:00Z",
            "anchors": [
                {
                    "anchor_id": "a1",
                    "level": "100.00",
                    "predicate": "low_equals",
                    "source_ref": "primary:a1",
                },
                {
                    "anchor_id": "a2",
                    "level": "102.00",
                    "predicate": "range_touch",
                    "source_ref": "primary:a2",
                },
                {
                    "anchor_id": "a3",
                    "level": "104.00",
                    "predicate": "close_at_or_above",
                    "source_ref": "primary:a3",
                },
            ],
            "expansion_probe": {"window_bars": 3, "source_ref": "primary:expansion"},
            "promotion_allowed": False,
        }

    def bar(self, minute: int, open_: float, high: float, low: float, close: float) -> MarketBar:
        return MarketBar(
            timestamp=datetime(2023, 3, 30, 12, minute, tzinfo=UTC),
            open=open_,
            high=high,
            low=low,
            close=close,
            is_closed=True,
            source_name="Exclusive Markets Ltd.",
            source_symbol="XAUUSD!",
        )

    def bars(self) -> tuple[MarketBar, ...]:
        return (
            self.bar(0, 101.0, 101.2, 100.0, 100.8),
            self.bar(1, 100.8, 101.8, 100.7, 101.7),
            self.bar(2, 101.7, 102.2, 101.5, 102.1),
            self.bar(3, 102.1, 105.0, 101.9, 104.5),
            self.bar(4, 104.5, 104.8, 104.0, 104.2),
        )

    def test_fixture_loads_strict_schema(self) -> None:
        fixture = load_source_fidelity_fixture(self.write_fixture(self.fixture_payload()))
        self.assertEqual(fixture.episode_id, "episode-1")
        self.assertEqual(fixture.timeframe_seconds, 60)
        self.assertEqual(fixture.anchors[0].predicate, AnchorPredicate.LOW_EQUALS)
        self.assertFalse(fixture.promotion_allowed)

    def test_ordered_distinct_anchor_path_and_expansion_are_measured(self) -> None:
        fixture = load_source_fidelity_fixture(self.write_fixture(self.fixture_payload()))
        result = evaluate_source_fidelity_fixture(
            bars=self.bars(),
            fixture=fixture,
            timeframe_seconds=60,
        )
        self.assertTrue(result.all_anchors_matched)
        self.assertTrue(result.expansion_probe_matched)
        self.assertEqual(
            [item.matched_at.minute for item in result.anchor_matches if item.matched_at is not None],
            [0, 2, 3],
        )
        self.assertIsNotNone(result.expansion_match)
        assert result.expansion_match is not None
        self.assertEqual(str(result.expansion_match.range), "4.3")

    def test_same_bar_cannot_satisfy_two_ordered_anchors(self) -> None:
        payload = self.fixture_payload()
        payload["anchors"] = [
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
        ]
        payload["expansion_probe"] = None
        fixture = load_source_fidelity_fixture(self.write_fixture(payload))
        result = evaluate_source_fidelity_fixture(
            bars=(self.bar(0, 101.0, 101.2, 100.0, 100.8),),
            fixture=fixture,
            timeframe_seconds=60,
        )
        self.assertFalse(result.all_anchors_matched)
        self.assertTrue(result.anchor_matches[0].matched)
        self.assertFalse(result.anchor_matches[1].matched)

    def test_missing_anchor_blocks_later_anchor_evaluation(self) -> None:
        payload = self.fixture_payload()
        anchors = payload["anchors"]
        assert isinstance(anchors, list)
        second = anchors[1]
        assert isinstance(second, dict)
        second["level"] = "999.00"
        fixture = load_source_fidelity_fixture(self.write_fixture(payload))
        result = evaluate_source_fidelity_fixture(
            bars=self.bars(),
            fixture=fixture,
            timeframe_seconds=60,
        )
        self.assertFalse(result.all_anchors_matched)
        self.assertFalse(result.anchor_matches[1].matched)
        self.assertIn("no distinct closed bar", result.anchor_matches[1].reason)
        self.assertFalse(result.anchor_matches[2].matched)
        self.assertIn("prior ordered anchor", result.anchor_matches[2].reason)

    def test_expansion_probe_requires_contiguous_bars(self) -> None:
        payload = self.fixture_payload()
        payload["anchors"] = [
            {
                "anchor_id": "a1",
                "level": "100.00",
                "predicate": "low_equals",
                "source_ref": "primary:a1",
            }
        ]
        payload["expansion_probe"] = {"window_bars": 3, "source_ref": "primary:expansion"}
        fixture = load_source_fidelity_fixture(self.write_fixture(payload))
        bars = (
            self.bar(0, 101.0, 101.2, 100.0, 100.8),
            self.bar(2, 100.8, 105.0, 100.7, 104.0),
            self.bar(3, 104.0, 105.0, 103.5, 104.5),
        )
        result = evaluate_source_fidelity_fixture(bars=bars, fixture=fixture, timeframe_seconds=60)
        self.assertFalse(result.expansion_probe_matched)
        assert result.expansion_match is not None
        self.assertFalse(result.expansion_match.matched)

    def test_timeframe_mismatch_is_rejected(self) -> None:
        fixture = load_source_fidelity_fixture(self.write_fixture(self.fixture_payload()))
        with self.assertRaisesRegex(SourceFidelityReplayError, "timeframe"):
            evaluate_source_fidelity_fixture(bars=self.bars(), fixture=fixture, timeframe_seconds=300)

    def test_duplicate_anchor_id_is_rejected(self) -> None:
        payload = self.fixture_payload()
        anchors = payload["anchors"]
        assert isinstance(anchors, list)
        second = anchors[1]
        assert isinstance(second, dict)
        second["anchor_id"] = "a1"
        with self.assertRaisesRegex(SourceFidelityReplayError, "duplicate anchor_id"):
            load_source_fidelity_fixture(self.write_fixture(payload))

    def test_unknown_predicate_is_rejected(self) -> None:
        payload = self.fixture_payload()
        anchors = payload["anchors"]
        assert isinstance(anchors, list)
        first = anchors[0]
        assert isinstance(first, dict)
        first["predicate"] = "fuzzy_near_enough"
        with self.assertRaisesRegex(SourceFidelityReplayError, "not supported"):
            load_source_fidelity_fixture(self.write_fixture(payload))

    def test_promotion_true_is_rejected(self) -> None:
        payload = self.fixture_payload()
        payload["promotion_allowed"] = True
        with self.assertRaisesRegex(SourceFidelityReplayError, "promotion_allowed=false"):
            load_source_fidelity_fixture(self.write_fixture(payload))

    def test_extra_fixture_field_is_rejected(self) -> None:
        payload = self.fixture_payload()
        payload["winning_trade"] = True
        with self.assertRaisesRegex(SourceFidelityReplayError, "schema mismatch"):
            load_source_fidelity_fixture(self.write_fixture(payload))


if __name__ == "__main__":
    unittest.main()
