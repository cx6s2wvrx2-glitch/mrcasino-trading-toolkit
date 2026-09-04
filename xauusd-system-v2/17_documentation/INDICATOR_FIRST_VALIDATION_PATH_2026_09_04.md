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

The second supplied screenshot also demonstrates two user-annotated HCS examples and the user identifies a retest relationship between them.

### Second screenshot provenance

- dimensions: `2048 x 1280`
- mode: `RGBA`
- byte size: `463548`
- SHA-256: `a26966a6c1ff78171d3e498aa5b83563d8f12a68f4c802e51dbf8cab73a19203`
- visible context: TradingView / `MNQ1!` / `15m`

The screenshot is visual/implementation evidence only and is not XAUUSD market ground truth.

A visual-source caution is also locked: the `Casino 9.0.3` row is hidden in the screenshot, while another indicator row beginning `Manipulation & Liqui...` is visible. Therefore the screenshot confirms the user's visual explanation but does not by itself prove which exact supplied source file rendered every visible arrow/annotation.

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
- explicit `Bear HCS RETESTING` / `Bull HCS RETESTING` states;
- opposite established-manipulation / negation logic;
- a separate HCS-context condition for the negation path.

V2 now has faithful non-certifying shadows for HCS count, HCS-zone retest and the BETA intra-negation/HCS-context gates.

## Canonical event stream for reconstruction

V2 normalizes supplied-indicator behavior into a simple chart/timeframe event stream. Current event vocabulary includes:

1. Strong FU bullish
2. Attempted FU bullish
3. Strong FU bearish
4. Attempted FU bearish
5. negating manipulation
6. HCS
7. HCS retest
8. negation with HCS context

`FU_NEGATION` and final `HCS_NEGATION` remain separate semantic promotions: the BETA implementation event is not automatically given those stronger source-level names until the corresponding source conditions are satisfied.

The event stream preserves metadata such as HCS count (`X1`, `X2`, ...), source helper, timeframe, direction, forming/confirmed state and relation to a prior tracked zone.

## B-01 / B-03 status under this architecture

The following are **not global blockers for the indicator-first event pipeline**:

- `B-01`: exact universal raw-OHLC rule for sufficient FU opposite break/move;
- `B-03`: universal numeric Strong-FU threshold.

They remain open only for:

- a source-independent raw detector;
- explaining discrepancies between supplied indicator output and source examples;
- future independent verification that does not rely on the supplied indicator implementation.

The project must not stop historical event reconstruction merely because B-01/B-03 remain unresolved. When the supplied code itself produces Strong/Attempted FU events, V2 may reproduce those implementation events with provenance and continue downstream analysis.

This does not mean those implementation events are automatically source-certified strategy truth.

## Authority / safety boundary

Indicator-first does **not** mean indicator-output-equals-certified-strategy-truth.

The supplied code is the operational detector/reference because it already embodies substantial Casino logic and exposes the chart structures the user relies on. Primary Casino/Reflection evidence and explicit user clarifications remain authoritative when meaning or behavior conflicts.

Therefore:

- do not infer a universal numeric Strong-FU threshold from marker colors;
- do not force every `A` into Reflection Form 1 or Form 2 without supporting evidence;
- do not treat MNQ screenshots as XAUUSD replay data;
- do not call every BETA opposite manipulation `FU negation`;
- do not call every BETA negation with HCS context a source-certified `HCS negation`;
- do not claim profitability/live certification merely because V2 matches the supplied indicator.

## Development sequence from here

1. Reproduce the four directional Strong/Attempted FU marker states. **DONE as supplied-code event adapters.**
2. Port the supplied-code negation states with clear separation between ordinary FU negation, x3 negation and self-negation. **ACTIVE; BETA opposite-manipulation shadow and tests exist.**
3. Port BETA HCS formation/count/retest state-machine behavior. **DONE as faithful non-certifying shadows.**
4. Port/identify HCS-negation behavior from supplied code and source evidence. **ACTIVE; HCS-context gate is now represented separately from final HCS-negation semantics.**
5. Produce one normalized event stream per chart/timeframe. **FOUNDATION IMPLEMENTED; next step is to feed it directly from sequential market bars/state.**
6. Compare V2 event stream against labelled screenshots/source examples.
7. Only when mismatches exist, use raw-OHLC diagnostics to explain them.
8. Then compose the full Casino strategy sequence on top of the validated event stream.
9. Then historical replay and backtest.

## March 1975 / 1986

The March diagnostics remain useful controls, but they no longer define the detector architecture. They should be revisited only after the supplied-indicator event stream has been faithfully reproduced.

## Immediate next engineering step

Build the sequential single-timeframe supplied-indicator runner that consumes closed bars in chronological order, updates the faithful FU/HCS/negation state, and emits `CasinoIndicatorEventFrame` objects.

That runner becomes the first real bridge from historical XAUUSD bars to the same simple event vocabulary the user sees visually on a chart.

## User action

No manual user action is required for this phase.
