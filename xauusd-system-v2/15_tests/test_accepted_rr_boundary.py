from __future__ import annotations

import unittest

from xauusd_v2.accepted_rr_boundary import AcceptedRRState, evaluate_accepted_rr


class AcceptedRRBoundaryTests(unittest.TestCase):
    def test_explicit_source_phrase_is_context_only_without_number(self) -> None:
        result = evaluate_accepted_rr(source_concept_explicit=True)
        self.assertEqual(result.state, AcceptedRRState.SOURCE_CONCEPT_ONLY)
        self.assertFalse(result.numeric_threshold_usable)

    def test_arbitrary_numeric_rr_is_blocked(self) -> None:
        result = evaluate_accepted_rr(source_concept_explicit=True, rr_threshold=5.0)
        self.assertEqual(result.state, AcceptedRRState.NOT_CERTIFIED)
        self.assertFalse(result.numeric_threshold_usable)

    def test_future_certified_numeric_definition_is_only_candidate(self) -> None:
        result = evaluate_accepted_rr(
            source_concept_explicit=True,
            rr_threshold=5.0,
            threshold_definition_certified=True,
        )
        self.assertEqual(result.state, AcceptedRRState.NUMERIC_RULE_CANDIDATE)
        self.assertTrue(result.numeric_threshold_usable)

    def test_numeric_rule_cannot_attach_to_unconfirmed_concept(self) -> None:
        result = evaluate_accepted_rr(
            source_concept_explicit=False,
            rr_threshold=5.0,
            threshold_definition_certified=True,
        )
        self.assertEqual(result.state, AcceptedRRState.NOT_CERTIFIED)

    def test_missing_source_evidence_fails_closed(self) -> None:
        result = evaluate_accepted_rr(source_concept_explicit=None)
        self.assertEqual(result.state, AcceptedRRState.NOT_CERTIFIED)

    def test_invalid_rr_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_accepted_rr(source_concept_explicit=True, rr_threshold=0.0)


if __name__ == "__main__":
    unittest.main()
