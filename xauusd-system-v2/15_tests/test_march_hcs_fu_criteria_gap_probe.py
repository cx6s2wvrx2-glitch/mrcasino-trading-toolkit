from __future__ import annotations

import unittest
from datetime import UTC, datetime

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.fu_completion import FUCompletionClass
from xauusd_v2.fu_criteria import FUCriteriaState
from xauusd_v2.march_hcs_fu_criteria_gap_probe import _observe_fu_criteria_gap
from xauusd_v2.march_hcs_second_node_probe import BasicFUProxy


class MarchHCSFUCriteriaGapProbeTests(unittest.TestCase):
    def bar(
        self,
        minute: int,
        *,
        open: float,
        high: float,
        low: float,
        close: float,
    ) -> MarketBar:
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

    def latest(self, *, wick_low: float, wick_high: float) -> BasicFUProxy:
        return BasicFUProxy(
            bar_open=datetime(2023, 3, 30, 11, 59, tzinfo=UTC),
            direction="bullish",
            wick_low=wick_low,
            wick_high=wick_high,
        )

    def test_exact_retest_localizes_conditional_attempted_fu_form_2_without_certifying_fu(self) -> None:
        previous = self.bar(0, open=100.0, high=102.0, low=98.0, close=101.0)
        current = self.bar(1, open=100.5, high=103.0, low=99.0, close=102.5)
        result = _observe_fu_criteria_gap(
            current=current,
            previous=previous,
            latest_prior=self.latest(wick_low=98.8, wick_high=99.4),
        )

        self.assertTrue(result["exact_latest_basic_fu_proxy_wick_retest"])
        self.assertEqual(result["observed_fu_criteria"]["state"], FUCriteriaState.NOT_CERTIFIED.value)
        self.assertEqual(
            result["observed_reflection_completion"]["classification"],
            FUCompletionClass.NOT_CERTIFIED.value,
        )
        self.assertEqual(
            result["conditional_if_fu_criteria_met"]["classification"],
            FUCompletionClass.ATTEMPTED_FU_FORM_2.value,
        )
        self.assertEqual(
            result["diagnostic"],
            "EXACT_RETEST_CONDITIONAL_ATTEMPTED_FU_FORM_2_IF_FU_CRITERIA_MET",
        )
        self.assertFalse(result["fu_criteria_certified"])
        self.assertFalse(result["attempted_fu_node_certified"])
        self.assertFalse(result["certified_hcs"])

    def test_exact_retest_can_localize_conditional_complete_fu_without_equating_it_to_strong_fu(self) -> None:
        previous = self.bar(0, open=100.0, high=102.0, low=98.0, close=101.0)
        current = self.bar(1, open=101.5, high=103.0, low=99.0, close=100.5)
        result = _observe_fu_criteria_gap(
            current=current,
            previous=previous,
            latest_prior=self.latest(wick_low=98.8, wick_high=99.4),
        )

        self.assertTrue(result["exact_latest_basic_fu_proxy_wick_retest"])
        self.assertEqual(
            result["conditional_if_fu_criteria_met"]["classification"],
            FUCompletionClass.COMPLETE_FU.value,
        )
        self.assertEqual(
            result["conditional_if_fu_criteria_met"]["node_family"],
            "complete_fu_not_equated_to_strong_fu",
        )
        self.assertEqual(
            result["diagnostic"],
            "EXACT_RETEST_CONDITIONAL_COMPLETE_FU_IF_FU_CRITERIA_MET",
        )
        self.assertFalse(result["strong_fu_node_certified"])
        self.assertFalse(result["certified_hcs"])

    def test_no_new_extreme_preserves_attempted_fu_form_1_lower_bound(self) -> None:
        previous = self.bar(0, open=100.0, high=102.0, low=98.0, close=101.0)
        current = self.bar(1, open=100.5, high=101.5, low=98.5, close=100.8)
        result = _observe_fu_criteria_gap(
            current=current,
            previous=previous,
            latest_prior=self.latest(wick_low=98.4, wick_high=99.0),
        )

        self.assertTrue(result["exact_latest_basic_fu_proxy_wick_retest"])
        self.assertEqual(
            result["observed_reflection_completion"]["classification"],
            FUCompletionClass.ATTEMPTED_FU_FORM_1.value,
        )
        self.assertEqual(
            result["conditional_if_fu_criteria_met"]["classification"],
            FUCompletionClass.ATTEMPTED_FU_FORM_1.value,
        )
        self.assertEqual(
            result["diagnostic"],
            "EXACT_RETEST_REFLECTION_ATTEMPTED_FU_FORM_1_LOWER_BOUND",
        )
        self.assertFalse(result["attempted_fu_node_certified"])
        self.assertFalse(result["certified_hcs"])

    def test_no_retest_is_not_promoted_by_conditional_completion(self) -> None:
        previous = self.bar(0, open=100.0, high=102.0, low=98.0, close=101.0)
        current = self.bar(1, open=100.5, high=103.0, low=99.0, close=102.5)
        result = _observe_fu_criteria_gap(
            current=current,
            previous=previous,
            latest_prior=self.latest(wick_low=95.0, wick_high=96.0),
        )

        self.assertFalse(result["exact_latest_basic_fu_proxy_wick_retest"])
        self.assertEqual(
            result["conditional_if_fu_criteria_met"]["classification"],
            FUCompletionClass.ATTEMPTED_FU_FORM_2.value,
        )
        self.assertEqual(
            result["diagnostic"],
            "NO_EXACT_LATEST_BASIC_FU_PROXY_WICK_RETEST_ON_THIS_TOUCH",
        )
        self.assertFalse(result["certified_hcs"])


if __name__ == "__main__":
    unittest.main()
