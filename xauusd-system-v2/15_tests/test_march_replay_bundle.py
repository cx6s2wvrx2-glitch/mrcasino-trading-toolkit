from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.march_replay_bundle import (
    MarchReplayBundleError,
    _EPISODES,
    _canonical_json_bytes,
    _write_immutable_json,
)
from xauusd_v2.r143_source_evidence import load_r143_source_evidence_map
from xauusd_v2.source_fidelity_replay import load_source_fidelity_fixture


class MarchReplayBundleTests(unittest.TestCase):
    @property
    def examples_root(self) -> Path:
        return Path(__file__).resolve().parents[1] / "06_examples"

    def test_bundle_episode_registry_is_exactly_march_buy_and_sell(self) -> None:
        self.assertEqual(
            _EPISODES,
            (
                (
                    "2023-03-30-buy",
                    "SOURCE_FIDELITY_2023_03_30_BUY.json",
                    "R143_SOURCE_EVIDENCE_2023_03_30_BUY.json",
                ),
                (
                    "2023-03-31-sell",
                    "SOURCE_FIDELITY_2023_03_31_SELL.json",
                    "R143_SOURCE_EVIDENCE_2023_03_31_SELL.json",
                ),
            ),
        )

    def test_governed_march_fixtures_and_evidence_maps_load(self) -> None:
        for _, fixture_name, evidence_name in _EPISODES:
            fixture = load_source_fidelity_fixture(self.examples_root / fixture_name)
            evidence = load_r143_source_evidence_map(self.examples_root / evidence_name)
            self.assertEqual(fixture.timeframe_seconds, 60)
            self.assertLess(fixture.window_start, fixture.window_end)
            self.assertFalse(fixture.promotion_allowed)
            self.assertFalse(evidence.promotion_allowed)
            self.assertFalse(evidence.performance_claim_allowed)
            self.assertFalse(evidence.live_execution_authorized)
            self.assertTrue(all(not stage.machine_stage_certified for stage in evidence.stages))

    def test_canonical_json_is_order_independent(self) -> None:
        left = _canonical_json_bytes({"b": 2, "a": 1})
        right = _canonical_json_bytes({"a": 1, "b": 2})
        self.assertEqual(left, right)
        self.assertEqual(json.loads(left), {"a": 1, "b": 2})

    def test_immutable_writer_is_idempotent_and_refuses_differing_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            first = _write_immutable_json(path, {"status": "A", "promotion_allowed": False})
            second = _write_immutable_json(path, {"promotion_allowed": False, "status": "A"})
            self.assertEqual(first, second)
            with self.assertRaisesRegex(MarchReplayBundleError, "refusing to overwrite"):
                _write_immutable_json(path, {"status": "B", "promotion_allowed": False})


if __name__ == "__main__":
    unittest.main()
