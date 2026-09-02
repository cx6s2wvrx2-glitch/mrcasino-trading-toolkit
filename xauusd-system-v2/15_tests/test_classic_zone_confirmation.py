from __future__ import annotations

import unittest

from xauusd_v2.classic_zone_confirmation import ClassicZoneState, evaluate_classic_zone_confirmation


class ClassicZoneConfirmationTests(unittest.TestCase):
    def test_without_any_first_reaction_zone_is_potential_not_confirmed(self) -> None:
        result = evaluate_classic_zone_confirmation(
            first_same_tf_reaction=False,
            manipulated_lower_tf_reaction=False,
        )
        self.assertEqual(result.state, ClassicZoneState.POTENTIAL_NOT_CONFIRMED)
        self.assertFalse(result.confirmed_for_same_tf_moves)

    def test_first_same_tf_reaction_confirms_zone_for_same_tf_moves(self) -> None:
        result = evaluate_classic_zone_confirmation(
            first_same_tf_reaction=True,
            manipulated_lower_tf_reaction=False,
        )
        self.assertEqual(result.state, ClassicZoneState.CONFIRMED_SAME_TF)
        self.assertTrue(result.confirmed_for_same_tf_moves)

    def test_manipulated_ltf_reaction_without_same_tf_confirmation_is_zone_of_manipulation(self) -> None:
        result = evaluate_classic_zone_confirmation(
            first_same_tf_reaction=False,
            manipulated_lower_tf_reaction=True,
        )
        self.assertEqual(result.state, ClassicZoneState.ZONE_OF_MANIPULATION)
        self.assertFalse(result.confirmed_for_same_tf_moves)

    def test_same_tf_confirmation_takes_precedence_when_both_reactions_exist(self) -> None:
        result = evaluate_classic_zone_confirmation(
            first_same_tf_reaction=True,
            manipulated_lower_tf_reaction=True,
        )
        self.assertEqual(result.state, ClassicZoneState.CONFIRMED_SAME_TF)

    def test_missing_same_tf_reaction_evidence_fails_closed(self) -> None:
        result = evaluate_classic_zone_confirmation(
            first_same_tf_reaction=None,
            manipulated_lower_tf_reaction=False,
        )
        self.assertEqual(result.state, ClassicZoneState.NOT_CERTIFIED)

    def test_missing_ltf_reaction_evidence_fails_closed(self) -> None:
        result = evaluate_classic_zone_confirmation(
            first_same_tf_reaction=False,
            manipulated_lower_tf_reaction=None,
        )
        self.assertEqual(result.state, ClassicZoneState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
