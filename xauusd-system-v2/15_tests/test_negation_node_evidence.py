from __future__ import annotations

import unittest

from xauusd_v2.hcs_semantic import HCSNodeType
from xauusd_v2.negation_node_evidence import (
    NegationEvidenceKind,
    beta_self_negation_together_evidence,
    hcs_node_from_negation_result,
)
from xauusd_v2.negation_semantic import (
    Direction,
    ManipulationType,
    NegationState,
    evaluate_negation,
)


class NegationNodeEvidenceTests(unittest.TestCase):
    def test_confirmed_ordinary_fu_negation_is_hcs_fu_negation_node(self) -> None:
        semantic = evaluate_negation(
            original_direction=Direction.BULLISH,
            original_type=ManipulationType.FU,
            candle_offset=1,
            candidate_direction=Direction.BEARISH,
            candidate_complete_fu=True,
        )
        evidence = hcs_node_from_negation_result(
            result=semantic,
            original_type=ManipulationType.FU,
            raw_negation_semantics_certified=True,
        )

        self.assertEqual(evidence.kind, NegationEvidenceKind.ORDINARY_FU_NEGATION)
        self.assertEqual(evidence.hcs_node_type, HCSNodeType.FU_NEGATION)
        self.assertTrue(evidence.hcs_node_label_resolved)
        self.assertTrue(evidence.raw_negation_semantics_certified)

    def test_uncertified_ordinary_fu_negation_keeps_node_label_but_not_certification(self) -> None:
        semantic = evaluate_negation(
            original_direction=Direction.BEARISH,
            original_type=ManipulationType.FU,
            candle_offset=2,
            candidate_direction=Direction.BULLISH,
            candidate_complete_fu=True,
        )
        evidence = hcs_node_from_negation_result(
            result=semantic,
            original_type=ManipulationType.FU,
            raw_negation_semantics_certified=False,
        )

        self.assertEqual(evidence.hcs_node_type, HCSNodeType.FU_NEGATION)
        self.assertFalse(evidence.raw_negation_semantics_certified)

    def test_x3_negation_is_not_silently_relabelled_as_fu_negation_hcs_node(self) -> None:
        semantic = evaluate_negation(
            original_direction=Direction.BULLISH,
            original_type=ManipulationType.X3,
            candle_offset=1,
            candidate_direction=Direction.BEARISH,
            candidate_complete_fu=False,
        )
        self.assertEqual(semantic.state, NegationState.CONFIRMED)

        evidence = hcs_node_from_negation_result(
            result=semantic,
            original_type=ManipulationType.X3,
            raw_negation_semantics_certified=True,
        )

        self.assertEqual(evidence.kind, NegationEvidenceKind.X3_NEGATION)
        self.assertIsNone(evidence.hcs_node_type)
        self.assertFalse(evidence.hcs_node_label_resolved)

    def test_non_confirmed_negation_has_no_hcs_node(self) -> None:
        semantic = evaluate_negation(
            original_direction=Direction.BULLISH,
            original_type=ManipulationType.FU,
            candle_offset=1,
            candidate_direction=Direction.BULLISH,
            candidate_complete_fu=True,
        )
        evidence = hcs_node_from_negation_result(
            result=semantic,
            original_type=ManipulationType.FU,
            raw_negation_semantics_certified=True,
        )

        self.assertEqual(evidence.kind, NegationEvidenceKind.NOT_CONFIRMED)
        self.assertIsNone(evidence.hcs_node_type)
        self.assertFalse(evidence.raw_negation_semantics_certified)

    def test_beta_self_negation_together_is_not_ordinary_fu_negation(self) -> None:
        evidence = beta_self_negation_together_evidence(observed=True)
        self.assertEqual(evidence.kind, NegationEvidenceKind.BETA_SELF_NEGATION_TOGETHER)
        self.assertIsNone(evidence.hcs_node_type)
        self.assertFalse(evidence.hcs_node_label_resolved)
        self.assertFalse(evidence.raw_negation_semantics_certified)


if __name__ == "__main__":
    unittest.main()
