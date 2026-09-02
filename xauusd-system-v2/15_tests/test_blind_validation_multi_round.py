from __future__ import annotations

import dataclasses
import unittest
from pathlib import Path

from xauusd_v2.agents.validation_agent import IndependentValidationDecision
from xauusd_v2.blind_validation_compare import compare_blind_multi_batch
from xauusd_v2.blind_validation_packet import build_blind_packet_multi
from xauusd_v2.blind_validation_runner import BlindValidationBatchResult
from xauusd_v2.validation import GroundTruthDataset, GroundTruthVector, load_ground_truth


class BlindValidationMultiRoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        base = Path(__file__).parent
        cls.datasets = tuple(
            load_ground_truth(base / f"ground_truth_round_{round_no:02d}.json")
            for round_no in (2, 3, 4, 5, 6, 7)
        )
        cls.packet = build_blind_packet_multi(cls.datasets)

    @staticmethod
    def _decision(vector_id: str, locator: str, label: str | None) -> IndependentValidationDecision:
        return IndependentValidationDecision(
            vector_id=vector_id,
            source_locator=locator,
            predicted_label=label,
            confidence=0.8 if label else 0.0,
            evidence=(),
            ambiguities=() if label else ("abstain",),
        )

    def test_rounds_02_to_07_create_exactly_56_blind_cases(self) -> None:
        self.assertEqual([len(dataset.vectors) for dataset in self.datasets], [20, 7, 6, 5, 8, 10])
        self.assertEqual(len(self.packet.cases), 56)
        self.assertEqual(len({case.vector_id for case in self.packet.cases}), 56)

    def test_case_schema_contains_no_answer_or_analyst_fields(self) -> None:
        fields = {field.name for field in dataclasses.fields(self.packet.cases[0])}
        self.assertEqual(fields, {"vector_id", "source_locator"})
        for forbidden in ("expected_label", "expected_class", "evidence", "forbidden_inference"):
            self.assertNotIn(forbidden, fields)

    def test_all_source_locators_are_preserved_exactly(self) -> None:
        expected = {
            vector.id: vector.source_locator
            for dataset in self.datasets
            for vector in dataset.vectors
        }
        actual = {case.vector_id: case.source_locator for case in self.packet.cases}
        self.assertEqual(actual, expected)

    def test_taxonomy_is_union_only_and_not_case_associated(self) -> None:
        expected = tuple(sorted({
            vector.expected_label
            for dataset in self.datasets
            for vector in dataset.vectors
        }))
        self.assertEqual(self.packet.taxonomy, expected)
        self.assertGreater(len(self.packet.taxonomy), 2)

    def test_clean_56_case_predictions_compare_as_all_agree_but_never_promote(self) -> None:
        decisions = tuple(
            self._decision(vector.id, vector.source_locator, vector.expected_label)
            for dataset in self.datasets
            for vector in dataset.vectors
        )
        report = compare_blind_multi_batch(
            datasets=self.datasets,
            batch=BlindValidationBatchResult(decisions=decisions),
        )
        self.assertEqual(report.total, 56)
        self.assertEqual(report.agree, 56)
        self.assertEqual(report.disagree, 0)
        self.assertEqual(report.ambiguous, 0)
        self.assertTrue(report.all_agree)
        self.assertFalse(report.promotion_allowed)

    def test_one_missing_prediction_becomes_ambiguous_not_silently_dropped(self) -> None:
        all_vectors = tuple(vector for dataset in self.datasets for vector in dataset.vectors)
        decisions = tuple(
            self._decision(vector.id, vector.source_locator, vector.expected_label)
            for vector in all_vectors[:-1]
        )
        report = compare_blind_multi_batch(
            datasets=self.datasets,
            batch=BlindValidationBatchResult(decisions=decisions),
        )
        self.assertEqual(report.total, 56)
        self.assertEqual(report.agree, 55)
        self.assertEqual(report.ambiguous, 1)
        self.assertFalse(report.all_agree)

    def test_unknown_prediction_id_is_rejected_across_all_rounds(self) -> None:
        batch = BlindValidationBatchResult(
            decisions=(self._decision("UNKNOWN", "primary:unknown", "anything"),)
        )
        with self.assertRaises(ValueError):
            compare_blind_multi_batch(datasets=self.datasets, batch=batch)

    def test_duplicate_ids_across_datasets_are_rejected_before_agent_run(self) -> None:
        duplicate = GroundTruthDataset(
            name="duplicate",
            status="candidate_not_verified",
            source_episode="primary",
            promotion_allowed=False,
            vectors=(
                GroundTruthVector(
                    id=self.datasets[0].vectors[0].id,
                    source_locator="primary:duplicate",
                    expected_label="other_label",
                    expected_class="invalid",
                    evidence=("primary evidence",),
                    forbidden_inference="",
                ),
            ),
        )
        with self.assertRaises(ValueError):
            build_blind_packet_multi((*self.datasets, duplicate))


if __name__ == "__main__":
    unittest.main()
