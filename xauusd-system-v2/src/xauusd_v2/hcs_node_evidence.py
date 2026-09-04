from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .casino_marker_semantics import (
    CasinoMarkerMeaning,
    CasinoVisibleMarker,
    semantic_for_visible_marker,
)
from .hcs_semantic import HCSNodeType, HCSResult, HCSRetestState, HCSState, evaluate_hcs


class HCSNodeEvidenceSource(StrEnum):
    USER_CLARIFIED_CASINO_MARKER = "user_clarified_casino_marker"
    SOURCE_LABELLED = "source_labelled"
    RAW_DERIVED_UNCERTIFIED = "raw_derived_uncertified"


@dataclass(frozen=True, slots=True)
class HCSNodeEvidence:
    node_type: HCSNodeType
    source: HCSNodeEvidenceSource
    source_label: str
    visible_marker: CasinoVisibleMarker | None
    node_label_resolved: bool
    raw_node_semantics_certified: bool


@dataclass(frozen=True, slots=True)
class HCSResearchEvaluation:
    grammar_result: HCSResult
    first_node: HCSNodeEvidence
    second_node: HCSNodeEvidence
    retest_semantics_certified: bool
    hcs_strategy_certified: bool
    reason: str


def hcs_node_from_casino_marker(marker: CasinoVisibleMarker) -> HCSNodeEvidence:
    """Map the user-clarified Casino marker legend into HCS node vocabulary.

    This resolves the node *label* only. It does not certify the helper's raw
    strategy semantics or any universal Strong-FU threshold.
    """

    semantic = semantic_for_visible_marker(marker)
    if semantic.meaning is CasinoMarkerMeaning.STRONG_FU:
        node_type = HCSNodeType.STRONG_FU
    elif semantic.meaning is CasinoMarkerMeaning.ATTEMPTED_FU:
        node_type = HCSNodeType.ATTEMPTED_FU
    else:  # pragma: no cover - defensive for future enum expansion
        raise ValueError(f"unsupported Casino marker meaning: {semantic.meaning!r}")

    return HCSNodeEvidence(
        node_type=node_type,
        source=HCSNodeEvidenceSource.USER_CLARIFIED_CASINO_MARKER,
        source_label=f"Casino visible marker {marker.value}",
        visible_marker=marker,
        node_label_resolved=True,
        raw_node_semantics_certified=False,
    )


def evaluate_hcs_research_evidence(
    *,
    first_node: HCSNodeEvidence,
    second_node: HCSNodeEvidence,
    retest_state: HCSRetestState,
    retest_semantics_certified: bool,
) -> HCSResearchEvaluation:
    """Run HCS grammar while preserving evidence provenance and certification.

    `evaluate_hcs` answers the semantic grammar question *assuming* eligible node
    types and retest evidence are already supplied. This wrapper prevents a
    user-clarified indicator marker from silently becoming certified raw HCS truth.
    """

    grammar = evaluate_hcs(
        first_node=first_node.node_type,
        second_node=second_node.node_type,
        retest_state=retest_state,
    )

    certified = (
        grammar.state is HCSState.CONFIRMED
        and first_node.raw_node_semantics_certified
        and second_node.raw_node_semantics_certified
        and retest_semantics_certified
    )

    if certified:
        reason = "HCS grammar is confirmed and both node semantics plus retest semantics are independently certified"
    elif grammar.state is HCSState.CONFIRMED:
        reason = (
            "HCS grammar is satisfied by the supplied node labels/retest state, but provenance is not sufficient "
            "for certified raw HCS strategy truth"
        )
    else:
        reason = "HCS grammar itself is not confirmed for the supplied evidence"

    return HCSResearchEvaluation(
        grammar_result=grammar,
        first_node=first_node,
        second_node=second_node,
        retest_semantics_certified=retest_semantics_certified,
        hcs_strategy_certified=certified,
        reason=reason,
    )
