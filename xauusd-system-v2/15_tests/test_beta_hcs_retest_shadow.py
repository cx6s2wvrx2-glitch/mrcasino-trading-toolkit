from __future__ import annotations

import unittest

from xauusd_v2.beta_hcs_retest_shadow import BetaHCSZone, update_beta_hcs_zone
from xauusd_v2.beta_hcs_shadow import BetaHCSDirection


class BetaHCSRetestShadowTests(unittest.TestCase):
    def test_bear_zone_break_then_retest(self) -> None:
        zone = BetaHCSZone(
            direction=BetaHCSDirection.BEAR,
            top_val=110.0,
            bottom_val=105.0,
            is_broken=True,
        )
        result = update_beta_hcs_zone(zone=zone, current_high=108.0, current_low=106.0)
        self.assertTrue(result.is_broken)
        self.assertTrue(result.retesting)
        self.assertFalse(result.delete_zone)
        self.assertEqual(result.next_top_val, 106.0)
        self.assertFalse(result.strategy_semantics_certified)

    def test_bear_zone_breaks_when_high_exceeds_top(self) -> None:
        zone = BetaHCSZone(
            direction=BetaHCSDirection.BEAR,
            top_val=110.0,
            bottom_val=105.0,
            is_broken=False,
        )
        result = update_beta_hcs_zone(zone=zone, current_high=111.0, current_low=109.0)
        self.assertTrue(result.is_broken)
        self.assertFalse(result.retesting)

    def test_bear_zone_is_deleted_when_low_falls_below_bottom(self) -> None:
        zone = BetaHCSZone(
            direction=BetaHCSDirection.BEAR,
            top_val=110.0,
            bottom_val=105.0,
            is_broken=True,
        )
        result = update_beta_hcs_zone(zone=zone, current_high=108.0, current_low=104.0)
        self.assertTrue(result.delete_zone)

    def test_bull_zone_break_then_retest(self) -> None:
        zone = BetaHCSZone(
            direction=BetaHCSDirection.BULL,
            top_val=110.0,
            bottom_val=105.0,
            is_broken=True,
        )
        result = update_beta_hcs_zone(zone=zone, current_high=109.0, current_low=107.0)
        self.assertTrue(result.retesting)
        self.assertFalse(result.delete_zone)
        self.assertEqual(result.next_bottom_val, 107.0)

    def test_bull_zone_breaks_when_low_falls_below_bottom(self) -> None:
        zone = BetaHCSZone(
            direction=BetaHCSDirection.BULL,
            top_val=110.0,
            bottom_val=105.0,
            is_broken=False,
        )
        result = update_beta_hcs_zone(zone=zone, current_high=106.0, current_low=104.0)
        self.assertTrue(result.is_broken)
        self.assertFalse(result.retesting)

    def test_bull_zone_is_deleted_when_high_exceeds_top(self) -> None:
        zone = BetaHCSZone(
            direction=BetaHCSDirection.BULL,
            top_val=110.0,
            bottom_val=105.0,
            is_broken=True,
        )
        result = update_beta_hcs_zone(zone=zone, current_high=111.0, current_low=107.0)
        self.assertTrue(result.delete_zone)


if __name__ == "__main__":
    unittest.main()
