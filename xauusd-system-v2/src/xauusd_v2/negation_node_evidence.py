from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .hcs_semantic import HCSNodeType
from .negation_semantic import ManipulationType, NegationResult, NegationState


class NegationEvidenceKind(StrEnum):
    ORDINARY_FU_NEGATION = "ordinary_fu_negation"
    X3_NEGATION = "x3_negation"
    BETA_SELF_NEGATION_TOGETHER = "beta_self_negation_together"
    NOT_CONFIRMED = "not_confirmed"


@dataclass(frozen=True, slots=True)
class NegationNodeEvidence:
    kind: NegationEvidenceKind
    hcs_node_type: HCSNodeType | None
    semantic_state: NegationState | None
    hcs_node_label_resolved: bool
    raw_negation_semantics_certified: bool
    reason: str


def hcs_node_from_negation_result(
    *,
    result: NegationResult,
    original_type: ManipulationType,
    raw_negation_semantics_certified: bool,
) -> NegationNodeEvidence:
    """Bridge confirmed negation semantics into HCS grammar without conflation.

    Primary HCS material names `FU negation` as an eligible HCS node. Reflection
    separately distinguishes x3 negation and self-negating x3 states. Therefore:

    - confirmed ordinary FU negation -> HCS FU_NEGATION node label;
    - confirmed x3 negation -> preserved as X3_NEGATION, not silently relabelled;
    - non-confirmed semantic results -> no HCS node.

    Certification remains provenance-dependent.
    """

    if result.state is not NegationState.CONFIRMED:
        return NegationNodeEvidence(
            kind=NegationEvidenceKind.NOT_CONFIRMED,
            hcs_node_type=None,
            semantic_state=result.state,
            hcs_node_label_resolved=False,
            raw_negation_semantics_certified=False,
            reason="negation semantics are not confirmed, so no FU-negation HCS node is available",
        )

    if original_type is ManipulationType.FU:
        return NegationNodeEvidence(
            kind=NegationEvidenceKind.ORDINARY_FU_NEGATION,
            hcs_node_type=HCSNodeType.FU_NEGATION,
            semantic_state=result.state,
            hcs_node_label_resolved=True,
            raw_negation_semantics_certified=raw_negation_semantics_certified,
            reason="confirmed ordinary FU negation maps to the source-listed FU_NEGATION HCS node type",
        )

    if original_type is ManipulationType.X3:
        return NegationNodeEvidence(
            kind=NegationEvidenceKind.X3_NEGATION,
            hcs_node_type=None,
            semantic_state=result.state,
            hcs_node_label_resolved=False,
            raw_negation_semantics_certified=raw_negation_semantics_certified,
            reason="confirmed x3 negation is preserved separately; source HCS grammar is not silently extended from FU negation to x3 negation",
        )

    raise ValueError(f"unsupported original manipulation type: {original_type!r}")


def beta_self_negation_together_evidence(*, observed: bool) -> NegationNodeEvidence:
    """Keep BETA same-candle self-negation implementation evidence out of FU negation.

    `sn_together` is useful supplied-code evidence, but it is not the same object as
    a next-candle/+2 ordinary FU negation under Reflection R-123/R-126.
    """

    if not observed:
        return NegationNodeEvidence(
            kind=NegationEvidenceKind.NOT_CONFIRMED,
            hcs_node_type=None,
            semantic_state=None,
            hcs_node_label_resolved=False,
            raw_negation_semantics_certified=False,
            reason="BETA self-negation-together state is not present",
        )

    return NegationNodeEvidence(
        kind=NegationEvidenceKind.BETA_SELF_NEGATION_TOGETHER,
        hcs_node_type=None,
        semantic_state=None,
        hcs_node_label_resolved=False,
        raw_negation_semantics_certified=False,
        reason="BETA self-negation-together is implementation evidence only and is not promoted to an ordinary FU-negation HCS node",
    )
