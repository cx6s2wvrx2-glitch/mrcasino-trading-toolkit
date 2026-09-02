from __future__ import annotations

import unittest
from datetime import UTC, datetime

from xauusd_v2.agents.quant_agent import (
    QuantitativeResearchAgent,
    ResearchExperimentSpec,
    ResearchWindow,
)


def dt(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=UTC)


def sha_ref(char: str) -> str:
    return "sha256:" + char * 64


def valid_spec(**overrides):
    values = {
        "experiment_id": "EXP-001",
        "strategy_version": "v0.1-candidate",
        "strategy_commit_sha": "a" * 40,
        "data_snapshot_ref": sha_ref("b"),
        "parameter_set_ref": sha_ref("c"),
        "cost_model_ref": sha_ref("d"),
        "symbol": "XAUUSD",
        "timeframe_seconds": 60,
        "train": ResearchWindow("train", dt(2022, 1, 1), dt(2023, 1, 1)),
        "validation": ResearchWindow("validation", dt(2023, 1, 2), dt(2024, 1, 1)),
        "test": ResearchWindow("test", dt(2024, 1, 2), dt(2025, 1, 1)),
        "confirmed_bars_only": True,
        "test_locked_until_final_evaluation": True,
    }
    values.update(overrides)
    return ResearchExperimentSpec(**values)


class QuantResearchAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = QuantitativeResearchAgent()

    def test_valid_reproducible_design_is_ready(self) -> None:
        report, run = self.agent.validate_experiment(spec=valid_spec())
        self.assertTrue(report.ready_for_research)
        self.assertEqual(report.blockers, ())
        self.assertTrue(run.payload["content_addressed_inputs_required"])
        self.assertFalse(run.payload["authority"]["may_modify_strategy"])
        self.assertFalse(run.payload["authority"]["may_authorize_trade"])

    def test_overlap_is_rejected(self) -> None:
        spec = valid_spec(
            validation=ResearchWindow("validation", dt(2022, 12, 1), dt(2024, 1, 1))
        )
        report, _ = self.agent.validate_experiment(spec=spec)
        self.assertFalse(report.ready_for_research)
        self.assertIn("train and validation windows overlap", report.blockers)

    def test_missing_cost_model_is_rejected(self) -> None:
        report, _ = self.agent.validate_experiment(spec=valid_spec(cost_model_ref=""))
        self.assertFalse(report.ready_for_research)
        self.assertTrue(any("cost_model_ref" in item for item in report.blockers))

    def test_strategy_commit_must_be_exact_full_sha(self) -> None:
        report, _ = self.agent.validate_experiment(spec=valid_spec(strategy_commit_sha="abc123"))
        self.assertFalse(report.ready_for_research)
        self.assertIn(
            "strategy_commit_sha must be an exact 40-character Git commit SHA",
            report.blockers,
        )

    def test_snapshot_ref_must_be_content_addressed(self) -> None:
        report, _ = self.agent.validate_experiment(
            spec=valid_spec(data_snapshot_ref="xauusd-snapshot-latest")
        )
        self.assertFalse(report.ready_for_research)
        self.assertIn(
            "data_snapshot_ref must be a content-addressed sha256:<64-hex> reference",
            report.blockers,
        )

    def test_parameter_ref_must_be_content_addressed(self) -> None:
        report, _ = self.agent.validate_experiment(spec=valid_spec(parameter_set_ref="params-v1"))
        self.assertFalse(report.ready_for_research)
        self.assertIn(
            "parameter_set_ref must be a content-addressed sha256:<64-hex> reference",
            report.blockers,
        )

    def test_cost_model_ref_must_be_content_addressed(self) -> None:
        report, _ = self.agent.validate_experiment(spec=valid_spec(cost_model_ref="costs-v1"))
        self.assertFalse(report.ready_for_research)
        self.assertIn(
            "cost_model_ref must be a content-addressed sha256:<64-hex> reference",
            report.blockers,
        )

    def test_non_xauusd_is_rejected(self) -> None:
        report, _ = self.agent.validate_experiment(spec=valid_spec(symbol="GC"))
        self.assertFalse(report.ready_for_research)
        self.assertIn("research scope is canonical XAUUSD only", report.blockers)

    def test_provisional_bar_research_is_rejected(self) -> None:
        report, _ = self.agent.validate_experiment(spec=valid_spec(confirmed_bars_only=False))
        self.assertFalse(report.ready_for_research)
        self.assertIn("research may use confirmed bars only", report.blockers)

    def test_unlocked_test_set_is_rejected(self) -> None:
        report, _ = self.agent.validate_experiment(
            spec=valid_spec(test_locked_until_final_evaluation=False)
        )
        self.assertFalse(report.ready_for_research)
        self.assertIn("test set must remain locked until final evaluation", report.blockers)

    def test_contiguous_windows_warn_but_do_not_fail(self) -> None:
        spec = valid_spec(
            validation=ResearchWindow("validation", dt(2023, 1, 1), dt(2024, 1, 1)),
            test=ResearchWindow("test", dt(2024, 1, 1), dt(2025, 1, 1)),
        )
        report, _ = self.agent.validate_experiment(spec=spec)
        self.assertTrue(report.ready_for_research)
        self.assertEqual(len(report.warnings), 2)

    def test_naive_datetime_window_is_rejected_at_construction(self) -> None:
        with self.assertRaises(ValueError):
            ResearchWindow("train", datetime(2022, 1, 1), datetime(2023, 1, 1))


if __name__ == "__main__":
    unittest.main()
