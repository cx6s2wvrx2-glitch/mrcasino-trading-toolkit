from __future__ import annotations

import dataclasses
import unittest
from pathlib import Path

from xauusd_v2.blind_validation_packet import build_blind_packet
from xauusd_v2.validation import load_ground_truth


class BlindValidationPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        dataset_path = Path(__file__).with_name("ground_truth_round_02.json")
        cls.dataset = load_ground_truth(dataset_path)
        cls.packet = build_blind_packet(cls.dataset)

    def test_packet_contains_all_round_02_cases(self) -> None:
        self.assertEqual(len(self.packet.cases), len(self.dataset.vectors))
        self.assertEqual(
            {case.vector_id for case in self.packet.cases},
            {vector.id for vector in self.dataset.vectors},
        )

    def test_per_case_schema_cannot_carry_expected_answer(self) -> None:
        fields = {field.name for field in dataclasses.fields(self.packet.cases[0])}
        self.assertEqual(fields, {"vector_id", "source_locator"})
        self.assertNotIn("expected_label", fields)
        self.assertNotIn("expected_class", fields)
        self.assertNotIn("evidence", fields)
        self.assertNotIn("forbidden_inference", fields)

    def test_taxonomy_is_multi_option_and_batch_wide(self) -> None:
        self.assertGreater(len(self.packet.taxonomy), 1)
        expected_taxonomy = tuple(sorted({v.expected_label for v in self.dataset.vectors}))
        self.assertEqual(self.packet.taxonomy, expected_taxonomy)

    def test_source_locators_are_preserved_exactly(self) -> None:
        source_by_id = {v.id: v.source_locator for v in self.dataset.vectors}
        for case in self.packet.cases:
            self.assertEqual(case.source_locator, source_by_id[case.vector_id])


if __name__ == "__main__":
    unittest.main()
