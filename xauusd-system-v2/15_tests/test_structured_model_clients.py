from __future__ import annotations

import sys
import unittest

from xauusd_v2.agents.base import AgentContractError
from xauusd_v2.structured_model_clients import CommandModelClientConfig, CommandStructuredModelClient


class CommandStructuredModelClientTests(unittest.TestCase):
    @staticmethod
    def client(script: str, *, timeout_seconds: float = 5.0) -> CommandStructuredModelClient:
        config = CommandModelClientConfig.from_command(
            (sys.executable, "-c", script),
            timeout_seconds=timeout_seconds,
        )
        return CommandStructuredModelClient(config)

    def test_round_trips_prompts_and_parses_json_object(self) -> None:
        script = (
            "import json,sys; "
            "request=json.load(sys.stdin); "
            "print(json.dumps({'predicted_label':'label_a','confidence':0.9,"
            "'evidence':[request['system'],request['user']],'ambiguities':[]}))"
        )
        payload = self.client(script).generate_json(system=" system ", user=" user ")
        self.assertEqual(payload["predicted_label"], "label_a")
        self.assertEqual(payload["evidence"], ["system", "user"])

    def test_empty_prompt_fails_before_external_command(self) -> None:
        client = self.client("raise SystemExit(99)")
        with self.assertRaises(AgentContractError):
            client.generate_json(system="", user="user")
        with self.assertRaises(AgentContractError):
            client.generate_json(system="system", user="   ")

    def test_nonzero_exit_fails_closed_without_exposing_stderr(self) -> None:
        client = self.client("import sys; print('secret diagnostic', file=sys.stderr); raise SystemExit(7)")
        with self.assertRaisesRegex(AgentContractError, "exit code 7") as caught:
            client.generate_json(system="system", user="user")
        self.assertNotIn("secret diagnostic", str(caught.exception))

    def test_allowlisted_safe_error_code_is_exposed_but_other_stderr_is_hidden(self) -> None:
        script = (
            "import sys; "
            "print('model-runner-safe-error: ANTHROPIC_HTTP_401', file=sys.stderr); "
            "print('secret diagnostic must stay hidden', file=sys.stderr); "
            "raise SystemExit(2)"
        )
        with self.assertRaisesRegex(AgentContractError, "ANTHROPIC_HTTP_401") as caught:
            self.client(script).generate_json(system="system", user="user")
        self.assertNotIn("secret diagnostic", str(caught.exception))

    def test_invalid_json_fails_closed(self) -> None:
        client = self.client("print('not-json')")
        with self.assertRaisesRegex(AgentContractError, "invalid JSON"):
            client.generate_json(system="system", user="user")

    def test_json_array_is_rejected(self) -> None:
        client = self.client("print('[]')")
        with self.assertRaisesRegex(AgentContractError, "one JSON object"):
            client.generate_json(system="system", user="user")

    def test_timeout_fails_closed(self) -> None:
        client = self.client("import time; time.sleep(1)", timeout_seconds=0.01)
        with self.assertRaisesRegex(AgentContractError, "timed out"):
            client.generate_json(system="system", user="user")

    def test_config_rejects_empty_command_and_nonpositive_timeout(self) -> None:
        with self.assertRaises(ValueError):
            CommandModelClientConfig.from_command(())
        with self.assertRaises(ValueError):
            CommandModelClientConfig.from_command((sys.executable,), timeout_seconds=0)


if __name__ == "__main__":
    unittest.main()
