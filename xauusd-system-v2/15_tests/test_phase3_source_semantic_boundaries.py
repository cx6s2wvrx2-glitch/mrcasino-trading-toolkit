from __future__ import annotations

import unittest

from xauusd_v2.phase3_source_semantic_boundaries import (
    LAOLSourceEvent,
    SourceBoundaryState,
    TFSSourceEvidence,
    evaluate_r143_laol_met_source,
    evaluate_tfs_source_at_decision_time,
)


class Phase3SourceSemanticBoundaryTests(unittest.TestCase):
    def test_liquidity_left_behind_cannot_be_promoted_to_laol_met(self) -> None:
        result = evaluate_r143_laol_met_source(event=LAOLSourceEvent.OTHER_LIQUIDITY)
        self.assertEqual(result.state, SourceBoundaryState.BLOCKED)

    def test_laol_respected_is_not_silently_laol_met(self) -> None:
        result = evaluate_r143_laol_met_source(event=LAOLSourceEvent.RESPECTED)
        self.assertEqual(result.state, SourceBoundaryState.BLOCKED)

    def test_laol_taken_is_not_silently_laol_met(self) -> None:
        result = evaluate_r143_laol_met_source(event=LAOLSourceEvent.TAKEN)
        self.assertEqual(result.state, SourceBoundaryState.BLOCKED)

    def test_only_explicit_r143_met_authority_observes_stage(self) -> None:
        result = evaluate_r143_laol_met_source(event=LAOLSourceEvent.R143_MET_EXPLICIT)
        self.assertEqual(result.state, SourceBoundaryState.OBSERVED)

    def test_timeframe_strength_context_does_not_establish_tfs(self) -> None:
        result = evaluate_tfs_source_at_decision_time(
            evidence=TFSSourceEvidence.TIMEFRAME_STRENGTH_CONTEXT,
            evidence_available_at="2023-03-31T12:34:00Z",
            decision_time="2023-03-31T12:34:00Z",
        )
        self.assertEqual(result.state, SourceBoundaryState.BLOCKED)

    def test_forming_daily_fu_does_not_establish_tfs(self) -> None:
        result = evaluate_tfs_source_at_decision_time(
            evidence=TFSSourceEvidence.FORMING_FU_BACKING,
            evidence_available_at="2023-03-31T12:34:00Z",
            decision_time="2023-03-31T12:34:00Z",
        )
        self.assertEqual(result.state, SourceBoundaryState.BLOCKED)

    def test_later_4h_close_cannot_retroactively_certify_1986_decision(self) -> None:
        result = evaluate_tfs_source_at_decision_time(
            evidence=TFSSourceEvidence.LATER_CONFIRMED_CLOSE,
            evidence_available_at="2023-03-31T16:00:00Z",
            decision_time="2023-03-31T12:34:00Z",
        )
        self.assertEqual(result.state, SourceBoundaryState.BLOCKED)
        self.assertIn("after the decision time", result.reason)

    def test_confirmed_prevalent_direction_available_by_decision_can_observe_tfs(self) -> None:
        result = evaluate_tfs_source_at_decision_time(
            evidence=TFSSourceEvidence.CONFIRMED_PREVALENT_DIRECTION,
            evidence_available_at="2023-03-31T12:30:00Z",
            decision_time="2023-03-31T12:34:00Z",
        )
        self.assertEqual(result.state, SourceBoundaryState.OBSERVED)

    def test_naive_timestamps_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_tfs_source_at_decision_time(
                evidence=TFSSourceEvidence.CONFIRMED_PREVALENT_DIRECTION,
                evidence_available_at="2023-03-31T12:30:00",
                decision_time="2023-03-31T12:34:00Z",
            )


if __name__ == "__main__":
    unittest.main()
