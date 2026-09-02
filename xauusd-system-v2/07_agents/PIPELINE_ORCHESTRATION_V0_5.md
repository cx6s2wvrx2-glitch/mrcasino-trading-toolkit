# XAUUSD V2 — Multi-Agent Pipeline Orchestration v0.5

Status: ACTIVE FOUNDATION / EVIDENCE-BEARING GATES / NO LIVE AUTHORITY
Date: 2026-09-02

## Canonical strategy path

`approved primary source -> Agent 01 knowledge -> Agent 02 candidate rules -> ground truth -> Agent 06 blind validation -> historical replay -> R-143/R-145 strategy gate -> Agent 05 research -> Agent 07 risk -> execution candidate`

## Strategy-candidate gate

The coordinator requires all of the following:
- validated XAUUSD market data;
- unambiguous market context;
- R-143 state = `COMPLETE_CANDIDATE`;
- R-145 LTF execution = `ENTRY_CANDIDATE`;
- an actual `BlindValidationComparisonReport` with zero disagreements/ambiguities and all cases agreed;
- an actual `HistoricalReplayGateReport` that passes reproducibility.

There is no free boolean for blind validation or historical reproducibility at this gate.

## Research gate

Research readiness receives the complete `StrategyCandidateReadinessInput` and reruns the strategy gate. A caller cannot bypass validation/replay by passing `True` flags. Source approval, frozen strategy version, ground truth readiness and approved research design remain additional requirements.

## Execution-candidate gate

Execution readiness receives the actual strategy readiness report, not `strategy_candidate_ready=True`. A blocked strategy report cannot be relabelled ready downstream. The deterministic Risk Engine remains a hard veto.

`EXECUTION_CANDIDATE` is never a live order. `live_execution_authorized=false` remains hard-coded by architecture.

## Blind-validation path

Per-case Agent-06 input contains only:
- ground-truth vector ID;
- exact primary source locator;
- actual resolved primary context;
- shared multi-option taxonomy.

It excludes expected label/class, analyst evidence summaries and forbidden-inference notes. If actual primary context cannot be resolved, validation fails closed.

Comparison with ground truth happens only after the blind run is complete.

## Historical replay path

R-143 events distinguish:
- `occurred_at`: when the event happened;
- `available_at`: when the system was legitimately allowed to know it.

Future/unclosed evidence remains invisible. An `IN_PROGRESS` session is a valid no-trade path; INVALID_ORDER, missing required evidence or lookahead fail reproducibility.

## Current ground truth

- Round 02: 20 primary-labelled cases — 12 executable, 7 partial, 1 context-only.
- Round 03: 7 additional explicit primary visual labels — 6 partial, 1 raw-blocked pending broker-quality fixtures.
- No ground-truth batch may auto-promote a strategy rule.

## Production gates still required

Certified strategy version -> independent provider validation -> broker-quality replay -> OOS -> walk-forward -> costs/slippage -> sensitivity/Monte Carlo -> paper/demo -> shadow -> tiny live -> deterministic MQL5 production.

No LLM enters the latency-critical live order path.
