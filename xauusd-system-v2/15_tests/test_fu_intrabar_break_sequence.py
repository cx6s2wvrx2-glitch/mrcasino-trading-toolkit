from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.fu_intrabar_break_sequence import (
    FUIntrabarBreakSequenceState,
    extract_fu_intrabar_break_sequence,
)
from xauusd_v2.liquidity_interaction import LiquiditySide, MarkedLiquidityReference


UTC = timezone.utc
PARENT_START = datetime(2023, 3, 30, 12, 30, tzinfo=UTC)


def bar(index: int, *, open: float, high: float, low: float, close: float) -> MarketBar:
    return MarketBar(
        timestamp=PARENT_START + timedelta(minutes=index),
        open=open,
        high=high,
        low=low,
        close=close,
        is_closed=True,
        source_name="Exclusive Markets",
        source_symbol="XAUUSD!",
    )


def below_reference() -> MarkedLiquidityReference:
    return MarkedLiquidityReference(
        reference_id="liq-below",
        level=96.0,
        side=LiquiditySide.BELOW,
        source_type="labelled_test",
    )


def above_reference() -> MarkedLiquidityReference:
    return MarkedLiquidityReference(
        reference_id="liq-above",
        level=109.0,
        side=LiquiditySide.ABOVE,
        source_type="labelled_test",
    )


class FUIntrabarBreakSequenceTests(unittest.TestCase):
    def test_bullish_post_take_previous_high_break_is_observed(self) -> None:
        bars = (
            bar(0, open=100, high=104, low=97, close=102),
            bar(1, open=102, high=104, low=94, close=99),  # first take below 96
            bar(2, open=99, high=111, low=98, close=108),  # later break above prev high 110
            bar(3, open=108, high=109, low=101, close=105),
            bar(4, open=105, high=108, low=102, close=106),
        )
        result = self._run(bars, below_reference())

        self.assertEqual(result.state, FUIntrabarBreakSequenceState.POST_TAKE_OPPOSITE_BREAK_OBSERVED)
        self.assertEqual(result.expected_fu_direction, "bullish")
        self.assertEqual(result.opposite_previous_extreme_name, "previous_high")
        self.assertEqual(result.first_take_child_index, 1)
        self.assertEqual(result.first_post_take_break_child_index, 2)
        self.assertTrue(result.post_take_opposite_break_observed)
        self.assertTrue(result.candidate_sequence_supported)
        self._assert_non_certifying(result)

    def test_break_on_same_child_as_take_keeps_order_unresolved(self) -> None:
        bars = (
            bar(0, open=100, high=104, low=97, close=102),
            bar(1, open=102, high=111, low=94, close=103),  # take + opposite break, order unknown
            bar(2, open=103, high=108, low=99, close=105),
            bar(3, open=105, high=109, low=101, close=106),
            bar(4, open=106, high=108, low=102, close=104),
        )
        result = self._run(bars, below_reference())

        self.assertEqual(result.state, FUIntrabarBreakSequenceState.BREAK_ON_TAKE_CHILD_ORDER_UNRESOLVED)
        self.assertTrue(result.opposite_break_on_take_child_observed)
        self.assertFalse(result.post_take_opposite_break_observed)
        self.assertFalse(result.candidate_sequence_supported)
        self._assert_non_certifying(result)

    def test_break_only_before_take_does_not_support_required_order(self) -> None:
        bars = (
            bar(0, open=100, high=111, low=97, close=108),  # opposite break before take
            bar(1, open=108, high=109, low=94, close=100),  # first take
            bar(2, open=100, high=108, low=98, close=104),
            bar(3, open=104, high=109, low=101, close=106),
            bar(4, open=106, high=108, low=102, close=104),
        )
        result = self._run(bars, below_reference())

        self.assertEqual(result.state, FUIntrabarBreakSequenceState.NO_POST_TAKE_OPPOSITE_BREAK)
        self.assertTrue(result.opposite_break_before_take_observed)
        self.assertFalse(result.opposite_break_on_take_child_observed)
        self.assertFalse(result.post_take_opposite_break_observed)
        self.assertFalse(result.candidate_sequence_supported)
        self._assert_non_certifying(result)

    def test_bearish_post_take_previous_low_break_is_observed(self) -> None:
        bars = (
            bar(0, open=100, high=108, low=98, close=104),
            bar(1, open=104, high=111, low=99, close=106),  # first take above 109
            bar(2, open=106, high=108, low=94, close=96),   # later break below prev low 95
            bar(3, open=96, high=103, low=96, close=100),
            bar(4, open=100, high=104, low=97, close=101),
        )
        result = self._run(bars, above_reference())

        self.assertEqual(result.state, FUIntrabarBreakSequenceState.POST_TAKE_OPPOSITE_BREAK_OBSERVED)
        self.assertEqual(result.expected_fu_direction, "bearish")
        self.assertEqual(result.opposite_previous_extreme_name, "previous_low")
        self.assertEqual(result.first_post_take_break_child_index, 2)
        self.assertTrue(result.candidate_sequence_supported)
        self._assert_non_certifying(result)

    def test_no_liquidity_take_is_fail_closed(self) -> None:
        bars = (
            bar(0, open=100, high=104, low=97, close=102),
            bar(1, open=102, high=108, low=97, close=106),
            bar(2, open=106, high=111, low=97, close=108),
            bar(3, open=108, high=109, low=98, close=103),
            bar(4, open=103, high=108, low=97, close=104),
        )
        result = self._run(bars, below_reference())

        self.assertEqual(result.state, FUIntrabarBreakSequenceState.NO_LIQUIDITY_TAKE)
        self.assertFalse(result.candidate_sequence_supported)
        self.assertIsNone(result.first_take_child_index)
        self._assert_non_certifying(result)

    def _run(self, bars, reference):
        return extract_fu_intrabar_break_sequence(
            parent_start=PARENT_START,
            parent_timeframe_seconds=300,
            child_timeframe_seconds=60,
            child_bars=bars,
            reference=reference,
            previous_high=110.0,
            previous_low=95.0,
            evaluation_time=PARENT_START + timedelta(minutes=5),
        )

    def _assert_non_certifying(self, result) -> None:
        self.assertFalse(result.fu_semantics_certified)
        self.assertFalse(result.b01_globally_resolved)
        self.assertFalse(result.strategy_truth_changed)


if __name__ == "__main__":
    unittest.main()
