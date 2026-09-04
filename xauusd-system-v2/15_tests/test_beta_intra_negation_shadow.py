from __future__ import annotations

import unittest

from xauusd_v2.beta_intra_negation_shadow import (
    BetaIntraDirection,
    BetaIntraEMComponents,
    beta_negation_has_hcs_context,
    evaluate_beta_intra_negating_manipulation,
)


class BetaIntraNegationShadowTests(unittest.TestCase):
    def test_latest_bull_plus_opposite_bear_em_is_detected(self) -> None:
        result = evaluate_beta_intra_negating_manipulation(
            last_valid_direction=BetaIntraDirection.BULL,
            last_valid_broken=False,
            candidate_direction=BetaIntraDirection.BEAR,
            components=BetaIntraEMComponents(third=True),
            candidate_confirmed=True,
        )
        self.assertTrue(result.detected)
        self.assertEqual(result.direction, BetaIntraDirection.BEAR)
        self.assertTrue(result.confirmed)
        self.assertFalse(result.forming)
        self.assertFalse(result.strategy_semantics_certified)

    def test_latest_bear_plus_opposite_bull_em_is_detected(self) -> None:
        result = evaluate_beta_intra_negating_manipulation(
            last_valid_direction=BetaIntraDirection.BEAR,
            last_valid_broken=False,
            candidate_direction=BetaIntraDirection.BULL,
            components=BetaIntraEMComponents(laol=True),
            candidate_confirmed=True,
        )
        self.assertTrue(result.detected)
        self.assertEqual(result.direction, BetaIntraDirection.BULL)

    def test_same_direction_candidate_is_rejected(self) -> None:
        result = evaluate_beta_intra_negating_manipulation(
            last_valid_direction=BetaIntraDirection.BULL,
            last_valid_broken=False,
            candidate_direction=BetaIntraDirection.BULL,
            components=BetaIntraEMComponents(hcs=True),
            candidate_confirmed=True,
        )
        self.assertFalse(result.detected)

    def test_broken_last_valid_structure_is_rejected(self) -> None:
        result = evaluate_beta_intra_negating_manipulation(
            last_valid_direction=BetaIntraDirection.BULL,
            last_valid_broken=True,
            candidate_direction=BetaIntraDirection.BEAR,
            components=BetaIntraEMComponents(hcs=True),
            candidate_confirmed=True,
        )
        self.assertFalse(result.detected)

    def test_no_em_component_is_rejected(self) -> None:
        result = evaluate_beta_intra_negating_manipulation(
            last_valid_direction=BetaIntraDirection.BEAR,
            last_valid_broken=False,
            candidate_direction=BetaIntraDirection.BULL,
            components=BetaIntraEMComponents(),
            candidate_confirmed=True,
        )
        self.assertFalse(result.detected)

    def test_unconfirmed_opposite_em_is_forming(self) -> None:
        result = evaluate_beta_intra_negating_manipulation(
            last_valid_direction=BetaIntraDirection.BULL,
            last_valid_broken=False,
            candidate_direction=BetaIntraDirection.BEAR,
            components=BetaIntraEMComponents(tbe=True),
            candidate_confirmed=False,
        )
        self.assertTrue(result.detected)
        self.assertTrue(result.forming)
        self.assertFalse(result.confirmed)

    def test_hcs_component_is_preserved(self) -> None:
        result = evaluate_beta_intra_negating_manipulation(
            last_valid_direction=BetaIntraDirection.BULL,
            last_valid_broken=False,
            candidate_direction=BetaIntraDirection.BEAR,
            components=BetaIntraEMComponents(hcs_forming=True),
            candidate_confirmed=False,
        )
        self.assertTrue(result.detected)
        self.assertTrue(result.contains_hcs_component)

    def test_hcs_context_true_from_bear_hcs_retest(self) -> None:
        self.assertTrue(
            beta_negation_has_hcs_context(
                bear_hcs_retesting=True,
                bull_hcs_retesting=False,
                same_direction_em_form_found=False,
                negating_pattern_contains_hcs=False,
            )
        )

    def test_hcs_context_true_from_bull_hcs_retest(self) -> None:
        self.assertTrue(
            beta_negation_has_hcs_context(
                bear_hcs_retesting=False,
                bull_hcs_retesting=True,
                same_direction_em_form_found=False,
                negating_pattern_contains_hcs=False,
            )
        )

    def test_hcs_context_true_from_negating_hcs_pattern_with_em_form(self) -> None:
        self.assertTrue(
            beta_negation_has_hcs_context(
                bear_hcs_retesting=False,
                bull_hcs_retesting=False,
                same_direction_em_form_found=True,
                negating_pattern_contains_hcs=True,
            )
        )

    def test_hcs_context_false_without_required_hcs_relation(self) -> None:
        self.assertFalse(
            beta_negation_has_hcs_context(
                bear_hcs_retesting=False,
                bull_hcs_retesting=False,
                same_direction_em_form_found=True,
                negating_pattern_contains_hcs=False,
            )
        )


if __name__ == "__main__":
    unittest.main()
