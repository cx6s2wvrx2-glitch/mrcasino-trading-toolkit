# XAUUSD V2 — Multi-Agent Pipeline Orchestration v0.2

Status: FOUNDATION ACTIVE / FAIL-CLOSED / NO LIVE AUTHORITY
Date: 2026-09-02

## 1. Knowledge and strategy lane

`Approved source -> Agent 01 Knowledge -> Agent 02 Rules -> Ground Truth -> Agent 06 Blind Validation -> Agent 05 Quant Research -> Agent 08 Improvement proposals`

Rules:
- Agent 01 output starts UNVERIFIED.
- Agent 02 output starts DRAFT/candidate.
- Ground-truth cases retain exact source locators and cannot self-promote.
- Agent 06 receives no expected label/class or analyst-authored answer summary and may abstain.
- Agent 05 rejects non-reproducible research designs before results count as evidence.
- Agent 08 may only propose changes; every change re-enters certification.

## 2. Strategy-candidate bridge added in v0.2

The coordinator now has an explicit deterministic strategy-candidate gate:

`validated data + unambiguous context + R-143 COMPLETE_CANDIDATE + R-145 ENTRY_CANDIDATE + blind validation passed + historical reproducibility passed -> STRATEGY_CANDIDATE_READY`

This closes the previous architectural gap where an external boolean could claim the strategy candidate was ready without proving the actual strategy sequence.

Fail-closed rules:
- incomplete/invalid R-143 sequence blocks progression;
- R-145 WAIT/NOT_CERTIFIED blocks progression;
- ambiguous/conflicting context blocks progression;
- missing blind validation blocks progression;
- missing historical reproducibility blocks progression.

## 3. Market and execution-candidate lane

`Validated XAUUSD data -> Agent 03 Data -> certified/candidate deterministic primitives -> Agent 04 Market State -> strategy-candidate gate -> Agent 07 Risk -> EXECUTION_CANDIDATE`

Rules:
- provisional bars cannot satisfy confirmed-only strategy conditions;
- ambiguous/conflicting market state is fail-closed;
- strategy candidate must come from deterministic source-backed gates, not an LLM opinion;
- incomplete risk policy = NOT_CONFIGURED;
- risk veto blocks progression;
- EXECUTION_CANDIDATE is not a live order.

## 4. Blind-validation infrastructure

Round-02 now has:
- an explicit implementation-coverage registry for all 20 GT-R02 cases;
- a leakage-safe blind packet containing only case ID + primary source locator per case;
- a batch runner that resolves primary source context separately and feeds Agent 06 only the source context + shared multi-label taxonomy;
- deterministic comparison to ground truth remains downstream and separate from Agent 06.

Expected labels/classes, analyst evidence summaries and forbidden-inference notes are not exposed to the blind validator.

## 5. Live execution intentionally unavailable

The coordinator always sets `live_execution_authorized=false`.

Future gates still required before any production execution path exists:
1. certified rule set;
2. real blind independent validation through an independent provider/runtime;
3. historical reproducibility on broker-quality XAUUSD data;
4. out-of-sample and walk-forward testing;
5. explicit cost/slippage/sensitivity/Monte Carlo testing;
6. paper/demo;
7. shadow mode;
8. tiny-live gate with explicit approved risk policy;
9. deterministic MQL5 execution + hard risk controls.

No LLM will be placed in the latency-critical order path.
