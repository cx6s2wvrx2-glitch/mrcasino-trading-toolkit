from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .agents.validation_agent import IndependentValidationAgent, IndependentValidationDecision
from .blind_validation_packet import BlindValidationPacket


@dataclass(frozen=True, slots=True)
class BlindValidationBatchResult:
    decisions: tuple[IndependentValidationDecision, ...]

    @property
    def predictions(self) -> dict[str, str | None]:
        return {decision.vector_id: decision.predicted_label for decision in self.decisions}


def run_blind_validation_batch(
    *,
    packet: BlindValidationPacket,
    agent: IndependentValidationAgent,
    source_context_resolver: Callable[[str], str],
) -> BlindValidationBatchResult:
    """Run Agent 06 without exposing ground-truth answers.

    The runner only accepts a blind packet, whose case schema contains no expected
    label/class/evidence fields. Source text/chart context is resolved separately by
    locator. Comparison to ground truth must happen later via `validation.py`.
    """
    decisions: list[IndependentValidationDecision] = []
    for case in packet.cases:
        source_context = source_context_resolver(case.source_locator).strip()
        if not source_context:
            raise ValueError(f"source context resolver returned empty content for {case.vector_id}")
        decision, _ = agent.validate(
            vector_id=case.vector_id,
            source_locator=case.source_locator,
            source_context=source_context,
            allowed_labels=packet.taxonomy,
        )
        decisions.append(decision)

    return BlindValidationBatchResult(decisions=tuple(decisions))
