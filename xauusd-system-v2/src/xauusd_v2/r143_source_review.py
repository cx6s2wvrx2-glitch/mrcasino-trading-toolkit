from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .r143_source_evidence_adapter import records_from_r143_source_evidence
from .strategy_evidence_sequence import evaluate_r143_evidence
from .strategy_sequence_review import render_strategy_sequence_review


def render_r143_source_review(payload: Mapping[str, Any]) -> str:
    """Render one source-labelled R-143 episode as a Phase-3 Greek review.

    The output preserves the distinction between explicit source evidence and
    machine certification. Partial/unresolved source stages stay BLOCKED.
    """
    records = records_from_r143_source_evidence(payload)
    sequence = evaluate_r143_evidence(records)

    episode_id = payload.get("episode_id", "unknown")
    source_locator = payload.get("source_locator", "unknown")

    review = render_strategy_sequence_review(records)
    next_stage = sequence.next_required_stage.name if sequence.next_required_stage is not None else "NONE"
    highest = sequence.highest_completed_stage.name if sequence.highest_completed_stage is not None else "NONE"

    return "\n".join(
        [
            f"SOURCE EPISODE: {episode_id}",
            f"SOURCE LOCATOR: {source_locator}",
            "SOURCE LABELS != MACHINE CERTIFICATION",
            "",
            review,
            "",
            "R-143 ΑΞΙΟΛΟΓΗΣΗ SOURCE PACKET",
            f"state={sequence.state.value}",
            f"highest_completed_stage={highest}",
            f"next_required_stage={next_stage}",
            f"reason={sequence.reason}",
            "complete_source_sequence_claim=false unless independently established by the source packet",
            "performance_claim_allowed=false",
            "live_execution_authorized=false",
        ]
    )
