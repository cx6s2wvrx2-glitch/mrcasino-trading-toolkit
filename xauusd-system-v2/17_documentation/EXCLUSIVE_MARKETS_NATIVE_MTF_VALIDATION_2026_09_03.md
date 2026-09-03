# Exclusive Markets Native MTF Validation — 2026-09-03

## Status

`PASS`

The immutable Exclusive Markets M1 snapshot was used to deterministically reconstruct higher-timeframe candidates. Representative native MT5 exports were then compared against those M1-derived candles.

This is a market-data boundary/OHLC validation only. It does not change strategy truth, resolve strategy blockers, permit promotion, or authorize live execution.

## Source snapshot

- Broker: `Exclusive Markets Ltd.`
- Broker symbol: `XAUUSD!`
- Source timezone: `EET` (broker-confirmed winter GMT+2 / summer GMT+3)
- M1 source bars: `1,999,671`
- Source SHA-256: `691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0`
- Normalized snapshot SHA-256: `ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`
- Frozen normalized horizon: through `2026-09-03T09:51:00+00:00` M1 open timestamp

## Native comparison results

### H1

- Native export bars: `3,979`
- Fully comparable inside frozen M1 horizon: `3,976`
- Newer native bars ignored: `3`
- Exact OHLC matches: `3,976`
- Missing candidate timestamps: `0`
- OHLC mismatches: `0`
- Result: `PASS`

### H4

- Native export bars: `1,040`
- Fully comparable inside frozen M1 horizon: `1,039`
- Newer native bars ignored: `1`
- Exact OHLC matches: `1,039`
- Missing candidate timestamps: `0`
- OHLC mismatches: `0`
- Result: `PASS`

### H8

- Native export bars: `521`
- Fully comparable inside frozen M1 horizon: `520`
- Newer native bars ignored: `1`
- Exact OHLC matches: `520`
- Missing candidate timestamps: `0`
- OHLC mismatches: `0`
- Result: `PASS`

### D1

- Native export bars: `174`
- Fully comparable inside frozen M1 horizon: `173`
- Newer native bars ignored: `1`
- Exact OHLC matches: `173`
- Missing candidate timestamps: `0`
- OHLC mismatches: `0`
- Result: `PASS`

## Interpretation

For the tested Exclusive Markets native timeframes, the deterministic broker-local M1 aggregation reproduces native MT5 candle boundaries and OHLC exactly over the representative 2026 sample, including winter/summer DST coverage.

This validates the aggregation method for the tested broker/timeframe family. It does not imply that arbitrary custom TradingView timeframes share the same anchor semantics.

## Multi-timeframe universe note

The archived beta implementation helper `BETA 1 + LAOL.txt` contains exactly `TF_COUNT = 25` configured minute timeframes:

`1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,20,30,35,40,45,50,55,60,90,100`

with implementation categories:

- ENTRY: `1–5m`
- SCALP: configured `6–20m`
- INTRA: configured `30–100m`

This beta list is implementation-helper evidence only, not strategy ground truth. Primary source material also shows higher/custom timeframes such as `12h, 7h, 5h, 4h, 3h, 50m` as an illustrative zone-drawing set and identifies a broader TFS hierarchy. Therefore production multi-timeframe support must be source-led and must not be frozen to the beta's 25 entries.

## Next gate

Before expanding arbitrary custom timeframe aggregation, determine for each candidate timeframe:

1. source authority and intended role (context / zone / TFS / confirmation / execution),
2. canonical reference feed (`FOREXCOM:XAUUSD` where applicable),
3. exact candle/session anchor semantics,
4. whether the timeframe is native, custom-minute, custom-hour, or synthetic,
5. whether representative native/reference candles can be independently validated.

`11h` remains separately blocked under B-07 until its session/candle anchor is certified.
