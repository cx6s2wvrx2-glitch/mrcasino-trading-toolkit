from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
_ALLOWED_IMAGE_MIME = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_MAX_IMAGE_BYTES = 25 * 1024 * 1024
_MAX_TOTAL_IMAGE_BYTES = 100 * 1024 * 1024

# Anthropic structured outputs do not accept numeric minimum/maximum constraints
# in raw JSON schemas. Keep the wire schema provider-compatible and enforce the
# 0..1 confidence contract after the response is returned in
# _validate_decision_payload().
_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "predicted_label": {"type": ["string", "null"]},
        "confidence": {
            "type": "number",
            "description": "Confidence from 0.0 to 1.0 inclusive; validated again locally.",
        },
        "evidence": {"type": "array", "items": {"type": "string"}},
        "ambiguities": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["predicted_label", "confidence", "evidence", "ambiguities"],
    "additionalProperties": False,
}


class AnthropicRunnerError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class AnthropicRunnerConfig:
    api_key: str
    model: str
    max_tokens: int = 2048
    timeout_seconds: float = 120.0
    workspace_id: str | None = None

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "AnthropicRunnerConfig":
        env = os.environ if environment is None else environment
        api_key = str(env.get("ANTHROPIC_API_KEY", "")).strip()
        model = str(env.get("XAUUSD_AGENT06_ANTHROPIC_MODEL", "")).strip()
        if not api_key:
            raise AnthropicRunnerError("ANTHROPIC_API_KEY is required")
        if not model:
            raise AnthropicRunnerError("XAUUSD_AGENT06_ANTHROPIC_MODEL is required")
        try:
            max_tokens = int(str(env.get("XAUUSD_AGENT06_ANTHROPIC_MAX_TOKENS", "2048")))
            timeout_seconds = float(str(env.get("XAUUSD_AGENT06_ANTHROPIC_TIMEOUT_SECONDS", "120")))
        except ValueError as exc:
            raise AnthropicRunnerError("invalid Anthropic runner numeric configuration") from exc
        if max_tokens <= 0:
            raise AnthropicRunnerError("Anthropic max tokens must be positive")
        if timeout_seconds <= 0:
            raise AnthropicRunnerError("Anthropic timeout must be positive")
        workspace_id = str(env.get("ANTHROPIC_WORKSPACE_ID", "")).strip() or None
        return cls(
            api_key=api_key,
            model=model,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            workspace_id=workspace_id,
        )


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _load_verified_image(item: object) -> tuple[bytes, str]:
    if not isinstance(item, dict):
        raise AnthropicRunnerError("image metadata must be an object")
    path_raw = str(item.get("path", "")).strip()
    mime_type = str(item.get("mime_type", "")).strip().lower()
    expected_sha = str(item.get("sha256", "")).strip().lower()
    try:
        expected_size = int(item.get("size_bytes"))
    except (TypeError, ValueError) as exc:
        raise AnthropicRunnerError("image size metadata is invalid") from exc
    if not path_raw:
        raise AnthropicRunnerError("image path is required")
    if mime_type not in _ALLOWED_IMAGE_MIME:
        raise AnthropicRunnerError("unsupported Anthropic image MIME type")
    if len(expected_sha) != 64 or any(ch not in "0123456789abcdef" for ch in expected_sha):
        raise AnthropicRunnerError("image SHA-256 metadata is invalid")
    if expected_size <= 0 or expected_size > _MAX_IMAGE_BYTES:
        raise AnthropicRunnerError("image size is outside runner safety limits")

    path = Path(path_raw)
    if not path.is_file():
        raise AnthropicRunnerError("primary image file is unavailable")
    payload = path.read_bytes()
    if len(payload) != expected_size:
        raise AnthropicRunnerError("primary image size changed before provider call")
    if _sha256(payload) != expected_sha:
        raise AnthropicRunnerError("primary image SHA-256 changed before provider call")
    return payload, mime_type


def _normalize_command_request(value: object) -> tuple[str, str, tuple[dict[str, Any], ...]]:
    if not isinstance(value, dict):
        raise AnthropicRunnerError("runner stdin must contain one JSON object")
    system = str(value.get("system", "")).strip()
    user = str(value.get("user", "")).strip()
    if not system:
        raise AnthropicRunnerError("system prompt is required")
    if not user:
        raise AnthropicRunnerError("user prompt is required")
    images_raw = value.get("images", [])
    if not isinstance(images_raw, list):
        raise AnthropicRunnerError("images must be an array")
    return system, user, tuple(images_raw)


def build_anthropic_request(command_request: object, config: AnthropicRunnerConfig) -> dict[str, Any]:
    system, user, image_items = _normalize_command_request(command_request)

    content: list[dict[str, Any]] = []
    total_image_bytes = 0
    for item in image_items:
        payload, mime_type = _load_verified_image(item)
        total_image_bytes += len(payload)
        if total_image_bytes > _MAX_TOTAL_IMAGE_BYTES:
            raise AnthropicRunnerError("total primary image payload exceeds runner safety limit")
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": base64.b64encode(payload).decode("ascii"),
                },
            }
        )
    content.append({"type": "text", "text": user})

    return {
        "model": config.model,
        "max_tokens": config.max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": content}],
        "output_config": {
            "format": {
                "type": "json_schema",
                "schema": _OUTPUT_SCHEMA,
            }
        },
    }


def _validate_decision_payload(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AnthropicRunnerError("Anthropic structured output must be a JSON object")
    expected_keys = {"predicted_label", "confidence", "evidence", "ambiguities"}
    if set(value) != expected_keys:
        raise AnthropicRunnerError("Anthropic structured output has unexpected fields")
    label = value["predicted_label"]
    if label is not None and not isinstance(label, str):
        raise AnthropicRunnerError("predicted_label must be a string or null")
    confidence = value["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise AnthropicRunnerError("confidence must be numeric")
    if not 0.0 <= float(confidence) <= 1.0:
        raise AnthropicRunnerError("confidence must be between 0 and 1")
    for key in ("evidence", "ambiguities"):
        items = value[key]
        if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
            raise AnthropicRunnerError(f"{key} must be an array of strings")
    return {
        "predicted_label": label,
        "confidence": float(confidence),
        "evidence": value["evidence"],
        "ambiguities": value["ambiguities"],
    }


def parse_anthropic_response(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AnthropicRunnerError("Anthropic response must be a JSON object")
    if value.get("type") != "message":
        raise AnthropicRunnerError("Anthropic response is not a message")
    stop_reason = value.get("stop_reason")
    if stop_reason != "end_turn":
        if stop_reason == "max_tokens":
            raise AnthropicRunnerError("Anthropic response stopped at max_tokens")
        if stop_reason == "refusal":
            raise AnthropicRunnerError("Anthropic response stopped with refusal")
        raise AnthropicRunnerError("Anthropic response did not complete with end_turn")
    content = value.get("content")
    if not isinstance(content, list):
        raise AnthropicRunnerError("Anthropic response content is invalid")
    text_blocks = [
        str(block.get("text", ""))
        for block in content
        if isinstance(block, dict) and block.get("type") == "text" and str(block.get("text", "")).strip()
    ]
    if len(text_blocks) != 1:
        raise AnthropicRunnerError("Anthropic response must contain exactly one structured text block")
    try:
        payload = json.loads(text_blocks[0])
    except json.JSONDecodeError as exc:
        raise AnthropicRunnerError("Anthropic structured output is not valid JSON") from exc
    return _validate_decision_payload(payload)


def _read_http_error_message(exc: urllib.error.HTTPError) -> str:
    try:
        body = exc.read()
    except Exception:
        return ""
    if not body:
        return ""
    try:
        value = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
        return ""
    if not isinstance(value, dict):
        return ""
    error = value.get("error")
    if not isinstance(error, dict):
        return ""
    return str(error.get("message", "")).strip().lower()


def _http_error_code(exc: urllib.error.HTTPError) -> str:
    status = int(exc.code)
    if status == 400:
        message = _read_http_error_message(exc)
        if "credit balance" in message or "billing" in message:
            return "ANTHROPIC_HTTP_400_BILLING"
        if "spend limit" in message:
            return "ANTHROPIC_HTTP_400_SPEND_LIMIT"
        if "model" in message and any(term in message for term in ("access", "available", "not found", "invalid")):
            return "ANTHROPIC_HTTP_400_MODEL"
    return f"ANTHROPIC_HTTP_{status}"


def call_anthropic(command_request: object, config: AnthropicRunnerConfig) -> dict[str, Any]:
    request_payload = build_anthropic_request(command_request, config)
    encoded = json.dumps(request_payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {
        "content-type": "application/json",
        "anthropic-version": ANTHROPIC_API_VERSION,
        "x-api-key": config.api_key,
        "user-agent": "xauusd-v2-agent06/0.1",
    }
    if config.workspace_id is not None:
        headers["anthropic-workspace-id"] = config.workspace_id
    request = urllib.request.Request(
        ANTHROPIC_MESSAGES_URL,
        data=encoded,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
            response_bytes = response.read()
    except urllib.error.HTTPError as exc:
        safe_code = _http_error_code(exc)
        raise AnthropicRunnerError(f"Anthropic API returned HTTP {exc.code} [{safe_code}]") from exc
    except urllib.error.URLError as exc:
        raise AnthropicRunnerError("Anthropic API request failed") from exc
    except TimeoutError as exc:
        raise AnthropicRunnerError("Anthropic API request timed out") from exc

    try:
        raw_response = json.loads(response_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AnthropicRunnerError("Anthropic API returned invalid JSON") from exc
    return parse_anthropic_response(raw_response)


def run_stdin_stdout(
    *,
    stdin_text: str,
    environment: Mapping[str, str] | None = None,
) -> str:
    try:
        command_request = json.loads(stdin_text)
    except json.JSONDecodeError as exc:
        raise AnthropicRunnerError("runner stdin is invalid JSON") from exc
    config = AnthropicRunnerConfig.from_environment(environment)
    decision = call_anthropic(command_request, config)
    return json.dumps(decision, ensure_ascii=False, separators=(",", ":"))


def _safe_runner_error_code(exc: AnthropicRunnerError) -> str:
    message = str(exc)
    bracketed = re.search(r"\[(ANTHROPIC_HTTP_[A-Z0-9_]+)\]", message)
    if bracketed is not None:
        return bracketed.group(1)
    if message == "ANTHROPIC_API_KEY is required":
        return "ANTHROPIC_CONFIG_KEY_MISSING"
    if message == "XAUUSD_AGENT06_ANTHROPIC_MODEL is required":
        return "ANTHROPIC_CONFIG_MODEL_MISSING"
    if message == "Anthropic API request failed":
        return "ANTHROPIC_NETWORK_ERROR"
    if message == "Anthropic API request timed out":
        return "ANTHROPIC_TIMEOUT"
    if message == "Anthropic response stopped at max_tokens":
        return "ANTHROPIC_STOP_MAX_TOKENS"
    if message == "Anthropic response stopped with refusal":
        return "ANTHROPIC_STOP_REFUSAL"
    return "ANTHROPIC_RUNNER_CONTRACT_ERROR"


def main() -> int:
    try:
        stdin_text = sys.stdin.read()
        stdout_text = run_stdin_stdout(stdin_text=stdin_text)
    except AnthropicRunnerError as exc:
        print(f"model-runner-safe-error: {_safe_runner_error_code(exc)}", file=sys.stderr)
        print(f"anthropic-runner-error: {exc}", file=sys.stderr)
        return 2
    print(stdout_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
