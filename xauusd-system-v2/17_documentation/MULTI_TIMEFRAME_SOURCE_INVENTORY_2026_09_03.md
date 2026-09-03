# Multi-Timeframe Source Inventory — 2026-09-03

## Purpose

Define the XAUUSD V2 timeframe universe from evidence, while keeping implementation helpers separate from primary strategy authority.

This is an inventory/engineering record only. It does not certify candle anchors for every custom timeframe and does not change strategy truth.

## A. Beta implementation helper — exact configured list

Source helper: `BETA 1 + LAOL.txt`

The file contains:

- `TF_COUNT = 25`
- configured minute intervals:

`1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 35, 40, 45, 50, 55, 60, 90, 100`

Implementation categories in that beta:

- ENTRY: 1–5m
- SCALP: configured 6–20m
- INTRA: configured 30–100m

Authority: implementation helper only. The beta repaints/forming states are not strategy ground truth.

## B. Primary source HTF zone/refinement sequence

Primary Reflection material gives the optimal HTF zone-marking descent as:

`4D → D1 → 18h → 15/14h → 12h → 11h → 7h → 5h → 4h → 3h → 1h → 50m`

It also states that zone refinement starts from the higher layers and descends, with 1h/50m specifically used for HCS zone marking in that sequence.

The `15/14h` notation is preserved as written and is not silently converted into two mandatory layers.

## C. Primary TFS hierarchy

Primary Reflection material enumerates five TFS settings:

- macro
- scalp
- intraday
- swing
- extreme swing

Additional primary/certified Reflection material gives a quantitative scale:

- 1–5m: LTF / minimum scalp
- 7–30m: scalp / intraday move
- 30m–3h: intraday
- 3h–7h: swing
- 7h–4D+: long-term / extreme swing

A primary swing sequence is also explicitly shown as:

`3h → 5h → 7h → 11h`

## D. Why the practical universe is about 35 layers

The beta helper itself has exactly 25 configured minute timeframes.

The primary HTF sequence contributes roughly ten additional higher-timeframe layers not present in that beta list (depending on how the source's `15/14h` alternative is represented). Therefore a practical full multi-confirmation universe is approximately 35 layers, rather than being limited to the beta's 25.

This reconciles the user-reported ~35-timeframe view with the exact beta code: `25` is the beta's configured count; `~35` is the broader source-led multi-timeframe universe.

## E. Engineering classes

### Already broker-native validated from Exclusive Markets M1

- H1
- H4
- H8
- D1

Representative native MT5 samples matched M1-derived OHLC exactly.

### Standard minute candidates derivable from M1 but not yet individually reference-anchor certified

Examples include beta minute intervals such as 2m, 3m, 4m, 6m, 7m, 8m, 9m, 11m, 12m, 13m, 14m, 20m, 35m, 40m, 45m, 50m, 55m, 90m, 100m.

These must not be assumed to share TradingView `FOREXCOM:XAUUSD` anchor semantics merely because they can be mathematically aggregated from broker M1.

### Custom HTF requiring explicit reference/session anchor validation

- 3h
- 5h
- 7h
- 11h
- 12h
- 14h / 15h
- 18h
- 4D

`11h` remains specifically blocked under B-07 until its session/candle anchor is certified.

## F. Feed separation

- Canonical visual/strategy reference: TradingView `FOREXCOM:XAUUSD` per user-provided Mr Casino clarification.
- Broker/execution research feed: Exclusive Markets `XAUUSD!`.

Custom timeframe geometry must be measured across feeds; it must never be forced to match silently.

## Next implementation gate

Build a governed timeframe registry where every timeframe records:

- duration
- source authority
- intended role (zone/context/TFS/confirmation/execution)
- reference feed
- anchor/session status
- aggregation status
- native/reference validation status
- blocker if unresolved

No custom timeframe becomes research-certified solely because the beta helper contains it.
