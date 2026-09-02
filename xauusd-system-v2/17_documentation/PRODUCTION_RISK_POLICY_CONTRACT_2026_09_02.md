# XAUUSD V2 — Production Risk Policy Contract

Date: 2026-09-02
Status: ENGINEERING CONTRACT READY / NUMERIC POLICY NOT YET USER-APPROVED
Blocker family: B-08

## Purpose

This contract separates **production account safety policy** from **strategy truth**.

Historical source statements about 3%, 5% or any other risk figure do not automatically become production limits. XAUUSD V2 must receive an explicit, complete, user-approved policy document before the deterministic Risk Engine can be treated as configured for production-safety evaluation.

This contract does not verify strategy rules, promote knowledge, authorize live trading or resolve B-08 by itself.

## Required JSON shape

A production policy must contain exactly these fields and no hidden extras:

```json
{
  "version": 1,
  "policy_id": "<non-empty unique policy id>",
  "policy_scope": "production_risk_safety_only",
  "approval_reference": "<explicit user-approval provenance>",
  "max_risk_fraction_per_trade": "<explicit numeric fraction>",
  "max_daily_loss_fraction": "<explicit numeric fraction>",
  "max_total_open_risk_fraction": "<explicit numeric fraction>",
  "max_concurrent_positions": "<explicit positive integer>",
  "strategy_truth_authority": false,
  "live_execution_authorized": false,
  "promotion_allowed": false
}
```

The quoted placeholders above are documentation only. A real policy file must provide numeric JSON values for the three fractions and an integer for concurrent positions.

## No defaults

The loader rejects a policy when any required limit is absent. It does not substitute historical values, test-fixture values or software defaults.

The following must therefore be explicitly decided and approved:
- maximum risk fraction per individual trade;
- maximum daily loss fraction;
- maximum projected total open-risk fraction;
- maximum concurrent positions.

A missing field means the policy is incomplete and the Risk Engine remains fail-closed.

## Safety boundaries

A valid policy document must explicitly keep:
- `strategy_truth_authority=false`;
- `live_execution_authorized=false`;
- `promotion_allowed=false`.

Any attempt to set one of those fields to `true` is rejected by the parser.

The policy is allowed to define deterministic **safety ceilings** only. It cannot create a setup, override a strategy veto, resolve an ambiguous market state, certify a strategy rule or authorize execution directly.

## Validation command

After the user has explicitly approved all numeric limits and approval provenance has been recorded, validate the file with:

```bash
xauusd-v2-risk-policy-check /absolute/path/production-risk-policy.json
```

A valid document returns:

```text
VALIDATED_POLICY_CONTRACT
```

An invalid, incomplete, extra-field or authority-escalating document returns `BLOCKED`.

## Engine mapping

Only after contract validation are the four explicit limits mapped into `RiskPolicy`:
- `max_risk_fraction_per_trade`;
- `max_daily_loss_fraction`;
- `max_total_open_risk_fraction`;
- `max_concurrent_positions`.

The existing deterministic Risk Engine can then evaluate a candidate against these ceilings. Its `APPROVE_CANDIDATE` state is still only a risk-gate pass; it is not live authorization.

## What remains unresolved

B-08 remains open because the real numeric production limits have **not** yet been explicitly approved by the user.

The software contract is complete enough to capture those decisions safely when made, but engineering completeness is not policy approval.

Until explicit approval exists:
- production risk policy = NOT CONFIGURED;
- B-08 = UNRESOLVED;
- live execution = DISABLED.

## Relevant implementation

- `src/xauusd_v2/agents/risk_agent.py`
- `src/xauusd_v2/risk_policy_io.py`
- `src/xauusd_v2/risk_policy_cli.py`
- `15_tests/test_risk_engine.py`
- `15_tests/test_risk_policy_io.py`
- `15_tests/test_risk_policy_cli.py`
