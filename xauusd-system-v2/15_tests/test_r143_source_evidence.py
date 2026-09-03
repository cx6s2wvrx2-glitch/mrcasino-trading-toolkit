from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.backtest_sequence import BacktestStage
from xauusd_v2.r143_source_evidence import (
    R143SourceEvidenceError,
    SourceEvidenceStatus,
    load_r143_source_evidence_map,
)


class R143SourceEvidenceTests(unittest.TestCase):
    def write(self, payload: dict[str, object]) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(payload, handle)
        handle.close()
        path = Path(handle.name)
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        return path

    def payload(self) -> dict[str, object]:
        stages = []
        for stage in BacktestStage:
            stages.append(
                {
                    "stage": stage.name,
                    "status": "explicit" if stage in {BacktestStage.HCS_ZONE_REACTION, BacktestStage.TFS} else "unresolved",
                    "source_refs": [f"primary:{stage.name}"] if stage in {BacktestStage.HCS_ZONE_REACTION, BacktestStage.TFS} else [],
                    "note": f"source evidence for {stage.name}",
                    "machine_stage_certified": False,
                }
            )
        return {
            "schema_version": "r143_source_evidence_map_v1",
            "episode_id": "episode",
            "source_locator": "primary:episode",
            "stages": stages,
            "complete_source_sequence_claim": False,
            "promotion_allowed": False,
            "performance_claim_allowed": False,
            "live_execution_authorized": False,
        }

    def test_valid_incomplete_source_map_loads_without_machine_certification(self) -> None:
        result = load_r143_source_evidence_map(self.write(self.payload()))
        self.assertEqual(len(result.stages), 6)
        self.assertEqual(result.stages[0].status, SourceEvidenceStatus.EXPLICIT)
        self.assertFalse(result.stages[0].machine_stage_certified)
        self.assertFalse(result.complete_source_sequence_claim)

    def test_stage_order_is_strict(self) -> None:
        payload = self.payload()
        stages = payload["stages"]
        assert isinstance(stages, list)
        stages[0], stages[1] = stages[1], stages[0]
        with self.assertRaisesRegex(R143SourceEvidenceError, "canonical R-143 order"):
            load_r143_source_evidence_map(self.write(payload))

    def test_complete_claim_cannot_hide_partial_or_unresolved_stage(self) -> None:
        payload = self.payload()
        payload["complete_source_sequence_claim"] = True
        with self.assertRaisesRegex(R143SourceEvidenceError, "requires explicit"):
            load_r143_source_evidence_map(self.write(payload))

    def test_machine_stage_certification_is_forbidden(self) -> None:
        payload = self.payload()
        stages = payload["stages"]
        assert isinstance(stages, list)
        stages[0]["machine_stage_certified"] = True
        with self.assertRaisesRegex(R143SourceEvidenceError, "cannot machine-certify"):
            load_r143_source_evidence_map(self.write(payload))

    def test_explicit_stage_requires_source_ref(self) -> None:
        payload = self.payload()
        stages = payload["stages"]
        assert isinstance(stages, list)
        stages[0]["source_refs"] = []
        with self.assertRaisesRegex(R143SourceEvidenceError, "requires at least one"):
            load_r143_source_evidence_map(self.write(payload))

    def test_promotion_flag_is_forbidden(self) -> None:
        payload = self.payload()
        payload["promotion_allowed"] = True
        with self.assertRaisesRegex(R143SourceEvidenceError, "promotion_allowed"):
            load_r143_source_evidence_map(self.write(payload))


if __name__ == "__main__":
    unittest.main()
