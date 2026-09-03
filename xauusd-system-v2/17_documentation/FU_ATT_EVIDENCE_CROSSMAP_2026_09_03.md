# XAUUSD V2 — FU / ATT FU Evidence Cross-Map

Date: 2026-09-03
Status: ACTIVE RECONSTRUCTION / NOT CERTIFIED / NO LIVE AUTHORITY
Scope: FU family only. HCS/Negation downstream use is referenced only where needed.

## Purpose

Create one coherent map between:
1. approved primary Casino/Reflection evidence,
2. explicit user clarifications,
3. supplied Strong-FU / ATT-FU implementation code,
4. current V2 executable modules.

This document does not promote any rule to VERIFIED and does not authorize performance or live-trading claims.

## Authority rule

1. Explicit primary Mr Casino source statement.
2. Explicit user clarification.
3. Supplied Casino_v7 / BETA code behavior as high-value implementation and interpretation evidence.
4. Current V2 detector behavior.

The supplied codebases must be used actively to understand mechanics, edge cases and candidate state transitions. They are not discarded as low-value helpers. If a code behavior conflicts with explicit primary/user evidence, the conflict is preserved rather than silently reconciled.

---

## 1. FU core validity

### Source-backed evidence

- `03_Analysis_Basics_.pdf`, p.4-5: FU takes liquidity and moves/reverses in the opposite direction within the same candle. A strong close with little/no rejection is desirable.
- `02_The_10_Free_Lessons_.pdf`, Lesson 4: valid FU is described with liquidity take plus break of structure from the same candle after liquidity is taken.
- `How to rinse the banks - A forex guide.pdf`, p.23: valid FU has liquidity take plus break of prior-candle high/low; the source excerpt does not fully settle whether body close beyond the level is universally required.

### Current V2 semantic contract

`fu_criteria.py` correctly keeps the semantic conjunction separate:
- liquidity taken,
- opposite-direction move,
- same candle.

It deliberately does not equate all liquidity with a previous-candle sweep.

### Current narrow raw proxy

`fu_basic_candidate.py` recognizes only the simplest previous-candle geometry:
- previous-low sweep + bullish candle,
- previous-high sweep + bearish candle,
- both-side sweep => ambiguous.

This is a conservative proxy, NOT the complete FU definition.

### Open boundary

`B-01` remains open: exact sufficient raw mechanic for the opposite-direction move / break is not yet universally certified.

### Reconstruction conclusion

Do not expand `basic_fu_candidate` ad hoc. Build a richer FU-family observability layer from source + supplied-code branches first, while preserving the semantic gate above it.

---

## 2. Complete FU vs Attempted FU

### Reflection source-backed classes

`GIANNO_CASINO_REFLECTION_MASTER.pdf`, p.33:

- R-120 COMPLETE FU: FU criteria are met AND close is within the previous candle open/close body.
- R-121 ATTEMPTED FU Form 1: price does not make a new high/low; it still counts as an FU-retest POI.
- R-122 ATTEMPTED FU Form 2: a new extreme/FU setup exists but required closure within the previous candle body is not achieved.

### Current V2 implementation

`fu_completion.py` already models these three branches fail-closed:
- no new high/low -> ATT Form 1,
- new high/low + FU criteria met + close inside previous body -> Complete FU,
- new high/low + FU criteria met + close outside previous body -> ATT Form 2,
- missing FU criteria -> NOT_CERTIFIED where required.

### Important limitation

`fu_basic_candidate.py` explicitly cannot detect ATT Form 1 because Form 1 may have no new high/low.

### Reconstruction conclusion

The FU-family detector cannot be built as only `basic_fu_candidate -> valid/invalid`. It needs separate stages:
1. raw observables,
2. liquidity / FU semantic evidence,
3. completion class.

---

## 3. Strong FU

### Source-backed evidence

`03_Analysis_Basics_.pdf` describes desirable/strong FU quality qualitatively: strong close, little or no rejection.

Reflection also uses `STRONG FU` as an HCS-capable component and in zone/retest hierarchy.

### Explicit user clarification

Strong FU / ATT FU primitive logic is fractal/timeframe-neutral. A 1m example does not create a different 1m-only primitive definition.

### Current V2 implementation

`fu_quality.py` measures objective candle quality only:
- body fraction,
- upper/lower wick fractions,
- close-side rejection,
- manipulation-side wick,
- normalized close location.

It intentionally has no universal numeric Strong-FU threshold.

### Open boundary

`B-03` remains open only for a universal numeric Strong-FU threshold.

### Reconstruction conclusion

Keep `is valid FU?` separate from `how strong/clean is this FU?`.
Do not invent a fixed body/wick percentage to resolve Strong FU.

---

## 4. Supplied Casino_v7 code — high-value mechanics evidence

Source: `Casino_v7.txt`, user-approved implementation reference.

`helper_fu_shadow.py` reproduces its core branch order without silently fixing unreachable/duplicate branches.

Important mechanics encoded by Casino_v7 include distinct contexts for:
- continuation FU / continuation ATT,
- pullback ATT-like behavior,
- reversal ATT variants,
- bullish and bearish symmetry/asymmetry,
- close relative to previous open/close/high/low,
- new extremes and return/closure relationships.

This is richer mechanical information than the narrow `basic_fu_candidate` proxy.

Known limitation/conflict from tests:
- Reflection ATT Form 1 can be missed entirely by Casino_v7 because it may have no sweep/new extreme.
- Some Reflection Complete FU geometry maps to `ATT` in Casino_v7.
- Some subset FU branches in Casino_v7 are unreachable because earlier branches capture them.

Conclusion: Casino_v7 is valuable for candidate geometry and branch decomposition, but its output labels cannot be copied directly as final Reflection truth.

---

## 5. Supplied BETA 1 + LAOL code — high-value architecture/mechanics evidence

Source: `BETA 1 + LAOL.txt`, user-approved beta implementation reference; user reports it repaints.

Core FU evidence currently shadowed in `helper_fu_shadow.py`:
- broad bullish/bearish FU candidates,
- both-side / x3 state,
- self-negation-together state,
- explicit exclusion ordering between those families.

Known behavior from tests:
- Reflection ATT Form 1 can be missed.
- Reflection Complete FU can be a BETA FU candidate.
- Reflection ATT Form 2 can collapse into broad bull/bear FU candidates.
- both-side outside-bar geometry can be routed to x3 instead of ordinary FU.

Conclusion: BETA is especially useful for broader state-machine relationships and exclusion/interaction between FU, x3, self-negation, HCS and forming states. Its broad FU candidate labels are not equivalent to final Reflection Complete/ATT labels.

---

## 6. FU liquidity and sequence

### Source-backed principle

FU is not a candle-shape pattern in isolation. Liquidity/context matters.
Primary sources repeatedly warn against trading every FU and place FU inside manipulation/liquidity reasoning.

### Current V2 implementation

`fu_liquidity_bridge.py` correctly requires an explicit marked-liquidity reference rather than guessing that every previous-candle extreme is the relevant liquidity.

It separates:
- objective liquidity interaction,
- ordered opposite move after the take,
- final semantic FU result.

`fu_intrabar_evidence.py` can inspect ordered child bars, but it deliberately does not invent a minimum reversal-distance threshold.

### Open boundary

The exact sufficient opposite-move mechanic remains B-01.
Tick/lower-timeframe path can be evidence for sequence in specific cases but is not the global strategy blocker.

---

## 7. FU retest is downstream and graded separately

Reflection R-54:
- 50% of FU wick touch = strongest retest grade,
- FU wick touch = stronger,
- >70% of full FU without wick touch = weak but can count.

`fu_retest_quality.py` correctly blocks the numeric 70% branch while the full-FU fib anchor/orientation remains unresolved (`B-02`).

This grading must not be confused with Strong-FU classification itself.

---

## 8. HCS / negation implications for later phase

Primary HCS evidence allows components from:
- Strong FU,
- Attempted FU,
- FU negation.

Therefore HCS cannot ultimately depend only on `basic_fu_candidate` nodes.

This is the main reason Phase 1 FU-family consolidation must finish before Phase 2 HCS detector changes.

The March 1975/1986 diagnostics remain useful examples, but they no longer drive the architecture by themselves.

---

## 9. Current truth map

### LOCKED / source-backed enough to implement as semantic structure

- FU requires liquidity plus opposite-direction behavior in the same candle.
- FU-family primitive logic is timeframe-neutral/fractal.
- Complete FU / ATT Form 1 / ATT Form 2 are distinct Reflection classes.
- ATT Form 1 can exist without a new high/low.
- Strongness/quality is conceptually separate from FU validity.
- HCS can use Strong FU / ATT FU / FU-negation family nodes.
- FU should not be treated as an isolated candle pattern without liquidity/context.

### HIGH-VALUE CODE EVIDENCE TO INTEGRATE

- Casino_v7 continuation / pullback / reversal branch geometry.
- Casino_v7 close relationships relative to previous OHLC.
- BETA broad FU/x3/self-negation exclusion ordering.
- BETA state-machine interactions around FU/HCS/forming states.

### STILL OPEN

- B-01 exact sufficient opposite-direction break/move mechanics.
- B-03 universal numeric Strong-FU threshold.
- Exact mapping from every Casino_v7/BETA branch to Reflection Complete/ATT classes.
- Exact raw detector for all valid liquidity forms before FU classification.

---

## 10. Immediate executable work

Do NOT rewrite the production/replay detector yet.

Next implementation step:

1. Add a versioned `fu_family_observability` layer that records the union of objective branch facts needed by:
   - primary semantics,
   - Reflection completion classes,
   - Casino_v7 continuation/pullback/reversal mechanics,
   - BETA x3/self-negation exclusions.
2. It must return observations/evidence, not `certified_fu=True`.
3. Add table-driven tests covering:
   - clear bullish/bearish Complete-FU candidates,
   - ATT Form 1,
   - ATT Form 2,
   - Casino_v7 continuation/pullback/reversal branches,
   - BETA x3 and self-negation exclusions,
   - both-side ambiguity,
   - doji/no-direction cases.
4. Then cross-run known source-labelled examples and quantify which unresolved FU cases are due to B-01 versus actual code gaps.
5. Only after that decide whether a new source-backed FU detector can replace/augment `basic_fu_candidate`.

No user manual action is required for this phase.
