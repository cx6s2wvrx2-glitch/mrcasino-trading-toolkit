from __future__ import annotations

import json
import unittest
from pathlib import Path


class TopDownScopeExclusionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = Path(__file__).parent / "topdown_scope_exclusions.json"
        cls.data = json.loads(path.read_text(encoding="utf-8"))

    def test_scope_is_xauusd_only(self) -> None:
        self.assertEqual(self.data["policy"], "XAUUSD-only strategy ground truth")

    def test_2021_11_30_gbpjpy_sequence_is_explicitly_excluded(self) -> None:
        item = self.data["exclusions"][0]
        self.assertEqual(item["sequence"], "2021-11-30")
        self.assertEqual(item["symbol"], "GBPJPY")
        self.assertEqual(item["reason"], "non_xauusd_symbol")
        self.assertTrue(item["inspected"])
        self.assertFalse(item["ground_truth_allowed"])
        self.assertFalse(item["promotion_allowed"])
        self.assertEqual(len(item["images"]), 2)


if __name__ == "__main__":
    unittest.main()
