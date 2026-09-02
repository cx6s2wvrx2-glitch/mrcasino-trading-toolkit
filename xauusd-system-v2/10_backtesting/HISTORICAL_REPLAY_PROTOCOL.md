# XAUUSD V2 — Historical Component Replay Protocol

Status: ACTIVE FOUNDATION / COMPONENT REPRODUCIBILITY ONLY / NOT PERFORMANCE BACKTEST
Date: 2026-09-02

## Purpose

Historical replay tests whether the source-backed strategy sequence can be reconstructed using only information legitimately available at each historical moment. It does **not** measure profitability yet.

## Broker-history prerequisite

Historical source alignment must use immutable broker-quality history rather than inferred chart pixels or a TradingView approximation.

Current deterministic path:
1. `xauusd-v2-ingest-mt5` validates an explicit MT5 CSV/TSV export and persists the raw source, normalized XAUUSD OHLC snapshot and ingestion manifest by SHA-256.
2. `mt5_snapshot_load.py` treats the persisted manifest as untrusted input, re-hashes both raw and normalized files, requires the canonical content-addressed store layout, reconstructs the persisted `DataSnapshotManifest`, and re-runs the normalized CSV through the deterministic data gate.
3. `xauusd-v2-replay-readiness` consumes only explicit source-chart broker/symbol/timeframe/window metadata and compares it with the verified persisted snapshot through `source_chart_alignment.py`.
4. Alignment alone never creates a replay-ready episode. Stage timestamps remain separately required.

The replay-readiness CLI deliberately does **not** accept a bare `stage_timestamps_certified=true` command-line assertion. Until a machine-verifiable source-certification artifact is implemented and supplied, a correctly broker-aligned episode remains `BLOCKED_STAGE_TIMESTAMPS`.

This prevents raw-data availability from being mistaken for strategy-sequence certification.

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

MT5 ingestion: `src/xauusd_v2/mt5_history_cli.py`

Immutable MT5 store: `src/xauusd_v2/mt5_snapshot_store.py`

Verified persisted snapshot loader: `src/xauusd_v2/mt5_snapshot_load.py`

Broker/source alignment: `src/xauusd_v2/source_chart_alignment.py`

Replay readiness CLI: `src/xauusd_v2/replay_readiness_cli.py`

Replay dataset loader: `src/xauusd_v2/component_replay_dataset.py`

Replay engine: `src/xauusd_v2/component_replay.py`

Batch gate: `src/xauusd_v2/historical_replay_gate.py`

No alignment, replay dataset or replay result may set or imply strategy VERIFIED status on its own.
