# XAUUSD V2 — Certification Blocker Triage

Date: 2026-09-01

Purpose: distinguish true implementation blockers from source-evolution, governance, and already-consolidated issues. No item is marked user-resolved here. `resolved_by_user` remains authoritative in Supabase.

## A. TRUE RAW-DETECTOR / PRODUCTION BLOCKERS

### A1 — Upstream `FU criteria met` predicate

**State:** NARROWED SOURCE-EVOLUTION BLOCKER

Primary Reflection R-120..R-122 now resolves the FU **completion classification**:

- no new high/low → `ATTEMPTED_FU_FORM_1`;
- FU criteria met + close within the previous candle open/close body → `COMPLETE_FU`;
- new high/low / FU-like setup without the required closure within the previous body → `ATTEMPTED_FU_FORM_2`.

Therefore wick-vs-close is no longer a free implementation choice for FU completion.

The remaining upstream wording evolves across approved sources:

- early Free Lessons: liquidity taken + break of structure in the same candle;
- Analysis Basics: liquidity taken + move in the opposite direction in the same candle, with explicit flexibility in definition;
- Reflection R-120..R-122: Complete/Attempted classification based on new-high/low behavior plus previous-body closure.

The R-120 primary visual does **not** justify converting the older BOS wording into a mandatory close beyond the opposite previous high/low.

**Implemented evidence layers:**

- `src/xauusd_v2/fu_observables.py` extracts previous-high/low sweep, candle direction, previous-body closure, outside-bar state and directional reversal-candidate facts without returning `valid_fu`.
- `src/xauusd_v2/fu_completion.py` applies only the source-confirmed Complete/Attempted completion layer and fails closed when upstream FU criteria are not certified.

**Remaining blocker:** certify the exact predicate represented by `FU criteria met` and reconcile/scope the earlier BOS wording. Do not infer it from Casino_v7/BETA helper logic.

### A2 — Imbalance constructs / raw geometry

**State:** SPLIT BLOCKER — DO NOT COLLAPSE CONSTRUCTS

Primary material now indicates at least two different constructs:

#### A2a — `Imbalanced candle` (main liquidity construct)

Later primary Casino material calls the main traded form an **imbalanced candle** and treats it as liquidity. The primary 1h and 5m examples visually show single-candle, immediate one-sided movement. Later Last Areas Liquidity material describes imbalanced candles as moves that start immediately in one direction while the high/low is not manipulated.

The implementation helper `Casino_v7` uses `open == low` / `open == high`, and the primary examples visually resemble that geometry, but helper code is not strategy authority and primary text has not yet stated the exact equality/tolerance mechanically.

**Policy:** do not promote `open==low/open==high` to canonical raw detector until primary visual certification establishes exact equality/tolerance and broker-feed behavior.

#### A2b — Classic / untested imbalance zone

Earlier instructional sources describe an untested multi-candle price area, but boundary descriptions differ:

- previous close → next open;
- previous wick → next wick.

This is not automatically the same construct as the later `imbalanced candle` liquidity primitive.

**Policy:** store `IMBALANCED_CANDLE` and `CLASSIC_UNTESTED_IMBALANCE_ZONE` as different candidate concepts. No universal IMB geometry switch.

### A3 — Strong FU determinization / calibration

**State:** CALIBRATION BLOCKER — NOT A MISSING SECRET PERCENTAGE

Approved Analysis Basics describes the desired Strong FU qualitatively as a **strong close with little or no rejection** and explicitly says **not to be too strict in its definition**. The source therefore does not provide a canonical numeric body/wick percentage that V2 may simply copy.

**Implemented measurement layer:** `src/xauusd_v2/fu_quality.py` now calculates objective, reproducible candle-shape metrics only:

- body fraction of full candle range,
- upper/lower wick fractions,
- close-side rejection fraction,
- manipulation-side wick fraction,
- normalized close location within the candle range.

It deliberately does **not** classify a candle as Strong FU and contains **no default threshold**.

**Remaining blocker:** calibrate and certify any machine boundary against labelled primary Strong-FU / ATT-FU examples, then blind-validate it. Implementation-helper thresholds cannot become strategy truth.

### A4 — FU retest fib anchor/orientation

**State:** BLOCKER FOR NUMERIC GRADING, NOT FOR BASIC VALIDITY

Cross-source consolidation is strong:

- >70% of full FU without wick touch = weak but counts,
- wick touch = stronger,
- 50% of FU wick = strongest.

The Master itself marks the exact 0/100 fib orientation as unresolved. A targeted search of the current Reflection Master and primary notebook did not surface a later labelled visual that explicitly fixes the anchor.

**Policy:** basic retest validity/relative grading may remain source-confirmed, but no numeric 70% raw detector is allowed until the anchor/orientation is visually certified.

### A5 — Production risk policy

**State:** PRODUCTION POLICY BLOCKER

Source material contains 3% vs 5% recommendations. V2 Risk Engine intentionally embeds neither.

**Policy:** production limits require explicit approved policy + stress testing. This does not block strategy-definition research.

## B. CONTEXT / SOURCE-EVOLUTION ITEMS — DO NOT COLLAPSE INTO ONE UNIVERSAL RULE

### B1 — Liquidity-type lists

**State:** CONTEXT-SCOPED, FORMAL CERTIFICATION PENDING

Later primary material indicates different scopes:

- broad/main liquidity types in Mr Casino Q&A: trendline, DB/DT, unmanipulated doji, IMB;
- Reflection R-207, 30m+ CORE marking: unfilled big-wick-to-fill + unmanipulated doji, breakout optional/advanced.

**Policy:** store scope/timeframe/context explicitly. Do not force one timeless list.

### B2 — Orderblock / zone boundaries

**State:** SUBSTANTIALLY NARROWED, ZONE-TYPE CERTIFICATION PENDING

Primary Reflection differentiates constructs:

- R-157 True Orderblock candidate: body-in-wick geometry;
- R-162 1m Strong-FU zone: entire Strong FU candle;
- R-167 full range: FU wick + body-in-wick OB, FU wick as main refinement.

**Policy:** no universal `include_wicks=true/false` switch. Boundary is zone-type-specific.

## C. OPERATIONALLY HANDLED GOVERNANCE ITEMS

### C1 — BASICSTOINSTITUTIONALTRADING.pptx authority

**State:** GOVERNANCE HANDLED

Classified as secondary instructional evidence, not direct Mr Casino authority. It cannot override primary strategy material.

### C2 — Reflection R-number collisions

**State:** GOVERNANCE HANDLED

Source labels are not unique IDs. V2 uses source label + page/section/occurrence + internal unique ID.

No automatic merge by `R-xxx` alone is allowed.

## D. CONCEPTS SUBSTANTIALLY CONSOLIDATED — FORMAL PROMOTION STILL CLOSED

### D1 — HCS definition breadth

**State:** CONCEPT CONSOLIDATED / NOT VERIFIED

The strict FU→FU retest case is a subset of the broader primary HCS grammar: eligible manipulation forms can retest each other; strongest and weaker forms remain distinguishable.

### D2 — FU retest validity vs quality

**State:** CONCEPT CONSOLIDATED / NUMERIC EDGE REMAINS

Body/close-enough retest can count; wick depth grades quality. Exact fib implementation remains A4.

### D3 — FU completion class

**State:** SOURCE-CONFIRMED CLASSIFICATION / UPSTREAM PREDICATE NOT VERIFIED

R-120..R-122 distinguish Complete FU from two Attempted-FU forms. This classification can be implemented deterministically **after** an upstream detector supplies whether FU criteria are met and whether a new high/low occurred.

This does not certify the upstream FU primitive and does not authorize VERIFIED promotion.

## Practical priority order

1. upstream `FU criteria met` source-evolution resolution
2. `IMBALANCED_CANDLE` exact raw geometry/tolerance on broker data
3. label/calibrate Strong-FU quality using objective metrics
4. FU-retest fib anchor/orientation
5. classic untested-imbalance zone boundary, if still needed as a separate strategy construct
6. labelled zone-type boundary examples
7. production risk policy only after strategy/research evidence is mature

## Current promotion rule

None of these classifications authorizes `VERIFIED` promotion. Primary visual certification + blind validation + historical reproducibility remain required.
