from __future__ import annotations

import unittest

from xauusd_v2.hcs_semantic import (
    HCSNodeType,
    HCSRetestState,
    HCSState,
    HCSStrength,
    evaluate_hcs,
)


class HCSSemanticTests(unittest.TestCase):
    def test_exact_strong_plus_strong_is_explicit_strongest(self) -> None:
        result = evaluate_hcs(
            first_node=HCSNodeType.STRONG_FU,
            second_node=HCSNodeType.STRONG_FU,
            retest_state=HCSRetestState.EXACT_WICK,
        )
        self.assertEqual(result.state, HCSState.CONFIRMED)
        self.assertEqual(result.strength, HCSStrength.EXPLICIT_STRONGEST)

    def test_att_plus_negation_is_explicit_weaker_form(self) -> None:
        result = evaluate_hcs(
            first_node=HCSNodeType.ATTEMPTED_FU,
            second_node=HCSNodeType.FU_NEGATION,
            retest_state=HCSRetestState.EXACT_WICK,
        )
        self.assertEqual(result.state, HCSState.CONFIRMED)
        self.assertEqual(result.strength, HCSStrength.EXPLICIT_WEAKER)

    def test_other_valid_combinations_remain_unranked_not_invented(self) -> None:
        result = evaluate_hcs(
            first_node=HCSNodeType.STRONG_FU,
            second_node=HCSNodeType.FU_NEGATION,
            retest_state=HCSRetestState.EXACT_WICK,
        )
        self.assertEqual(result.state, HCSState.CONFIRMED)
        self.assertEqual(result.strength, HCSStrength.UNRANKED)

    def test_source_confirmed_near_enough_can_count(self) -> None:
        result = evaluate_hcs(
            first_node=HCSNodeType.STRONG_FU,
            second_node=HCSNodeType.ATTEMPTED_FU,
            retest_state=HCSRetestState.NEAR_ENOUGH_SOURCE_CONFIRMED,
        )
        self.assertEqual(result.state, HCSState.CONFIRMED)

    def test_unknown_retest_distance_fails_closed(self) -> None:
        result = evaluate_hcs(
            first_node=HCSNodeType.STRONG_FU,
            second_node=HCSNodeType.ATTEMPTED_FU,
            retest_state=HCSRetestState.UNKNOWN,
        )
        self.assertEqual(result.state, HCSState.NOT_CERTIFIED)
        self.assertIsNone(result.strength)

    def test_no_retest_is_not_hcs(self) -> None:
        result = evaluate_hcs(
            first_node=HCSNodeType.STRONG_FU,
            second_node=HCSNodeType.ATTEMPTED_FU,
            retest_state=HCSRetestState.NO_RETEST,
        )
        self.assertEqual(result.state, HCSState.NOT_HCS)


if __name__ == "__main__":
    unittest.main()
