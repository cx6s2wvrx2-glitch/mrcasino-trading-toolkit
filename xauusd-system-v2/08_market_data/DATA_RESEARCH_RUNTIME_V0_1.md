# XAUUSD V2 — Data → Research Runtime v0.1

Status: foundation / not production.

## Goal

Connect Agent 03 (XAUUSD Data) to Agent 05 (Quantitative Research) without allowing dirty data, provisional candles, snapshot drift, or uncertified strategy logic to enter a performance backtest.

## Immutable snapshot contract

Historical CSV input must contain:

- `timestamp` — timezone-aware ISO-8601 bar-open timestamp
- `open`
- `high`
- `low`
- `close`

The runtime computes a SHA-256 digest over the original file bytes. The canonical snapshot reference is:

`sha256:<digest>`

The snapshot retains:

- canonical symbol: XAUUSD
- original source/broker name
- original broker symbol alias (for example `XAUUSD.a`)
- timeframe
- bar count
- first/last timestamp
- coverage end
- closed/provisional state

No silent price-source merging is allowed.

## Two readiness levels

### DATA_READY

Requires:

- valid Agent 03 OHLC/time/provenance checks
- immutable snapshot reference match
- closed-only historical data
- snapshot covers train → validation → locked test windows
- valid Agent 05 research design

`DATA_READY` does **not** authorize a strategy performance backtest when strategy certification is incomplete.

### BACKTEST_READY

Requires everything in `DATA_READY` plus an explicit upstream strategy-certification-ready gate.

The runtime does not infer this gate itself.

## Current V2 state

Because canonical strategy rules are not yet VERIFIED, the expected maximum state today is `DATA_READY`. This is intentional and fail-closed.

## Explicitly not implemented yet

- MT5 broker adapter
- Parquet/DuckDB storage adapter
- tick-data ingestion
- raw-OHLC FU/HCS/TS strategy detectors
- trade simulator
- performance metrics engine
- production risk configuration
- live execution
