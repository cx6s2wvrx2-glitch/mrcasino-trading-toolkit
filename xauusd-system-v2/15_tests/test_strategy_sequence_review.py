from __future__ import annotations

import unittest

from xauusd_v2.strategy_evidence_sequence import EvidenceState, StrategyEvidenceRecord, StrategyEvidenceStage
from xauusd_v2.strategy_sequence_review import render_strategy_sequence_review


class StrategySequenceReviewTests(unittest.TestCase):
    def test_review_renders_observed_missing_and_blocked_states(self) -> None:
        text = render_strategy_sequence_review(
            [
                StrategyEvidenceRecord(
                    stage=StrategyEvidenceStage.DIRECTIONAL_CONTEXT,
                    state=EvidenceState.OBSERVED,
                    evidence_ref="fixture:direction",
                    timeframe_minutes=15,
                    event_time="2023-03-30T12:00:00Z",
                ),
                StrategyEvidenceRecord(
                    stage=StrategyEvidenceStage.LIQUIDITY_CALCULATION,
                    state=EvidenceState.MISSING,
                    note="active LAOL not resolved",
                ),
                StrategyEvidenceRecord(
                    stage=StrategyEvidenceStage.POI_ZONE_CONTEXT,
                    state=EvidenceState.BLOCKED,
                    note="source boundary unresolved",
                ),
            ]
        )

        self.assertIn("[ΠΑΡΑΤΗΡΗΘΗΚΕ] Κατεύθυνση / top-down context", text)
        self.assertIn("TF=15m", text)
        self.assertIn("evidence=fixture:direction", text)
        self.assertIn("[ΛΕΙΠΕΙ] Liquidity calculation", text)
        self.assertIn("[ΜΠΛΟΚΑΡΙΣΜΕΝΟ] POI / zone context", text)

    def test_absent_stage_is_rendered_fail_closed(self) -> None:
        text = render_strategy_sequence_review([])
        self.assertIn("δεν έχει δοθεί evidence record", text)
        self.assertIn("NOT STRATEGY-CERTIFIED", text)

    def test_review_preserves_source_reference(self) -> None:
        text = render_strategy_sequence_review(
            [
                StrategyEvidenceRecord(
                    stage=StrategyEvidenceStage.HCS_ZONE_REACTION,
                    state=EvidenceState.OBSERVED,
                    source_ref="Reflection:R-143",
                )
            ]
        )
        self.assertIn("source=Reflection:R-143", text)


if __name__ == "__main__":
    unittest.main()
