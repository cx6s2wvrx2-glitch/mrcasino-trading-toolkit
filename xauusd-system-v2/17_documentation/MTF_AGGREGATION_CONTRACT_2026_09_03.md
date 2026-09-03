# Multi-Timeframe Aggregation Contract — 2026-09-03

## Purpose

Build deterministic higher-timeframe XAUUSD **candidate** candles from the verified immutable Exclusive Markets M1 snapshot without re-exporting full history for every timeframe.

This layer is market-data construction only. It has no strategy authority and does not certify native MT5 boundaries by itself.

## Governed derived timeframes

Allowed from M1:

- `M5`
- `M10`
- `M15`
- `M30`
- `H1`
- `H4`
- `H8`
- `D1`

The broker-local boundary clock comes from the explicitly proven MT5 source timezone. For the first Exclusive Markets dataset this is `EET`, which follows GMT+2 in winter and GMT+3 in summer.

## Boundary rule

1. Source M1 timestamps are already normalized to UTC.
2. Each timestamp is converted to the broker timezone.
3. The parent bucket is selected on the broker-local clock.
4. The parent bucket start is converted back to UTC for canonical storage.
5. OHLC is reconstructed only from the actual M1 bars present in that bucket.

This is necessary because UTC boundaries move by one hour when the broker changes between winter and summer time.

## Missing-minute rule

Missing minutes are never synthesized or forward-filled.

Every derived candle records:

- actual M1 child count
- expected minute slots
- leading missing minutes
- internal missing minutes
- trailing missing minutes
- first and last actual child timestamp

A market closure at the beginning or end of a bucket remains visible as coverage metadata. An internal missing interval also remains visible. No gap is silently repaired.

A final parent bucket cut by the end of the source snapshot is not emitted as a closed higher-timeframe candidate.

## Native MT5 validation status

Derived candles remain:

`DERIVED_CANDIDATE_NOT_NATIVE_CERTIFIED`

until representative native MT5 higher-timeframe bars are exported and compared against the M1 reconstruction.

The next validation pass should use small representative samples from native MT5 for:

- H1
- H4
- H8
- D1

The purpose is to certify broker candle boundaries and OHLC reconstruction, not to create duplicate full-history datasets.

## 11h boundary

Synthetic 11h construction is explicitly blocked.

B-07 / R-118 does not yet certify the 11h candle/session anchor. The aggregation CLI must reject `H11`, `11H`, `M660`, or equivalent synthesis requests.

An already-formed provenance-bearing 11h series remains governed by the existing 11h gate; this contract does not change that rule.

## Feed separation

- TradingView strategy/reference feed: `FOREXCOM:XAUUSD` per the user-provided Mr Casino clarification.
- Current broker/execution research feed: Exclusive Markets `XAUUSD!`.

Derived Exclusive Markets candles must never be silently treated as identical to FOREXCOM candles. Cross-feed differences are evidence to measure during source alignment.

## Governance

Successful multi-timeframe derivation does **not**:

- change strategy truth
- resolve B-01 through B-08
- auto-promote any rule
- certify native broker boundaries before the comparison pass
- authorize paper trading
- authorize production risk
- authorize live execution
