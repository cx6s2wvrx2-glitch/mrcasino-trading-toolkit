from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import UTC, datetime

from xauusd_v2.data_snapshot import DataSnapshotManifest
from xauusd_v2.source_chart_alignment import (
    SourceChartAlignmentRequest,
    SourceChartAlignmentState,
    align_source_chart_to_snapshot,
)


class SourceChartAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = DataSnapshotManifest(
            snapshot_id="sha256:abc",
            sha256="abc",
            canonical_symbol="XAUUSD",
            timeframe_seconds=300,
            source_name="IC Markets",
            source_symbol="XAUUSD",
            source_file_name="xauusd.csv",
            bar_count=100,
            first_timestamp=datetime(2023, 11, 1, 8, 0, tzinfo=UTC),
            last_timestamp=datetime(2023, 11, 1, 16, 15, tzinfo=UTC),
            coverage_end=datetime(2023, 11, 1, 16, 20, tzinfo=UTC),
            closed_only=True,
        )

    def request(self, **overrides: object) -> SourceChartAlignmentRequest:
        values: dict[str, object] = {
            "source_id": "primary-source-id",
            "source_locator": "top down analysis (1).zip#sequence:2023-11-01",
            "broker_name": "IC Markets",
            "source_symbol": "XAUUSD",
            "timeframe_seconds": 300,
            "window_start": datetime(2023, 11, 1, 9, 0, tzinfo=UTC),
            "window_end": datetime(2023, 11, 1, 10, 0, tzinfo=UTC),
        }
        values.update(overrides)
        return SourceChartAlignmentRequest(**values)

    def test_exact_broker_symbol_timeframe_window_and_grid_align(self) -> None:
        result = align_source_chart_to_snapshot(request=self.request(), snapshot=self.snapshot)
        self.assertEqual(result.state, SourceChartAlignmentState.ALIGNED_CANDIDATE)
        self.assertTrue(result.aligned)
        self.assertEqual(result.snapshot_id, "sha256:abc")

    def test_missing_chart_time_is_blocked_not_inferred(self) -> None:
        result = align_source_chart_to_snapshot(
            request=self.request(window_start=None, window_end=None), snapshot=self.snapshot
        )
        self.assertEqual(result.state, SourceChartAlignmentState.MISSING_SOURCE_TIME)
        self.assertFalse(result.aligned)

    def test_missing_broker_identity_is_blocked(self) -> None:
        result = align_source_chart_to_snapshot(
            request=self.request(broker_name=None), snapshot=self.snapshot
        )
        self.assertEqual(result.state, SourceChartAlignmentState.MISSING_BROKER_IDENTITY)

    def test_broker_mismatch_is_blocked(self) -> None:
        result = align_source_chart_to_snapshot(
            request=self.request(broker_name="Pepperstone"), snapshot=self.snapshot
        )
        self.assertEqual(result.state, SourceChartAlignmentState.BROKER_MISMATCH)

    def test_broker_symbol_mismatch_is_blocked(self) -> None:
        result = align_source_chart_to_snapshot(
            request=self.request(source_symbol="GOLD"), snapshot=self.snapshot
        )
        self.assertEqual(result.state, SourceChartAlignmentState.SYMBOL_MISMATCH)

    def test_timeframe_mismatch_is_blocked(self) -> None:
        result = align_source_chart_to_snapshot(
            request=self.request(timeframe_seconds=60), snapshot=self.snapshot
        )
        self.assertEqual(result.state, SourceChartAlignmentState.TIMEFRAME_MISMATCH)

    def test_window_outside_snapshot_is_blocked(self) -> None:
        result = align_source_chart_to_snapshot(
            request=self.request(window_start=datetime(2023, 11, 1, 7, 55, tzinfo=UTC)),
            snapshot=self.snapshot,
        )
        self.assertEqual(result.state, SourceChartAlignmentState.WINDOW_OUTSIDE_SNAPSHOT)

    def test_off_bar_grid_timestamp_is_blocked(self) -> None:
        result = align_source_chart_to_snapshot(
            request=self.request(window_start=datetime(2023, 11, 1, 9, 1, tzinfo=UTC)),
            snapshot=self.snapshot,
        )
        self.assertEqual(result.state, SourceChartAlignmentState.OFF_BAR_GRID)

    def test_provisional_snapshot_cannot_align_for_historical_replay(self) -> None:
        provisional = replace(self.snapshot, closed_only=False)
        result = align_source_chart_to_snapshot(request=self.request(), snapshot=provisional)
        self.assertEqual(result.state, SourceChartAlignmentState.SNAPSHOT_NOT_CLOSED)

    def test_naive_source_timestamp_is_not_certified(self) -> None:
        result = align_source_chart_to_snapshot(
            request=self.request(window_start=datetime(2023, 11, 1, 9, 0)), snapshot=self.snapshot
        )
        self.assertEqual(result.state, SourceChartAlignmentState.NOT_CERTIFIED)

    def test_non_xauusd_request_is_not_certified(self) -> None:
        result = align_source_chart_to_snapshot(
            request=self.request(canonical_symbol="EURUSD"), snapshot=self.snapshot
        )
        self.assertEqual(result.state, SourceChartAlignmentState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
