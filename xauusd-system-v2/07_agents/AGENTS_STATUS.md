# XAUUSD V2 — Canonical Agent Status

Status date: 2026-09-02

This file distinguishes architecture role IDs from implementation order. The canonical role IDs are fixed below.

| ID | Agent | Current state | Model/data connection | Authority boundary |
|---|---|---|---|---|
| 01 | Knowledge / Understanding Agent | IMPLEMENTED v0.1 | provider-neutral client contract; no production provider adapter yet | Extracts only from user-approved sources; output starts UNVERIFIED |
| 02 | Strategy Formalization Agent | IMPLEMENTED v0.1 | provider-neutral client contract; source-backed semantic strategy modules feed formalization; no production provider adapter yet | Creates DRAFT/candidate rules only; cannot promote |
| 03 | XAUUSD Data Agent | IMPLEMENTED v0.1 deterministic foundation | immutable CSV snapshot runtime + explicit broker precision contract; no MT5 connection yet | Validates XAUUSD bars/provenance/time; preserves broker metadata; no strategy or trade authority |
| 04 | Market State / Context Agent | IMPLEMENTED v0.1 fail-closed context foundation | consumes semantic confirmed/provisional context; TFS/TS semantic state modules available upstream; no autonomous raw-market interpretation yet | Reports aligned/conflicting/ambiguous context only; no entry or execution authority |
| 05 | Quantitative Research Agent | IMPLEMENTED v0.1 deterministic research-design gate | connected to immutable historical data/research readiness runtime; R-143 sequence + R-215 research scale available; no full trade simulator yet | Rejects leakage/non-reproducible experiments; cannot modify strategy, select live risk, or authorize trades |
| 06 | Independent Validation Agent | IMPLEMENTED v0.1 blind contract + batch infrastructure | leakage-safe blind packet + batch runner implemented; no production independent provider adapter yet | Cannot see expected label/class; may abstain; cannot promote or trade |
| 07 | Risk Agent / Deterministic Risk Engine | IMPLEMENTED v0.1 hard-veto foundation | no broker/account connection; production risk policy intentionally unset | No embedded default risk percentage; incomplete policy = NOT_CONFIGURED; may veto but cannot create a signal or authorize execution directly |
| 08 | Continuous Improvement Agent | IMPLEMENTED v0.1 proposal-governance foundation | no automated strategy mutation/promotion connection | Accepts evidence-backed change proposals only; cannot mutate rules, mark VERIFIED, override validation/risk, or promote directly |

## Implemented strategy/evidence layers

- FU stack: semantic FU criteria, conservative raw candidate, Complete/ATT classification, threshold-free quality metrics and faithful Casino_v7/BETA shadow evaluators.
- Helper comparison preserves disagreement; helper behavior never becomes strategy truth automatically.
- Liquidity stack: marked-level interaction + R-207 30m+ core-marking taxonomy.
- Zone stack: lifecycle, True Orderblock body-in-wick geometry, scoped 1m Strong-FU full-candle zone and FU-wick + body-in-wick refinement range.
- HCS, negation, final R-213 x3, TFS established/as-forming, True Stop, R-145 LTF execution, R-143 backtest sequence and target hierarchy have fail-closed semantic gates.
- Threshold-free imbalanced-candle observables remain separate from classic imbalance/FVG; no canonical `is_imbalance` classifier exists yet.
- Broker precision contract requires explicit broker/source symbol, digits and tick size; no default IMB tolerance exists.
- Round-02 ground truth: 20 primary-labelled cases with explicit coverage mapping: 12 EXECUTABLE, 7 PARTIAL, 1 CONTEXT_ONLY, 0 VERIFIED promotions.
- Blind-validation infrastructure strips expected label/class, analyst evidence summaries and forbidden-inference notes before Agent 06 sees a case.
- Orchestrator v0.2 requires R-143 COMPLETE + R-145 ENTRY_CANDIDATE + blind validation + historical reproducibility before STRATEGY_CANDIDATE_READY.

## Test status

Latest confirmed GitHub Actions full V2 regression: **244/244 tests passed** on Python 3.12, run `33589646417` / job `100120848840`.

## Non-negotiable architecture rules

1. Agent numbering follows role architecture, not build order.
2. No agent can self-promote strategy truth.
3. Ambiguity is fail-closed.
4. Data Agent preserves provisional vs confirmed bars.
5. Independent Validator never receives the expected label/class or analyst-authored answer summary.
6. Market State Agent cannot manufacture missing strategy primitives.
7. Quant Research Agent requires versioned strategy, frozen data snapshot, explicit cost model, and time-ordered train/validation/test windows before research is admissible.
8. Risk Engine contains no default 3%/5% assumption; production limits require explicit approved policy configuration.
9. Risk Engine veto outranks strategy readiness and cannot be overridden by an LLM.
10. Continuous Improvement Agent may propose only; every change must re-enter certification/validation before promotion.
11. Imbalance geometry/tolerance is broker-feed-sensitive and cannot inherit TradingView/helper equality logic as strategy truth.
12. Helper code is implementation evidence only: primary source -> canonical/candidate rule -> helper comparison.
13. R-143 sequence stages may not be skipped in certified backtesting.
14. Strategy-candidate readiness must be proven by deterministic gates; no free external boolean bypass.
15. No LLM is permitted in the latency-critical live execution path.
