from __future__ import annotations

import json
import unittest
from pathlib import Path

from xauusd_v2.candidate_detectors import ZoneType, evaluate_standard_entry_gate, evaluate_zone_lifecycle


FIXTURES_PATH = Path(__file__).with_name("detector_fixtures_round_01.json")
GROUND_TRUTH_PATH = Path(__file__).with_name("ground_truth_round_02.json")


class DetectorFixtureTests(unittest.TestCase):
    def test_all_fixtures_trace_to_round_02_ground_truth(self) -> None:
        fixtures = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))["fixtures"]
        ground_truth = json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))["test_vectors"]
        valid_refs = {v["id"] for v in ground_truth}
        self.assertTrue(fixtures)
        self.assertTrue(all(f["ground_truth_ref"] in valid_refs for f in fixtures))

    def test_fixture_outputs(self) -> None:
        fixtures = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))["fixtures"]
        for fixture in fixtures:
            with self.subTest(fixture=fixture["id"]):
                inputs = dict(fixture["inputs"])
                if fixture["detector"] == "zone_lifecycle":
                    inputs["zone_type"] = ZoneType(inputs["zone_type"])
                    result = evaluate_zone_lifecycle(**inputs)
                elif fixture["detector"] == "standard_entry_gate":
                    result = evaluate_standard_entry_gate(**inputs)
                else:
                    self.fail(f"unknown detector {fixture['detector']}")
                self.assertEqual(result.state.value, fixture["expected_state"])


if __name__ == "__main__":
    unittest.main()
