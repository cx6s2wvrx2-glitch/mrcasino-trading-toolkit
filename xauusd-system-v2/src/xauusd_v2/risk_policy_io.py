from __future__ import annotations

import json
from dataclasses import dataclass
from math import isfinite
from pathlib import Path

from .agents.risk_agent import RiskPolicy


class RiskPolicyIOError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ProductionRiskPolicyDocument:
    version: int
    policy_id: str
    policy_scope: str
    approval_reference: str
    max_risk_fraction_per_trade: float
    max_daily_loss_fraction: float
    max_total_open_risk_fraction: float
    max_concurrent_positions: int
    strategy_truth_authority: bool
    live_execution_authorized: bool
    promotion_allowed: bool

    def to_engine_policy(self) -> RiskPolicy:
        return RiskPolicy(
            max_risk_fraction_per_trade=self.max_risk_fraction_per_trade,
            max_daily_loss_fraction=self.max_daily_loss_fraction,
            max_total_open_risk_fraction=self.max_total_open_risk_fraction,
            max_concurrent_positions=self.max_concurrent_positions,
        )


_REQUIRED_FIELDS = {
    "version",
    "policy_id",
    "policy_scope",
    "approval_reference",
    "max_risk_fraction_per_trade",
    "max_daily_loss_fraction",
    "max_total_open_risk_fraction",
    "max_concurrent_positions",
    "strategy_truth_authority",
    "live_execution_authorized",
    "promotion_allowed",
}
_POLICY_SCOPE = "production_risk_safety_only"


def _required_nonempty_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RiskPolicyIOError(f"{field} must be a non-empty string")
    return value.strip()


def _fraction(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RiskPolicyIOError(f"{field} must be a numeric fraction")
    result = float(value)
    if not isfinite(result) or not 0.0 < result < 1.0:
        raise RiskPolicyIOError(f"{field} must be finite and strictly between 0 and 1")
    return result


def _positive_int(value: object, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise RiskPolicyIOError(f"{field} must be a positive integer")
    return value


def _must_be_false(value: object, *, field: str) -> bool:
    if value is not False:
        raise RiskPolicyIOError(f"{field} must be false")
    return False


def parse_production_risk_policy(value: object) -> ProductionRiskPolicyDocument:
    if not isinstance(value, dict):
        raise RiskPolicyIOError("production risk policy must be a JSON object")
    keys = set(value)
    if keys != _REQUIRED_FIELDS:
        missing = sorted(_REQUIRED_FIELDS - keys)
        extra = sorted(keys - _REQUIRED_FIELDS)
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
        raise RiskPolicyIOError("production risk policy fields must match exactly: " + "; ".join(details))

    version = value["version"]
    if isinstance(version, bool) or version != 1:
        raise RiskPolicyIOError("production risk policy version must be 1")

    scope = _required_nonempty_string(value["policy_scope"], field="policy_scope")
    if scope != _POLICY_SCOPE:
        raise RiskPolicyIOError(f"policy_scope must be {_POLICY_SCOPE!r}")

    return ProductionRiskPolicyDocument(
        version=1,
        policy_id=_required_nonempty_string(value["policy_id"], field="policy_id"),
        policy_scope=scope,
        approval_reference=_required_nonempty_string(
            value["approval_reference"], field="approval_reference"
        ),
        max_risk_fraction_per_trade=_fraction(
            value["max_risk_fraction_per_trade"], field="max_risk_fraction_per_trade"
        ),
        max_daily_loss_fraction=_fraction(
            value["max_daily_loss_fraction"], field="max_daily_loss_fraction"
        ),
        max_total_open_risk_fraction=_fraction(
            value["max_total_open_risk_fraction"], field="max_total_open_risk_fraction"
        ),
        max_concurrent_positions=_positive_int(
            value["max_concurrent_positions"], field="max_concurrent_positions"
        ),
        strategy_truth_authority=_must_be_false(
            value["strategy_truth_authority"], field="strategy_truth_authority"
        ),
        live_execution_authorized=_must_be_false(
            value["live_execution_authorized"], field="live_execution_authorized"
        ),
        promotion_allowed=_must_be_false(value["promotion_allowed"], field="promotion_allowed"),
    )


def load_production_risk_policy(path: str | Path) -> ProductionRiskPolicyDocument:
    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RiskPolicyIOError("production risk policy file could not be read") from exc
    except json.JSONDecodeError as exc:
        raise RiskPolicyIOError("production risk policy is not valid JSON") from exc
    return parse_production_risk_policy(value)
