# XAUUSD V2 — Canonical Agent Status

Status date: 2026-09-02

| ID | Agent | Current state | Connection | Authority boundary |
|---|---|---|---|---|
| 01 | Knowledge / Understanding | IMPLEMENTED v0.1 | provider-neutral; no production model adapter | Approved sources only; output starts UNVERIFIED |
| 02 | Strategy Formalization | IMPLEMENTED v0.1 | provider-neutral | DRAFT/candidate rules only; cannot promote |
| 03 | XAUUSD Data | IMPLEMENTED v0.1 | immutable snapshots + broker precision; no MT5 yet | Validates data/provenance/time; no trade authority |
| 04 | Market State / Context | IMPLEMENTED v0.1 | consumes confirmed/provisional semantic context | aligned/conflicting/ambiguous only; no trade authority |
| 05 | Quant Research | IMPLEMENTED v0.1 | reproducible research gate; R-143/R-215 layers available | Cannot change strategy or authorize trades |
| 06 | Independent Validation | IMPLEMENTED v0.1 + blind batch infrastructure | leakage-safe packet, primary-context resolver, downstream comparison; no production independent provider yet | Never sees expected answer; may abstain; cannot promote |
| 07 | Risk Engine | IMPLEMENTED v0.1 | no broker/account connection; production policy unset | Hard veto; no default 3%/5%; cannot create signals |
| 08 | Continuous Improvement | IMPLEMENTED v0.1 | proposal/governance foundation | Propose only; every change re-enters certification |

## Strategy/evidence implementation

- FU: semantic criteria, conservative raw candidate, Complete/ATT classification, threshold-free quality metrics, Casino_v7/BETA shadow comparison.
- Liquidity: marked-level interaction + R-207 30m+ core taxonomy.
- Zones: lifecycle, True Orderblock body-in-wick, scoped 1m Strong-FU zone, FU-wick + body-in-wick refinement.
- HCS, negation, final R-213 x3, TFS established/as-forming, True Stop, R-145 LTF execution, R-143 sequence and target hierarchy use fail-closed gates.
- Imbalanced-candle observables remain separate from classic imbalance/FVG; no canonical `is_imbalance` classifier yet.
- Broker precision requires explicit broker/source symbol, digits and tick size.
- Historical component replay distinguishes `occurred_at` from `available_at`; future evidence is hidden.
- Historical replay batch treats valid no-entry sessions as `IN_PROGRESS`, not failures.

## Ground truth

- Round 02: 20 primary-labelled cases — 12 EXECUTABLE, 7 PARTIAL, 1 CONTEXT_ONLY.
- Round 03: 7 additional explicit primary visual labels — 6 PARTIAL, 1 RAW_BLOCKED.
- Current database examples after Round 03: 60.
- VERIFIED promotions from these datasets: 0.

## Orchestration

Current orchestrator: **v0.5**.

Critical gates no longer accept free readiness booleans:
- strategy candidate consumes actual blind-validation and historical-replay reports;
- research reruns the full strategy evidence gate;
- execution consumes the actual strategy readiness report;
- a blocked report cannot be relabelled ready downstream;
- live execution authorization remains false by construction.

Canonical specification: `07_agents/PIPELINE_ORCHESTRATION_V0_5.md`.

## Test status

Latest confirmed GitHub Actions regression: **284/284 PASS** on Python 3.12, run `33590480750`, job `100123291079`.

## Non-negotiable rules

1. No agent self-promotes strategy truth.
2. Ambiguity is fail-closed.
3. Provisional bars cannot satisfy confirmed conditions.
4. Agent 06 never receives the expected answer.
5. Actual primary context must be available for blind validation; no summary fallback.
6. Helper code is implementation evidence only, never strategy authority.
7. R-143 stage order cannot be skipped.
8. Research requires frozen/versioned strategy, clean data, explicit costs and proper time splits.
9. Risk veto outranks strategy readiness.
10. Production risk limits require explicit approved policy.
11. No LLM is permitted in the latency-critical live order path.
