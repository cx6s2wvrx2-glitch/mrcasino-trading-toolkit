from __future__ import annotations

import unittest

from xauusd_v2.phase3_stage_comparison import (
    BrokerStageEvidenceRecord,
    ComparisonState,
    compare_source_to_broker_stages,
)
from xauusd_v2.strategy_evidence_sequence import EvidenceState, StrategyEvidenceRecord, StrategyEvidenceStage


def source(stage: StrategyEvidenceStage, state: EvidenceState) -> StrategyEvidenceRecord:
    return StrategyEvidenceRecord(
        stage=stage,
        state=state,
        evidence_ref=f"source:{stage.value}" if state is EvidenceState.OBSERVED else None,
    )


def broker(
    stage: StrategyEvidenceStage,
    state: EvidenceState,
    *,
    path: bool | None = None,
    certified: bool = False,
    aligned: bool = False,
) -> BrokerStageEvidenceRecord:
    return BrokerStageEvidenceRecord(
        stage=stage,
        semantic_state=state,
        broker_path_observed=path,
        evidence_ref=f"broker:{stage.value}" if path or certified else None,
        machine_stage_certified=certified,
        reference_feed_aligned=aligned,
    )


class Phase3StageComparisonTests(unittest.TestCase):
    def test_source_explicit_broker_path_is_not_semantic_equivalence(self) -> None:
        result = compare_source_to_broker_stages(
            [source(StrategyEvidenceStage.TRUE_STOP_RESPECTED, EvidenceState.OBSERVED)],
            [broker(StrategyEvidenceStage.TRUE_STOP_RESPECTED, EvidenceState.BLOCKED, path=True)],
        )[0]
        self.assertEqual(result.comparison_state, ComparisonState.SOURCE_OBSERVED_BROKER_PATH_ONLY)
        self.assertFalse(result.canonical_equivalence_allowed)

    def test_both_semantic_observed_still_need_reference_alignment(self) -> None:
        result = compare_source_to_broker_stages(
            [source(StrategyEvidenceStage.HCS_ZONE_REACTION, EvidenceState.OBSERVED)],
            [
                broker(
                    StrategyEvidenceStage.HCS_ZONE_REACTION,
                    EvidenceState.OBSERVED,
                    path=True,
                    certified=True,
                    aligned=False,
                )
            ],
        )[0]
        self.assertEqual(result.comparison_state, ComparisonState.BOTH_OBSERVED_REFERENCE_UNALIGNED)
        self.assertFalse(result.canonical_equivalence_allowed)

    def test_reference_aligned_both_observed_can_allow_stage_equivalence_only(self) -> None:
        result = compare_source_to_broker_stages(
            [source(StrategyEvidenceStage.HCS_ZONE_REACTION, EvidenceState.OBSERVED)],
            [
                broker(
                    StrategyEvidenceStage.HCS_ZONE_REACTION,
                    EvidenceState.OBSERVED,
                    path=True,
                    certified=True,
                    aligned=True,
                )
            ],
        )[0]
        self.assertEqual(result.comparison_state, ComparisonState.BOTH_OBSERVED_REFERENCE_ALIGNED)
        self.assertTrue(result.canonical_equivalence_allowed)

    def test_both_blocked_can_still_preserve_broker_path_observation(self) -> None:
        result = compare_source_to_broker_stages(
            [source(StrategyEvidenceStage.TARGETS_AND_TIMING, EvidenceState.BLOCKED)],
            [broker(StrategyEvidenceStage.TARGETS_AND_TIMING, EvidenceState.BLOCKED, path=True)],
        )[0]
        self.assertEqual(result.comparison_state, ComparisonState.SOURCE_BLOCKED_BROKER_PATH_OBSERVED)
        self.assertFalse(result.canonical_equivalence_allowed)

    def test_observed_broker_semantic_requires_machine_certification(self) -> None:
        with self.assertRaises(ValueError):
            broker(
                StrategyEvidenceStage.TFS_CONFIRMED,
                EvidenceState.OBSERVED,
                path=True,
                certified=False,
            )

    def test_observed_broker_path_requires_provenance(self) -> None:
        with self.assertRaises(ValueError):
            BrokerStageEvidenceRecord(
                stage=StrategyEvidenceStage.LAOL_MET,
                semantic_state=EvidenceState.BLOCKED,
                broker_path_observed=True,
            )

    def test_missing_broker_stage_stays_incomplete(self) -> None:
        result = compare_source_to_broker_stages(
            [source(StrategyEvidenceStage.TFS_CONFIRMED, EvidenceState.OBSERVED)],
            [],
        )[0]
        self.assertEqual(result.comparison_state, ComparisonState.MISSING_OR_INCOMPLETE)
        self.assertFalse(result.canonical_equivalence_allowed)


if __name__ == "__main__":
    unittest.main()
