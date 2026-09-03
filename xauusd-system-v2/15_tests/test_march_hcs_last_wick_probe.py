from __future__ import annotations

import unittest
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.fu_basic_candidate import BasicFUCandidateState
from xauusd_v2.march_hcs_last_wick_probe import (
    BasicFUProxy,
    _diagnose_touch,
    _probe_hcs_spec,
)
from xauusd_v2.march_semantic_probe import MarchSemanticProbeSpec
from xauusd_v2.primitive_replay_scan import HCSCandidateForm, scan_primitive_replay_window


class MarchHCSLastWickProbeTests(unittest.TestCase):
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

    def spec(self, *, level: str, end_minute: int) -> MarchSemanticProbeSpec:
        return MarchSemanticProbeSpec(
            probe_id="hcs-probe",
            episode_id="episode",
            source_ref="PRIMARY_NARRATIVE_2023_03_30_31#fixture",
            source_role="easy_1m_hcs_reentry",
            primitive_family="HCS",
            level=Decimal(level),
            timeframe_seconds=60,
            window_start=datetime(2023, 3, 30, 12, 0, tzinfo=UTC),
            window_end=datetime(2023, 3, 30, 12, end_minute, tzinfo=UTC),
            note="source-labelled HCS with no certified occurrence timestamp",
        )

    def test_touch_is_strict_only_when_latest_prior_wick_retests_and_second_basic_fu_exists(self) -> None:
        bar = self.bar(2, open=100.2, high=101.0, low=99.2, close=99.4)
        latest = BasicFUProxy(
            bar_open=datetime(2023, 3, 30, 12, 1, tzinfo=UTC),
            direction="bullish",
            wick_low=98.5,
            wick_high=99.5,
        )
        result = _diagnose_touch(
            bar=bar,
            latest_prior=latest,
            current_basic={"state": BasicFUCandidateState.BEARISH.value, "direction": "bearish"},
            broad_hcs_items=[],
        )
        self.assertTrue(result["exact_last_basic_fu_proxy_wick_retest"])
        self.assertTrue(result["strict_last_wick_basic_hcs_proxy"])
        self.assertEqual(result["diagnostic"], "STRICT_LAST_WICK_BASIC_HCS_PROXY_PRESENT")
        self.assertFalse(result["certified_hcs"])

    def test_broad_any_prior_match_is_not_promoted_when_latest_prior_wick_does_not_retest(self) -> None:
        bar = self.bar(3, open=99.2, high=100.8, low=98.8, close=100.5)
        latest = BasicFUProxy(
            bar_open=datetime(2023, 3, 30, 12, 2, tzinfo=UTC),
            direction="bearish",
            wick_low=101.0,
            wick_high=101.5,
        )
        broad = SimpleNamespace(
            first_bar_open=datetime(2023, 3, 30, 12, 1, tzinfo=UTC),
            hcs_candidate_form=HCSCandidateForm.CONTINUATION,
        )
        result = _diagnose_touch(
            bar=bar,
            latest_prior=latest,
            current_basic={"state": BasicFUCandidateState.BULLISH.value, "direction": "bullish"},
            broad_hcs_items=[broad],
        )
        self.assertFalse(result["exact_last_basic_fu_proxy_wick_retest"])
        self.assertFalse(result["strict_last_wick_basic_hcs_proxy"])
        self.assertTrue(result["broad_any_prior_basic_hcs_proxy"])
        self.assertTrue(result["broad_only_not_last_wick"])
        self.assertEqual(result["diagnostic"], "SECOND_BASIC_FU_PROXY_PRESENT_NO_EXACT_LAST_WICK_RETEST")

    def test_ambiguous_second_basic_fu_is_preserved_not_guessed(self) -> None:
        bar = self.bar(2, open=99.4, high=101.2, low=98.8, close=99.5)
        latest = BasicFUProxy(
            bar_open=datetime(2023, 3, 30, 12, 1, tzinfo=UTC),
            direction="bullish",
            wick_low=98.5,
            wick_high=99.5,
        )
        result = _diagnose_touch(
            bar=bar,
            latest_prior=latest,
            current_basic={"state": BasicFUCandidateState.AMBIGUOUS.value, "direction": None},
            broad_hcs_items=[],
        )
        self.assertFalse(result["strict_last_wick_basic_hcs_proxy"])
        self.assertEqual(result["diagnostic"], "LAST_WICK_RETEST_PRESENT_SECOND_BASIC_FU_AMBIGUOUS")

    def test_full_probe_detects_strict_latest_wick_proxy_without_certification(self) -> None:
        bars = (
            self.bar(0, open=100.0, high=101.0, low=99.0, close=100.0),
            self.bar(1, open=99.5, high=100.5, low=98.5, close=100.4),
            self.bar(2, open=100.2, high=101.0, low=99.2, close=99.4),
        )
        primitive = scan_primitive_replay_window(
            bars=bars,
            timeframe_seconds=60,
            scan_start=datetime(2023, 3, 30, 12, 0, tzinfo=UTC),
            scan_end=datetime(2023, 3, 30, 12, 3, tzinfo=UTC),
        )
        report = _probe_hcs_spec(bars, primitive, self.spec(level="100.8", end_minute=3))
        self.assertEqual(report["strict_last_wick_basic_hcs_proxy_bar_count"], 1)
        self.assertEqual(report["diagnostic"], "STRICT_LAST_WICK_BASIC_HCS_PROXY_PRESENT_ON_SOURCE_LEVEL_TOUCH")
        self.assertEqual(report["certified_hcs_count"], 0)
        self.assertFalse(report["semantic_stage_certification"])
        self.assertFalse(report["promotion_allowed"])

    def test_full_probe_exposes_any_prior_overbreadth_against_latest_wick(self) -> None:
        bars = (
            self.bar(0, open=100.0, high=101.0, low=99.0, close=100.0),
            self.bar(1, open=99.5, high=100.5, low=98.5, close=100.4),
            self.bar(2, open=101.0, high=101.5, low=100.0, close=100.2),
            self.bar(3, open=99.2, high=100.8, low=98.8, close=100.5),
        )
        primitive = scan_primitive_replay_window(
            bars=bars,
            timeframe_seconds=60,
            scan_start=datetime(2023, 3, 30, 12, 0, tzinfo=UTC),
            scan_end=datetime(2023, 3, 30, 12, 4, tzinfo=UTC),
        )
        report = _probe_hcs_spec(bars, primitive, self.spec(level="98.9", end_minute=4))
        self.assertEqual(report["strict_last_wick_basic_hcs_proxy_bar_count"], 0)
        self.assertGreaterEqual(report["broad_any_prior_basic_hcs_proxy_bar_count"], 1)
        self.assertGreaterEqual(report["broad_only_not_last_wick_bar_count"], 1)
        self.assertEqual(report["diagnostic"], "BROAD_ANY_PRIOR_PROXY_PRESENT_BUT_STRICT_LAST_WICK_PROXY_ABSENT")
        self.assertFalse(report["promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
