from __future__ import annotations

import unittest

from xauusd_v2.timeframe_registry import (
    TIMEFRAME_REGISTRY,
    get_timeframe,
    reference_anchor_certified,
)


class TimeframeRegistryTests(unittest.TestCase):
    def test_beta_helper_has_exact_twenty_five_configured_timeframes(self) -> None:
        configured = [item for item in TIMEFRAME_REGISTRY if item.beta_configured]
        self.assertEqual(len(configured), 25)
        self.assertEqual(
            [item.minutes for item in configured],
            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,20,30,35,40,45,50,55,60,90,100],
        )

    def test_primary_swing_layers_are_registered(self) -> None:
        for code in ("H3", "H5", "H7", "H11"):
            self.assertIn("swing", get_timeframe(code).roles)

    def test_h11_fails_closed_under_b07(self) -> None:
        item = get_timeframe("H11")
        self.assertEqual(item.blocker, "B-07")
        self.assertEqual(item.reference_anchor_status, "BLOCKED")
        self.assertFalse(reference_anchor_certified("H11"))

    def test_native_validated_broker_layers_do_not_imply_reference_anchor_certification(self) -> None:
        for code in ("H1", "H4", "H8", "D1"):
            item = get_timeframe(code)
            self.assertEqual(item.broker_validation_status, "BROKER_NATIVE_OHLC_VALIDATED")
            self.assertFalse(reference_anchor_certified(code))

    def test_14h_15h_are_preserved_as_alternative_source_slots(self) -> None:
        self.assertIn("15/14h", get_timeframe("H14").source_note or "")
        self.assertIn("15/14h", get_timeframe("H15").source_note or "")


if __name__ == "__main__":
    unittest.main()
