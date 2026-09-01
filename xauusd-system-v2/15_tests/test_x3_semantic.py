from __future__ import annotations

import unittest

from xauusd_v2.x3_semantic import X3State, evaluate_x3_primitive


class X3SemanticTests(unittest.TestCase):
    def test_fu_plus_negation_same_candle_is_x3(self) -> None:
        result = evaluate_x3_primitive(
            fu_characteristics_same_candle=True,
            negation_characteristics_same_candle=True,
        )
        self.assertEqual(result.state, X3State.CONFIRMED)

    def test_fu_without_negation_is_not_x3(self) -> None:
        result = evaluate_x3_primitive(
            fu_characteristics_same_candle=True,
            negation_characteristics_same_candle=False,
        )
        self.assertEqual(result.state, X3State.NOT_X3)

    def test_negation_without_fu_is_not_x3(self) -> None:
        result = evaluate_x3_primitive(
            fu_characteristics_same_candle=False,
            negation_characteristics_same_candle=True,
        )
        self.assertEqual(result.state, X3State.NOT_X3)

    def test_missing_fu_evidence_fails_closed(self) -> None:
        result = evaluate_x3_primitive(
            fu_characteristics_same_candle=None,
            negation_characteristics_same_candle=True,
        )
        self.assertEqual(result.state, X3State.NOT_CERTIFIED)

    def test_missing_negation_evidence_fails_closed(self) -> None:
        result = evaluate_x3_primitive(
            fu_characteristics_same_candle=True,
            negation_characteristics_same_candle=None,
        )
        self.assertEqual(result.state, X3State.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
