from __future__ import annotations

import unittest

from xauusd_v2.backtest_sequence import (
    BacktestStage,
    SequenceState,
    evaluate_r143_sequence,
)


class BacktestSequenceTests(unittest.TestCase):
    def test_complete_sequence_reaches_complete_candidate(self) -> None:
        result = evaluate_r143_sequence(
            hcs_zone_reaction=True,
            tfs_confirmed=True,
            laol_met=True,
            true_stop_respected=True,
            ten_min_true_stop_established=True,
            targets_and_timing_defined=True,
        )
        self.assertEqual(result.state, SequenceState.COMPLETE_CANDIDATE)

    def test_sequence_can_stop_cleanly_after_tfs(self) -> None:
        result = evaluate_r143_sequence(
            hcs_zone_reaction=True,
            tfs_confirmed=True,
            laol_met=False,
            true_stop_respected=False,
            ten_min_true_stop_established=False,
            targets_and_timing_defined=False,
        )
        self.assertEqual(result.state, SequenceState.IN_PROGRESS)
        self.assertEqual(result.highest_completed_stage, BacktestStage.TFS)
        self.assertEqual(result.next_required_stage, BacktestStage.LAOL_MET)

    def test_later_stage_cannot_skip_laol(self) -> None:
        result = evaluate_r143_sequence(
            hcs_zone_reaction=True,
            tfs_confirmed=True,
            laol_met=False,
            true_stop_respected=True,
            ten_min_true_stop_established=False,
            targets_and_timing_defined=False,
        )
        self.assertEqual(result.state, SequenceState.INVALID_ORDER)
        self.assertEqual(result.next_required_stage, BacktestStage.LAOL_MET)

    def test_tfs_cannot_exist_in_sequence_before_zone_reaction(self) -> None:
        result = evaluate_r143_sequence(
            hcs_zone_reaction=False,
            tfs_confirmed=True,
            laol_met=False,
            true_stop_respected=False,
            ten_min_true_stop_established=False,
            targets_and_timing_defined=False,
        )
        self.assertEqual(result.state, SequenceState.INVALID_ORDER)
        self.assertEqual(result.next_required_stage, BacktestStage.HCS_ZONE_REACTION)

    def test_missing_evidence_fails_closed(self) -> None:
        result = evaluate_r143_sequence(
            hcs_zone_reaction=True,
            tfs_confirmed=None,
            laol_met=False,
            true_stop_respected=False,
            ten_min_true_stop_established=False,
            targets_and_timing_defined=False,
        )
        self.assertEqual(result.state, SequenceState.NOT_CERTIFIED)
        self.assertEqual(result.next_required_stage, BacktestStage.TFS)

    def test_targets_cannot_appear_before_10m_ts_established(self) -> None:
        result = evaluate_r143_sequence(
            hcs_zone_reaction=True,
            tfs_confirmed=True,
            laol_met=True,
            true_stop_respected=True,
            ten_min_true_stop_established=False,
            targets_and_timing_defined=True,
        )
        self.assertEqual(result.state, SequenceState.INVALID_ORDER)
        self.assertEqual(result.next_required_stage, BacktestStage.TEN_MIN_TRUE_STOP_ESTABLISHED)


if __name__ == "__main__":
    unittest.main()
