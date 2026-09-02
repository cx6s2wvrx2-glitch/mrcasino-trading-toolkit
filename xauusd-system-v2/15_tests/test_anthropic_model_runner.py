from __future__ import annotations

import hashlib
import io
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
    _safe_runner_error_code,
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
        confidence_schema = schema["properties"]["confidence"]
        self.assertEqual(confidence_schema["type"], "number")
        self.assertNotIn("minimum", confidence_schema)
        self.assertNotIn("maximum", confidence_schema)

    def test_173_allowed_labels_use_compact_index_schema_not_large_enum(self) -> None:
        labels = [f"taxonomy_label_{index:03d}_with_realistic_suffix" for index in range(173)]
        payload = build_anthropic_request(
            {
                "system": "system",
                "user": f"ALLOWED LABEL TAXONOMY: {labels!r}",
                "allowed_labels": labels,
            },
            self.config(),
        )
        schema = payload["output_config"]["format"]["schema"]
        self.assertEqual(
            set(schema["required"]),
            {"predicted_label_index", "confidence", "evidence", "ambiguities"},
        )
        index_schema = schema["properties"]["predicted_label_index"]
        self.assertEqual(index_schema["type"], ["integer", "null"])
        self.assertNotIn("enum", index_schema)
        self.assertNotIn("predicted_label", schema["properties"])
        schema_text = json.dumps(schema)
        self.assertNotIn(labels[0], schema_text)
        self.assertNotIn(labels[-1], schema_text)
        content = payload["messages"][0]["content"]
        self.assertIn("ZERO-BASED", content[-1]["text"])
        self.assertIn("predicted_label_index", content[-1]["text"])

    def test_indexed_response_maps_back_to_exact_taxonomy_label(self) -> None:
        labels = ("att_fu_hcs", "hcs_zone_respected_once", "no_trade")
        text = json.dumps(
            {
                "predicted_label_index": 1,
                "confidence": 0.8,
                "evidence": ["source evidence"],
                "ambiguities": [],
            }
        )
        result = parse_anthropic_response(self.decision_response(text=text), allowed_labels=labels)
        self.assertEqual(result["predicted_label"], "hcs_zone_respected_once")
        self.assertNotEqual(result["predicted_label"], "att_fu_hcs_hcs_zone_respected_once")

    def test_out_of_range_taxonomy_index_is_rejected_fail_closed(self) -> None:
        labels = ("att_fu_hcs", "hcs_zone_respected_once", "no_trade")
        text = json.dumps(
            {
                "predicted_label_index": 3,
                "confidence": 0.8,
                "evidence": ["source evidence"],
                "ambiguities": [],
            }
        )
        with self.assertRaisesRegex(AnthropicRunnerError, "outside frozen taxonomy") as raised:
            parse_anthropic_response(self.decision_response(text=text), allowed_labels=labels)
        self.assertEqual(
            _safe_runner_error_code(raised.exception),
            "ANTHROPIC_LABEL_INDEX_OUTSIDE_TAXONOMY",
        )

    def test_invalid_allowed_label_payload_fails_before_provider_call(self) -> None:
        with self.assertRaisesRegex(AnthropicRunnerError, "at least two"):
            build_anthropic_request(
                {"system": "system", "user": "user", "allowed_labels": ["only-one"]},
                self.config(),
            )
        with self.assertRaisesRegex(AnthropicRunnerError, "only strings"):
            build_anthropic_request(
                {"system": "system", "user": "user", "allowed_labels": ["valid", 7]},
                self.config(),
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

    def test_call_anthropic_maps_indexed_provider_response_before_stdout_contract(self) -> None:
        text = json.dumps(
            {
                "predicted_label_index": 1,
                "confidence": 0.75,
                "evidence": ["source visual evidence"],
                "ambiguities": [],
            }
        )
        response = self.decision_response(text=text)
        with patch("urllib.request.urlopen", return_value=_Response(response)):
            result = call_anthropic(
                {
                    "system": "system",
                    "user": "ALLOWED LABEL TAXONOMY: ['candidate-b', 'candidate-c']",
                    "allowed_labels": ["candidate-b", "candidate-c"],
                },
                self.config(),
            )
        self.assertEqual(result["predicted_label"], "candidate-c")
        self.assertNotIn("predicted_label_index", result)

    def test_confidence_range_is_enforced_locally_after_provider_response(self) -> None:
        text = json.dumps(
            {
                "predicted_label": "candidate-a",
                "confidence": 1.25,
                "evidence": [],
                "ambiguities": [],
            }
        )
        with self.assertRaisesRegex(AnthropicRunnerError, "between 0 and 1"):
            parse_anthropic_response(self.decision_response(text=text))

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
        self.assertEqual(_safe_runner_error_code(raised.exception), "ANTHROPIC_HTTP_429")

    def test_billing_http_400_is_reduced_to_safe_code(self) -> None:
        body = io.BytesIO(
            json.dumps(
                {
                    "type": "error",
                    "error": {
                        "type": "invalid_request_error",
                        "message": "Your credit balance is too low to access the Anthropic API",
                    },
                }
            ).encode("utf-8")
        )
        error = urllib.error.HTTPError(
            ANTHROPIC_MESSAGES_URL,
            400,
            "bad request",
            hdrs=None,
            fp=body,
        )
        with patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(AnthropicRunnerError) as raised:
                call_anthropic({"system": "system", "user": "user"}, self.config())
        self.assertEqual(_safe_runner_error_code(raised.exception), "ANTHROPIC_HTTP_400_BILLING")
        self.assertNotIn("credit balance", str(raised.exception).lower())

    def test_schema_complexity_http_400_is_reduced_to_safe_code(self) -> None:
        body = io.BytesIO(
            json.dumps(
                {
                    "type": "error",
                    "error": {
                        "type": "invalid_request_error",
                        "message": "Schema is too complex for compilation.",
                    },
                }
            ).encode("utf-8")
        )
        error = urllib.error.HTTPError(
            ANTHROPIC_MESSAGES_URL,
            400,
            "bad request",
            hdrs=None,
            fp=body,
        )
        with patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(AnthropicRunnerError) as raised:
                call_anthropic({"system": "system", "user": "user"}, self.config())
        self.assertEqual(
            _safe_runner_error_code(raised.exception),
            "ANTHROPIC_HTTP_400_SCHEMA_COMPLEX",
        )
        self.assertNotIn("schema is too complex", str(raised.exception).lower())

    def test_non_end_turn_response_fails_closed(self) -> None:
        with self.assertRaisesRegex(AnthropicRunnerError, "max_tokens") as raised:
            parse_anthropic_response(self.decision_response(stop_reason="max_tokens"))
        self.assertEqual(_safe_runner_error_code(raised.exception), "ANTHROPIC_STOP_MAX_TOKENS")

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
