from __future__ import annotations

import unittest

from xauusd_v2.ltf_execution import (
    LTFExecutionMode,
    LTFExecutionState,
    LTFExecutionTrigger,
    evaluate_r145_ltf_execution,
)


class LTFExecutionTests(unittest.TestCase):
    def test_confirmed_1m_negation_sequence_is_candidate(self) -> None:
        result = evaluate_r145_ltf_execution(
            retail_liquidity_manipulated=True,
            ltf_laol_taken=True,
            trigger=LTFExecutionTrigger.ONE_MIN_NEGATION,
            mode=LTFExecutionMode.CONFIRMED,
            ten_min_ts_established=True,
            ten_min_ts_forming=False,
            full_tfs_factors_present=True,
        )
        self.assertEqual(result.state, LTFExecutionState.ENTRY_CANDIDATE)

    def test_confirmed_3m_hcs_negation_sequence_is_candidate(self) -> None:
        result = evaluate_r145_ltf_execution(
            retail_liquidity_manipulated=True,
            ltf_laol_taken=True,
            trigger=LTFExecutionTrigger.THREE_MIN_HCS_NEGATION,
            mode=LTFExecutionMode.CONFIRMED,
            ten_min_ts_established=True,
            ten_min_ts_forming=False,
            full_tfs_factors_present=True,
        )
        self.assertEqual(result.state, LTFExecutionState.ENTRY_CANDIDATE)

    def test_missing_retail_manipulation_forces_wait(self) -> None:
        result = evaluate_r145_ltf_execution(
            retail_liquidity_manipulated=False,
            ltf_laol_taken=True,
            trigger=LTFExecutionTrigger.ONE_MIN_NEGATION,
            mode=LTFExecutionMode.CONFIRMED,
            ten_min_ts_established=True,
            ten_min_ts_forming=False,
            full_tfs_factors_present=True,
        )
        self.assertEqual(result.state, LTFExecutionState.WAIT)

    def test_missing_laol_taken_forces_wait(self) -> None:
        result = evaluate_r145_ltf_execution(
            retail_liquidity_manipulated=True,
            ltf_laol_taken=False,
            trigger=LTFExecutionTrigger.ONE_MIN_NEGATION,
            mode=LTFExecutionMode.CONFIRMED,
            ten_min_ts_established=True,
            ten_min_ts_forming=False,
            full_tfs_factors_present=True,
        )
        self.assertEqual(result.state, LTFExecutionState.WAIT)

    def test_confirmed_mode_waits_for_10m_ts_establishment(self) -> None:
        result = evaluate_r145_ltf_execution(
            retail_liquidity_manipulated=True,
            ltf_laol_taken=True,
            trigger=LTFExecutionTrigger.ONE_MIN_NEGATION,
            mode=LTFExecutionMode.CONFIRMED,
            ten_min_ts_established=False,
            ten_min_ts_forming=True,
            full_tfs_factors_present=True,
        )
        self.assertEqual(result.state, LTFExecutionState.WAIT)

    def test_aggressive_mode_allows_forming_only_with_full_tfs(self) -> None:
        result = evaluate_r145_ltf_execution(
            retail_liquidity_manipulated=True,
            ltf_laol_taken=True,
            trigger=LTFExecutionTrigger.ONE_MIN_NEGATION,
            mode=LTFExecutionMode.AGGRESSIVE,
            ten_min_ts_established=False,
            ten_min_ts_forming=True,
            full_tfs_factors_present=True,
        )
        self.assertEqual(result.state, LTFExecutionState.ENTRY_CANDIDATE)

    def test_aggressive_mode_without_full_tfs_waits(self) -> None:
        result = evaluate_r145_ltf_execution(
            retail_liquidity_manipulated=True,
            ltf_laol_taken=True,
            trigger=LTFExecutionTrigger.ONE_MIN_NEGATION,
            mode=LTFExecutionMode.AGGRESSIVE,
            ten_min_ts_established=False,
            ten_min_ts_forming=True,
            full_tfs_factors_present=False,
        )
        self.assertEqual(result.state, LTFExecutionState.WAIT)

    def test_missing_trigger_fails_closed(self) -> None:
        result = evaluate_r145_ltf_execution(
            retail_liquidity_manipulated=True,
            ltf_laol_taken=True,
            trigger=None,
            mode=LTFExecutionMode.CONFIRMED,
            ten_min_ts_established=True,
            ten_min_ts_forming=False,
            full_tfs_factors_present=True,
        )
        self.assertEqual(result.state, LTFExecutionState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
