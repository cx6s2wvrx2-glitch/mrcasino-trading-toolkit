# XAUUSD V2 — Primary Evidence Audit for B-01 to B-04

Date: 2026-09-02
Scope: XAUUSD V2 only
Status: PRIMARY-EVIDENCE RECONCILIATION / NO VERIFIED PROMOTION / NO DATABASE RESOLUTION

## Purpose

This audit follows the open-boundary reconciliation instruction to re-check already recovered primary evidence for B-01 through B-04 before requesting new source material. It narrows each blocker to the smallest remaining unknown without inventing thresholds, geometry, broker tolerances or strategy rules.

Nothing in this document:
- changes `resolved_by_user`;
- changes source approval/status;
- promotes knowledge or rules to VERIFIED;
- authorizes live execution;
- treats implementation helpers as strategy authority.

A user clarification recorded on 2026-09-02 is now part of the scope reconciliation: Strong FU and ATT FU use the same primitive logic across all timeframes. Timeframe changes authority/context/downstream application, not the primitive definition. See `01_sources/USER_CLARIFICATION_FU_TIMEFRAME_SCOPE_2026_09_02.md`.

## B-01 — FU sufficient opposite-direction move / break mechanics

Primary evidence reviewed:
- `03_Analysis_Basics_.pdf`, source page labelled PAGE 03 / physical PDF page 4;
- `04_FU_Retests_.pdf`, source page labelled PAGE 01 / physical PDF page 2.

What the primary text establishes:
- the FU event takes liquidity and then moves in the opposite direction inside the same candle/event;
- strong close with little/no rejection is preferred as higher-quality evidence;
- the source explicitly warns against an over-rigid FU definition.

What the primary text does **not** establish mechanically:
- a universal wick-breach requirement for the sufficient opposite move;
- a universal body-close-through requirement;
- one fixed BOS level that every FU must break;
- a universal pip/displacement threshold.

Reconciled boundary:
- B-01 remains open only at the raw mechanical sufficiency layer.
- V2 may continue to record liquidity take, opposite-side movement, close location, previous-level breaches and intrabar ordering as observables.
- No one of those observables may be silently promoted into the universal FU break rule.

Next evidence capable of resolving B-01:
- primary labelled positive/negative FU fixtures with exact broker OHLC or an explicit source statement defining the sufficient break mechanically.

## B-02 — R-54 70% full-FU Fibonacci anchor/orientation

Primary evidence reviewed:
- `GIANNO_CASINO_REFLECTION_MASTER.pdf`, early Reflection text and R-54/R-75 reconciliation;
- `04_FU_Retests_.pdf` for the older baseline retest concept.

What is established:
- the R-54 quality ordering itself is source-backed:
  1. past 70% of the full FU without wick touch = weak but still counts;
  2. FU wick touch = stronger;
  3. 50% of the FU wick = strongest.
- older FU-retest material supports the retest concept but does not supply the 70% full-candle fib construction.

What remains explicitly unresolved in the Reflection material:
- where fib 0 is anchored;
- where fib 100 is anchored;
- therefore the exact directional/orientation formula for the 70% boundary.

Reconciled boundary:
- B-02 is **not** an uncertainty about whether the 70% grading exists.
- B-02 is only the reproducible 0/100 anchor/orientation needed to calculate that numeric branch.
- Wick-touch and half-wick branches may remain separately observable; the 70% branch must stay blocked until its anchor is proven.

## B-03 — Universal Strong-FU quantitative threshold

Primary evidence reviewed:
- `03_Analysis_Basics_.pdf` FU section;
- `GIANNO_CASINO_REFLECTION_MASTER.pdf` Strong-FU examples, including the 1-minute zone application;
- explicit user clarification dated 2026-09-02 on FU-family timeframe scope.

What is established:
- Strong-FU quality is associated with a strong close and little/no rejection;
- Strong FU is a strength/quality class within the FU family, not a separate 1m concept;
- **the same Strong-FU / ATT-FU primitive logic applies on every timeframe**;
- timeframe changes authority, top-down weighting, move scale and downstream use, not the primitive definition;
- Reflection contains a specific 1-minute zone application in which the full Strong-FU candle is marked and the cited 1-minute example breaks both the previous high and low.

Critical scope distinction:
- the 1-minute `breaks previous high + low` statement is source-backed **1-minute zone geometry/application**;
- it is **not** the definition of Strong FU itself;
- equally, no 1m example may be used to imply that Strong FU or ATT FU have different primitive logic on higher timeframes.

Reconciled boundary:
- the timeframe-scope question is closed by explicit user clarification: FU-family primitive logic is fractal/timeframe-invariant;
- B-03 remains open **only** on the question of a universal quantitative Strong-FU classifier: body%, wick%, rejection%, pip/range threshold, or explicit confirmation that no numeric threshold is intended;
- V2 should retain threshold-free quality observables until that quantitative boundary is certified.

## B-04 — Broker-specific Imbalanced-Candle calibration

Primary evidence reviewed:
- `09_Imbalances.pdf`, including the labelled XAUUSD H1 `Imbalance` and M5 `Classic imbalance` examples;
- older `02_The_10_Free_Lessons.pdf` imbalance material as historical baseline only.

What the later primary Imbalances source establishes:
- the trade-relevant main type is an `imbalanced candle`;
- imbalance belongs under liquidity and must be interpreted with timeframe strength;
- the source explicitly uses broker data rather than TradingView for imbalance observation;
- H1 and M5 labelled visual examples are distinct evidence cases.

What the older baseline establishes:
- the free-lesson `classic imbalance` describes an untested area between the previous close and next open.

What remains unresolved:
- the later broker-specific `imbalanced candle` cannot safely be collapsed into the older classic-gap/FVG construct;
- the primary labelled screenshots do not provide a reproducible numeric broker tolerance by themselves;
- exact equality/near-equality and wick/body geometry therefore remain observables, not a certified classifier.

Reconciled boundary:
- B-04 requires broker-quality OHLC fixtures aligned to labelled primary examples, not a TradingView approximation.
- The new immutable MT5 snapshot/reload/alignment path is the correct technical prerequisite for this calibration.

## Net result

No blocker is promoted or database-resolved by this audit.

The remaining unknowns are now narrower:
- **B-01:** exact sufficient raw FU break/move mechanic;
- **B-02:** exact fib 0/100 orientation only;
- **B-03:** exact universal numeric Strong-FU threshold, if one exists; timeframe scope itself is no longer open;
- **B-04:** exact broker-OHLC classifier/tolerance for the later Imbalanced-Candle construct.

This means future work should not re-open already settled concepts such as:
- FU = liquidity take plus opposite-direction move in the same event;
- R-54 retest quality ordering itself;
- Strong-FU qualitative association with strong close / low rejection;
- Strong FU / ATT FU primitive logic being consistent across timeframes;
- broker-only provenance requirement for imbalances.

## Next actions

1. Keep Agent-06 independent validation separate from blocker resolution.
2. Obtain/ingest broker MT5 history before attempting B-04 calibration.
3. Use primary labelled fixtures plus immutable broker snapshots for any raw-detector certification.
4. Keep B-01/B-02/B-03 fail-closed on their remaining mechanical/numeric unknowns; do not re-open the now-clarified FU-family timeframe scope.
5. Do not mutate the unresolved database rows from this audit alone.