from __future__ import annotations

import unittest

from xauusd_v2.backtest_sequence import BacktestStage, SequenceState
from xauusd_v2.ltf_execution import LTFExecutionMode, LTFExecutionState, LTFExecutionTrigger
from xauusd_v2.strategy_evidence_sequence import (
    ContextGateState,
    EvidenceState,
    StrategyEvidenceRecord,
    StrategyEvidenceStage,
    evaluate_pre_entry_context,
    evaluate_r143_evidence,
    evaluate_r145_evidence,
)


def observed(stage: StrategyEvidenceStage) -> StrategyEvidenceRecord:
    return StrategyEvidenceRecord(
        stage=stage,
        state=EvidenceState.OBSERVED,
        evidence_ref=f"fixture:{stage.value}",
    )


def missing(stage: StrategyEvidenceStage) -> StrategyEvidenceRecord:
    return StrategyEvidenceRecord(stage=stage, state=EvidenceState.MISSING)


def blocked(stage: StrategyEvidenceStage) -> StrategyEvidenceRecord:
    return StrategyEvidenceRecord(stage=stage, state=EvidenceState.BLOCKED, note="semantic boundary unresolved")


class StrategyEvidenceSequenceTests(unittest.TestCase):
    def test_context_gate_requires_liquidity_before_model_review(self) -> None:
        result = evaluate_pre_entry_context(
            [
                observed(StrategyEvidenceStage.DIRECTIONAL_CONTEXT),
                missing(StrategyEvidenceStage.LIQUIDITY_CALCULATION),
                observed(StrategyEvidenceStage.POI_ZONE_CONTEXT),
            ]
        )
        self.assertEqual(result.state, ContextGateState.WAIT)
        self.assertEqual(result.first_unready_stage, StrategyEvidenceStage.LIQUIDITY_CALCULATION)

    def test_context_gate_blocks_unresolved_source_boundary(self) -> None:
        result = evaluate_pre_entry_context(
            [
                observed(StrategyEvidenceStage.DIRECTIONAL_CONTEXT),
                blocked(StrategyEvidenceStage.LIQUIDITY_CALCULATION),
                observed(StrategyEvidenceStage.POI_ZONE_CONTEXT),
            ]
        )
        self.assertEqual(result.state, ContextGateState.BLOCKED)
        self.assertEqual(result.first_unready_stage, StrategyEvidenceStage.LIQUIDITY_CALCULATION)

    def test_context_gate_ready_does_not_mean_trade_allowed(self) -> None:
        result = evaluate_pre_entry_context(
            [
                observed(StrategyEvidenceStage.DIRECTIONAL_CONTEXT),
                observed(StrategyEvidenceStage.LIQUIDITY_CALCULATION),
                observed(StrategyEvidenceStage.POI_ZONE_CONTEXT),
            ]
        )
        self.assertEqual(result.state, ContextGateState.READY_FOR_MODEL_REVIEW)

    def test_r143_complete_path_is_only_complete_candidate(self) -> None:
        result = evaluate_r143_evidence(
            [
                observed(StrategyEvidenceStage.HCS_ZONE_REACTION),
                observed(StrategyEvidenceStage.TFS_CONFIRMED),
                observed(StrategyEvidenceStage.LAOL_MET),
                observed(StrategyEvidenceStage.TRUE_STOP_RESPECTED),
                observed(StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED),
                observed(StrategyEvidenceStage.TARGETS_AND_TIMING),
            ]
        )
        self.assertEqual(result.state, SequenceState.COMPLETE_CANDIDATE)

    def test_r143_blocked_stage_fails_closed_not_false(self) -> None:
        result = evaluate_r143_evidence(
            [
                observed(StrategyEvidenceStage.HCS_ZONE_REACTION),
                blocked(StrategyEvidenceStage.TFS_CONFIRMED),
                missing(StrategyEvidenceStage.LAOL_MET),
                missing(StrategyEvidenceStage.TRUE_STOP_RESPECTED),
                missing(StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED),
                missing(StrategyEvidenceStage.TARGETS_AND_TIMING),
            ]
        )
        self.assertEqual(result.state, SequenceState.NOT_CERTIFIED)
        self.assertEqual(result.next_required_stage, BacktestStage.TFS)

    def test_r143_later_observation_cannot_skip_laol(self) -> None:
        result = evaluate_r143_evidence(
            [
                observed(StrategyEvidenceStage.HCS_ZONE_REACTION),
                observed(StrategyEvidenceStage.TFS_CONFIRMED),
                missing(StrategyEvidenceStage.LAOL_MET),
                observed(StrategyEvidenceStage.TRUE_STOP_RESPECTED),
                missing(StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED),
                missing(StrategyEvidenceStage.TARGETS_AND_TIMING),
            ]
        )
        self.assertEqual(result.state, SequenceState.INVALID_ORDER)
        self.assertEqual(result.next_required_stage, BacktestStage.LAOL_MET)

    def test_r145_confirmed_path_requires_established_10m_true_stop(self) -> None:
        result = evaluate_r145_evidence(
            [
                observed(StrategyEvidenceStage.RETAIL_LIQUIDITY_MANIPULATED),
                observed(StrategyEvidenceStage.LTF_LAOL_TAKEN),
                observed(StrategyEvidenceStage.LTF_TRIGGER),
                missing(StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED),
            ],
            trigger=LTFExecutionTrigger.ONE_MIN_NEGATION,
            mode=LTFExecutionMode.CONFIRMED,
        )
        self.assertEqual(result.state, LTFExecutionState.WAIT)

    def test_r145_confirmed_path_reaches_entry_candidate_only_after_all_gates(self) -> None:
        result = evaluate_r145_evidence(
            [
                observed(StrategyEvidenceStage.RETAIL_LIQUIDITY_MANIPULATED),
                observed(StrategyEvidenceStage.LTF_LAOL_TAKEN),
                observed(StrategyEvidenceStage.LTF_TRIGGER),
                observed(StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED),
            ],
            trigger=LTFExecutionTrigger.THREE_MIN_HCS_NEGATION,
            mode=LTFExecutionMode.CONFIRMED,
        )
        self.assertEqual(result.state, LTFExecutionState.ENTRY_CANDIDATE)

    def test_r145_trigger_missing_waits_after_liquidity_sequence(self) -> None:
        result = evaluate_r145_evidence(
            [
                observed(StrategyEvidenceStage.RETAIL_LIQUIDITY_MANIPULATED),
                observed(StrategyEvidenceStage.LTF_LAOL_TAKEN),
                missing(StrategyEvidenceStage.LTF_TRIGGER),
                observed(StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED),
            ],
            trigger=None,
            mode=LTFExecutionMode.CONFIRMED,
        )
        self.assertEqual(result.state, LTFExecutionState.WAIT)

    def test_r145_blocked_liquidity_fails_closed(self) -> None:
        result = evaluate_r145_evidence(
            [
                blocked(StrategyEvidenceStage.RETAIL_LIQUIDITY_MANIPULATED),
                observed(StrategyEvidenceStage.LTF_LAOL_TAKEN),
                observed(StrategyEvidenceStage.LTF_TRIGGER),
                observed(StrategyEvidenceStage.TEN_MIN_TRUE_STOP_ESTABLISHED),
            ],
            trigger=LTFExecutionTrigger.ONE_MIN_NEGATION,
            mode=LTFExecutionMode.CONFIRMED,
        )
        self.assertEqual(result.state, LTFExecutionState.NOT_CERTIFIED)

    def test_r145_aggressive_path_keeps_forming_and_full_tfs_separate(self) -> None:
        result = evaluate_r145_evidence(
            [
                observed(StrategyEvidenceStage.RETAIL_LIQUIDITY_MANIPULATED),
                observed(StrategyEvidenceStage.LTF_LAOL_TAKEN),
                observed(StrategyEvidenceStage.LTF_TRIGGER),
                observed(StrategyEvidenceStage.TEN_MIN_TRUE_STOP_FORMING),
                observed(StrategyEvidenceStage.FULL_TFS_FACTORS),
            ],
            trigger=LTFExecutionTrigger.ONE_MIN_NEGATION,
            mode=LTFExecutionMode.AGGRESSIVE,
        )
        self.assertEqual(result.state, LTFExecutionState.ENTRY_CANDIDATE)

    def test_observed_record_requires_provenance(self) -> None:
        with self.assertRaises(ValueError):
            StrategyEvidenceRecord(
                stage=StrategyEvidenceStage.DIRECTIONAL_CONTEXT,
                state=EvidenceState.OBSERVED,
            )

    def test_duplicate_stage_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_pre_entry_context(
                [
                    observed(StrategyEvidenceStage.DIRECTIONAL_CONTEXT),
                    observed(StrategyEvidenceStage.DIRECTIONAL_CONTEXT),
                ]
            )


if __name__ == "__main__":
    unittest.main()
