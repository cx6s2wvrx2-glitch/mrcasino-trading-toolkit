from __future__ import annotations

from typing import Any, Protocol


class StructuredModelClient(Protocol):
    """Provider-neutral interface. Real OpenAI/Anthropic adapters come later."""

    def generate_json(self, *, system: str, user: str) -> dict[str, Any]: ...


class AgentContractError(ValueError):
    """Raised when an agent output violates a non-negotiable V2 contract."""
