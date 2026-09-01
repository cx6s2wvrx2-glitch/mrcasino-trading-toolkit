from __future__ import annotations

import unittest

from xauusd_v2.agents.improvement_agent import (
    ContinuousImprovementAgent,
    ImprovementProposal,
    ImprovementProposalState,
)


def proposal(**overrides):
    values = {
        "proposal_id": "IMP-001",
        "base_strategy_version": "v0.1-candidate",
        "affected_rule_codes": ("XAU-V2-LAOL-001",),
        "evidence_refs": ("GT-R02-006", "EXP-001"),
        "observed_failure_modes": ("edge-case misclassification",),
        "proposed_change": "Refine LAOL priority condition without changing unrelated modules.",
        "validation_plan": (
            "re-run ground truth",
            "out-of-sample historical test",
            "walk-forward validation",
        ),
        "rollback_criteria": ("revert if OOS agreement worsens",),
        "requests_direct_promotion": False,
    }
    values.update(overrides)
    return ImprovementProposal(**values)


class ImprovementAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = ContinuousImprovementAgent()

    def test_complete_proposal_is_proposal_only(self) -> None:
        review, run = self.agent.review_proposal(proposal=proposal())
        self.assertEqual(review.state, ImprovementProposalState.PROPOSAL_ONLY)
        self.assertEqual(review.blockers, ())
        self.assertFalse(run.payload["authority"]["may_promote_to_production"])

    def test_missing_evidence_is_rejected(self) -> None:
        review, _ = self.agent.review_proposal(proposal=proposal(evidence_refs=()))
        self.assertEqual(review.state, ImprovementProposalState.REJECTED_INCOMPLETE)
        self.assertIn("evidence_refs are required", review.blockers)

    def test_missing_failure_mode_is_rejected(self) -> None:
        review, _ = self.agent.review_proposal(
            proposal=proposal(observed_failure_modes=())
        )
        self.assertEqual(review.state, ImprovementProposalState.REJECTED_INCOMPLETE)

    def test_missing_validation_plan_is_rejected(self) -> None:
        review, _ = self.agent.review_proposal(proposal=proposal(validation_plan=()))
        self.assertEqual(review.state, ImprovementProposalState.REJECTED_INCOMPLETE)

    def test_missing_rollback_is_rejected(self) -> None:
        review, _ = self.agent.review_proposal(proposal=proposal(rollback_criteria=()))
        self.assertEqual(review.state, ImprovementProposalState.REJECTED_INCOMPLETE)

    def test_direct_promotion_request_is_rejected(self) -> None:
        review, _ = self.agent.review_proposal(
            proposal=proposal(requests_direct_promotion=True)
        )
        self.assertEqual(review.state, ImprovementProposalState.REJECTED_INCOMPLETE)
        self.assertTrue(any("direct promotion" in item for item in review.blockers))

    def test_missing_affected_rules_is_rejected(self) -> None:
        review, _ = self.agent.review_proposal(
            proposal=proposal(affected_rule_codes=())
        )
        self.assertEqual(review.state, ImprovementProposalState.REJECTED_INCOMPLETE)


if __name__ == "__main__":
    unittest.main()
