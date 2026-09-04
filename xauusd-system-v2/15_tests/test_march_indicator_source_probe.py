from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.march_indicator_source_probe import (
    STATUS,
    build_march_indicator_source_level_probe,
    load_probe_specs,
)


class MarchIndicatorSourceProbeTests(unittest.TestCase):
    def _bar(
        self,
        minute: int,
        *,
        open: float,
        high: float,
        low: float,
        close: float,
        closed: bool = True,
    ) -> MarketBar:
        return MarketBar(
            timestamp=datetime(2026, 9, 4, 0, 0, tzinfo=UTC) + timedelta(minutes=minute),
            open=open,
            high=high,
            low=low,
            close=close,
            is_closed=closed,
            source_name="test_feed",
            source_symbol="XAUUSD!",
        )

    def _fixture(self, root: Path) -> Path:
        path = root / "probe.json"
        path.write_text(
            json.dumps(
                {
                    "schema_version": "test",
                    "probes": [
                        {
                            "probe_id": "test_hcs_level",
                            "episode_id": "test_episode",
                            "source_role": "test_hcs",
                            "primitive_family": "HCS",
                            "level": "100.00",
                            "timeframe_seconds": 60,
                            "window_start": "2026-09-04T00:01:00Z",
                            "window_end": "2026-09-04T00:04:00Z",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_load_probe_specs_keeps_governed_m1_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = self._fixture(Path(tmp))
            specs = load_probe_specs(fixture)

        self.assertEqual(len(specs), 1)
        self.assertEqual(specs[0].probe_id, "test_hcs_level")
        self.assertEqual(str(specs[0].level), "100.00")
        self.assertEqual(specs[0].primitive_family, "HCS")

    def test_verified_probe_reports_marker_and_source_proxy_on_level_touches(self) -> None:
        bars = (
            self._bar(0, open=100.0, high=105.0, low=95.0, close=100.0),
            self._bar(1, open=101.0, high=107.0, low=94.0, close=106.0),
            # Body is deliberately >30% of range so the supplied helper doji filter
            # cannot erase the otherwise-strong continuation marker.
            self._bar(2, open=102.0, high=109.0, low=93.0, close=108.0),
            self._bar(3, open=108.0, high=110.0, low=99.0, close=109.0, closed=False),
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = self._fixture(root)
            snapshot_file = root / "snapshot.csv"
            snapshot_file.write_bytes(b"synthetic")
            snapshot = SimpleNamespace(
                timeframe_seconds=60,
                source_name="test_feed",
                source_symbol="XAUUSD!",
                coverage_end=datetime(2026, 9, 4, 0, 4, tzinfo=UTC),
                source_file_name="snapshot.csv",
                snapshot_id="sha256:test",
            )
            verified = SimpleNamespace(
                snapshot=snapshot,
                canonical_snapshot_path=snapshot_file,
                normalized_sha256="test",
            )

            with (
                patch(
                    "xauusd_v2.march_indicator_source_probe.load_verified_persisted_mt5_snapshot",
                    return_value=verified,
                ),
                patch(
                    "xauusd_v2.march_indicator_source_probe.load_xauusd_csv_snapshot_bytes",
                    return_value=(bars, snapshot, None),
                ),
            ):
                report = build_march_indicator_source_level_probe(
                    root / "manifest.json",
                    fixture_path=fixture,
                )

        self.assertEqual(report["status"], STATUS)
        self.assertFalse(report["strategy_semantics_certified"])
        self.assertFalse(report["reference_feed_alignment_complete"])
        probe = report["probes"][0]
        self.assertEqual(probe["level_touch_bar_count"], 2)
        self.assertEqual(probe["touch_bars_with_strong_fu_marker"], 2)
        self.assertEqual(probe["touch_bars_with_source_marker_proxy_hcs"], 1)
        self.assertEqual(
            probe["source_marker_proxy_candidate_counts_by_form"],
            {"strong_strong": 1},
        )
        self.assertEqual(len(probe["touch_observations"]), 2)
        self.assertTrue(probe["touch_observations"][1]["source_marker_proxy_candidates"])


if __name__ == "__main__":
    unittest.main()
