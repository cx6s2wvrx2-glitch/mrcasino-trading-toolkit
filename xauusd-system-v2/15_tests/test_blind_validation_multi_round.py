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
        cls.datasets = tuple(load_ground_truth(base / f"ground_truth_round_{round_no:02d}.json") for round_no in (2,3,4,5,6,7,8,9,10,11,12,13))
        cls.packet = build_blind_packet_multi(cls.datasets)

    @staticmethod
    def _decision(vector_id: str, locator: str, label: str | None) -> IndependentValidationDecision:
        return IndependentValidationDecision(vector_id=vector_id, source_locator=locator, predicted_label=label, confidence=0.8 if label else 0.0, evidence=(), ambiguities=() if label else ("abstain",))

    def test_rounds_02_to_13_create_exactly_173_blind_cases(self) -> None:
        self.assertEqual([len(d.vectors) for d in self.datasets], [20,7,6,5,8,10,10,4,20,30,24,29])
        self.assertEqual(len(self.packet.cases), 173)
        self.assertEqual(len({case.vector_id for case in self.packet.cases}), 173)

    def test_case_schema_contains_no_answer_or_analyst_fields(self) -> None:
        fields = {field.name for field in dataclasses.fields(self.packet.cases[0])}
        self.assertEqual(fields, {"vector_id","source_locator"})
        for forbidden in ("expected_label","expected_class","evidence","forbidden_inference"):
            self.assertNotIn(forbidden, fields)

    def test_all_source_locators_are_preserved_exactly(self) -> None:
        expected = {v.id:v.source_locator for d in self.datasets for v in d.vectors}
        actual = {c.vector_id:c.source_locator for c in self.packet.cases}
        self.assertEqual(actual, expected)

    def test_taxonomy_is_union_only_and_not_case_associated(self) -> None:
        expected = tuple(sorted({v.expected_label for d in self.datasets for v in d.vectors}))
        self.assertEqual(self.packet.taxonomy, expected)

    def test_clean_173_case_predictions_compare_as_all_agree_but_never_promote(self) -> None:
        decisions = tuple(self._decision(v.id,v.source_locator,v.expected_label) for d in self.datasets for v in d.vectors)
        report = compare_blind_multi_batch(datasets=self.datasets,batch=BlindValidationBatchResult(decisions=decisions))
        self.assertEqual((report.total,report.agree,report.disagree,report.ambiguous),(173,173,0,0))
        self.assertTrue(report.all_agree)
        self.assertFalse(report.promotion_allowed)

    def test_one_missing_prediction_becomes_ambiguous_not_silently_dropped(self) -> None:
        all_vectors = tuple(v for d in self.datasets for v in d.vectors)
        decisions = tuple(self._decision(v.id,v.source_locator,v.expected_label) for v in all_vectors[:-1])
        report = compare_blind_multi_batch(datasets=self.datasets,batch=BlindValidationBatchResult(decisions=decisions))
        self.assertEqual((report.total,report.agree,report.ambiguous),(173,172,1))
        self.assertFalse(report.all_agree)

    def test_unknown_prediction_id_is_rejected_across_all_rounds(self) -> None:
        with self.assertRaises(ValueError):
            compare_blind_multi_batch(datasets=self.datasets,batch=BlindValidationBatchResult(decisions=(self._decision("UNKNOWN","primary:unknown","anything"),)))

    def test_duplicate_ids_across_datasets_are_rejected_before_agent_run(self) -> None:
        duplicate = GroundTruthDataset(name="duplicate",status="candidate_not_verified",source_episode="primary",promotion_allowed=False,vectors=(GroundTruthVector(id=self.datasets[0].vectors[0].id,source_locator="primary:duplicate",expected_label="other_label",expected_class="invalid",evidence=("primary evidence",),forbidden_inference=""),))
        with self.assertRaises(ValueError):
            build_blind_packet_multi((*self.datasets,duplicate))


if __name__ == "__main__":
    unittest.main()
