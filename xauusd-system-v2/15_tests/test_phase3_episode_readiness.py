from __future__ import annotations

import json
import unittest
from pathlib import Path

from xauusd_v2.phase3_broker_evidence import broker_records_from_payload
from xauusd_v2.phase3_episode_readiness import (
    EpisodeReadinessState,
    evaluate_phase3_episode_readiness,
    render_episode_readiness_gr,
)
from xauusd_v2.r143_source_evidence_adapter import records_from_r143_source_evidence
from xauusd_v2.strategy_evidence_sequence import StrategyEvidenceStage


EXAMPLES = Path(__file__).resolve().parents[1] / "06_examples"


def load_json(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def evaluate(source_name: str, broker_name: str):
    return evaluate_phase3_episode_readiness(
        records_from_r143_source_evidence(load_json(source_name)),
        broker_records_from_payload(load_json(broker_name)),
        reference_feed_aligned=False,
    )


class Phase3EpisodeReadinessTests(unittest.TestCase):
    def test_march_buy_is_blocked_at_source_laol(self) -> None:
        result = evaluate(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        self.assertEqual(result.state, EpisodeReadinessState.BLOCKED_SOURCE_SEMANTICS)
        self.assertEqual(result.source_frontier.stage, StrategyEvidenceStage.LAOL_MET)
        self.assertEqual(result.broker_frontier.stage, StrategyEvidenceStage.HCS_ZONE_REACTION)
        self.assertFalse(result.canonical_sequence_ready)

    def test_march_sell_is_blocked_at_source_tfs(self) -> None:
        result = evaluate(
            "R143_SOURCE_EVIDENCE_2023_03_31_SELL.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_31_SELL.json",
        )
        self.assertEqual(result.state, EpisodeReadinessState.BLOCKED_SOURCE_SEMANTICS)
        self.assertEqual(result.source_frontier.stage, StrategyEvidenceStage.TFS_CONFIRMED)
        self.assertEqual(result.broker_frontier.stage, StrategyEvidenceStage.HCS_ZONE_REACTION)

    def test_readiness_never_enables_strategy_or_live_authority(self) -> None:
        result = evaluate(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        self.assertFalse(result.strategy_certified)
        self.assertFalse(result.performance_claim_allowed)
        self.assertFalse(result.promotion_allowed)
        self.assertFalse(result.live_execution_authorized)

    def test_greek_renderer_surfaces_both_independent_frontiers(self) -> None:
        result = evaluate(
            "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
            "PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json",
        )
        text = render_episode_readiness_gr(result, title="30/3 BUY")
        self.assertIn("Πρώτο κενό πηγής: laol_met", text)
        self.assertIn("Πρώτο κενό broker semantics: hcs_zone_reaction", text)
        self.assertIn("FOREXCOM alignment: ΟΧΙ", text)
        self.assertIn("Live execution: ΟΧΙ", text)


if __name__ == "__main__":
    unittest.main()
