from __future__ import annotations

import unittest
from datetime import UTC, datetime

from xauusd_v2.backtest_sequence import BacktestSequenceResult, BacktestStage, SequenceState
from xauusd_v2.component_replay import ComponentReplayResult
from xauusd_v2.historical_replay_gate import HistoricalReplayGateState, evaluate_historical_replay_batch


class HistoricalReplayGateTests(unittest.TestCase):
    def result(self, state: SequenceState, *, lookahead: bool = False) -> ComponentReplayResult:
        highest = BacktestStage.TARGETS_AND_TIMING if state is SequenceState.COMPLETE_CANDIDATE else None
        next_stage = BacktestStage.HCS_ZONE_REACTION if state is SequenceState.IN_PROGRESS else None
        return ComponentReplayResult(
            evaluation_time=datetime(2026, 1, 5, tzinfo=UTC),
            sequence=BacktestSequenceResult(state, highest, next_stage, state.value),
            visible_confirmations=(),
            future_confirmations_hidden=0,
            lookahead_used=lookahead,
        )

    def test_complete_and_no_trade_sessions_can_pass_together(self) -> None:
        report = evaluate_historical_replay_batch(
            (
                self.result(SequenceState.COMPLETE_CANDIDATE),
                self.result(SequenceState.IN_PROGRESS),
                self.result(SequenceState.IN_PROGRESS),
            )
        )
        self.assertEqual(report.state, HistoricalReplayGateState.PASS)
        self.assertTrue(report.historical_reproducible)
        self.assertEqual(report.complete_candidates, 1)
        self.assertEqual(report.valid_in_progress, 2)

    def test_invalid_order_fails_batch(self) -> None:
        report = evaluate_historical_replay_batch((self.result(SequenceState.INVALID_ORDER),))
        self.assertEqual(report.state, HistoricalReplayGateState.FAIL)
        self.assertFalse(report.historical_reproducible)

    def test_not_certified_missing_evidence_fails_batch(self) -> None:
        report = evaluate_historical_replay_batch((self.result(SequenceState.NOT_CERTIFIED),))
        self.assertEqual(report.state, HistoricalReplayGateState.FAIL)
        self.assertEqual(report.not_certified, 1)

    def test_any_lookahead_violation_fails_batch(self) -> None:
        report = evaluate_historical_replay_batch(
            (
                self.result(SequenceState.COMPLETE_CANDIDATE),
                self.result(SequenceState.IN_PROGRESS, lookahead=True),
            )
        )
        self.assertEqual(report.state, HistoricalReplayGateState.FAIL)
        self.assertEqual(report.lookahead_violations, 1)

    def test_empty_batch_is_not_a_pass(self) -> None:
        report = evaluate_historical_replay_batch(())
        self.assertEqual(report.state, HistoricalReplayGateState.EMPTY)
        self.assertFalse(report.historical_reproducible)
        self.assertTrue(report.blockers)


if __name__ == "__main__":
    unittest.main()
