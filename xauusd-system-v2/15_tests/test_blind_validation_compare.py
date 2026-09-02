from __future__ import annotations

import unittest

from xauusd_v2.agents.validation_agent import IndependentValidationDecision
from xauusd_v2.blind_validation_compare import compare_blind_batch
from xauusd_v2.blind_validation_runner import BlindValidationBatchResult
from xauusd_v2.validation import GroundTruthDataset, GroundTruthVector


class BlindValidationCompareTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = GroundTruthDataset(
            name="test",
            status="candidate_not_verified",
            source_episode="primary",
            promotion_allowed=False,
            vectors=(
                GroundTruthVector("V1", "s1", "a", "valid", ("e1",), ""),
                GroundTruthVector("V2", "s2", "b", "invalid", ("e2",), ""),
                GroundTruthVector("V3", "s3", "c", "edge_case", ("e3",), ""),
            ),
        )

    def _decision(self, vector_id: str, label: str | None) -> IndependentValidationDecision:
        return IndependentValidationDecision(
            vector_id=vector_id,
            source_locator=f"source:{vector_id}",
            predicted_label=label,
            confidence=0.8 if label else 0.0,
            evidence=(),
            ambiguities=() if label else ("ambiguous",),
        )

    def test_summary_counts_agree_disagree_ambiguous(self) -> None:
        batch = BlindValidationBatchResult(
            decisions=(
                self._decision("V1", "a"),
                self._decision("V2", "wrong"),
                self._decision("V3", None),
            )
        )
        report = compare_blind_batch(dataset=self.dataset, batch=batch)
        self.assertEqual((report.agree, report.disagree, report.ambiguous, report.total), (1, 1, 1, 3))
        self.assertFalse(report.all_agree)
        self.assertFalse(report.promotion_allowed)

    def test_all_agree_still_does_not_promote(self) -> None:
        batch = BlindValidationBatchResult(
            decisions=(
                self._decision("V1", "a"),
                self._decision("V2", "b"),
                self._decision("V3", "c"),
            )
        )
        report = compare_blind_batch(dataset=self.dataset, batch=batch)
        self.assertTrue(report.all_agree)
        self.assertEqual(report.agree, 3)
        self.assertFalse(report.promotion_allowed)

    def test_missing_prediction_becomes_ambiguous(self) -> None:
        batch = BlindValidationBatchResult(decisions=(self._decision("V1", "a"),))
        report = compare_blind_batch(dataset=self.dataset, batch=batch)
        self.assertEqual(report.agree, 1)
        self.assertEqual(report.ambiguous, 2)

    def test_unknown_vector_id_is_rejected(self) -> None:
        batch = BlindValidationBatchResult(decisions=(self._decision("UNKNOWN", "a"),))
        with self.assertRaises(ValueError):
            compare_blind_batch(dataset=self.dataset, batch=batch)


if __name__ == "__main__":
    unittest.main()
