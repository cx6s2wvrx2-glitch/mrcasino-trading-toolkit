# XAUUSD V2 — Multi-Agent Pipeline Orchestration v0.1

Status: FOUNDATION / FAIL-CLOSED / NO LIVE AUTHORITY
Date: 2026-09-01

## 1. Knowledge and strategy lane

`Approved source -> Agent 01 Knowledge -> Agent 02 Rules -> Agent 06 Blind Validation -> Agent 05 Quant Research -> Agent 08 Improvement proposals`

Rules:
- Agent 01 output starts UNVERIFIED.
- Agent 02 output starts DRAFT.
- Agent 06 does not receive the expected answer and may abstain.
- Agent 05 rejects non-reproducible research designs before results count as evidence.
- Agent 08 may only propose changes; every change re-enters certification.

## 2. Market and execution-candidate lane

`Validated XAUUSD data -> Agent 03 Data -> certified/deterministic primitives -> Agent 04 Market State -> entry gate -> Agent 07 Risk -> EXECUTION_CANDIDATE`

Rules:
- provisional bars cannot satisfy confirmed-only strategy conditions;
- ambiguous/conflicting market state is fail-closed;
- entry candidate must come from certified/deterministic strategy logic, not an LLM;
- incomplete risk policy = NOT_CONFIGURED;
- risk veto blocks progression;
- EXECUTION_CANDIDATE is not a live order.

## 3. Live execution intentionally unavailable in v0.1

The coordinator always sets `live_execution_authorized=false`.

Future gates still required before any production execution path exists:
1. certified rule set;
2. real blind independent validation;
3. historical reproducibility on broker-quality XAUUSD data;
4. out-of-sample and walk-forward testing;
5. cost/slippage/sensitivity/Monte Carlo testing;
6. paper/demo;
7. shadow mode;
8. tiny-live gate with explicit approved risk policy;
9. deterministic MQL5 execution + hard risk controls.

No LLM will be placed in the latency-critical order path.
