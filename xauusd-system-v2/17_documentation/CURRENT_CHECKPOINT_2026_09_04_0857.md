# XAUUSD V2 checkpoint — 2026-09-04 08:57 Europe/Athens

## Scope
Only `xauusd-system-v2/`.

## Real M15 replay received from the persisted Exclusive Markets XAUUSD! snapshot
Snapshot SHA256: `ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`
Window: `2023-03-30T00:00:00Z` to `2023-04-01T00:00:00Z`
Timeframe: M15
Derived bars affected by source gaps inside window: 0
Events on gap-affected derived bars: 0

Observed supplied Casino/BETA output:
- attempted FU markers: 33
- strong FU markers: 7
- BETA HCS events: 8
- bearish events: 30
- bullish events: 18

Observed narrow source-style Strong/ATT marker proxy:
- candidates: 20 on 15 second-node bars
- attempted+attempted: 11
- strong+attempted: 8
- strong+strong: 1

BETA HCS vs source-marker proxy by second-node bar:
- BETA HCS bars: 8
- source-marker proxy bars: 15
- overlap: 1
- BETA-only: 7
- source-proxy-only: 14

## Interpretation boundary
The supplied BETA HCS state machine and the narrow source-style `latest prior Strong/ATT marker wick retest` proxy are materially different implementations on the real March M15 broker data. The BETA HCS output must therefore not be treated as equivalent to source HCS truth.

The real replay also shows same-candle dual marker output can occur (for example M15 bars can emit a Strong marker for one direction and an Attempted marker for the other). The diagnostic preserves both nodes rather than inventing an ordering or discarding one.

No source occurrence timestamp is certified. No source HCS/FU semantics are certified. `FOREXCOM:XAUUSD` remains REQUIRED / DEFERRED / NOT ALIGNED.

## New next diagnostic implemented
`src/xauusd_v2/march_indicator_source_probe.py`

Purpose: use the actual supplied Casino Strong/ATT marker output and actual BETA/source-marker HCS outputs on **M1**, then inspect every exact broker bar touching the governed March source levels:
- 1973.00 — source role: strongest 1m FU closure
- 1975.00 — source role: easy 1m HCS re-entry
- 1986.00 — source role: clearest 1m HCS sell entry

For every touch it records:
- exact OHLC and UTC bar time
- Strong/Attempted marker output and visual direction
- same-bar dual marker state
- BETA HCS output
- source-marker HCS proxy candidates ending on that bar
- prior marker time/direction/wick and proxy form

This localizes the actual source-labelled examples using the user's supplied indicator mechanics instead of the older generic basic-FU proxy.

Tests are in `15_tests/test_march_indicator_source_probe.py`.

## CI
Code head `a50f817ce6a1fdaa9e443ad7911808a5e6b69ddf` passed the XAUUSD V2 test check before this checkpoint was written.

## Hard boundary
- no strategy certification
- no performance/profitability claim
- no promotion
- no live execution authorization
- no Supabase changes
- do not silently equate Exclusive Markets `XAUUSD!` geometry with canonical `FOREXCOM:XAUUSD`
