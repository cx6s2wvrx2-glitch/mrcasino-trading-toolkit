# TFS / True Stop — Certification Draft

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01
Round: 01 — mechanical decomposition started

Only approved V2 sources are used. No legacy inheritance and no code-derived strategy semantics.

## 1. TFS core definition

Primary Reflection evidence:

- R-107: TFS = confirmed prevalent direction.
- R-58: TFS represents bank-order pressure / intensity of intended move, not merely a technical indicator.
- R-59: TFS has multiple settings: macro, scalp, intraday, swing, extreme swing.
- R-217: two modes exist — ESTABLISHED and AS FORMING.

Core implementation consequence:

`TFS` must be modeled as a stateful directional context, not as a single candle label.

## 2. Mechanical candidate rules — TFS

### C-TFS-001 — Confirmed prevalent direction

Source: Reflection R-107.

Candidate rule:

TFS may be labelled `ESTABLISHED` only after the relevant confirming candle/context is closed and the prevalent direction is confirmed.

Output:

`TFS.direction = bullish | bearish`

`TFS.state = ESTABLISHED`

Hard rule:

A still-forming candle cannot be stored as historical established truth.

This directly supports the V2 anti-repaint architecture:

- live forming state = provisional;
- closed/confirmed state = immutable historical state.

### C-TFS-002 — Minimum confirmation layer for refined entry context

Source: Reflection R-107.

Candidate rule:

Refined entry decisions require 10m/15m+ TFS confirmation according to the active setup.

Output:

`entry_context_tfs_confirmed = true | false`

Open:

The exact choice between 10m, 15m or higher must be derived from the specific TFS setting / source examples, not guessed.

### C-TFS-003 — ESTABLISHED versus AS_FORMING

Source: Reflection R-217.

Candidate states:

- `ESTABLISHED`: confirmed prevalent direction.
- `AS_FORMING`: forming TFS information used only when an already established prevalent TFS exists.

Candidate gate:

`AS_FORMING` is NOT permitted to create an independent direction from zero context.

It can create a provisional/power-POI context only on top of an already established prevalent TFS.

### C-TFS-004 — Multi-setting separation

Sources: Reflection R-59/R-60.

Candidate architecture:

Maintain independent TFS state for at least:

- macro
- scalp
- intraday
- swing
- extreme swing

Do not collapse them into one global bullish/bearish flag.

True reversal / LAOL logic must be evaluated within the relevant TFS setting.

### C-TFS-005 — TFS scale is descriptive evidence, not production target logic

Source: Reflection R-215.

Source claim records approximate TFS groupings and pip scales.

V2 handling:

- preserve the source claim;
- do not turn the stated pip ranges into production profit targets without empirical validation;
- use the timeframe grouping first as a classification hypothesis.

## 3. True Stop core definition

Primary Reflection R-108:

TRUE STOP = the low/high where all 10m+ TFS factors align; this is a Main POI. LTF HCS/negation entry follows after the TS is respected plus final liquidity calculation.

Core consequence:

`True Stop` is contextual and stateful.

It is NOT equivalent to:

- any swing high/low;
- any FU wick;
- any HCS by itself;
- a fixed stop-loss placement rule.

## 4. Mechanical candidate rules — True Stop

### C-TS-001 — True Stop candidate creation

Source: Reflection R-108.

Candidate preconditions:

1. a low/high candidate exists;
2. relevant 10m+ TFS factors align;
3. the point functions as the active Main POI for the current context.

Output:

`TS.state = CANDIDATE`

Open blocker:

The exact exhaustive list of `all 10m+ TFS factors` is not yet mechanically decomposed. Until that list is certified, automated TS creation remains candidate-only.

### C-TS-002 — TS respect gate

Sources: R-108 + R-143.

Candidate sequence requires TS to be respected before final entry progression.

Output:

`TS.respected = true | false | unresolved`

Open:

Exact candle-level mechanics for `respected` require labelled examples.

### C-TS-003 — HCS refinement hierarchy

Source: Reflection R-65.

Candidate relationship:

`HCS refinement = retest of TRUE STOP`

Hierarchy candidate:

`HCS_refinement > ordinary_FU_retest`

This is a strength/context relationship, not a guarantee of trade success.

### C-TS-004 — HCS establishment prerequisite

Source: Reflection R-180 occurrence 2.

Candidate rule:

An HCS is ESTABLISHED only if the left FU was retested first.

If that prerequisite is absent:

- do not label the HCS established;
- the next valid point becomes the EST TFS POI according to the source sequence.

This needs frame-level positive/negative examples before coding.

### C-TS-005 — Broken LTF true-stop information is directional context, not standalone entry

Source: primary Price Action Reflection 2023-04-03.

Candidate interpretation:

A broken 1m HCS true stop may support continuation when broader liquidity, target and HTF/TFS context agree.

Hard restriction:

`broken_LTF_TS` alone must not create direction or entry.

## 5. TFS / TS entry sequence

### C-ENTRY-TFS-001 — Retest of established TFS

Source: Reflection R-182.

Candidate rule:

Entry is evaluated on RETEST of an established TFS with confirmed prevalent direction.

Required state:

- `TFS.state = ESTABLISHED`
- `TFS.direction = confirmed`
- retest event detected

Still required later:

- liquidity/LAOL context
- TS context
- approved entry trigger

### C-ENTRY-TFS-002 — Official backtest sequence

Source: Reflection R-143.

The system must be able to reproduce this order:

`HCS zone reaction`
→ `TFS`
→ `LAOL met`
→ `TS respected`
→ `10m TS established`
→ `core + major + LAOL target / timing`

This sequence becomes a mandatory test scaffold for the later deterministic engine.

If the historical engine cannot reproduce the source-labelled order without future information, it fails certification.

### C-ENTRY-TFS-003 — LTF execution sequence

Source: Reflection R-145.

Candidate flow:

`retail liquidity manipulated`
→ `LTF LAOL taken`
→ trigger through `1m negation` OR `3m HCS + negation`

Aggressive mode is allowed only with fuller TFS context.

No aggressive mode may bypass deterministic risk gates.

### C-ENTRY-TFS-004 — Directional checklist before entry

Source: Reflection R-209.

Directional outlook candidate checklist:

- Zones
- HTF TFS
- EST TFS
- major liquidity taken
- major liquidity to target

Entry adds:

- core LTF liquidity
- advanced entry-model TS

This is a candidate checklist, not yet a numeric score.

## 6. Primary Price Action Reflection corroboration

The 2023-04-02/03 text+visual episode supports several contextual relationships:

- after liquidity is generated, a True Stop can form;
- breaking a 1m HCS True Stop can support broader continuation when an IMB/major target and wider context agree;
- aggressive entry while higher-TF structure is still forming is discussed only when zone, liquidity left behind, respected TS, TFS, major target and broken opposing TS already align;
- after a completed HTF close establishes strength, comparable higher-TF evidence is needed before assuming true negation in the opposite direction.

These observations are evidence for state-machine design, not standalone production rules yet.

## 7. Candidate state machine

### TFS

`UNKNOWN`
→ `FORMING_PROVISIONAL`
→ `ESTABLISHED`
→ `RETESTED`
→ `RESPECTED / CONTINUING`
→ `NEGATED / REPLACED`

Important:

`FORMING_PROVISIONAL` must never be rewritten into historical truth after the fact.

### True Stop

`NONE`
→ `CANDIDATE`
→ `ESTABLISHED`
→ `RETESTED`
→ `RESPECTED`
→ `BROKEN / INVALIDATED`

These states are architecture candidates. Transition conditions remain to be certified from primary examples.

## 8. Required labelled tests

### TFS established

- positive: confirmed prevalent direction after close;
- negative: forming-only signal without established backing;
- edge: HTF established but LTF temporarily opposite.

### TFS as-forming

- positive: forming continuation on top of established prevalent TFS;
- negative: forming signal attempting to create a new independent direction;
- edge: forming signal near possible negation.

### True Stop

- positive: source-labelled Main POI with aligned 10m+ TFS factors;
- negative: visually similar low/high without full context;
- edge: competing TS candidates on adjacent TFs.

### TS respected

- positive: source-labelled respect followed by valid refinement;
- negative: level breaks / fails context;
- edge: wick penetration versus body/close treatment.

### Established HCS prerequisite

- positive: left FU retested first;
- negative: HCS-like structure without prior left-FU retest;
- edge: partial/ambiguous retest.

## 9. Open questions after Round 01

Do not ask the user until existing primary sources/visuals are exhausted.

1. Exact complete list of `all 10m+ TFS factors` in R-108.
2. Exact deterministic definition of TS `respected`.
3. Exact transition from TFS `AS_FORMING` to `ESTABLISHED`.
4. Exact invalidation/negation rule for established TFS by setting.
5. Exact TF selection logic when 10m and 15m disagree.
6. Whether wick-only penetration can preserve TS respect in every context or only specific ones.
7. Exact relationship between HCS establishment, EST TFS POI and later TS establishment.

## 10. Current certification state

Strong enough for labelled-example construction:

- TFS = confirmed prevalent direction;
- closed/confirmed versus forming/provisional separation;
- ESTABLISHED versus AS_FORMING distinction;
- True Stop is contextual Main POI, not a candle pattern;
- HCS refinement is hierarchically tied to TS retest;
- entry on retest of established TFS is a core source-supported candidate;
- official backtest sequence R-143 is a mandatory validation scaffold.

NOT VERIFIED / NOT production-ready:

- full TFS factor list;
- state-transition mechanics;
- exact respect/invalidation geometry;
- deterministic multi-TF conflict resolution.

Ambiguity => `NO_TRADE / NOT_CERTIFIED`.