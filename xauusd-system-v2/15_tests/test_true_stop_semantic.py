from __future__ import annotations

import unittest

from xauusd_v2.true_stop_semantic import (
    LTFTrigger,
    TrueStopEntryState,
    TrueStopState,
    evaluate_true_stop_entry,
    evaluate_true_stop_main_poi,
    evaluate_true_stop_respect,
)


class TrueStopSemanticTests(unittest.TestCase):
    def test_aligned_10m_plus_factors_create_main_poi_candidate(self) -> None:
        result = evaluate_true_stop_main_poi(
            all_required_10m_plus_tfs_factors_aligned=True,
            ten_min_plus_hcs_or_negation_manipulation_present=True,
        )
        self.assertEqual(result.state, TrueStopState.MAIN_POI_CANDIDATE)

    def test_missing_manipulation_is_not_true_stop(self) -> None:
        result = evaluate_true_stop_main_poi(
            all_required_10m_plus_tfs_factors_aligned=True,
            ten_min_plus_hcs_or_negation_manipulation_present=False,
        )
        self.assertEqual(result.state, TrueStopState.NOT_TRUE_STOP)

    def test_missing_alignment_evidence_fails_closed(self) -> None:
        result = evaluate_true_stop_main_poi(
            all_required_10m_plus_tfs_factors_aligned=None,
            ten_min_plus_hcs_or_negation_manipulation_present=True,
        )
        self.assertEqual(result.state, TrueStopState.NOT_CERTIFIED)

    def test_confirmed_main_poi_can_be_respected(self) -> None:
        result = evaluate_true_stop_respect(main_poi_confirmed=True, price_respected_poi=True)
        self.assertEqual(result.state, TrueStopState.RESPECTED)

    def test_unrespected_main_poi_is_not_respected_true_stop(self) -> None:
        result = evaluate_true_stop_respect(main_poi_confirmed=True, price_respected_poi=False)
        self.assertEqual(result.state, TrueStopState.NOT_TRUE_STOP)

    def test_hcs_entry_requires_respect_and_liquidity_resolution(self) -> None:
        result = evaluate_true_stop_entry(
            true_stop_respected=True,
            ltf_trigger=LTFTrigger.HCS,
            final_liquidity_calculation_resolved=True,
        )
        self.assertEqual(result.state, TrueStopEntryState.ENTRY_CANDIDATE)

    def test_negation_trigger_is_equally_eligible_semantically(self) -> None:
        result = evaluate_true_stop_entry(
            true_stop_respected=True,
            ltf_trigger=LTFTrigger.NEGATION,
            final_liquidity_calculation_resolved=True,
        )
        self.assertEqual(result.state, TrueStopEntryState.ENTRY_CANDIDATE)

    def test_unresolved_liquidity_forces_wait(self) -> None:
        result = evaluate_true_stop_entry(
            true_stop_respected=True,
            ltf_trigger=LTFTrigger.HCS,
            final_liquidity_calculation_resolved=False,
        )
        self.assertEqual(result.state, TrueStopEntryState.WAIT)

    def test_missing_trigger_fails_closed(self) -> None:
        result = evaluate_true_stop_entry(
            true_stop_respected=True,
            ltf_trigger=None,
            final_liquidity_calculation_resolved=True,
        )
        self.assertEqual(result.state, TrueStopEntryState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
