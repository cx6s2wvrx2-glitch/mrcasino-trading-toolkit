from __future__ import annotations

import unittest

from xauusd_v2.beta_hcs_shadow import (
    BetaHCSBoxState,
    BetaHCSDirection,
    BetaTrackedManipulationBox,
    evaluate_beta_hcs_interaction,
)


class BetaHCSShadowTests(unittest.TestCase):
    def _bull_box(self, **overrides):
        values = dict(
            direction=BetaHCSDirection.BULL,
            timeframe="15",
            creation_time=1000,
            state=BetaHCSBoxState.ESTABLISHED,
            base_pattern="FU BULL",
            top_val=101.0,
            bottom_val=99.0,
            original_top=102.0,
            original_bottom=98.0,
            hcs_count=0,
        )
        values.update(overrides)
        return BetaTrackedManipulationBox(**values)

    def test_confirmed_same_direction_fu_inside_bull_box_increments_hcs(self) -> None:
        result = evaluate_beta_hcs_interaction(
            box=self._bull_box(),
            current_direction=BetaHCSDirection.BULL,
            current_is_fu=True,
            current_is_sn=False,
            current_high=103.0,
            current_low=100.0,
            current_time=2000,
            current_confirmed=True,
        )
        self.assertTrue(result.hcs)
        self.assertFalse(result.hcs_forming)
        self.assertEqual(result.next_hcs_count, 1)
        self.assertEqual(result.next_pattern_text, "FU BULL [HCS X1]")
        self.assertFalse(result.strategy_semantics_certified)

    def test_unconfirmed_interaction_is_hcs_forming_without_increment(self) -> None:
        result = evaluate_beta_hcs_interaction(
            box=self._bull_box(hcs_count=2),
            current_direction=BetaHCSDirection.BULL,
            current_is_fu=False,
            current_is_sn=True,
            current_high=103.0,
            current_low=100.0,
            current_time=2000,
            current_confirmed=False,
        )
        self.assertFalse(result.hcs)
        self.assertTrue(result.hcs_forming)
        self.assertEqual(result.next_hcs_count, 2)

    def test_opposite_direction_does_not_increment_beta_hcs(self) -> None:
        result = evaluate_beta_hcs_interaction(
            box=self._bull_box(),
            current_direction=BetaHCSDirection.BEAR,
            current_is_fu=True,
            current_is_sn=False,
            current_high=101.0,
            current_low=100.0,
            current_time=2000,
            current_confirmed=True,
        )
        self.assertFalse(result.hcs)
        self.assertIn("same direction", result.reason)

    def test_source_creation_candle_is_skipped(self) -> None:
        result = evaluate_beta_hcs_interaction(
            box=self._bull_box(),
            current_direction=BetaHCSDirection.BULL,
            current_is_fu=True,
            current_is_sn=False,
            current_high=103.0,
            current_low=100.0,
            current_time=1000,
            current_confirmed=True,
        )
        self.assertFalse(result.hcs)

    def test_forming_box_is_skipped(self) -> None:
        result = evaluate_beta_hcs_interaction(
            box=self._bull_box(state=BetaHCSBoxState.FORMING),
            current_direction=BetaHCSDirection.BULL,
            current_is_fu=True,
            current_is_sn=False,
            current_high=103.0,
            current_low=100.0,
            current_time=2000,
            current_confirmed=True,
        )
        self.assertFalse(result.hcs)

    def test_non_fu_sn_base_is_skipped(self) -> None:
        result = evaluate_beta_hcs_interaction(
            box=self._bull_box(base_pattern="LAOL"),
            current_direction=BetaHCSDirection.BULL,
            current_is_fu=True,
            current_is_sn=False,
            current_high=103.0,
            current_low=100.0,
            current_time=2000,
            current_confirmed=True,
        )
        self.assertFalse(result.hcs)

    def test_first_50m_hcs_creates_separate_beta_hcs_zone(self) -> None:
        result = evaluate_beta_hcs_interaction(
            box=self._bull_box(timeframe="50"),
            current_direction=BetaHCSDirection.BULL,
            current_is_fu=True,
            current_is_sn=False,
            current_high=103.0,
            current_low=100.0,
            current_time=2000,
            current_confirmed=True,
        )
        self.assertTrue(result.creates_hcs_zone_in_supplied_beta)

    def test_second_50m_hcs_does_not_create_second_separate_zone(self) -> None:
        result = evaluate_beta_hcs_interaction(
            box=self._bull_box(timeframe="50", hcs_count=1),
            current_direction=BetaHCSDirection.BULL,
            current_is_fu=True,
            current_is_sn=False,
            current_high=103.0,
            current_low=100.0,
            current_time=2000,
            current_confirmed=True,
        )
        self.assertEqual(result.next_hcs_count, 2)
        self.assertFalse(result.creates_hcs_zone_in_supplied_beta)

    def test_bear_interaction_uses_high_inside_box(self) -> None:
        box = BetaTrackedManipulationBox(
            direction=BetaHCSDirection.BEAR,
            timeframe="15",
            creation_time=1000,
            state=BetaHCSBoxState.ESTABLISHED,
            base_pattern="SN BEAR",
            top_val=110.0,
            bottom_val=105.0,
            original_top=111.0,
            original_bottom=104.0,
            hcs_count=0,
        )
        result = evaluate_beta_hcs_interaction(
            box=box,
            current_direction=BetaHCSDirection.BEAR,
            current_is_fu=False,
            current_is_sn=True,
            current_high=106.0,
            current_low=100.0,
            current_time=2000,
            current_confirmed=True,
        )
        self.assertTrue(result.hcs)
        self.assertEqual(result.next_pattern_text, "SN BEAR [HCS X1]")


if __name__ == "__main__":
    unittest.main()
