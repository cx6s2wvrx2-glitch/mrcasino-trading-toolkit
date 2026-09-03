from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.march_semantic_probe import (
    MarchSemanticProbeError,
    MarchSemanticProbeSpec,
    _probe_one,
    load_march_semantic_probe_specs,
)
from xauusd_v2.primitive_replay_scan import scan_primitive_replay_window


class MarchSemanticProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime(2023, 3, 30, 12, 0, tzinfo=UTC)
        self.end = datetime(2023, 3, 30, 12, 3, tzinfo=UTC)

    def bar(self, minute: int, *, open: float, high: float, low: float, close: float) -> MarketBar:
        return MarketBar(
            timestamp=datetime(2023, 3, 30, 12, minute, tzinfo=UTC),
            open=open,
            high=high,
            low=low,
            close=close,
            is_closed=True,
            source_name="Exclusive Markets Ltd.",
            source_symbol="XAUUSD!",
        )

    def spec(self, *, family: str, level: str) -> MarchSemanticProbeSpec:
        return MarchSemanticProbeSpec(
            probe_id=f"probe-{family.lower()}-{level}",
            episode_id="episode",
            source_ref="PRIMARY_NARRATIVE_2023_03_30_31#fixture",
            source_role="source_role",
            primitive_family=family,
            level=Decimal(level),
            timeframe_seconds=60,
            window_start=self.start,
            window_end=self.end,
            note="source-labelled role with no certified occurrence timestamp",
        )

    def scan(self, bars: tuple[MarketBar, ...]):
        return scan_primitive_replay_window(
            bars=bars,
            timeframe_seconds=60,
            scan_start=self.start,
            scan_end=self.end,
        )

    def test_governed_fixture_targets_explicit_fu_hcs_roles_not_generic_price_anchors(self) -> None:
        fixture = Path(__file__).resolve().parents[1] / "06_examples" / "MARCH_SOURCE_SEMANTIC_PROBES.json"
        specs = load_march_semantic_probe_specs(fixture)
        self.assertEqual(
            [(item.source_role, item.primitive_family, str(item.level)) for item in specs],
            [
                ("strongest_1m_fu_closure", "FU", "1973.00"),
                ("easy_1m_hcs_reentry", "HCS", "1975.00"),
                ("clearest_1m_hcs_sell_entry", "HCS", "1986.00"),
            ],
        )
        self.assertNotIn("1984.19", {str(item.level) for item in specs})
        self.assertNotIn("1972.70", {str(item.level) for item in specs})

    def test_fu_probe_reports_all_level_touches_and_raw_match_without_certification(self) -> None:
        bars = (
            self.bar(0, open=100.0, high=101.0, low=99.0, close=100.0),
            self.bar(1, open=99.5, high=100.5, low=98.5, close=100.4),
            self.bar(2, open=100.4, high=100.8, low=99.8, close=100.2),
        )
        report = _probe_one(bars, self.scan(bars), self.spec(family="FU", level="99.0"))
        self.assertEqual(report["level_touch_bar_count"], 2)
        self.assertEqual(report["raw_requested_family_match_bar_count"], 1)
        self.assertEqual(report["diagnostic"], "RAW_FU_CANDIDATE_PRESENT_ON_SOURCE_LEVEL_TOUCH")
        self.assertFalse(report["source_occurrence_timestamp_certified"])
        self.assertFalse(report["occurrence_timestamp_inferred"])
        self.assertFalse(report["nearest_bar_substitution_allowed"])
        self.assertFalse(report["price_tolerance_applied"])
        self.assertEqual(report["certified_fu_count"], 0)
        self.assertEqual(report["certified_hcs_count"], 0)
        self.assertFalse(report["promotion_allowed"])

    def test_fu_probe_does_not_use_adjacent_candidate_as_nearest_bar_substitute(self) -> None:
        bars = (
            self.bar(0, open=100.0, high=101.0, low=99.0, close=100.0),
            self.bar(1, open=99.5, high=100.5, low=98.5, close=100.4),
            self.bar(2, open=100.4, high=102.5, low=100.0, close=101.0),
        )
        report = _probe_one(bars, self.scan(bars), self.spec(family="FU", level="102.0"))
        self.assertEqual(report["level_touch_bar_count"], 1)
        self.assertEqual(report["raw_requested_family_match_bar_count"], 0)
        self.assertEqual(report["diagnostic"], "NO_RAW_FU_CANDIDATE_ON_SOURCE_LEVEL_TOUCH")
        self.assertFalse(report["touch_observations"][0]["raw_requested_family_match"])

    def test_hcs_probe_requires_source_style_hcs_on_same_level_touch_bar(self) -> None:
        bars = (
            self.bar(0, open=100.0, high=101.0, low=99.0, close=100.0),
            self.bar(1, open=99.5, high=100.5, low=98.5, close=100.4),
            self.bar(2, open=100.2, high=101.0, low=99.2, close=99.4),
        )
        report = _probe_one(bars, self.scan(bars), self.spec(family="HCS", level="100.8"))
        self.assertEqual(report["level_touch_bar_count"], 2)
        matching = [item for item in report["touch_observations"] if item["raw_requested_family_match"]]
        self.assertEqual(len(matching), 1)
        self.assertGreaterEqual(matching[0]["source_style_hcs_candidate_count"], 1)
        self.assertIn("negation", matching[0]["source_style_hcs_candidate_forms"])
        self.assertEqual(report["diagnostic"], "RAW_HCS_CANDIDATE_PRESENT_ON_SOURCE_LEVEL_TOUCH")
        self.assertEqual(report["certified_hcs_count"], 0)

    def test_fixture_cannot_enable_certification_or_promotion(self) -> None:
        fixture = {
            "schema_version": "march_source_semantic_probes_v1",
            "probes": [
                {
                    "probe_id": "p1",
                    "episode_id": "episode",
                    "source_ref": "source#ref",
                    "source_role": "role",
                    "primitive_family": "FU",
                    "level": "1973.00",
                    "timeframe_seconds": 60,
                    "window_start": "2023-03-30T00:00:00Z",
                    "window_end": "2023-03-31T00:00:00Z",
                    "note": "note"
                }
            ],
            "source_occurrence_timestamps_certified": False,
            "semantic_stage_certification": False,
            "performance_claim_allowed": False,
            "promotion_allowed": True,
            "live_execution_authorized": False
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            with self.assertRaisesRegex(MarchSemanticProbeError, "promotion_allowed must remain false"):
                load_march_semantic_probe_specs(path)


if __name__ == "__main__":
    unittest.main()
