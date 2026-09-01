# FU Family — Certification Draft

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01

This module consolidates approved FU-family evidence. It does not allow implementation helpers to define strategy truth.

## 1. Core FU meaning

Cross-source support is strong that an FU is a manipulation candle/event, not a standalone entry signal.

Current source-supported core:
- it takes/manipulates liquidity;
- it then moves in the opposite direction inside the same candle/event;
- stronger FU quality is associated with a stronger close and less rejection;
- FU must always be interpreted inside liquidity, TFS and broader price-action context.

## 2. Candidate mechanical validity model

A candidate FU should not be accepted merely because it has a large wick.

Minimum evidence currently supports:
1. a liquidity event occurs;
2. the same FU structure produces the opposite-side movement/break described in the source;
3. the event is interpreted on its own timeframe;
4. context must not contradict the higher/prevalent TFS.

### Open item — exact break criterion

Earlier material says valid FU requires liquidity taken + BOS in the same candle. A later book narrows this toward breaking the previous candle high/low. The corpus still does not mechanically certify whether the required break is:
- wick breach,
- body close beyond the level,
- or context-dependent.

Until primary visual certification resolves this, code must expose:
`fu_break_status = wick_only | body_close | ambiguous`
and must not silently treat all three as equivalent.

## 3. Attempted FU (AFU)

User-confirmed abbreviation:
`AFU = Attempted FU`.

Source-supported behavior:
- Attempted FU is weaker than a completed FU;
- it can itself be retested;
- later/stronger manipulation may build from it;
- Reflection includes ATT FU among certain liquidity structures on 30m+;
- HCS can include ATT FU in weaker forms.

AFU must therefore remain a distinct state, not be auto-promoted to FU.

## 4. Strong FU (SFU)

User-confirmed abbreviation:
`SFU = Strong FU`.

Current source-supported interpretation:
- a Strong FU is a quality/strength class of FU, not a different independent concept;
- strong close / low rejection is repeatedly associated with higher FU strength;
- FU strength contributes to timeframe authority, continuation confidence and hold logic;
- strong FU still does not override liquidity calculation.

The exact quantitative candle-shape threshold for SFU is NOT yet certified.

## 5. FU Retest — validity versus quality

FU retest must be separated into two questions:
1. Does a retest count as a retest?
2. How strong/high-quality is that retest?

Current primary evidence:
- Q&A: a 1m FU retest can occur on the body; wick does not always have to be met.
- Reflection R-54 grading:
  - >70% fib of full FU without wick touch = weak but counts;
  - FU wick touch = stronger;
  - 50% of FU wick = strongest.
- Primary Reflection visual evidence also shows HCS can sometimes be considered when the wick is not quite met but price is near enough in context, with x3 confirmation taking prevalence.
- Casino notebook labels `Negation + ATT FU retest = Adv FU retest` as an advanced variant.

Therefore candidate state model:
`retest_valid = true | false`
`retest_quality = weak | stronger | strongest | advanced | unresolved`

Do not encode 50% wick as a mandatory condition for every valid retest.

Remaining blocker:
- exact fib anchor/orientation for the >70% full-FU grading is not yet visually certified.

## 6. FU Negation

Base source definition:
- FU in one direction;
- immediately following candle forms FU in the opposite direction.

Current hierarchy/context:
- higher-timeframe FU should not be negated by random lower-timeframe FU;
- primary Price Action Reflection says a 4h FU/closed strength needs comparable opposite-side higher-timeframe strength before the larger opposite move is considered;
- 1m negation may act as LTF execution trigger;
- HTF negation can contribute to directional authority.

Negation therefore needs at least:
`source_tf`, `opposing_tf`, `formation_strength`, `context_alignment`.

## 7. x3 — final primitive definition now source-confirmed

Reflection R-213 gives the final primitive definition:

`x3 = one candle containing BOTH FU and negation characteristics embedded at macro level inside the same candle.`

This closes the earlier speculative geometry question around whether x3 meant merely three bodies, triple range, or three separate moves.

Primary Q&A adds the operational manipulation sequence view:
1. FU wick/manipulation in one direction;
2. negation attempt from the opposite side;
3. the negation attempt is broken.

These are treated as compatible descriptions of the same x3 manipulation logic at different explanatory levels, pending labelled detector tests.

Primary Q&A also mentions related variants/structures:
- x3 FU candle;
- x3 HCS retest;
- three candles, each contributing one manipulation.

Casino primary notebook adds examples/labels for x3 negation, x3-by-x3, HCS x3 and TS build sequences.

Important:
- the core x3 primitive itself is now much better defined;
- `x3 by x3` remains a separate unresolved advanced concept;
- multi-candle variants must not be silently collapsed into the single-candle R-213 detector.

Mr Casino describes x3 as very strong manipulation, but liquidity calculation still outranks x3 by itself.

## 8. Strength hierarchy — current candidate

Older Last Areas material gives:
`ATT FU < FU < FU retest < HCS < multiple HCS`.

Reflection later adds nuance and an inferred refresh hierarchy:
`Adv HCS > HCS > weaker HCS (ATT FU)` and `Adv FU retest > FU retest`.

Direct primary HCS evidence clarifies:
- strongest HCS = two Strong FU retesting each other;
- ATT FU + negation wick = weaker HCS form.

Use this only as a provisional ranking framework. Do not convert to arbitrary numeric weights yet.

## 9. Timeframe authority

Current source-supported principles:
- timeframe matters materially;
- HTF FU cannot be casually overridden by LTF FU;
- stronger opposite-side HTF evidence is required for true negation/reversal;
- FU at higher timeframe can support a larger directional move;
- LTF FU is primarily useful for refinement/execution when HTF context already agrees;
- Reflection R-216: `The LTF builds the HTF but HTF commands the LTF`.

Candidate rule:
`LTF FU cannot independently overturn active HTF TFS/FU authority.`

Exact timeframe-equivalence relationships remain source-specific and require chart certification before production use.

## 10. Entry use

FU is not an automatic entry.

Current approved evidence supports:
- after-close FU entries exist as an older/basic method;
- as-forming FU entries are aggressive and only valid in stronger surrounding context;
- primary Q&A: sole 1m FU forming may be considered only with prior FU retest/zone reaction and extreme opposite-side liquidity;
- Price Action Reflection: after buys were established, 5m ATT FU retest + strong 1m FU close is presented as an advanced entry; later 1m HCS is the easier re-entry.

Therefore candidate gate:
`FU entry requires pre-existing context; FU itself is never sufficient.`

## 11. FU → HCS relationship — conflict narrowed substantially

Older HCS material gives both a strict example and a broader grammar.
Direct primary evidence now clarifies the broader grammar:
- HCS can use Strong FU, ATT FU or FU negation;
- any two eligible manipulation forms retesting each other can form HCS;
- strongest = two Strong FU retesting each other;
- weaker example = ATT FU + negation wick.

Therefore the strict `FU retest where retest also forms FU` structure is treated as a subset, not necessarily a contradictory definition.

Reflection R-65 places HCS refinement above ordinary FU retest and ties it to TRUE STOP.
Reflection/primary visual evidence says HCS has an FU from the left to react/retest before the POI establishes; wick retest becomes part of the HCS range.

Do not simplify HCS to `any FU retest`.

## 12. Candidate state machine

Provisional FU-family state model for later implementation:

`NONE`
→ `ATTEMPTED_FU`
→ `FU_CONFIRMED`
→ optional `FU_RETESTED`
→ optional `FU_NEGATED`
→ optional `X3_CONFIRMED`

Each state must carry:
- timeframe;
- direction;
- liquidity reference;
- close confirmation status;
- retest validity;
- retest quality;
- HTF/TFS context;
- source-evidence provenance.

No transition should be inferred from future bars in historical data.

## 13. Open certification questions after current primary review

Before VERIFIED status:
1. exact FU break criterion: wick vs close;
2. exact mechanical SFU threshold;
3. exact AFU geometry and completion transition;
4. labelled positive/negative examples for FU;
5. labelled positive/negative examples for AFU;
6. labelled positive/negative examples for SFU;
7. labelled FU-negation examples across TF hierarchy;
8. exact detector boundaries for multi-candle x3 variants and `x3 by x3`;
9. precise rules for timeframe-equivalence claims;
10. exact fib anchor/orientation for FU-retest >70% grading;
11. quantitative HCS `near enough` tolerance.

No longer treated as an open primitive-definition question:
- core x3 meaning, because R-213 provides the final source definition.

Ambiguous cases remain `NOT CERTIFIED / NO TRADE`.
