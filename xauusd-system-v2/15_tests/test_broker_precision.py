from __future__ import annotations

from decimal import Decimal
import unittest

from xauusd_v2.broker_precision import BrokerPriceSpec, is_exact_same_broker_price, price_distance_in_ticks


class BrokerPrecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = BrokerPriceSpec.from_strings(
            broker_name="example-broker",
            source_symbol="XAUUSD.a",
            digits=2,
            tick_size="0.01",
        )

    def test_distance_in_ticks_is_explicit_and_reproducible(self) -> None:
        distance = price_distance_in_ticks(price_a="2500.00", price_b="2500.03", spec=self.spec)
        self.assertEqual(distance, Decimal("3"))

    def test_sub_tick_distance_is_preserved_not_rounded_to_zero(self) -> None:
        distance = price_distance_in_ticks(price_a="2500.000", price_b="2500.005", spec=self.spec)
        self.assertEqual(distance, Decimal("0.5"))

    def test_exact_same_broker_price_uses_declared_digits(self) -> None:
        self.assertTrue(is_exact_same_broker_price(price_a="2500.001", price_b="2500.004", spec=self.spec))

    def test_different_broker_prices_remain_different(self) -> None:
        self.assertFalse(is_exact_same_broker_price(price_a="2500.00", price_b="2500.01", spec=self.spec))

    def test_missing_broker_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BrokerPriceSpec.from_strings(broker_name="", source_symbol="XAUUSD", digits=2, tick_size="0.01")

    def test_non_positive_tick_size_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BrokerPriceSpec.from_strings(broker_name="broker", source_symbol="XAUUSD", digits=2, tick_size="0")

    def test_negative_digits_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BrokerPriceSpec.from_strings(broker_name="broker", source_symbol="XAUUSD", digits=-1, tick_size="0.01")

    def test_invalid_tick_size_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BrokerPriceSpec.from_strings(broker_name="broker", source_symbol="XAUUSD", digits=2, tick_size="not-a-number")


if __name__ == "__main__":
    unittest.main()
