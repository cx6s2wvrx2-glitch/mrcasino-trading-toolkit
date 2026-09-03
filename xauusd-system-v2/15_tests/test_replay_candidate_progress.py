from __future__ import annotations

import unittest

from xauusd_v2.replay_candidate_registry import (
    ReplayCandidateState,
    replay_candidates_by_id,
)


class ReplayCandidateProgressTests(unittest.TestCase):
    def test_rc001_remains_timestamp_blocked_semantic_gold_standard(self) -> None:
        candidate = replay_candidates_by_id()["RC-001"]
        self.assertEqual(candidate.state, ReplayCandidateState.TIMESTAMP_BLOCKED)
        self.assertIn("R-143", candidate.sequence_evidence)

    def test_rc003_raw_data_blocker_is_closed_but_timestamps_are_not(self) -> None:
        candidate = replay_candidates_by_id()["RC-003"]
        self.assertEqual(candidate.state, ReplayCandidateState.TIMESTAMP_BLOCKED)
        self.assertIn("immutable Exclusive Markets M1 replay slice", candidate.sequence_evidence)
        self.assertIn("Raw broker history is no longer the blocker", candidate.blocker or "")
        self.assertIn("capture/stage", candidate.blocker or "")


if __name__ == "__main__":
    unittest.main()
