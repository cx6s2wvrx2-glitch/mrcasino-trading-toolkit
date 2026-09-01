from __future__ import annotations

import unittest
from pathlib import Path

from xauusd_v2.validation import can_promote_dataset, compare_predictions, load_ground_truth


DATASET_PATH = Path(__file__).with_name("ground_truth_round_01.json")


class GroundTruthContractTests(unittest.TestCase):
    def test_round_01_dataset_loads_and_is_fail_closed(self) -> None:
        dataset = load_ground_truth(DATASET_PATH)
        self.assertEqual(len(dataset.vectors), 6)
        self.assertFalse(dataset.promotion_allowed)
        self.assertEqual(len({vector.id for vector in dataset.vectors}), 6)
        self.assertTrue(all(vector.evidence for vector in dataset.vectors))

    def test_exact_predictions_agree_but_do_not_auto_promote(self) -> None:
        dataset = load_ground_truth(DATASET_PATH)
        predictions = {vector.id: vector.expected_label for vector in dataset.vectors}
        outcomes = compare_predictions(dataset, predictions)

        self.assertTrue(all(outcome.result == "AGREE" for outcome in outcomes))
        self.assertFalse(
            can_promote_dataset(
                dataset,
                outcomes,
                blind_independent_validator=True,
                historical_reproducible=True,
            )
        )

    def test_missing_prediction_is_ambiguous(self) -> None:
        dataset = load_ground_truth(DATASET_PATH)
        predictions = {vector.id: vector.expected_label for vector in dataset.vectors[1:]}
        outcomes = compare_predictions(dataset, predictions)

        self.assertEqual(outcomes[0].result, "AMBIGUOUS")
        self.assertFalse(
            can_promote_dataset(
                dataset,
                outcomes,
                blind_independent_validator=True,
                historical_reproducible=True,
            )
        )

    def test_wrong_prediction_is_disagree(self) -> None:
        dataset = load_ground_truth(DATASET_PATH)
        predictions = {vector.id: vector.expected_label for vector in dataset.vectors}
        predictions[dataset.vectors[0].id] = "wrong_label"
        outcomes = compare_predictions(dataset, predictions)

        self.assertEqual(outcomes[0].result, "DISAGREE")
        self.assertFalse(
            can_promote_dataset(
                dataset,
                outcomes,
                blind_independent_validator=True,
                historical_reproducible=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
