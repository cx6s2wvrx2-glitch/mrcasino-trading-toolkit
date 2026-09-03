from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import AgentRunResult
from ..primary_context_payload import PrimaryContextPayload
from .base import AgentContractError, StructuredModelClient
from .prompts import VALIDATION_AGENT_SYSTEM


_FOCUSED_VERDICTS = ("SUPPORTED", "CONTRADICTED", "INSUFFICIENT")


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
    """Independent source validator.

    Legacy V1 mode receives only primary source evidence, source locator and the
    batch-wide label taxonomy. Focused V2 mode additionally receives one explicit
    candidate claim/question, while the expected adjudication remains hidden.
    Comparison/promotion always happens outside this agent.
    """

    name = "independent_validation_agent_06"
    version = "0.3.0"

    def __init__(self, client: StructuredModelClient) -> None:
        self.client = client

    @staticmethod
    def _normalize_inputs(
        *, vector_id: str, source_locator: str, allowed_labels: tuple[str, ...]
    ) -> tuple[str, str, tuple[str, ...]]:
        normalized_vector_id = vector_id.strip()
        normalized_locator = source_locator.strip()
        labels = tuple(dict.fromkeys(label.strip() for label in allowed_labels if label.strip()))
        if not normalized_vector_id:
            raise AgentContractError("vector_id is required")
        if not normalized_locator:
            raise AgentContractError("source_locator is required")
        if len(labels) < 2:
            raise AgentContractError("blind validation requires at least two allowed labels")
        return normalized_vector_id, normalized_locator, labels

    @staticmethod
    def _normalize_focus(focus: str, labels: tuple[str, ...]) -> str:
        normalized = focus.strip()
        if not normalized:
            return ""
        if tuple(labels) != _FOCUSED_VERDICTS:
            raise AgentContractError(
                "focused claim adjudication requires taxonomy SUPPORTED/CONTRADICTED/INSUFFICIENT"
            )
        return normalized

    @staticmethod
    def _label_contract(labels: tuple[str, ...], focus: str) -> str:
        if not focus:
            return (
                f"ALLOWED LABEL TAXONOMY: {list(labels)!r}\n\n"
                "LABEL CONTRACT: predicted_label must be either null or one exact string copied verbatim "
                "from ALLOWED LABEL TAXONOMY. Never merge, concatenate, rename, summarize, or invent labels."
            )

        readable_focus = focus.replace("_", " ")
        return (
            "FOCUSED CLAIM ADJUDICATION MODE. The candidate claim below is the QUESTION being reviewed; "
            "it is not an expected answer and it does not imply that the claim is correct.\n"
            f"CANDIDATE CLAIM ID: {focus}\n"
            f"CANDIDATE CLAIM TEXT: {readable_focus}\n"
            f"ALLOWED VERDICTS: {list(labels)!r}\n\n"
            "VERDICT CONTRACT:\n"
            "- SUPPORTED: the supplied primary source directly and clearly supports the candidate claim as written.\n"
            "- CONTRADICTED: the supplied primary source directly conflicts with the candidate claim as written.\n"
            "- INSUFFICIENT: the source does not clearly establish the exact candidate claim, the claim overstates "
            "the source, or material ambiguity remains.\n"
            "Choose exactly one verdict when possible. Do not infer support merely from the wording of the claim; "
            "inspect the actual primary source evidence."
        )

    def _parse_decision(
        self,
        *,
        raw: dict[str, Any],
        vector_id: str,
        source_locator: str,
        labels: tuple[str, ...],
    ) -> tuple[IndependentValidationDecision, AgentRunResult]:
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

    def validate(
        self,
        *,
        vector_id: str,
        source_locator: str,
        source_context: str,
        allowed_labels: tuple[str, ...],
        focus: str = "",
    ) -> tuple[IndependentValidationDecision, AgentRunResult]:
        vector_id, source_locator, labels = self._normalize_inputs(
            vector_id=vector_id,
            source_locator=source_locator,
            allowed_labels=allowed_labels,
        )
        focus = self._normalize_focus(focus, labels)
        source_context = source_context.strip()
        if not source_context:
            raise AgentContractError("source_context is required")

        user_prompt = (
            f"VECTOR ID: {vector_id}\n"
            f"SOURCE LOCATOR: {source_locator}\n"
            f"{self._label_contract(labels, focus)}\n\n"
            f"PRIMARY SOURCE CONTEXT:\n{source_context}"
        )
        constrained_generate = getattr(self.client, "generate_json_with_allowed_labels", None)
        if constrained_generate is not None and callable(constrained_generate):
            raw = constrained_generate(
                system=VALIDATION_AGENT_SYSTEM,
                user=user_prompt,
                allowed_labels=labels,
            )
        else:
            raw = self.client.generate_json(system=VALIDATION_AGENT_SYSTEM, user=user_prompt)
        return self._parse_decision(
            raw=raw,
            vector_id=vector_id,
            source_locator=source_locator,
            labels=labels,
        )

    def validate_multimodal(
        self,
        *,
        vector_id: str,
        source_locator: str,
        source_context: PrimaryContextPayload,
        allowed_labels: tuple[str, ...],
        focus: str = "",
    ) -> tuple[IndependentValidationDecision, AgentRunResult]:
        vector_id, source_locator, labels = self._normalize_inputs(
            vector_id=vector_id,
            source_locator=source_locator,
            allowed_labels=allowed_labels,
        )
        focus = self._normalize_focus(focus, labels)
        payload = source_context.normalized()
        if not payload.images:
            return self.validate(
                vector_id=vector_id,
                source_locator=source_locator,
                source_context=payload.text,
                allowed_labels=labels,
                focus=focus,
            )

        constrained_multimodal_generate = getattr(
            self.client,
            "generate_json_multimodal_with_allowed_labels",
            None,
        )
        multimodal_generate = getattr(self.client, "generate_json_multimodal", None)
        if (
            constrained_multimodal_generate is None
            or not callable(constrained_multimodal_generate)
        ) and (multimodal_generate is None or not callable(multimodal_generate)):
            raise AgentContractError("configured model client does not support primary images")

        source_text = payload.text if payload.text else "[No primary source text; inspect the attached primary source image evidence.]"
        user_prompt = (
            f"VECTOR ID: {vector_id}\n"
            f"SOURCE LOCATOR: {source_locator}\n"
            f"{self._label_contract(labels, focus)}\n\n"
            f"PRIMARY SOURCE TEXT:\n{source_text}\n\n"
            f"PRIMARY SOURCE IMAGES: {len(payload.images)} file(s) supplied out-of-band. "
            "Inspect the actual image evidence; do not infer missing chart content from the locator."
        )
        if constrained_multimodal_generate is not None and callable(constrained_multimodal_generate):
            raw = constrained_multimodal_generate(
                system=VALIDATION_AGENT_SYSTEM,
                user=user_prompt,
                images=payload.images,
                allowed_labels=labels,
            )
        else:
            raw = multimodal_generate(
                system=VALIDATION_AGENT_SYSTEM,
                user=user_prompt,
                images=payload.images,
            )
        return self._parse_decision(
            raw=raw,
            vector_id=vector_id,
            source_locator=source_locator,
            labels=labels,
        )
