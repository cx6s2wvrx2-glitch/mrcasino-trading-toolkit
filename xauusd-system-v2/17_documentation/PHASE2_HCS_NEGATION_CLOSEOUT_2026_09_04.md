# XAUUSD V2 — Phase 2 HCS / Negation Research Closeout

Date: 2026-09-04
Scope: `xauusd-system-v2/` only
Status: RESEARCH FOUNDATION COMPLETE / NOT STRATEGY-CERTIFIED

## What Phase 2 set out to do

Build a clean chart-event layer on top of the supplied Strong/Attempted FU marker output, without rediscovering every pattern from raw OHLC and without conflating supplied implementation behavior with source-style strategy logic.

## What is now implemented

### Supplied-code events

- bullish Strong FU;
- bullish Attempted FU;
- bearish Strong FU;
- bearish Attempted FU;
- BETA HCS counter events;
- BETA HCS retest events;
- neutral BETA negation implementation events.

### Source-style research relationships

- HCS proxy from a later FU-family node retesting the latest prior visible FU-family wick;
- FU Negation proxy from the latest prior Strong/ATT manipulation to an opposite Strong/F on candle +1 or +2;
- ATT → opposite ATT is not promoted to ordinary FU Negation;
- a physical Strong/F node that is also the negating node may carry the semantic role `fu_negation` inside HCS without being double-counted as two physical nodes;
- HCS + Negation proxy from a formed source-style HCS whose physical second node is negated by an opposite Strong/F within +1/+2;
- negation-of-negation / x3 territory remains excluded.

### Unified timeline

`casino_analysis_event_stream.py` merges these into one candle-by-candle timeline while retaining provenance:

- `supplied_casino_helper`;
- `supplied_beta_state_machine`;
- `source_marker_proxy`.

Research proxies remain explicitly candidate-only.

### Human review output

`casino_human_review.py` produces a compact Greek review suitable as the textual backbone for the final visual/PDF validation artifact.

The history CLI supports `--review` in addition to the technical `--summary` and full JSON modes.

## Real replay evidence so far

Corrected replay remains consistent with the following March interpretation:

- `1973`: clean bullish Strong FU observation in supplied-helper replay;
- `1986`: useful ATT-to-ATT retest / source-style HCS control; it is not ordinary FU Negation;
- `1975`: unresolved on Exclusive Markets geometry and must not be force-matched;
- 12:31 + 12:32 must not be merged into a staged HCS without governing authority.

A broader M15 replay also shows that the supplied BETA HCS mechanism and the source-style latest-FU-wick HCS proxy are not interchangeable. Their divergence must remain visible rather than silently normalized.

## What this phase does NOT claim

Phase 2 does not certify:

- universal raw FU semantics;
- every source-style HCS candidate as a true source occurrence;
- exact FOREXCOM:XAUUSD geometry;
- x3 / x3-by-x3 / negation-of-negation raw grammar;
- True Stop or TFS;
- trading edge, profitability, risk readiness or live execution.

## Why Phase 2 can close as a research foundation

The downstream analyzer now has the simple event language the user asked for:

`Strong FU / ATT FU / HCS / FU Negation / HCS + Negation`

with provenance and fail-closed boundaries preserved internally.

The remaining open questions no longer require the system to stay stuck rebuilding FU/HCS from scratch. They can be addressed in context during the full strategy-sequence phase.

## Next phase

Phase 3: full strategy-sequence composition.

Target path:

`liquidity/context → manipulation event stack → direction/POI → True Stop/TFS evidence → LTF refinement/entry → targets/management`

Before profitability backtesting, the system must show that this sequence can be reconstructed on known source examples and on real replay without future leakage.
