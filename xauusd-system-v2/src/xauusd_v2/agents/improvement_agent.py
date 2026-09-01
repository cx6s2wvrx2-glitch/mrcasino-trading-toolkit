from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..models import AgentRunResult


class ImprovementProposalState(StrEnum):
    REJECTED_INCOMPLETE = "REJECTED_INCOMPLETE"
    PROPOSAL_ONLY = "PROPOSAL_ONLY"


@dataclass(frozen=True, slots=True)
class ImprovementProposal:
    proposal_id: str
    base_strategy_version: str
    affected_rule_codes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    observed_failure_modes: tuple[str, ...]
    proposed_change: str
    validation_plan: tuple[str, ...]
    rollback_criteria: tuple[str, ...]
    requests_direct_promotion: bool = False


@dataclass(frozen=True, slots=True)
class ImprovementReview:
    state: ImprovementProposalState
    blockers: tuple[str, ...]
    proposal_id: str
    base_strategy_version: str


class ContinuousImprovementAgent:
    """Governance gate for strategy-change proposals.

    It may package evidence-backed improvement proposals, but it cannot mutate
    strategy rules, mark them VERIFIED, or request direct production promotion.
    """

    name = "continuous_improvement_agent_08"
    version = "0.1.0"

    def review_proposal(
        self,
        *,
        proposal: ImprovementProposal,
    ) -> tuple[ImprovementReview, AgentRunResult]:
        blockers: list[str] = []

        if not proposal.proposal_id.strip():
            blockers.append("proposal_id is required")
        if not proposal.base_strategy_version.strip():
            blockers.append("base_strategy_version is required")
        if not tuple(item.strip() for item in proposal.affected_rule_codes if item.strip()):
            blockers.append("at least one affected rule code is required")
        if not tuple(item.strip() for item in proposal.evidence_refs if item.strip()):
            blockers.append("evidence_refs are required")
        if not tuple(item.strip() for item in proposal.observed_failure_modes if item.strip()):
            blockers.append("observed failure modes are required")
        if not proposal.proposed_change.strip():
            blockers.append("proposed_change is required")
        if not tuple(item.strip() for item in proposal.validation_plan if item.strip()):
            blockers.append("validation_plan is required")
        if not tuple(item.strip() for item in proposal.rollback_criteria if item.strip()):
            blockers.append("rollback_criteria are required")
        if proposal.requests_direct_promotion:
            blockers.append("direct promotion is prohibited; proposal must re-enter certification ladder")

        state = (
            ImprovementProposalState.REJECTED_INCOMPLETE
            if blockers
            else ImprovementProposalState.PROPOSAL_ONLY
        )
        review = ImprovementReview(
            state=state,
            blockers=tuple(blockers),
            proposal_id=proposal.proposal_id.strip(),
            base_strategy_version=proposal.base_strategy_version.strip(),
        )
        run = AgentRunResult(
            agent_name=self.name,
            agent_version=self.version,
            input_refs=tuple(
                dict.fromkeys(
                    item.strip()
                    for item in (
                        proposal.proposal_id,
                        proposal.base_strategy_version,
                        *proposal.affected_rule_codes,
                        *proposal.evidence_refs,
                    )
                    if item.strip()
                )
            ),
            payload={
                "state": review.state.value,
                "blockers": list(review.blockers),
                "authority": {
                    "may_modify_strategy_directly": False,
                    "may_mark_verified": False,
                    "may_promote_to_production": False,
                    "may_override_validation_or_risk": False,
                },
            },
            needs_review=True,
        )
        return review, run
