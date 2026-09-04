# XAUUSD V2 — CURRENT CHECKPOINT — 2026-09-04 07:55 Europe/Athens

## Current path

The project is now on the indicator-first validation path.

User-clarified visual legend:
- bright green = bullish Strong FU
- faded green = bullish Attempted FU
- bright red = bearish Strong FU
- faded red = bearish Attempted FU

The supplied indicator/code is treated as the first event detector. Strategy analysis consumes normalized events instead of rediscovering every FU from scratch.

## Implemented and tested

Existing normalized supplied-code event layers:
- Strong FU / Attempted FU directional marker semantics
- HCS Xn supplied BETA shadow
- HCS retest supplied BETA shadow
- BETA negation + HCS-context adapters

New historical sequential runner:
- `src/xauusd_v2/casino_historical_event_runner.py`
- closed bars processed strictly left-to-right
- final provisional bar cannot emit confirmed events
- Casino_v7 Strong/ATT helper behavior + supplied current-candle doji filter
- independent BETA broad FU/SN state
- BETA tracked-box HCS X1/X2/... state
- BETA 50/60-minute HCS-zone retest state
- normalized output through `CasinoIndicatorEventFrame`
- all strategy certification, performance, promotion and live flags remain false

Tests:
- `15_tests/test_casino_historical_event_runner.py`
- Strong bullish marker
- Attempted bullish marker
- supplied doji filtering
- HCS X1 -> X2 sequential state
- provisional-bar future-leak prevention
- monotonic-history validation

CI:
- run #571, head `413f74bdd21ca23e98ecea478a256ac4ba4462a9`, completed success

## Verified snapshot bridge

New files:
- `src/xauusd_v2/casino_history_report.py`
- `src/xauusd_v2/casino_history_report_cli.py`

Registered CLI:
- `xauusd-v2-indicator-history`

Behavior:
- re-verifies the persisted MT5 snapshot before replay
- supports M1 directly and governed derived M5/M10/M15/M30/H1/H4/H8/D1
- derived candles use the source timezone stored in the verified ingestion manifest; timezone is not inferred
- replay state is seeded from available history before the requested output window so HCS state is not reset at the window boundary
- reports event counts and event records
- reports gap-affected derived bars
- does not claim reference-feed alignment or strategy certification

CI:
- run #574, head `a829953df79c66aea09d6a862709d66071592c5d`, completed success

## Supplied BETA source facts used

The supplied BETA code computes broad FU candidates per timeframe from current/previous OHLC, stores those booleans, then uses same-direction FU/SN interactions with tracked boxes to increment HCS count. The supplied code creates tracked bear boxes from high to body-top and bull boxes from body-bottom to low and maintains the box state sequentially.

This BETA behavior remains implementation evidence and is not silently equated to the complete source HCS grammar.

## Governance unchanged

Reference feed:
- `FOREXCOM:XAUUSD = REQUIRED / DEFERRED / NOT ALIGNED`
- broker research feed remains Exclusive Markets `XAUUSD!`
- never silently equate feeds

No certification or promotion of:
- FU source truth
- HCS source truth
- True Stop
- TFS
- six-stage R-143 automation
- profitability / expected return
- production risk readiness
- live execution

No Supabase changes were made in this sequence.

## Next exact action

Run `casino_history_report_cli` against the persisted March MT5 ingestion manifest for M15 over 2023-03-30 through 2023-04-01 and inspect the real Strong/ATT/HCS event stream. This requires the user's local persisted snapshot; it cannot be executed from GitHub CI alone.

After the real output is inspected, the next code layer is multi-timeframe negation/HCS-context composition on top of the emitted event stream, not a return to raw-FU threshold reverse engineering.
