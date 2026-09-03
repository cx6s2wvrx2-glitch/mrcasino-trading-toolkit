from __future__ import annotations

import unittest
from datetime import UTC, datetime
from decimal import Decimal

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.fu_completion import FUCompletionClass
from xauusd_v2.march_hcs_second_node_probe import BasicFUProxy, _level_touched, _observe_second_node


class MarchHCSSecondNodeProbeTests(unittest.TestCase):
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

    def test_exact_retest_can_expose_reflection_attempted_fu_form_1_while_basic_proxy_is_none(self) -> None:
        previous = self.bar(0, open=105.0, high=110.0, low=95.0, close=100.0)
        current = self.bar(1, open=101.0, high=108.0, low=97.0, close=103.0)
        latest = BasicFUProxy(
            bar_open=datetime(2023, 3, 30, 11, 59, tzinfo=UTC),
            direction="bullish",
            wick_low=96.0,
            wick_high=98.0,
        )

        result = _observe_second_node(
            current=current,
            previous=previous,
            latest_prior=latest,
            timeframe_seconds=60,
        )

        self.assertTrue(result["exact_last_basic_fu_proxy_wick_retest"])
        self.assertEqual(result["basic_fu_state"], "none")
        self.assertEqual(
            result["reflection_completion_lower_bound"]["classification"],
            FUCompletionClass.ATTEMPTED_FU_FORM_1.value,
        )
        self.assertEqual(
            result["diagnostic"],
            "LAST_WICK_RETEST_WITH_REFLECTION_ATTEMPTED_FU_FORM_1",
        )
        self.assertFalse(result["attempted_fu_node_certified"])
        self.assertFalse(result["certified_hcs"])

    def test_v7_att_shadow_is_preserved_as_implementation_evidence_only(self) -> None:
        previous = self.bar(0, open=105.0, high=110.0, low=95.0, close=100.0)
        current = self.bar(1, open=94.0, high=111.0, low=94.0, close=106.0)
        latest = BasicFUProxy(
            bar_open=datetime(2023, 3, 30, 11, 59, tzinfo=UTC),
            direction="bullish",
            wick_low=94.0,
            wick_high=95.0,
        )

        result = _observe_second_node(
            current=current,
            previous=previous,
            latest_prior=latest,
            timeframe_seconds=60,
        )

        self.assertTrue(result["exact_last_basic_fu_proxy_wick_retest"])
        self.assertEqual(result["basic_fu_state"], "ambiguous")
        self.assertEqual(
            result["reflection_completion_lower_bound"]["classification"],
            FUCompletionClass.NOT_CERTIFIED.value,
        )
        self.assertEqual(result["casino_v7_shadow"]["bullish"], "att_fu")
        self.assertTrue(result["casino_v7_shadow"]["implementation_evidence_only"])
        self.assertEqual(
            result["diagnostic"],
            "LAST_WICK_RETEST_WITH_V7_ATT_IMPLEMENTATION_EVIDENCE",
        )
        self.assertFalse(result["attempted_fu_node_certified"])
        self.assertFalse(result["fu_negation_node_certified"])
        self.assertFalse(result["certified_hcs"])

    def test_decimal_source_level_is_not_rounded_into_touch(self) -> None:
        bar = self.bar(1, open=99.0, high=100.0, low=98.0, close=99.5)
        level = Decimal("100.0000000000000000001")
        self.assertEqual(float(level), 100.0)
        self.assertFalse(_level_touched(bar, level))


if __name__ == "__main__":
    unittest.main()
