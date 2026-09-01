from __future__ import annotations

import unittest

from xauusd_v2.candidate_detectors import (
    CertificationState,
    ZoneType,
    evaluate_standard_entry_gate,
    evaluate_zone_lifecycle,
)


class CandidateDetectorTests(unittest.TestCase):
    def test_broken_fu_zone_requires_body_close(self) -> None:
        result = evaluate_zone_lifecycle(
            zone_type=ZoneType.BROKEN_FU_WICK,
            body_close_break=False,
            main_same_tf_reactions=0,
        )
        self.assertEqual(result.state, CertificationState.INACTIVE)

    def test_broken_fu_zone_expires_after_one_main_reaction(self) -> None:
        result = evaluate_zone_lifecycle(
            zone_type=ZoneType.BROKEN_FU_WICK,
            body_close_break=True,
            main_same_tf_reactions=1,
        )
        self.assertEqual(result.state, CertificationState.EXPIRED)
        self.assertEqual(result.reaction_quota, 1)

    def test_broken_hcs_zone_has_two_main_reactions(self) -> None:
        active = evaluate_zone_lifecycle(
            zone_type=ZoneType.BROKEN_HCS,
            body_close_break=True,
            main_same_tf_reactions=1,
        )
        expired = evaluate_zone_lifecycle(
            zone_type=ZoneType.BROKEN_HCS,
            body_close_break=True,
            main_same_tf_reactions=2,
        )
        self.assertEqual(active.state, CertificationState.ACTIVE)
        self.assertEqual(expired.state, CertificationState.EXPIRED)
        self.assertEqual(active.reaction_quota, 2)

    def test_weakest_att_fu_zone_fails_closed_below_3h(self) -> None:
        result = evaluate_zone_lifecycle(
            zone_type=ZoneType.WEAKEST_ATT_FU,
            body_close_break=None,
            main_same_tf_reactions=0,
            timeframe_minutes=50,
        )
        self.assertEqual(result.state, CertificationState.NOT_CERTIFIED)

    def test_entry_gate_waits_without_established_10m_ts(self) -> None:
        result = evaluate_standard_entry_gate(
            liquidity_calculation_resolved=True,
            ltf_laol_taken=True,
            ts_10m_established=False,
            ts_respected=True,
            htf_context_aligned=True,
            ltf_trigger_present=True,
        )
        self.assertEqual(result.state, CertificationState.WAIT)

    def test_entry_gate_ready_candidate_only_when_all_semantic_gates_pass(self) -> None:
        result = evaluate_standard_entry_gate(
            liquidity_calculation_resolved=True,
            ltf_laol_taken=True,
            ts_10m_established=True,
            ts_respected=True,
            htf_context_aligned=True,
            ltf_trigger_present=True,
        )
        self.assertEqual(result.state, CertificationState.READY_CANDIDATE)

    def test_entry_gate_missing_evidence_is_not_certified(self) -> None:
        result = evaluate_standard_entry_gate(
            liquidity_calculation_resolved=True,
            ltf_laol_taken=True,
            ts_10m_established=True,
            ts_respected=None,
            htf_context_aligned=True,
            ltf_trigger_present=True,
        )
        self.assertEqual(result.state, CertificationState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
