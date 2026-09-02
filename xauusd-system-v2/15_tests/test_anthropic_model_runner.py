from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from xauusd_v2.anthropic_model_runner import (
    ANTHROPIC_MESSAGES_URL,
    AnthropicRunnerConfig,
    AnthropicRunnerError,
    build_anthropic_request,
    call_anthropic,
    parse_anthropic_response,
)


PNG = b"\x89PNG\r\n\x1a\n" + b"A" * 64


class _Response:
    def __init__(self, payload: dict) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


class AnthropicModelRunnerTests(unittest.TestCase):
    def config(self) -> AnthropicRunnerConfig:
        return AnthropicRunnerConfig(api_key="secret-test-key", model="explicit-test-model")

    def decision_response(self, *, text: str | None = None, stop_reason: str = "end_turn") -> dict:
        if text is None:
            text = json.dumps(
                {
                    "predicted_label": "candidate-a",
                    "confidence": 0.75,
                    "evidence": ["source visual evidence"],
                    "ambiguities": [],
                }
            )
        return {
            "id": "msg_test",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": text}],
            "model": "explicit-test-model",
            "stop_reason": stop_reason,
        }

    def test_environment_requires_key_and_explicit_model(self) -> None:
        with self.assertRaisesRegex(AnthropicRunnerError, "ANTHROPIC_API_KEY"):
            AnthropicRunnerConfig.from_environment({})
        with self.assertRaisesRegex(AnthropicRunnerError, "XAUUSD_AGENT06_ANTHROPIC_MODEL"):
            AnthropicRunnerConfig.from_environment({"ANTHROPIC_API_KEY": "key"})
        config = AnthropicRunnerConfig.from_environment(
            {
                "ANTHROPIC_API_KEY": "key",
                "XAUUSD_AGENT06_ANTHROPIC_MODEL": "model-name",
                "XAUUSD_AGENT06_ANTHROPIC_MAX_TOKENS": "4096",
                "XAUUSD_AGENT06_ANTHROPIC_TIMEOUT_SECONDS": "45",
            }
        )
        self.assertEqual(config.model, "model-name")
        self.assertEqual(config.max_tokens, 4096)
        self.assertEqual(config.timeout_seconds, 45.0)

    def test_text_request_uses_structured_output_schema(self) -> None:
        payload = build_anthropic_request(
            {"system": "system", "user": "user"},
            self.config(),
        )
        self.assertEqual(payload["model"], "explicit-test-model")
        self.assertEqual(payload["system"], "system")
        content = payload["messages"][0]["content"]
        self.assertEqual(content, [{"type": "text", "text": "user"}])
        schema = payload["output_config"]["format"]["schema"]
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            set(schema["required"]),
            {"predicted_label", "confidence", "evidence", "ambiguities"},
        )

    def test_multimodal_request_base64_encodes_verified_primary_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "source.png"
            path.write_bytes(PNG)
            payload = build_anthropic_request(
                {
                    "system": "system",
                    "user": "user",
                    "images": [
                        {
                            "path": str(path),
                            "mime_type": "image/png",
                            "sha256": hashlib.sha256(PNG).hexdigest(),
                            "size_bytes": len(PNG),
                        }
                    ],
                },
                self.config(),
            )
            content = payload["messages"][0]["content"]
            self.assertEqual(content[0]["type"], "image")
            self.assertEqual(content[0]["source"]["type"], "base64")
            self.assertEqual(content[0]["source"]["media_type"], "image/png")
            self.assertEqual(content[-1], {"type": "text", "text": "user"})

    def test_mutated_primary_image_fails_before_provider_call(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "source.png"
            path.write_bytes(PNG)
            metadata = {
                "path": str(path),
                "mime_type": "image/png",
                "sha256": hashlib.sha256(PNG).hexdigest(),
                "size_bytes": len(PNG),
            }
            path.write_bytes(PNG + b"mutated")
            with self.assertRaisesRegex(AnthropicRunnerError, "size changed"):
                build_anthropic_request(
                    {"system": "system", "user": "user", "images": [metadata]},
                    self.config(),
                )

    def test_valid_api_response_returns_only_decision_object(self) -> None:
        response = self.decision_response()
        with patch("urllib.request.urlopen", return_value=_Response(response)) as urlopen:
            result = call_anthropic({"system": "system", "user": "user"}, self.config())
        self.assertEqual(result["predicted_label"], "candidate-a")
        self.assertEqual(result["confidence"], 0.75)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, ANTHROPIC_MESSAGES_URL)
        self.assertNotIn("secret-test-key", json.dumps(result))

    def test_http_error_fails_closed_without_response_body_or_key(self) -> None:
        error = urllib.error.HTTPError(
            ANTHROPIC_MESSAGES_URL,
            429,
            "rate limited with secret-test-key",
            hdrs=None,
            fp=None,
        )
        with patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaisesRegex(AnthropicRunnerError, "HTTP 429") as raised:
                call_anthropic({"system": "system", "user": "user"}, self.config())
        self.assertNotIn("secret-test-key", str(raised.exception))

    def test_non_end_turn_response_fails_closed(self) -> None:
        with self.assertRaisesRegex(AnthropicRunnerError, "end_turn"):
            parse_anthropic_response(self.decision_response(stop_reason="max_tokens"))

    def test_malformed_or_extra_structured_fields_fail_closed(self) -> None:
        with self.assertRaisesRegex(AnthropicRunnerError, "valid JSON"):
            parse_anthropic_response(self.decision_response(text="not-json"))
        extra = json.dumps(
            {
                "predicted_label": None,
                "confidence": 0.0,
                "evidence": [],
                "ambiguities": ["uncertain"],
                "unexpected": "field",
            }
        )
        with self.assertRaisesRegex(AnthropicRunnerError, "unexpected fields"):
            parse_anthropic_response(self.decision_response(text=extra))


if __name__ == "__main__":
    unittest.main()
