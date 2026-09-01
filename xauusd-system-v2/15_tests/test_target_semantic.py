from __future__ import annotations

import unittest

from xauusd_v2.target_semantic import TargetClass, TargetState, evaluate_target


class TargetSemanticTests(unittest.TestCase):
    def test_core_is_minimum_target_after_poi_respect(self) -> None:
        result = evaluate_target(
            target_class=TargetClass.CORE_BREAKOUT_LIQUIDITY,
            opposite_laol_or_poi_respected=True,
            target_level_identified=True,
        )
        self.assertEqual(result.state, TargetState.MINIMUM_TARGET_ELIGIBLE)

    def test_major_is_context_target_candidate(self) -> None:
        result = evaluate_target(
            target_class=TargetClass.MAJOR_LIQUIDITY,
            opposite_laol_or_poi_respected=True,
            target_level_identified=True,
        )
        self.assertEqual(result.state, TargetState.CONTEXT_TARGET_CANDIDATE)

    def test_opposite_laol_is_context_target_candidate(self) -> None:
        result = evaluate_target(
            target_class=TargetClass.OPPOSITE_LAOL,
            opposite_laol_or_poi_respected=True,
            target_level_identified=True,
        )
        self.assertEqual(result.state, TargetState.CONTEXT_TARGET_CANDIDATE)

    def test_target_before_poi_respect_is_not_eligible(self) -> None:
        result = evaluate_target(
            target_class=TargetClass.CORE_BREAKOUT_LIQUIDITY,
            opposite_laol_or_poi_respected=False,
            target_level_identified=True,
        )
        self.assertEqual(result.state, TargetState.NOT_ELIGIBLE)

    def test_trail_level_without_selection_rule_fails_closed(self) -> None:
        result = evaluate_target(
            target_class=TargetClass.TRAIL_LEVEL,
            opposite_laol_or_poi_respected=True,
            target_level_identified=True,
            trail_selection_certified=None,
        )
        self.assertEqual(result.state, TargetState.NOT_CERTIFIED)

    def test_certified_trail_level_can_be_context_candidate(self) -> None:
        result = evaluate_target(
            target_class=TargetClass.TRAIL_LEVEL,
            opposite_laol_or_poi_respected=True,
            target_level_identified=True,
            trail_selection_certified=True,
        )
        self.assertEqual(result.state, TargetState.CONTEXT_TARGET_CANDIDATE)

    def test_missing_target_level_evidence_fails_closed(self) -> None:
        result = evaluate_target(
            target_class=TargetClass.MAJOR_LIQUIDITY,
            opposite_laol_or_poi_respected=True,
            target_level_identified=None,
        )
        self.assertEqual(result.state, TargetState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
