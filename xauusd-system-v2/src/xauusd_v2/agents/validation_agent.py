from __future__ import annotations

from dataclasses import dataclass

from ..models import AgentRunResult
from .base import AgentContractError, StructuredModelClient
from .prompts import VALIDATION_AGENT_SYSTEM


@dataclass(frozen=True, slots=True)
class IndependentValidationDecision:
    vector_id: str
    source_locator: str
    predicted_label: str | None
    confidence: float
    evidence: tuple[str, ...]
    ambiguities: tuple[str, ...]

    @property
    def abstained(self) -> bool:
        return self.predicted_label is None


class IndependentValidationAgent:
    """Blind validator.

    This agent is intentionally not given an expected/candidate label. It only
    receives source evidence, a locator, and a label taxonomy. Comparison with
    ground truth happens later in the deterministic validation layer.
    """

    name = "independent_validation_agent_06"
    version = "0.1.0"

    def __init__(self, client: StructuredModelClient) -> None:
        self.client = client

    def validate(
        self,
        *,
        vector_id: str,
        source_locator: str,
        source_context: str,
        allowed_labels: tuple[str, ...],
    ) -> tuple[IndependentValidationDecision, AgentRunResult]:
        vector_id = vector_id.strip()
        source_locator = source_locator.strip()
        source_context = source_context.strip()
        labels = tuple(dict.fromkeys(label.strip() for label in allowed_labels if label.strip()))

        if not vector_id:
            raise AgentContractError("vector_id is required")
        if not source_locator:
            raise AgentContractError("source_locator is required")
        if not source_context:
            raise AgentContractError("source_context is required")
        if len(labels) < 2:
            raise AgentContractError("blind validation requires at least two allowed labels")

        user_prompt = (
            f"VECTOR ID: {vector_id}\n"
            f"SOURCE LOCATOR: {source_locator}\n"
            f"ALLOWED LABEL TAXONOMY: {list(labels)!r}\n\n"
            f"PRIMARY SOURCE CONTEXT:\n{source_context}"
        )
        raw = self.client.generate_json(system=VALIDATION_AGENT_SYSTEM, user=user_prompt)

        raw_label = raw.get("predicted_label")
        predicted_label = None if raw_label is None or not str(raw_label).strip() else str(raw_label).strip()
        if predicted_label is not None and predicted_label not in labels:
            raise AgentContractError(f"validator returned unsupported label: {predicted_label}")

        confidence = float(raw.get("confidence", 0.0))
        if not 0.0 <= confidence <= 1.0:
            raise AgentContractError("confidence must be between 0 and 1")

        evidence = tuple(str(item).strip() for item in raw.get("evidence", []) if str(item).strip())
        ambiguities = tuple(str(item).strip() for item in raw.get("ambiguities", []) if str(item).strip())

        if predicted_label is None and not ambiguities:
            ambiguities = ("Validator abstained without a specific ambiguity; manual review required.",)

        decision = IndependentValidationDecision(
            vector_id=vector_id,
            source_locator=source_locator,
            predicted_label=predicted_label,
            confidence=confidence,
            evidence=evidence,
            ambiguities=ambiguities,
        )
        result = AgentRunResult(
            agent_name=self.name,
            agent_version=self.version,
            input_refs=(vector_id, source_locator),
            payload=raw,
            needs_review=True,
        )
        return decision, result
