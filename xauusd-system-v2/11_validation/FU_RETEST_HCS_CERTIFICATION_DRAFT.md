# FU Retest + HCS — Certification Draft

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01

This module consolidates only currently approved strategy sources. It does not infer strategy truth from implementation helpers and does not auto-promote source claims to VERIFIED.

## 1. Separation of concepts

The system must keep the following as distinct entities:

- FU retest validity
- FU retest quality/strength
- Attempted-FU retest
- Advanced FU retest
- HCS formation
- HCS establishment
- HCS strength
- HCS as True-Stop refinement
- HCS as LTF entry model

A generic `retest=true` flag is insufficient.

## 2. FU retest — validity and quality are separate

Cross-source support is now strong:

- FU retest is a retest of a previously formed FU and is price-action information, not an automatic trade trigger.
- Attempted FU may also retest, but its use requires lower-timeframe/context confirmation.
- Primary Q&A: a valid 1m FU retest may occur on the body; wick contact is not mandatory for every valid retest.
- Reflection R-54 grades quality separately:
  - >70% of full FU without wick touch = WEAK but still counts;
  - FU wick touch = STRONGER;
  - 50% of FU wick = STRONGEST.
- Casino primary notebook labels `Negation + ATT FU retest = Adv FU retest`.

Candidate model:

`retest_validity = valid | invalid | ambiguous`

`retest_quality = weak | stronger | strongest | advanced | unresolved`

Remaining blocker:
- exact fib anchor/orientation for the >70% full-FU grading remains unresolved.

## 3. FU retest is not automatically an entry

Source-supported gate:

- A retest may contribute directional/context information without being an entry.
- Entry use depends on liquidity calculation, TFS/True Stop, zone placement and LTF confirmation.
- Primary Price Action Reflection shows an advanced example where direction is already established and a 5m ATT-FU retest + strong 1m FU close is used as an optimal advanced entry.
- A later 1m HCS in the same narrative is presented as the easier re-entry because direction is more established.

Therefore:

`FU_RETEST_FOUND != ENTRY_ALLOWED`

## 4. HCS grammar — conflict substantially clarified

Direct primary evidence now clarifies that HCS is a family of two-manipulation retest structures, not only one strict geometry.

Eligible components explicitly shown/stated:
- Strong FU
- Attempted FU
- FU negation

Primary Casino/Reflection statement:
- any two eligible manipulation forms retesting each other can form HCS;
- strongest HCS = two Strong FU retesting each other;
- ATT FU + negation wick = weaker HCS form.

The older strict example:
`FU exists -> FU is retested -> retest itself forms another FU`

is therefore treated as a valid subset of the broader grammar, not necessarily a contradictory definition.

Candidate representation:

`hcs_component_A`
`hcs_component_B`
`hcs_retest_relationship`
`hcs_variant = strong_fu_pair | att_fu_negation | other_source_confirmed | unresolved`

Hard restriction:
`plain FU retest != HCS automatically`.

## 5. HCS establishment is separate from HCS formation

Reflection R-180 and newly reviewed primary visual evidence add a critical state transition:

- HCS is ESTABLISHED only when the required left-side FU/retest relationship has occurred first.
- Primary visual annotation: for HCS there is an FU from the left to react; when an FU is retested, the wick retest becomes part of the HCS range.
- Without the prerequisite context, do not label the HCS established.

Future state machine:

`HCS_FORMING`
`HCS_FORMED`
`HCS_ESTABLISHED`
`HCS_RETESTED`
`HCS_RESPECTED`
`HCS_BROKEN`

This separation is mandatory for historical reproducibility and anti-repaint design.

## 6. HCS tolerance — exact wick touch is not universally mandatory

Primary visual edge case now exists:

- TS is marked respected;
- chart annotation states HCS can still be considered even though price did not quite meet the wick but was `near enough in the moment`;
- x3 confirmations are stated to take prevalence.

Therefore:
- exact wick touch cannot be hard-coded as a universal HCS-validity requirement;
- however no numeric `near enough` threshold is yet certified.

Candidate field:
`hcs_retest_tolerance = exact_touch | near_enough_contextual | invalid | unresolved`

Open blocker:
quantitative tolerance remains unknown.

## 7. HCS strength hierarchy — candidate only

Current sources support relative hierarchy:

- ATT FU < FU < FU retest < HCS < multiple HCS.
- Strongest HCS example: two Strong FU retesting one another.
- Weaker HCS example: Attempted FU + negation wick.
- Reflection R-223 is inference-level and suggests `Adv HCS > HCS > weaker HCS` and `Adv FU retest > FU retest`.
- Older timeframe-strength material states 30m HCS = 1h FU, but universality remains unverified.

Candidate field:
`hcs_strength = weak | standard | strong | multiple | unresolved`

No numeric score is certified yet.

## 8. HCS and True Stop

Strong primary/Reflection support:

- Reflection R-65: HCS refinement is a retest of a TRUE STOP and sits above ordinary FU retest in hierarchy.
- Reflection R-108: True Stop is a contextual Main POI where all 10m+ TFS factors align; LTF HCS/negation follows after respect plus final liquidity calculation.
- Primary notebook/Reflection charts now provide both positive and negative TS-build sequences.

Positive sequence observed:
`retail liquidity manipulated`
→ `LTF LAOL taken starts 10m TS`
→ `1m HCS x3`
→ `1m x3 negation / x3-by-x3`
→ `10m HCS EST`

Negative sequence observed:
- no prior 10m TS established;
- outside timing;
- x3 self-negation alone is weaker and not enough for a strong POI.

Therefore:

`HCS_PATTERN alone != TRUE_STOP`

and

`TRUE_STOP_CONTEXT + valid HCS refinement` can become an entry candidate.

## 9. HCS as entry model

Reflection R-221 frames HCS as an entry model containing:

- liquidity manipulation;
- refinement point;
- reaction / True-Stop retest logic;
- fractal use on scalp/LTF.

Reflection R-145 and newly reviewed primary charts support:

`retail liquidity manipulation`
→ `LTF LAOL taken`
→ `1m negation OR 3m HCS + negation`

More aggressive use appears only with full TFS factors and 10m TS forming.
Standard/safer continuation is shown after 10m TS is established, with LTF HCS/core-liquidity refinement.

Thus HCS entry is contextual, not pattern-only.

## 10. Aggressive vs confirmed use

Aggressive HCS/FU entries may exist, but only when stronger context is already aligned.

Candidate gate:

- liquidity/LAOL context known;
- prevalent TFS direction known;
- relevant zone known;
- True Stop respected or equivalent contextual support;
- opposite-side/target liquidity supports the trade;
- forming HCS/FU remains provisional until its required confirmation event occurs.

This preserves:

`LIVE_PROVISIONAL` vs `CONFIRMED_IMMUTABLE`.

## 11. Current labelled visual evidence

Primary notebook / embedded Reflection examples now include:

### Valid
- minimum 1m manipulated sequence used for LTF TS build;
- LTF LAOL + x3/HCS sequence building 10m HCS EST;
- HCS left-side FU reaction/retest prerequisite.

### Invalid
- no 1m TS sequence -> wait for the correct bank-entry sequence;
- no prior 10m TS + outside timing -> x3 self-negation alone is insufficient for strong POI.

### Edge cases
- stronger prior-side TS remains in play against weaker opposing TS;
- near-wick HCS can count contextually without exact touch;
- aggressive 10m-TS-forming entry versus established 10m-TS entry flow.

All remain UNVERIFIED until independent relabelling and historical reproducibility tests are run.

## 12. Remaining certification blockers

1. exact FU-retest fib anchor/orientation for >70% grading;
2. exact HCS `near enough` tolerance;
3. exact exhaustive component combinations for all HCS variants;
4. exact HCS invalidation/break criterion;
5. exact quantitative HCS strength boundaries, if any;
6. whether 30m HCS = 1h FU generalizes;
7. more positive/negative/edge examples for plain FU retest and ATT-FU retest;
8. more examples separating HCS_FORMED from HCS_ESTABLISHED;
9. independent validation and historical timestamp reproducibility.

The old broad question `strict HCS definition versus extended grammar` is now substantially narrowed: direct primary evidence supports the extended grammar, with the strict FU/FU case treated as a subset.

Until all required gates pass, ambiguous observations produce:
`NOT_CERTIFIED / NO_TRADE`.

## 13. Implementation contract for later Python/MQL5

Future detector objects should expose at least:

- timeframe
- direction
- source_FU_id
- retest_timestamp
- retest_geometry
- retest_validity
- retest_quality
- manipulation_component_A
- manipulation_component_B
- hcs_variant
- hcs_retest_tolerance
- hcs_state
- hcs_strength
- true_stop_ref
- laol_ref
- tfs_state_ref
- confirmation_timestamp
- provisional_or_confirmed
- provenance_refs

The strategy definition must be finalized before implementation helpers are allowed to map these fields.