from __future__ import annotations

import unittest

from xauusd_v2.replay_candidate_readiness import (
    ReplayCandidateReadinessState,
    evaluate_replay_candidate_readiness,
)
from xauusd_v2.replay_candidate_registry import ReplayCandidate, ReplayCandidateState
from xauusd_v2.source_chart_alignment import SourceChartAlignmentResult, SourceChartAlignmentState


class ReplayCandidateReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidate = ReplayCandidate(
            candidate_id="RC-X",
            source_id="source-1",
            locator="source.zip#sequence:2023-11-01",
            state=ReplayCandidateState.RAW_DATA_BLOCKED,
            sequence_evidence="primary sequence",
            blocker="raw alignment missing",
        )
        self.aligned = SourceChartAlignmentResult(
            state=SourceChartAlignmentState.ALIGNED_CANDIDATE,
            source_id="source-1",
            source_locator="source.zip#sequence:2023-11-01",
            snapshot_id="sha256:abc",
            aligned=True,
            reason="aligned",
        )

    def test_alignment_alone_never_makes_replay_ready(self) -> None:
        result = evaluate_replay_candidate_readiness(
            candidate=self.candidate,
            alignment=self.aligned,
            stage_timestamps_certified=False,
        )
        self.assertEqual(result.state, ReplayCandidateReadinessState.BLOCKED_STAGE_TIMESTAMPS)
        self.assertFalse(result.replay_ready)

    def test_missing_stage_timestamp_evidence_fails_closed(self) -> None:
        result = evaluate_replay_candidate_readiness(
            candidate=self.candidate,
            alignment=self.aligned,
            stage_timestamps_certified=None,
        )
        self.assertEqual(result.state, ReplayCandidateReadinessState.BLOCKED_STAGE_TIMESTAMPS)

    def test_unaligned_source_is_blocked_even_with_stage_timestamps(self) -> None:
        unaligned = SourceChartAlignmentResult(
            state=SourceChartAlignmentState.BROKER_MISMATCH,
            source_id=self.aligned.source_id,
            source_locator=self.aligned.source_locator,
            snapshot_id=self.aligned.snapshot_id,
            aligned=False,
            reason="mismatch",
        )
        result = evaluate_replay_candidate_readiness(
            candidate=self.candidate,
            alignment=unaligned,
            stage_timestamps_certified=True,
        )
        self.assertEqual(result.state, ReplayCandidateReadinessState.BLOCKED_ALIGNMENT)

    def test_alignment_from_other_source_cannot_unlock_candidate(self) -> None:
        wrong = SourceChartAlignmentResult(
            state=SourceChartAlignmentState.ALIGNED_CANDIDATE,
            source_id="other-source",
            source_locator=self.aligned.source_locator,
            snapshot_id=self.aligned.snapshot_id,
            aligned=True,
            reason="aligned elsewhere",
        )
        result = evaluate_replay_candidate_readiness(
            candidate=self.candidate,
            alignment=wrong,
            stage_timestamps_certified=True,
        )
        self.assertEqual(result.state, ReplayCandidateReadinessState.BLOCKED_ALIGNMENT)

    def test_context_only_source_cannot_be_upgraded_by_alignment(self) -> None:
        context_only = ReplayCandidate(
            candidate_id="RC-CONTEXT",
            source_id="source-1",
            locator=self.candidate.locator,
            state=ReplayCandidateState.CONTEXT_ONLY,
            sequence_evidence="training protocol",
            blocker="not a single session",
        )
        result = evaluate_replay_candidate_readiness(
            candidate=context_only,
            alignment=self.aligned,
            stage_timestamps_certified=True,
        )
        self.assertEqual(result.state, ReplayCandidateReadinessState.BLOCKED_CONTEXT_ONLY)
        self.assertFalse(result.replay_ready)

    def test_both_alignment_and_stage_timestamps_create_replay_candidate_only(self) -> None:
        result = evaluate_replay_candidate_readiness(
            candidate=self.candidate,
            alignment=self.aligned,
            stage_timestamps_certified=True,
        )
        self.assertEqual(result.state, ReplayCandidateReadinessState.READY_CANDIDATE)
        self.assertTrue(result.replay_ready)
        self.assertIn("may enter historical replay", result.reason)


if __name__ == "__main__":
    unittest.main()
