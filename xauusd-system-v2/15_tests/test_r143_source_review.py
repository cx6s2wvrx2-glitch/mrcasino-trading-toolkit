from __future__ import annotations

import unittest

from xauusd_v2.r143_source_review import render_r143_source_review


class R143SourceReviewTests(unittest.TestCase):
    def test_unresolved_source_stage_is_visible_not_force_completed(self) -> None:
        payload = {
            "schema_version": "r143_source_evidence_map_v1",
            "episode_id": "march-buy-fixture",
            "source_locator": "source#buy",
            "stages": [
                {"stage": "HCS_ZONE_REACTION", "status": "explicit", "source_refs": ["source#hcs"], "note": "hcs", "machine_stage_certified": False},
                {"stage": "TFS", "status": "explicit", "source_refs": ["source#tfs"], "note": "tfs", "machine_stage_certified": False},
                {"stage": "LAOL_MET", "status": "unresolved", "source_refs": ["source#laol"], "note": "laol unresolved", "machine_stage_certified": False},
                {"stage": "TRUE_STOP_RESPECTED", "status": "explicit", "source_refs": ["source#ts"], "note": "ts", "machine_stage_certified": False},
                {"stage": "TEN_MIN_TRUE_STOP_ESTABLISHED", "status": "unresolved", "source_refs": [], "note": "10m unresolved", "machine_stage_certified": False},
                {"stage": "TARGETS_AND_TIMING", "status": "partial", "source_refs": ["source#target"], "note": "partial target", "machine_stage_certified": False},
            ],
            "complete_source_sequence_claim": False,
            "promotion_allowed": False,
            "performance_claim_allowed": False,
            "live_execution_authorized": False,
        }

        text = render_r143_source_review(payload)
        self.assertIn("SOURCE EPISODE: march-buy-fixture", text)
        self.assertIn("SOURCE LABELS != MACHINE CERTIFICATION", text)
        self.assertIn("[ΜΠΛΟΚΑΡΙΣΜΕΝΟ] LAOL met", text)
        self.assertIn("state=not_certified", text)
        self.assertIn("next_required_stage=LAOL_MET", text)
        self.assertIn("performance_claim_allowed=false", text)


if __name__ == "__main__":
    unittest.main()
