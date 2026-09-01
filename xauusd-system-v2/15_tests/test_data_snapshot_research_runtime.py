from __future__ import annotations

import unittest
from datetime import datetime, timezone

from xauusd_v2.agents.quant_agent import QuantitativeResearchAgent, ResearchExperimentSpec, ResearchWindow
from xauusd_v2.data_snapshot import DataSnapshotError, load_xauusd_csv_snapshot_bytes
from xauusd_v2.research_runtime import ResearchRuntimeStatus, prepare_research_runtime


UTC = timezone.utc


def _csv_bytes() -> bytes:
    return (
        "timestamp,open,high,low,close\n"
        "2024-01-01T00:00:00Z,2060.0,2061.0,2059.5,2060.5\n"
        "2024-01-01T00:05:00Z,2060.5,2062.0,2060.0,2061.5\n"
        "2024-01-01T00:10:00Z,2061.5,2063.0,2061.0,2062.5\n"
    ).encode("utf-8")


def _spec(snapshot_id: str) -> ResearchExperimentSpec:
    return ResearchExperimentSpec(
        experiment_id="EXP-001",
        strategy_version="candidate-v0.1",
        strategy_commit_sha="abc123",
        data_snapshot_ref=snapshot_id,
        parameter_set_ref="params:none",
        cost_model_ref="costs:v1",
        symbol="XAUUSD",
        timeframe_seconds=300,
        train=ResearchWindow("train", datetime(2024, 1, 1, 0, 0, tzinfo=UTC), datetime(2024, 1, 1, 0, 5, tzinfo=UTC)),
        validation=ResearchWindow("validation", datetime(2024, 1, 1, 0, 5, tzinfo=UTC), datetime(2024, 1, 1, 0, 10, tzinfo=UTC)),
        test=ResearchWindow("test", datetime(2024, 1, 1, 0, 10, tzinfo=UTC), datetime(2024, 1, 1, 0, 15, tzinfo=UTC)),
    )


class DataSnapshotResearchRuntimeTests(unittest.TestCase):
    def _closed_snapshot(self):
        return load_xauusd_csv_snapshot_bytes(
            _csv_bytes(),
            source_name="fixture-broker",
            source_symbol="XAUUSD.a",
            timeframe_seconds=300,
            evaluation_time=datetime(2024, 1, 1, 0, 20, tzinfo=UTC),
            source_file_name="fixture.csv",
        )

    def test_snapshot_is_sha256_content_addressed_and_closed(self) -> None:
        bars, manifest, report = self._closed_snapshot()
        self.assertEqual(len(bars), 3)
        self.assertTrue(manifest.snapshot_id.startswith("sha256:"))
        self.assertEqual(manifest.snapshot_id, f"sha256:{manifest.sha256}")
        self.assertTrue(manifest.closed_only)
        self.assertEqual(report.provisional_bars, 0)
        self.assertEqual(manifest.source_symbol, "XAUUSD.a")

    def test_same_bytes_produce_same_snapshot_id(self) -> None:
        _, first, _ = self._closed_snapshot()
        _, second, _ = self._closed_snapshot()
        self.assertEqual(first.snapshot_id, second.snapshot_id)

    def test_missing_csv_column_is_rejected(self) -> None:
        bad = b"timestamp,open,high,low\n2024-01-01T00:00:00Z,1,2,0\n"
        with self.assertRaises(DataSnapshotError):
            load_xauusd_csv_snapshot_bytes(
                bad,
                source_name="fixture",
                source_symbol="XAUUSD",
                timeframe_seconds=300,
                evaluation_time=datetime(2024, 1, 1, 1, 0, tzinfo=UTC),
            )

    def test_provisional_snapshot_is_not_performance_research_ready(self) -> None:
        _, manifest, report = load_xauusd_csv_snapshot_bytes(
            _csv_bytes(),
            source_name="fixture",
            source_symbol="XAUUSD",
            timeframe_seconds=300,
            evaluation_time=datetime(2024, 1, 1, 0, 12, tzinfo=UTC),
        )
        runtime, _ = prepare_research_runtime(
            spec=_spec(manifest.snapshot_id),
            snapshot=manifest,
            data_report=report,
            strategy_certification_ready=True,
        )
        self.assertEqual(runtime.status, ResearchRuntimeStatus.BLOCKED)
        self.assertTrue(any("closed-only" in blocker for blocker in runtime.blockers))

    def test_clean_data_without_strategy_certification_stops_at_data_ready(self) -> None:
        _, manifest, report = self._closed_snapshot()
        runtime, design = prepare_research_runtime(
            spec=_spec(manifest.snapshot_id),
            snapshot=manifest,
            data_report=report,
            strategy_certification_ready=False,
            quant_agent=QuantitativeResearchAgent(),
        )
        self.assertTrue(design.ready_for_research)
        self.assertEqual(runtime.status, ResearchRuntimeStatus.DATA_READY)
        self.assertTrue(runtime.data_ready)
        self.assertFalse(runtime.strategy_certification_ready)

    def test_certified_strategy_can_reach_backtest_ready(self) -> None:
        _, manifest, report = self._closed_snapshot()
        runtime, _ = prepare_research_runtime(
            spec=_spec(manifest.snapshot_id),
            snapshot=manifest,
            data_report=report,
            strategy_certification_ready=True,
        )
        self.assertEqual(runtime.status, ResearchRuntimeStatus.BACKTEST_READY)

    def test_snapshot_reference_mismatch_is_blocked(self) -> None:
        _, manifest, report = self._closed_snapshot()
        runtime, _ = prepare_research_runtime(
            spec=_spec("sha256:not-the-snapshot"),
            snapshot=manifest,
            data_report=report,
            strategy_certification_ready=True,
        )
        self.assertEqual(runtime.status, ResearchRuntimeStatus.BLOCKED)
        self.assertTrue(any("snapshot_ref" in blocker for blocker in runtime.blockers))


if __name__ == "__main__":
    unittest.main()
