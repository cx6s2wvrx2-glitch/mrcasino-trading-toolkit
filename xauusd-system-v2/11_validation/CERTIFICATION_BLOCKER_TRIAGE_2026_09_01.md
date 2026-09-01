# XAUUSD V2 — Certification Blocker Triage

Date: 2026-09-01

Purpose: distinguish true implementation blockers from source-evolution, governance, and already-consolidated issues. No item is marked user-resolved here. `resolved_by_user` remains authoritative in Supabase.

## A. TRUE RAW-DETECTOR / PRODUCTION BLOCKERS

### A1 — FU validity break criterion

**State:** BLOCKER

Approved material requires liquidity taken + break/BOS in the FU event, but the corpus does not yet certify whether FU validity requires:

- wick breach of the previous high/low,
- body close beyond the previous high/low,
- or a context-dependent distinction.

**Policy:** raw detector must preserve `wick_only`, `body_close`, and `ambiguous` as distinct states. Do not borrow body-close logic from broken-zone activation.

### A2 — Imbalance geometry

**State:** BLOCKER

Competing candidate geometry remains:

- previous candle close → next candle open,
- previous wick → next wick.

Primary later material strongly supports the strategic use of IMB but has not yet certified the exact universal geometry boundary.

**Policy:** no canonical raw imbalance detector until labelled primary visual geometry examples resolve the boundary.

### A3 — Strong FU quantitative threshold

**State:** BLOCKER

`SFU = Strong FU` is user-confirmed. Sources associate strength with strong close / low rejection, but no exact numeric body/wick threshold is certified.

**Policy:** no invented percentage threshold from Pine/EX5 helpers.

### A4 — FU retest fib anchor/orientation

**State:** BLOCKER FOR NUMERIC GRADING, NOT FOR BASIC VALIDITY

Cross-source consolidation is strong:

- >70% of full FU without wick touch = weak but counts,
- wick touch = stronger,
- 50% of FU wick = strongest.

The unresolved part is the exact mechanical fib anchor/orientation and boundary cases.

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

## Practical priority order

1. FU validity break criterion
2. Imbalance geometry
3. Strong FU threshold
4. FU-retest fib anchor/orientation
5. labelled zone-type boundary examples
6. production risk policy only after strategy/research evidence is mature

## Current promotion rule

None of these classifications authorizes `VERIFIED` promotion. Primary visual certification + blind validation + historical reproducibility remain required.
