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

## 5. FU Retest

FU retest must be separated into two questions:
1. Does a retest count as a retest?
2. How strong/high-quality is that retest?

Current primary evidence:
- Q&A: a 1m FU retest can occur on the body; wick does not always have to be met.
- Reflection R-54 grading:
  - >70% fib of full FU without wick touch = weak but counts;
  - FU wick touch = stronger;
  - 50% of FU wick = strongest.

Therefore candidate state model:
`retest_valid = true/false`
`retest_quality = weak | stronger | strongest | unresolved`

Do not encode 50% wick as a mandatory condition for every valid retest.

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

## 7. x3 FU / x3 manipulation

Primary Q&A gives the strongest direct definition currently available:
1. FU wick/manipulation in one direction;
2. negation attempt from the opposite side;
3. the negation attempt is broken.

Mr Casino describes x3 FU as the strongest manipulation type, but also states liquidity calculation is more important than the x3 concept by itself.

Variants mentioned in the primary Q&A:
- x3 FU candle;
- x3 HCS retest;
- three candles, each contributing one manipulation.

These variants must NOT be collapsed into one detector until labelled visual examples certify their exact geometry.

## 8. Strength hierarchy — current candidate

Older Last Areas material gives:
`ATT FU < FU < FU retest < HCS < multiple HCS`.

Reflection later adds nuance and an inferred refresh hierarchy where advanced HCS / advanced FU retest outrank ordinary variants.

Use this only as a provisional ranking framework. Do not convert to arbitrary numeric weights yet.

## 9. Timeframe authority

Current source-supported principles:
- timeframe matters materially;
- HTF FU cannot be casually overridden by LTF FU;
- stronger opposite-side HTF evidence is required for true negation/reversal;
- FU at higher timeframe can support a larger directional move;
- LTF FU is primarily useful for refinement/execution when HTF context already agrees.

Candidate rule:
`LTF FU cannot independently overturn active HTF TFS/FU authority.`

Exact timeframe-equivalence relationships (for example 30m FU vs 15m FU retest) remain source-specific and require chart certification before production use.

## 10. Entry use

FU is not an automatic entry.

Current approved evidence supports:
- after-close FU entries exist as an older/basic method;
- as-forming FU entries are aggressive and only valid in stronger surrounding context;
- primary Q&A: sole 1m FU forming may be considered only with prior FU retest/zone reaction and extreme opposite-side liquidity;
- Price Action Reflection: after buys were established, 5m ATT FU retest + strong 1m FU close is presented as an advanced entry; later 1m HCS is the easier re-entry.

Therefore candidate gate:
`FU entry requires pre-existing context; FU itself is never sufficient.`

## 11. FU → HCS relationship

Older HCS material defines HCS from FU/retest interaction and later broadens eligible components.
Reflection R-65 places HCS refinement above ordinary FU retest and ties it to TRUE STOP.
Reflection R-180 requires a left FU retest before HCS can be ESTABLISHED.

Do not simplify HCS to 'any FU retest'. The current corpus explicitly distinguishes them.

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
- retest quality;
- HTF/TFS context;
- source-evidence provenance.

No transition should be inferred from future bars in historical data.

## 13. Open certification questions

Before VERIFIED status:
1. exact FU break criterion: wick vs close;
2. exact mechanical SFU threshold;
3. exact AFU geometry and completion transition;
4. labelled positive/negative examples for FU;
5. labelled positive/negative examples for AFU;
6. labelled positive/negative examples for SFU;
7. labelled FU-negation examples across TF hierarchy;
8. labelled x3 FU examples for each stated variant;
9. precise rules for timeframe-equivalence claims;
10. clear separation of valid FU retest from entry-quality FU retest.

Ambiguous cases remain `NOT CERTIFIED / NO TRADE`.
