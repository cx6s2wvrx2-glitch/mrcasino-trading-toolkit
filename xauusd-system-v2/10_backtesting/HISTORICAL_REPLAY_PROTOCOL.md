# XAUUSD V2 — Historical Component Replay Protocol

Status: ACTIVE FOUNDATION / COMPONENT REPRODUCIBILITY ONLY / NOT PERFORMANCE BACKTEST
Date: 2026-09-02

## Purpose

Historical replay tests whether the source-backed strategy sequence can be reconstructed using only information legitimately available at each historical moment. It does **not** measure profitability yet.

## Session format

Each session must include:
- unique `session_id`;
- exact session-level `source_ref`;
- timezone-aware `evaluation_time`;
- zero or one canonical confirmation for each R-143 stage;
- for every confirmation: `stage`, `occurred_at`, `available_at`, exact `source_ref`.

Allowed R-143 stages:
1. `HCS_ZONE_REACTION`
2. `TFS`
3. `LAOL_MET`
4. `TRUE_STOP_RESPECTED`
5. `TEN_MIN_TRUE_STOP_ESTABLISHED`
6. `TARGETS_AND_TIMING`

## Time semantics

`occurred_at` = when the market event happened.

`available_at` = when the system was allowed to know the event. For close-confirmed rules this must be the relevant candle close or later.

Historical replay at time T must ignore every confirmation whose `available_at > T`.

## Valid outcomes

- `COMPLETE_CANDIDATE`: the full R-143 sequence was available in source order.
- `IN_PROGRESS`: valid no-entry/incomplete path. This is **not** a failure and must not be converted into a trade.
- `INVALID_ORDER`: later strategy stage occurred before an earlier required stage; reproducibility fails.
- `NOT_CERTIFIED`: required evidence is unavailable/unknown; reproducibility fails until evidence is supplied.

## Batch reproducibility gate

A replay batch passes component reproducibility only when:
- no session uses unavailable/future evidence;
- no session has INVALID_ORDER;
- no session is NOT_CERTIFIED due to missing required evidence.

The batch may contain any number of legitimate IN_PROGRESS/no-trade sessions.

## What replay does not prove

A passing replay does not prove:
- profitability;
- target expectancy;
- win rate;
- acceptable drawdown;
- robustness across brokers;
- production risk policy;
- live execution readiness.

Those require broker-quality history, certified detectors, OOS/walk-forward, cost/slippage, sensitivity and later deployment gates.

## Governance

Machine loader: `src/xauusd_v2/component_replay_dataset.py`

Replay engine: `src/xauusd_v2/component_replay.py`

Batch gate: `src/xauusd_v2/historical_replay_gate.py`

No replay dataset may set or imply strategy VERIFIED status on its own.
