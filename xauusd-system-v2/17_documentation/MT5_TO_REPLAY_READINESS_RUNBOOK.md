# XAUUSD V2 — MT5 to Historical Replay Readiness Runbook

Status: FOUNDATION / FAIL-CLOSED / NO PERFORMANCE CLAIMS
Date: 2026-09-02

## Purpose

This runbook describes the deterministic path from an original broker MT5 history export to a broker/source alignment assessment for one registered historical replay candidate.

It does **not** certify strategy stages, measure profitability, promote any rule to VERIFIED, or authorize live execution.

## 1. Ingest original MT5 history

Use the original broker export without editing its rows.

```bash
xauusd-v2-ingest-mt5 \
  --source "/absolute/path/XAUUSD_history.tsv" \
  --broker-name "EXACT BROKER NAME" \
  --broker-symbol "EXACT BROKER SYMBOL" \
  --source-timezone "EXPLICIT BROKER TIMEZONE" \
  --timeframe-seconds 60 \
  --evaluation-time "2026-09-02T18:00:00+00:00" \
  --store-root "$HOME/.xauusd-v2/mt5"
```

Required metadata must come from real broker/export provenance. Do not infer broker timezone, symbol alias or timeframe from chart appearance.

The command persists three immutable content-addressed objects:
- original raw MT5 bytes;
- canonical UTC XAUUSD OHLC CSV;
- ingestion/audit JSON manifest.

## 2. Never edit persisted objects

The replay path re-hashes the original raw file and canonical snapshot. Any byte change causes a fail-closed rejection.

The ingestion manifest itself is treated as untrusted input and is checked against:
- exact schema;
- canonical content-addressed paths;
- SHA-256 of raw bytes;
- SHA-256 of normalized bytes;
- broker/symbol/timeframe provenance;
- reconstructed `DataSnapshotManifest`;
- deterministic re-validation of the normalized OHLC file.

## 3. Evaluate a registered replay candidate

Example for a candidate whose source-chart metadata has been explicitly established:

```bash
xauusd-v2-replay-readiness \
  --candidate-id "RC-003" \
  --manifest "$HOME/.xauusd-v2/mt5/ingestions/<source-sha>--<snapshot-sha>.json" \
  --broker-name "EXACT BROKER NAME" \
  --source-symbol "EXACT BROKER SYMBOL" \
  --timeframe-seconds 60 \
  --window-start "2023-11-01T08:00:00+00:00" \
  --window-end "2023-11-01T12:00:00+00:00"
```

The source window must be timezone-aware and exactly aligned to the declared timeframe grid.

## 4. Interpret the output correctly

Possible alignment outcomes include:
- exact aligned candidate;
- broker mismatch;
- broker-symbol mismatch;
- timeframe mismatch;
- timestamp/grid mismatch;
- source window outside snapshot coverage;
- provisional/unclosed snapshot blocked.

Even an exact broker/chart alignment does **not** make the episode replay-ready by itself.

The current CLI intentionally reports stage timestamp certification as unavailable and therefore keeps an otherwise aligned episode at `BLOCKED_STAGE_TIMESTAMPS`.

A future machine-verifiable source-certification artifact must establish the R-143 `occurred_at` and `available_at` evidence before historical component replay can be unlocked.

## 5. What this path is allowed to prove

It can prove that:
- the exact MT5 source bytes were preserved;
- the normalized OHLC snapshot is reproducible and untampered;
- explicit source-chart broker/symbol/timeframe/window metadata either aligns or does not align with that snapshot.

It cannot prove:
- that a visual source label is correct;
- that an unresolved strategy boundary is resolved;
- that all R-143 stages are source-certified;
- that a setup was profitable;
- that the strategy is robust or production-ready.

## Relevant code

- `src/xauusd_v2/mt5_history.py`
- `src/xauusd_v2/mt5_history_cli.py`
- `src/xauusd_v2/mt5_snapshot_store.py`
- `src/xauusd_v2/mt5_snapshot_load.py`
- `src/xauusd_v2/source_chart_alignment.py`
- `src/xauusd_v2/replay_candidate_registry.py`
- `src/xauusd_v2/replay_candidate_readiness.py`
- `src/xauusd_v2/replay_readiness_cli.py`
- `10_backtesting/HISTORICAL_REPLAY_PROTOCOL.md`
