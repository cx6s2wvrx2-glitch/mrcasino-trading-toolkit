from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .agents.base import AgentContractError


@dataclass(frozen=True, slots=True)
class CommandModelClientConfig:
    """Configuration for a provider-independent structured-model subprocess adapter.

    The configured command receives exactly one JSON object on stdin:
    {"system": <system prompt>, "user": <user prompt>}.

    It must emit exactly one JSON object on stdout. API credentials belong in the
    subprocess environment or an external secret manager; they must never be embedded
    in the command arguments, blind packet, runtime manifest, or repository.
    """

    command: tuple[str, ...]
    timeout_seconds: float = 120.0
    environment: Mapping[str, str] | None = None

    @classmethod
    def from_command(
        cls,
        command: Sequence[str],
        *,
        timeout_seconds: float = 120.0,
        environment: Mapping[str, str] | None = None,
    ) -> "CommandModelClientConfig":
        normalized = tuple(str(part).strip() for part in command if str(part).strip())
        if not normalized:
            raise ValueError("external model command is required")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        return cls(command=normalized, timeout_seconds=float(timeout_seconds), environment=environment)


class CommandStructuredModelClient:
    """Run a real external model behind a narrow JSON stdin/stdout contract.

    This adapter deliberately knows nothing about OpenAI, Anthropic, or any other
    provider SDK. That keeps Agent 06 independent from provider libraries and makes
    answer-leakage review possible at one stable boundary.
    """

    def __init__(self, config: CommandModelClientConfig) -> None:
        if not config.command:
            raise ValueError("external model command is required")
        if config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.config = config

    def generate_json(self, *, system: str, user: str) -> dict[str, Any]:
        normalized_system = system.strip()
        normalized_user = user.strip()
        if not normalized_system:
            raise AgentContractError("system prompt is required")
        if not normalized_user:
            raise AgentContractError("user prompt is required")

        request = json.dumps(
            {"system": normalized_system, "user": normalized_user},
            ensure_ascii=False,
            separators=(",", ":"),
        )

        try:
            completed = subprocess.run(
                self.config.command,
                input=request,
                text=True,
                capture_output=True,
                timeout=self.config.timeout_seconds,
                check=False,
                env=None if self.config.environment is None else dict(self.config.environment),
            )
        except subprocess.TimeoutExpired as exc:
            raise AgentContractError("external model command timed out") from exc
        except OSError as exc:
            raise AgentContractError("external model command could not be started") from exc

        if completed.returncode != 0:
            raise AgentContractError(
                f"external model command failed with exit code {completed.returncode}"
            )

        stdout = completed.stdout.strip()
        if not stdout:
            raise AgentContractError("external model command returned empty stdout")

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise AgentContractError("external model command returned invalid JSON") from exc

        if not isinstance(payload, dict):
            raise AgentContractError("external model command must return one JSON object")
        return payload
