# XAUUSD V2 — Indicator-First Validation Path

Date: 2026-09-04
Status: ACTIVE ARCHITECTURE / RESEARCH ONLY / NOT LIVE AUTHORITY

## Why this document exists

The project had begun over-reconstructing Strong FU / Attempted FU / HCS from generic raw-OHLC proxies even though the user had already supplied working indicator code that exposes these structures directly on-chart.

This document locks the simpler architecture:

> supplied Casino/BETA code = operational chart sensor / event reference
> source material + explicit user clarifications = semantic authority / validation
> V2 = faithful event reproduction first, strategy composition second

Raw-OHLC diagnostics remain useful for debugging discrepancies, but are no longer the default way to rediscover every primitive from scratch.

## User-clarified visual legend

Explicit clarification on 2026-09-04:

- bright green = **bullish Strong FU**
- faded green = **bullish Attempted FU**
- bright red = **bearish Strong FU**
- faded red = **bearish Attempted FU**

Earlier clarification remains:

- `F` = Strong FU
- `A` = Attempted FU

The second supplied screenshot also visibly demonstrates two HCS annotations and the user identifies a retest relationship between them.

### Second screenshot provenance

- dimensions: `2048 x 1280`
- mode: `RGBA`
- byte size: `463548`
- SHA-256: `a26966a6c1ff78171d3e498aa5b83563d8f12a68f4c802e51dbf8cab73a19203`
- visible context: TradingView / `MNQ1!` / `15m`

The screenshot is implementation/legend evidence only and is not XAUUSD market ground truth.

## Supplied-code evidence that supports the indicator-first path

### Casino_v7

The supplied Pine code exposes four directional FU-family states:

- `isFUBullv6`
- `isAttFUBullv6`
- `isFUBearv6`
- `isAttFUBearv6`

and renders `F` or `A` markers above/below bars.

V2 preserves the original legacy helper labels internally, then adapts them to the user-clarified Strong/Attempted semantics.

### BETA 1 + LAOL

The supplied BETA state machine already contains operational HCS tracking:

- directional `bear_hcs` / `bull_hcs` states;
- tracked FU/SN boxes;
- HCS counter increments (`hcs_count`);
- rendered text `HCS Xn`;
- separate HCS zone objects;
- explicit `Bear HCS RETESTING` / `Bull HCS RETESTING` states.

This is high-value detector/state-machine evidence and should be ported/tested faithfully before inventing a replacement HCS scanner.

## Canonical event stream for reconstruction

V2 should normalize supplied-indicator behavior into events such as:

1. Strong FU bullish
2. Attempted FU bullish
3. Strong FU bearish
4. Attempted FU bearish
5. FU negation
6. HCS
7. HCS retest
8. HCS negation

The event model may preserve implementation metadata such as HCS count (`X1`, `X2`, ...), source helper, timeframe, direction and relation to a prior tracked zone.

## Authority / safety boundary

Indicator-first does **not** mean indicator-output-equals-certified-strategy-truth.

The supplied code is the operational detector/reference because it already embodies substantial Casino logic and exposes the chart structures the user relies on. Primary Casino/Reflection evidence and explicit user clarifications remain authoritative when meaning or behavior conflicts.

Therefore:

- do not infer a universal numeric Strong-FU threshold from marker colors;
- do not force every `A` into Reflection Form 1 or Form 2 without supporting evidence;
- do not treat MNQ screenshots as XAUUSD replay data;
- do not claim FU/HCS/profitability/live certification merely because V2 matches the supplied indicator.

## Development sequence from here

1. Reproduce the four directional Strong/Attempted FU marker states.
2. Port the supplied-code negation states with clear separation between ordinary FU negation, x3 negation and self-negation.
3. Port BETA HCS formation/count/retest state-machine behavior.
4. Port/identify HCS-negation behavior from supplied code and source evidence.
5. Produce one normalized event stream per chart/timeframe.
6. Compare V2 event stream against labelled screenshots/source examples.
7. Only when mismatches exist, use raw-OHLC diagnostics to explain them.
8. Then compose the full Casino strategy sequence on top of the validated event stream.
9. Then historical replay and backtest.

## March 1975 / 1986

The March diagnostics remain useful controls, but they no longer define the detector architecture. They should be revisited only after the supplied-indicator event stream has been faithfully reproduced.

## User action

No manual user action is required for this phase.
