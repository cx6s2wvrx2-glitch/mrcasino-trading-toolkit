from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from xauusd_v2.risk_policy_cli import main


VALID = {
    "version": 1,
    "policy_id": "risk-policy-001",
    "policy_scope": "production_risk_safety_only",
    "approval_reference": "user-approval:example",
    "max_risk_fraction_per_trade": 0.01,
    "max_daily_loss_fraction": 0.03,
    "max_total_open_risk_fraction": 0.02,
    "max_concurrent_positions": 2,
    "strategy_truth_authority": False,
    "live_execution_authorized": False,
    "promotion_allowed": False,
}


class RiskPolicyCliTests(unittest.TestCase):
    def test_valid_contract_reports_limits_without_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "policy.json"
            path.write_text(json.dumps(VALID), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main([str(path)])
            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["status"], "VALIDATED_POLICY_CONTRACT")
            self.assertEqual(payload["policy_id"], "risk-policy-001")
            self.assertFalse(payload["strategy_truth_authority"])
            self.assertFalse(payload["live_execution_authorized"])
            self.assertFalse(payload["promotion_allowed"])

    def test_invalid_contract_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "policy.json"
            value = dict(VALID)
            value["live_execution_authorized"] = True
            path.write_text(json.dumps(value), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = main([str(path)])
            self.assertEqual(code, 2)
            payload = json.loads(stderr.getvalue())
            self.assertEqual(payload["status"], "BLOCKED")
            self.assertIn("live_execution_authorized", payload["error"])


if __name__ == "__main__":
    unittest.main()
