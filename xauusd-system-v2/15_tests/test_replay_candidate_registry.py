from __future__ import annotations

import unittest

from xauusd_v2.replay_candidate_registry import (
    ReplayCandidateState,
    replay_candidate_counts,
    replay_candidates_by_id,
)


class ReplayCandidateRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = replay_candidates_by_id()

    def test_three_source_backed_candidates_are_registered(self) -> None:
        self.assertEqual(set(self.registry), {"RC-001", "RC-002", "RC-003"})

    def test_no_candidate_is_falsely_ready(self) -> None:
        counts = replay_candidate_counts()
        self.assertEqual(counts[ReplayCandidateState.READY], 0)
        self.assertEqual(counts[ReplayCandidateState.TIMESTAMP_BLOCKED], 2)
        self.assertEqual(counts[ReplayCandidateState.RAW_DATA_BLOCKED], 0)
        self.assertEqual(counts[ReplayCandidateState.CONTEXT_ONLY], 1)

    def test_every_non_ready_candidate_names_a_blocker(self) -> None:
        for candidate in self.registry.values():
            self.assertIsNot(candidate.state, ReplayCandidateState.READY)
            self.assertTrue(candidate.blocker and candidate.blocker.strip())

    def test_reflection_sequence_does_not_infer_chart_timestamps(self) -> None:
        candidate = self.registry["RC-001"]
        self.assertEqual(candidate.state, ReplayCandidateState.TIMESTAMP_BLOCKED)
        self.assertIn("do not infer", (candidate.blocker or "").lower())

    def test_topdown_raw_alignment_is_complete_but_stage_timestamps_remain_blocked(self) -> None:
        candidate = self.registry["RC-003"]
        self.assertEqual(candidate.state, ReplayCandidateState.TIMESTAMP_BLOCKED)
        self.assertIn("Raw broker history is no longer the blocker", candidate.blocker or "")
        self.assertIn("capture/stage", candidate.blocker or "")
        self.assertIn("Do not infer", candidate.blocker or "")


if __name__ == "__main__":
    unittest.main()
