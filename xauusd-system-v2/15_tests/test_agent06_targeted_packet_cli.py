from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2 import agent06_targeted_packet_cli
from xauusd_v2.blind_validation_packet_io import load_blind_packet


class Agent06TargetedPacketCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.datasets = self.root / "datasets"
        self.datasets.mkdir()
        self.review = self.root / "review.json"
        self.output = self.root / "packet.json"

        (self.datasets / "ground_truth_round_02.json").write_text(
            json.dumps(
                {
                    "dataset": "fixture",
                    "status": "candidate_not_verified",
                    "source_episode": "fixture",
                    "promotion_allowed": False,
                    "test_vectors": [
                        {
                            "id": "GT-R02-001",
                            "source_locator": "source#1",
                            "expected_label": "claim_one",
                            "expected_class": "valid",
                            "evidence": ["secret evidence one"],
                            "forbidden_inference": "secret forbidden one",
                        },
                        {
                            "id": "GT-R02-002",
                            "source_locator": "source#2",
                            "expected_label": "claim_two",
                            "expected_class": "edge_case",
                            "evidence": ["secret evidence two"],
                            "forbidden_inference": "secret forbidden two",
                        },
                        {
                            "id": "GT-R02-003",
                            "source_locator": "source#3",
                            "expected_label": "claim_three",
                            "expected_class": "valid",
                            "evidence": ["secret evidence three"],
                            "forbidden_inference": "secret forbidden three",
                        },
                    ],
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        self.review.write_text(
            json.dumps(
                {
                    "status": "AGENT06_LOCATOR_SET_REVIEW_READY",
                    "audit_status": "AUDIT_PASS",
                    "run_id": "agent06-anthropic-fixture",
                    "promotion_allowed": False,
                    "strategy_truth_changed": False,
                    "unresolved_disagree": 1,
                    "abstain": 1,
                    "cases": [
                        {
                            "vector_id": "GT-R02-001",
                            "source_locator": "source#1",
                            "adjusted_result": "UNRESOLVED_DISAGREE",
                        },
                        {
                            "vector_id": "GT-R02-002",
                            "source_locator": "source#2",
                            "adjusted_result": "ABSTAIN",
                        },
                        {
                            "vector_id": "GT-R02-003",
                            "source_locator": "source#3",
                            "adjusted_result": "LOCATOR_SET_AGREE",
                        },
                    ],
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def test_builds_only_unresolved_and_abstained_focused_cases(self) -> None:
        rc = agent06_targeted_packet_cli.main(
            [
                "--review",
                str(self.review),
                "--datasets-dir",
                str(self.datasets),
                "--output",
                str(self.output),
                "--rounds",
                "2",
            ]
        )
        self.assertEqual(rc, 0)
        raw = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(raw["version"], 2)
        self.assertEqual(raw["taxonomy"], ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT"])
        self.assertEqual([case["vector_id"] for case in raw["cases"]], ["GT-R02-001", "GT-R02-002"])
        self.assertEqual([case["focus"] for case in raw["cases"]], ["claim_one", "claim_two"])
        serialized = self.output.read_text(encoding="utf-8")
        self.assertNotIn("secret evidence", serialized)
        self.assertNotIn("secret forbidden", serialized)
        self.assertNotIn("expected_class", serialized)
        self.assertNotIn("expected_verdict", serialized)

        packet = load_blind_packet(self.output)
        self.assertEqual(len(packet.cases), 2)
        self.assertEqual(packet.cases[0].focus, "claim_one")

    def test_requires_audited_source_review(self) -> None:
        payload = json.loads(self.review.read_text(encoding="utf-8"))
        payload["audit_status"] = "AUDIT_FAIL"
        self.review.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "requires an audited source run"):
            agent06_targeted_packet_cli.main(
                [
                    "--review",
                    str(self.review),
                    "--datasets-dir",
                    str(self.datasets),
                    "--output",
                    str(self.output),
                    "--rounds",
                    "2",
                ]
            )


if __name__ == "__main__":
    unittest.main()
