# XAUUSD V2 — Canonical Agent Status

Status date: 2026-09-01

This file distinguishes architecture role IDs from implementation order. The canonical role IDs are fixed below.

| ID | Agent | Current state | Model/data connection | Authority boundary |
|---|---|---|---|---|
| 01 | Knowledge / Understanding Agent | IMPLEMENTED v0.1 | provider-neutral client contract; no production provider adapter yet | Extracts only from user-approved sources; output starts UNVERIFIED |
| 02 | Strategy Formalization Agent | IMPLEMENTED v0.1 | provider-neutral client contract; no production provider adapter yet | Creates DRAFT rules only; cannot promote |
| 03 | XAUUSD Data Agent | IMPLEMENTED v0.1 deterministic foundation | immutable CSV snapshot runtime added; explicit broker precision contract added; no MT5 connection yet | Validates XAUUSD bars/provenance/time; preserves broker metadata requirements; no strategy or trade authority |
| 04 | Market State / Context Agent | IMPLEMENTED v0.1 fail-closed context foundation | consumes semantic confirmed/provisional context; no raw-market interpretation yet | Reports aligned/conflicting/ambiguous context only; no entry or execution authority |
| 05 | Quantitative Research Agent | IMPLEMENTED v0.1 deterministic research-design gate | connected to immutable historical data/research readiness runtime; no trade simulator yet | Rejects leakage/non-reproducible experiments; cannot modify strategy, select live risk, or authorize trades |
| 06 | Independent Validation Agent | IMPLEMENTED v0.1 blind contract | provider-neutral client contract; no production provider adapter yet | Cannot see expected label; may abstain; cannot promote or trade |
| 07 | Risk Agent / Deterministic Risk Engine | IMPLEMENTED v0.1 hard-veto foundation | no broker/account connection; production risk policy intentionally unset | No embedded default risk percentage; incomplete policy = NOT_CONFIGURED; may veto but cannot create a signal or authorize execution directly |
| 08 | Continuous Improvement Agent | IMPLEMENTED v0.1 proposal-governance foundation | no automated strategy mutation/promotion connection | Accepts evidence-backed change proposals only; cannot mutate rules, mark VERIFIED, override validation/risk, or promote directly |

## Implemented agent tests and evidence layers

- Agent 06 blind-validation contract: 5/5 tests passed.
- Agent 03 market-data contract: 7/7 tests passed.
- Agent 04 market-state/context contract: 6/6 tests passed.
- Agent 05 quantitative-research design contract: 8/8 tests passed.
- Agent 07 deterministic-risk contract: 10/10 tests passed.
- Agent 08 continuous-improvement governance contract: 7/7 tests passed.
- Immutable data snapshot + Agent03→Agent05 research runtime are included in full regression.
- Source-backed FU completion layer, raw FU observables and threshold-free FU quality metrics are included in full regression.
- Threshold-free imbalanced-candle observables are included; no canonical `is_imbalance` classifier exists yet.
- Broker precision contract requires explicit broker/source symbol, digits and tick size; no default IMB tolerance exists.
- Latest GitHub Actions full V2 regression: **114/114 tests passed** on Python 3.12, run `33560840408`.

## Non-negotiable architecture rules

1. Agent numbering follows role architecture, not build order.
2. No agent can self-promote strategy truth.
3. Ambiguity is fail-closed.
4. Data Agent preserves provisional vs confirmed bars.
5. Independent Validator never receives the expected label.
6. Market State Agent cannot manufacture missing strategy primitives.
7. Quant Research Agent requires versioned strategy, frozen data snapshot, explicit cost model, and time-ordered train/validation/test windows before research is admissible.
8. Risk Engine contains no default 3%/5% assumption; production limits require explicit approved policy configuration.
9. Risk Engine veto outranks strategy readiness and cannot be overridden by an LLM.
10. Continuous Improvement Agent may propose only; every change must re-enter certification/validation before promotion.
11. Imbalance geometry/tolerance is broker-feed-sensitive and cannot inherit TradingView/helper equality logic as strategy truth.
12. No LLM is permitted in the latency-critical live execution path.
