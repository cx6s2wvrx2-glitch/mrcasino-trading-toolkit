# XAUUSD V2 — Multi-Agent Pipeline Orchestration v0.2

Status: FOUNDATION ACTIVE / FAIL-CLOSED / NO LIVE AUTHORITY
Date: 2026-09-02

## Knowledge and strategy lane

`Approved source -> Agent 01 Knowledge -> Agent 02 Rules -> Ground Truth -> Agent 06 Blind Validation -> Agent 05 Quant Research -> Agent 08 Improvement proposals`

- Agent 01 output starts UNVERIFIED.
- Agent 02 output starts DRAFT/candidate.
- Ground truth preserves exact primary source locators and cannot self-promote.
- Agent 06 receives no expected label/class or analyst answer summary and may abstain.
- Agent 05 rejects leakage/non-reproducible research designs.
- Agent 08 can propose only; every change re-enters certification.

## Strategy-candidate bridge

`validated data + unambiguous context + R-143 COMPLETE_CANDIDATE + R-145 ENTRY_CANDIDATE + blind validation passed + historical reproducibility passed -> STRATEGY_CANDIDATE_READY`

A later stage cannot compensate for an earlier missing stage. No free external boolean can bypass the strategy sequence.

## Market and execution-candidate lane

`Agent 03 validated XAUUSD data -> source-backed primitives -> Agent 04 context -> strategy-candidate bridge -> Agent 07 risk veto -> EXECUTION_CANDIDATE`

`EXECUTION_CANDIDATE` is never a live order. `live_execution_authorized=false` remains hard-coded by architecture.

## Blind validation

Round-02 has:
- 20 primary-labelled cases;
- explicit implementation coverage registry;
- leakage-safe blind packet containing only vector ID + primary locator per case;
- primary-context resolver contract that fails closed if actual source context is unavailable;
- Agent-06 batch runner;
- downstream deterministic comparison report.

Expected labels/classes, analyst evidence summaries and forbidden-inference notes are excluded from Agent 06 inputs.

## Future production gates

Before any live execution path can exist:
1. certified rule set;
2. real independent Agent-06 provider/runtime validation;
3. broker-quality historical reproducibility;
4. OOS + walk-forward;
5. costs/slippage/sensitivity/Monte Carlo;
6. paper/demo;
7. shadow;
8. tiny-live with explicit approved risk policy;
9. deterministic MQL5 execution with hard risk controls.

No LLM enters the latency-critical live order path.
