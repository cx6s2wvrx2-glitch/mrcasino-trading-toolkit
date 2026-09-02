from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from xauusd_v2.backtest_sequence import BacktestStage, SequenceState
from xauusd_v2.component_replay import TimedStageConfirmation, replay_r143_at


class ComponentReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.t0 = datetime(2026, 1, 5, 8, 0, tzinfo=UTC)

    def event(self, stage: BacktestStage, minutes: int, *, available_delay: int = 0) -> TimedStageConfirmation:
        occurred = self.t0 + timedelta(minutes=minutes)
        return TimedStageConfirmation(
            stage=stage,
            occurred_at=occurred,
            available_at=occurred + timedelta(minutes=available_delay),
            source_ref=f"fixture:{stage.name}",
        )

    def ordered_sequence(self) -> tuple[TimedStageConfirmation, ...]:
        return tuple(self.event(stage, index * 10) for index, stage in enumerate(BacktestStage, start=1))

    def test_after_first_stage_sequence_waits_for_tfs(self) -> None:
        events = self.ordered_sequence()
        report = replay_r143_at(events, evaluation_time=self.t0 + timedelta(minutes=15))
        self.assertEqual(report.sequence.state, SequenceState.IN_PROGRESS)
        self.assertEqual(report.sequence.next_required_stage, BacktestStage.TFS)
        self.assertEqual(len(report.visible_confirmations), 1)
        self.assertEqual(report.future_confirmations_hidden, 5)

    def test_future_confirmations_are_not_leaked(self) -> None:
        events = self.ordered_sequence()
        report = replay_r143_at(events, evaluation_time=self.t0 + timedelta(minutes=35))
        self.assertEqual(report.sequence.highest_completed_stage, BacktestStage.LAOL_MET)
        self.assertEqual(report.sequence.next_required_stage, BacktestStage.TRUE_STOP_RESPECTED)
        self.assertFalse(report.lookahead_used)

    def test_complete_ordered_history_reaches_complete_candidate(self) -> None:
        events = self.ordered_sequence()
        report = replay_r143_at(events, evaluation_time=self.t0 + timedelta(minutes=90))
        self.assertEqual(report.sequence.state, SequenceState.COMPLETE_CANDIDATE)
        self.assertEqual(report.future_confirmations_hidden, 0)
        self.assertFalse(report.lookahead_used)

    def test_stage_that_occurs_out_of_source_order_is_invalid(self) -> None:
        events = (
            self.event(BacktestStage.HCS_ZONE_REACTION, 10),
            self.event(BacktestStage.TFS, 30),
            self.event(BacktestStage.LAOL_MET, 20),
        )
        report = replay_r143_at(events, evaluation_time=self.t0 + timedelta(minutes=60))
        self.assertEqual(report.sequence.state, SequenceState.INVALID_ORDER)
        self.assertIn("out of source order", report.sequence.reason)

    def test_evidence_available_only_after_candle_close_stays_hidden(self) -> None:
        event = self.event(BacktestStage.HCS_ZONE_REACTION, 10, available_delay=10)
        before_close = replay_r143_at((event,), evaluation_time=self.t0 + timedelta(minutes=15))
        after_close = replay_r143_at((event,), evaluation_time=self.t0 + timedelta(minutes=21))
        self.assertIsNone(before_close.sequence.highest_completed_stage)
        self.assertEqual(after_close.sequence.highest_completed_stage, BacktestStage.HCS_ZONE_REACTION)

    def test_naive_evaluation_time_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            replay_r143_at((), evaluation_time=datetime(2026, 1, 5, 8, 0))

    def test_naive_event_timestamp_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            TimedStageConfirmation(
                stage=BacktestStage.TFS,
                occurred_at=datetime(2026, 1, 5, 8, 0),
                available_at=datetime(2026, 1, 5, 8, 1),
                source_ref="fixture",
            )

    def test_evidence_cannot_be_available_before_occurrence(self) -> None:
        with self.assertRaises(ValueError):
            TimedStageConfirmation(
                stage=BacktestStage.TFS,
                occurred_at=self.t0 + timedelta(minutes=10),
                available_at=self.t0 + timedelta(minutes=9),
                source_ref="fixture",
            )

    def test_source_ref_is_required(self) -> None:
        with self.assertRaises(ValueError):
            TimedStageConfirmation(
                stage=BacktestStage.TFS,
                occurred_at=self.t0,
                available_at=self.t0,
                source_ref=" ",
            )


if __name__ == "__main__":
    unittest.main()
