from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .agents.base import AgentContractError
from .primary_context_payload import PrimaryImageEvidence


_SAFE_RUNNER_ERROR_PREFIX = "model-runner-safe-error: "
_SAFE_RUNNER_ERROR_CODE = re.compile(r"^[A-Z0-9_:-]{1,80}$")


def _extract_safe_runner_error_code(stderr: str) -> str | None:
    """Return only an explicitly marked, tightly constrained diagnostic code.

    Arbitrary subprocess stderr remains hidden. Provider wrappers may emit one
    machine-safe code such as ``ANTHROPIC_HTTP_401`` for operator diagnostics;
    free-form error text, response bodies and credentials are never propagated.
    """

    for line in stderr.splitlines():
        if not line.startswith(_SAFE_RUNNER_ERROR_PREFIX):
            continue
        code = line[len(_SAFE_RUNNER_ERROR_PREFIX) :].strip()
        if _SAFE_RUNNER_ERROR_CODE.fullmatch(code):
            return code
    return None


def _normalize_allowed_labels(allowed_labels: Sequence[str]) -> tuple[str, ...]:
    labels = tuple(dict.fromkeys(str(label).strip() for label in allowed_labels if str(label).strip()))
    if len(labels) < 2:
        raise AgentContractError("blind validation requires at least two allowed labels")
    return labels


@dataclass(frozen=True, slots=True)
class CommandModelClientConfig:
    """Configuration for a provider-independent structured-model subprocess adapter.

    The configured command receives exactly one JSON object on stdin. Text-only calls
    contain {"system", "user"}. Multimodal calls additionally contain an `images`
    array with local primary-source file path, MIME type, SHA-256 and size metadata.
    Agent-06 classification calls may also include an `allowed_labels` array so the
    provider wrapper can enforce the frozen batch taxonomy in its native structured
    output schema.

    The subprocess is responsible for sending those source files to the real model
    provider. API credentials belong in the subprocess environment or an external
    secret manager; they must never be embedded in command arguments, blind packets,
    runtime manifests, or repository files.
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
    provider SDK. Provider-specific wrappers remain outside Agent 06. That keeps the
    blind boundary reviewable and lets the same validator run against a genuinely
    independent model later.
    """

    def __init__(self, config: CommandModelClientConfig) -> None:
        if not config.command:
            raise ValueError("external model command is required")
        if config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.config = config

    def _run_request(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        request = json.dumps(
            request_payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        environment = None
        if self.config.environment is not None:
            environment = dict(os.environ)
            environment.update({str(key): str(value) for key, value in self.config.environment.items()})

        try:
            completed = subprocess.run(
                self.config.command,
                input=request,
                text=True,
                capture_output=True,
                timeout=self.config.timeout_seconds,
                check=False,
                env=environment,
            )
        except subprocess.TimeoutExpired as exc:
            raise AgentContractError("external model command timed out") from exc
        except OSError as exc:
            raise AgentContractError("external model command could not be started") from exc

        if completed.returncode != 0:
            safe_code = _extract_safe_runner_error_code(completed.stderr)
            suffix = f" ({safe_code})" if safe_code is not None else ""
            raise AgentContractError(
                f"external model command failed with exit code {completed.returncode}{suffix}"
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

    def generate_json(self, *, system: str, user: str) -> dict[str, Any]:
        normalized_system = system.strip()
        normalized_user = user.strip()
        if not normalized_system:
            raise AgentContractError("system prompt is required")
        if not normalized_user:
            raise AgentContractError("user prompt is required")
        return self._run_request({"system": normalized_system, "user": normalized_user})

    def generate_json_with_allowed_labels(
        self,
        *,
        system: str,
        user: str,
        allowed_labels: Sequence[str],
    ) -> dict[str, Any]:
        normalized_system = system.strip()
        normalized_user = user.strip()
        if not normalized_system:
            raise AgentContractError("system prompt is required")
        if not normalized_user:
            raise AgentContractError("user prompt is required")
        labels = _normalize_allowed_labels(allowed_labels)
        return self._run_request(
            {
                "system": normalized_system,
                "user": normalized_user,
                "allowed_labels": list(labels),
            }
        )

    def generate_json_multimodal(
        self,
        *,
        system: str,
        user: str,
        images: tuple[PrimaryImageEvidence, ...],
    ) -> dict[str, Any]:
        normalized_system = system.strip()
        normalized_user = user.strip()
        if not normalized_system:
            raise AgentContractError("system prompt is required")
        if not normalized_user:
            raise AgentContractError("user prompt is required")
        if not images:
            raise AgentContractError("multimodal call requires at least one primary image")

        serialized_images: list[dict[str, Any]] = []
        for image in images:
            image.verify()
            serialized_images.append(
                {
                    "path": image.path,
                    "mime_type": image.mime_type,
                    "sha256": image.sha256,
                    "size_bytes": image.size_bytes,
                }
            )
        return self._run_request(
            {
                "system": normalized_system,
                "user": normalized_user,
                "images": serialized_images,
            }
        )

    def generate_json_multimodal_with_allowed_labels(
        self,
        *,
        system: str,
        user: str,
        images: tuple[PrimaryImageEvidence, ...],
        allowed_labels: Sequence[str],
    ) -> dict[str, Any]:
        normalized_system = system.strip()
        normalized_user = user.strip()
        if not normalized_system:
            raise AgentContractError("system prompt is required")
        if not normalized_user:
            raise AgentContractError("user prompt is required")
        if not images:
            raise AgentContractError("multimodal call requires at least one primary image")
        labels = _normalize_allowed_labels(allowed_labels)

        serialized_images: list[dict[str, Any]] = []
        for image in images:
            image.verify()
            serialized_images.append(
                {
                    "path": image.path,
                    "mime_type": image.mime_type,
                    "sha256": image.sha256,
                    "size_bytes": image.size_bytes,
                }
            )
        return self._run_request(
            {
                "system": normalized_system,
                "user": normalized_user,
                "images": serialized_images,
                "allowed_labels": list(labels),
            }
        )
