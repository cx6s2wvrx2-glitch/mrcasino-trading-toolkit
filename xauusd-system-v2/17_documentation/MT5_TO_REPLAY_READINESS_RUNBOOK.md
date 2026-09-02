# XAUUSD V2 — MT5 to Historical Replay Readiness Runbook

Status: FOUNDATION / FAIL-CLOSED / NO PERFORMANCE CLAIMS
Date: 2026-09-02

## Purpose

This runbook defines the deterministic path from an original broker MT5 XAUUSD history export to an immutable broker snapshot and then to one registered historical replay candidate.

It does **not** certify strategy truth, measure profitability, promote any rule to VERIFIED, or authorize live execution.

## 1. Preserve the original broker export

Use the original MT5 export exactly as produced by the broker/terminal. Do not edit rows, timestamps, OHLC values, headers or delimiters before validation.

Required metadata must come from real provenance:
- exact broker name;
- exact broker symbol used for gold;
- explicit timezone of the exported timestamps;
- exact timeframe in seconds;
- timezone-aware evaluation time.

The system never infers broker timezone, symbol alias or timeframe from chart appearance.

## 2. Validate first with `--dry-run`

Before persisting anything, validate and fingerprint the export:

```bash
xauusd-v2-ingest-mt5 \
  "/absolute/path/XAUUSD_history.tsv" \
  --broker-name "EXACT BROKER NAME" \
  --broker-symbol "EXACT BROKER SYMBOL" \
  --source-timezone "EXPLICIT BROKER TIMEZONE" \
  --timeframe-seconds 60 \
  --evaluation-time "2026-09-02T18:00:00+00:00" \
  --dry-run
```

A successful dry-run returns `VALIDATED_NOT_PERSISTED` plus:
- source SHA-256;
- normalized snapshot SHA-256 and snapshot ID;
- source byte size;
- bar count;
- first/last UTC timestamp;
- `closed_only` state;
- gap count and gap durations;
- detected delimiter;
- detected optional MT5 columns.

No snapshot-store files are created by the dry-run.

A failed validation returns `BLOCKED` and nothing is persisted.

## 3. Persist only after the dry-run is acceptable

Use the same unmodified source and the same explicit metadata, now with `--store-root`:

```bash
xauusd-v2-ingest-mt5 \
  "/absolute/path/XAUUSD_history.tsv" \
  --broker-name "EXACT BROKER NAME" \
  --broker-symbol "EXACT BROKER SYMBOL" \
  --source-timezone "EXPLICIT BROKER TIMEZONE" \
  --timeframe-seconds 60 \
  --evaluation-time "2026-09-02T18:00:00+00:00" \
  --store-root "$HOME/.xauusd-v2/mt5"
```

The command persists three content-addressed objects:
- original raw MT5 bytes;
- canonical UTC XAUUSD OHLC CSV;
- ingestion/audit JSON manifest.

Persistence is immutable and idempotent for identical bytes. A conflicting/tampered content-addressed object is rejected rather than overwritten.

## 4. Never edit persisted objects

The replay path reopens and re-hashes the original raw file and canonical snapshot. Any byte change causes fail-closed rejection.

The ingestion manifest is also treated as untrusted input and checked against:
- exact schema;
- canonical content-addressed paths;
- SHA-256 of raw bytes;
- SHA-256 of normalized bytes;
- broker/symbol/timeframe provenance;
- reconstructed `DataSnapshotManifest`;
- deterministic re-validation of normalized OHLC bytes.

## 5. Evaluate source-chart alignment for a registered candidate

Example:

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

The source window must be timezone-aware, inside snapshot coverage and aligned to the declared timeframe grid.

Possible outcomes include:
- exact alignment;
- broker mismatch;
- broker-symbol mismatch;
- timeframe mismatch;
- timestamp/grid mismatch;
- source window outside snapshot coverage;
- provisional/unclosed snapshot block.

Exact alignment alone does **not** make the episode replay-ready.

## 6. R-143 six-stage timestamp certification

The current system supports a strict optional stage evidence artifact:

```bash
xauusd-v2-replay-readiness \
  --candidate-id "RC-003" \
  --manifest "$HOME/.xauusd-v2/mt5/ingestions/<source-sha>--<snapshot-sha>.json" \
  --broker-name "EXACT BROKER NAME" \
  --source-symbol "EXACT BROKER SYMBOL" \
  --timeframe-seconds 60 \
  --window-start "2023-11-01T08:00:00+00:00" \
  --window-end "2023-11-01T12:00:00+00:00" \
  --stage-certification "/absolute/path/r143-stage-certification.json"
```

The artifact must be bound to the exact candidate, source locator, immutable snapshot, broker, symbol and timeframe. It must map all six R-143 stages to real closed broker bars with timezone-aware `occurred_at` and `available_at` evidence.

Canonical stage order:
1. HCS zone reaction;
2. TFS;
3. LAOL met;
4. True Stop respected;
5. 10m True Stop established;
6. targets and timing.

The loader reopens the exact persisted snapshot and verifies the referenced bars. Stage order, availability order and referenced-bar order cannot move backward. Evidence cannot become available before the referenced broker candle closes.

A bare `stage_timestamps_certified=true` flag is not accepted.

## 7. Interpret `replay_ready` correctly

A candidate may reach `replay_ready=true` only at the historical replay admissibility layer when both exact broker/chart alignment and a valid six-stage evidence artifact are present.

That state still means:
- `promotion_allowed=false`;
- `strategy_verified=false`;
- `performance_claim_allowed=false`.

Replay admissibility is not strategy certification and is not a profitability claim.

## 8. What this path is allowed to prove

It can prove that:
- the exact MT5 source bytes were preserved;
- the normalized OHLC snapshot is reproducible and untampered;
- explicit source-chart broker/symbol/timeframe/window metadata aligns or does not align;
- six source-labelled R-143 stages, when supplied, map to admissible closed broker bars without lookahead.

It cannot prove:
- that an unresolved strategy boundary has been resolved;
- that a visual label is automatically correct;
- that a setup was profitable;
- that the strategy is robust or production-ready;
- that live execution is authorized.

## Current real-data truth

As of 2026-09-02:
- real broker XAUUSD MT5 export ingested into the project evidence path = 0;
- real immutable broker-aligned replay episodes = 0;
- real six-stage R-143 certification artifacts = 0;
- real historical performance/backtest evidence = 0.

Do not replace these missing facts with TradingView approximations or inferred timestamps.

## Relevant code

- `src/xauusd_v2/mt5_history.py`
- `src/xauusd_v2/mt5_history_cli.py`
- `src/xauusd_v2/mt5_snapshot_store.py`
- `src/xauusd_v2/mt5_snapshot_load.py`
- `src/xauusd_v2/source_chart_alignment.py`
- `src/xauusd_v2/replay_candidate_registry.py`
- `src/xauusd_v2/replay_candidate_readiness.py`
- `src/xauusd_v2/replay_stage_certification.py`
- `src/xauusd_v2/replay_readiness_cli.py`
- `17_documentation/REPLAY_STAGE_CERTIFICATION_CONTRACT_2026_09_02.md`
- `10_backtesting/HISTORICAL_REPLAY_PROTOCOL.md`
