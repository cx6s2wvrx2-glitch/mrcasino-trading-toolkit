from __future__ import annotations

import unittest

from xauusd_v2.phase3_stage_comparison import ComparisonState, StageComparisonResult
from xauusd_v2.phase3_stage_comparison_review import render_source_broker_comparison
from xauusd_v2.strategy_evidence_sequence import EvidenceState, StrategyEvidenceStage


class Phase3StageComparisonReviewTests(unittest.TestCase):
    def test_review_keeps_path_separate_from_semantic_equivalence(self) -> None:
        text = render_source_broker_comparison(
            [
                StageComparisonResult(
                    stage=StrategyEvidenceStage.TRUE_STOP_RESPECTED,
                    source_state=EvidenceState.OBSERVED,
                    broker_semantic_state=EvidenceState.BLOCKED,
                    broker_path_observed=True,
                    reference_feed_aligned=False,
                    comparison_state=ComparisonState.SOURCE_OBSERVED_BROKER_PATH_ONLY,
                    canonical_equivalence_allowed=False,
                    reason="price anchor exists but semantic stage is blocked",
                )
            ]
        )
        self.assertIn("Πηγή: ΠΑΡΑΤΗΡΗΘΗΚΕ", text)
        self.assertIn("Broker semantic: ΜΠΛΟΚΑΡΙΣΜΕΝΟ", text)
        self.assertIn("Broker price/path observation: ΝΑΙ", text)
        self.assertIn("Canonical equivalence allowed: ΟΧΙ", text)
        self.assertIn("Broker path ≠ semantic stage", text)


if __name__ == "__main__":
    unittest.main()
