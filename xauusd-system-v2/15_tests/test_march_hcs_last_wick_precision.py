from __future__ import annotations

import unittest
from datetime import UTC, datetime
from decimal import Decimal

from xauusd_v2.agents.data_agent import MarketBar
from xauusd_v2.march_hcs_last_wick_probe import _level_touched


class MarchHCSLastWickPrecisionTests(unittest.TestCase):
    def test_sub_float_decimal_above_high_is_not_rounded_into_touch(self) -> None:
        bar = MarketBar(
            timestamp=datetime(2023, 3, 30, 12, 0, tzinfo=UTC),
            open=99.0,
            high=100.0,
            low=98.0,
            close=99.5,
            is_closed=True,
            source_name="Exclusive Markets Ltd.",
            source_symbol="XAUUSD!",
        )
        level = Decimal("100.0000000000000000001")
        self.assertEqual(float(level), 100.0)
        self.assertFalse(_level_touched(bar, level))


if __name__ == "__main__":
    unittest.main()
