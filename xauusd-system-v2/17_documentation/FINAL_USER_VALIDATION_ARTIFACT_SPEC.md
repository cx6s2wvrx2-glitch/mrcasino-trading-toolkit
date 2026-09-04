# XAUUSD V2 — Final User Validation Artifact Spec

Date: 2026-09-04
Scope: `xauusd-system-v2/` only
Status: REQUIRED BEFORE MOVING BEYOND STRATEGY-UNDERSTANDING / BUILD PHASE

## Purpose

The final user-facing validation pack must let the user visually verify both:

1. what the system has actually implemented; and
2. what the assistant has actually understood about the strategy.

It must not require the user to read source code, terminal logs or internal JSON.

## Required deliverables

### A. Visual architecture / strategy understanding diagram

Must show, in one clear flow:

- supplied Casino helper markers;
- bullish Strong FU = bright green / `F`;
- bullish Attempted FU = faded green / `A`;
- bearish Strong FU = bright red / `F`;
- bearish Attempted FU = faded red / `A`;
- FU-family wick / retest relationship;
- HCS formation from a prior FU-family node and a later FU-family node;
- ordinary FU Negation relationship;
- `HCS + Negation` as a separate composite;
- BETA implementation state kept separate from source-style HCS logic;
- provenance labels for supplied-code events versus source-marker research proxies;
- unresolved boundaries, especially x3 / negation-of-negation, True Stop, TFS and exact reference-feed alignment.

The diagram must be in human Greek language. Technical identifiers may appear only as small secondary labels.

### B. Real replay visual / annotated timeline

Must be based on actual verified XAUUSD replay data, not synthetic bars.

At minimum include:

- one example of a Strong FU marker;
- one Attempted FU marker;
- one source-style HCS candidate;
- one FU Negation candidate if present in the chosen real replay window;
- one HCS + Negation candidate if present;
- a visible legend explaining provenance and candidate-only status;
- the March reference examples `1973`, `1975`, `1986`, with `1975` shown as unresolved rather than force-matched.

If a required compound event does not occur in the selected March window, use another real verified replay window and state that explicitly.

### C. Compact written explanation

Maximum target: 3–5 pages total for the whole pack unless the visual timeline requires an appendix.

Must answer:

- What does the system read first?
- What is supplied directly by the user's code?
- What relationships are constructed on top of those signals?
- What is implementation evidence versus source-style candidate logic?
- What is still unknown?
- What comes next before backtest / demo / live?

## Visual conventions

The final artifact should mirror the user's visual language where practical:

- bright green = bullish Strong FU;
- faded green = bullish Attempted FU;
- bright red = bearish Strong FU;
- faded red = bearish Attempted FU.

HCS and negation overlays should be visually distinct from raw FU markers.

Do not use a fake TradingView screenshot. If an actual chart screenshot is not available from the verified replay, use an explicitly labelled generated schematic/timeline based on real replay timestamps and data.

## Governance

The artifact must never present any of the following as proven when they remain unresolved:

- source-certified universal FU semantics;
- source-certified HCS occurrence at every proxy candidate;
- exact `FOREXCOM:XAUUSD` alignment;
- profitability or expected return;
- True Stop / TFS completion;
- production risk readiness;
- live execution authorization.

Every source-marker proxy must remain visibly marked as candidate/research evidence unless later upgraded by governed evidence.

## Build dependency

The Greek human-readable replay review (`casino_human_review.py`) is the textual backbone of this artifact.

The unified analysis event stream is the machine-readable backbone.

The final PDF/visual must be generated only after enough real replay windows have been inspected to make the examples representative and not cherry-picked.
