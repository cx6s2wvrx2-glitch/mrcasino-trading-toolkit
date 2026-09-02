from __future__ import annotations

import unittest

from xauusd_v2.x3_by_x3_boundary import X3ByX3State, register_x3_by_x3_source_label


class X3ByX3BoundaryTests(unittest.TestCase):
    def test_explicit_primary_label_is_context_only_not_detector(self) -> None:
        result = register_x3_by_x3_source_label(
            explicitly_labelled_by_approved_primary_source=True
        )
        self.assertEqual(result.state, X3ByX3State.SOURCE_LABEL_ONLY)
        self.assertTrue(result.usable_as_context_label)
        self.assertFalse(result.raw_detector_allowed)
        self.assertFalse(result.strategy_condition_allowed)

    def test_absence_of_explicit_label_cannot_be_replaced_by_inference(self) -> None:
        result = register_x3_by_x3_source_label(
            explicitly_labelled_by_approved_primary_source=False
        )
        self.assertEqual(result.state, X3ByX3State.NOT_LABELLED)
        self.assertFalse(result.usable_as_context_label)
        self.assertFalse(result.raw_detector_allowed)
        self.assertIn("cannot be filled by inference", result.reason)

    def test_missing_source_label_evidence_fails_closed(self) -> None:
        result = register_x3_by_x3_source_label(
            explicitly_labelled_by_approved_primary_source=None
        )
        self.assertEqual(result.state, X3ByX3State.NOT_CERTIFIED)
        self.assertFalse(result.raw_detector_allowed)
        self.assertFalse(result.strategy_condition_allowed)

    def test_no_state_ever_authorizes_raw_detector(self) -> None:
        for value in (True, False, None):
            result = register_x3_by_x3_source_label(
                explicitly_labelled_by_approved_primary_source=value
            )
            self.assertFalse(result.raw_detector_allowed)
            self.assertFalse(result.strategy_condition_allowed)


if __name__ == "__main__":
    unittest.main()
