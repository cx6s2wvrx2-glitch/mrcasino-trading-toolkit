# FU Retest + HCS — Certification Draft

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01

This module consolidates only currently approved strategy sources. It does not infer strategy truth from implementation helpers and does not auto-resolve source conflicts.

## 1. Separation of concepts

The system must keep the following as distinct entities:

- FU retest validity
- FU retest quality/strength
- Attempted-FU retest
- HCS formation
- HCS establishment
- HCS strength
- HCS as True-Stop refinement
- HCS as LTF entry model

A generic `retest=true` flag is insufficient.

## 2. FU retest — current supported definition

Cross-source support:

- FU retest is a retest of a previously formed FU and is price-action information, not an automatic trade trigger.
- Attempted FU may also retest, but its use requires lower-timeframe/context confirmation.
- Primary Q&A shows a valid 1m FU retest may occur on the body; wick contact is not mandatory for every valid retest.
- Reflection R-54 grades retest quality separately from validity:
  - >70% of full FU without wick touch = weak but still counts;
  - FU wick touch = stronger;
  - 50% of FU wick = strongest.

### Candidate model

`retest_validity = valid | invalid | ambiguous`

`retest_quality = weak | stronger | strongest | unresolved`

These must not be collapsed into one field.

## 3. FU retest is not automatically an entry

Source-supported gate:

- A retest may contribute directional/context information without being an entry.
- Entry use depends on liquidity calculation, TFS/True Stop, zone placement and LTF confirmation.
- Primary Price Action Reflection shows an advanced example where direction is already established and a 5m ATT-FU retest + strong 1m FU close is used as an optimal advanced entry.
- A later 1m HCS in the same narrative is presented as the easier re-entry because direction is more established.

Therefore:

`FU_RETEST_FOUND != ENTRY_ALLOWED`

## 4. HCS — strict base definition candidate

Direct HCS source gives the strict base definition:

1. a FU exists;
2. that FU is retested;
3. the retest itself forms another FU.

Candidate output:

`HCS_FORMED`

This is stronger evidence than the older derived annotation that broadly equated `FU -> retest` with HCS.

## 5. HCS — component extension

The same HCS source broadens eligible manipulation components and states that an HCS can be constructed from two eligible manipulation forms retesting one another, including:

- Strong FU
- Attempted FU
- FU negation

This creates a real specification problem: the system must distinguish the strict base definition from the broader component family until chart certification determines the exact canonical grammar.

Candidate representation:

`hcs_grammar = strict_fu_fu | extended_two_manipulations | unresolved`

No code should silently treat every retest as HCS.

## 6. HCS establishment is separate from HCS formation

Reflection R-180 occurrence 2 adds a critical state transition:

- HCS is ESTABLISHED only if the left FU was retested first.
- Without that prior retest, the HCS is not established; the next valid point becomes the established TFS POI.

Therefore future state machine must distinguish:

`HCS_FORMING`
`HCS_FORMED`
`HCS_ESTABLISHED`
`HCS_RETESTED`
`HCS_RESPECTED`
`HCS_BROKEN`

This separation is mandatory for historical reproducibility and for eliminating repaint-style ambiguity.

## 7. HCS strength hierarchy — candidate only

Current sources support relative hierarchy but not every quantitative boundary:

- ATT FU < FU < FU retest < HCS < multiple HCS.
- Strongest HCS example: two Strong FU retesting one another.
- Weaker HCS example: Attempted FU + negation wick.
- Reflection R-223 is explicitly inference-level and suggests Adv HCS > HCS > weaker HCS; it must not be promoted as source-confirmed without visual certification.
- Older timeframe-strength material states 30m HCS = 1h FU, but universality of the exact 2x mapping remains unverified.

The future engine therefore needs:

`hcs_strength = weak | standard | strong | multiple | unresolved`

No numeric score is certified yet.

## 8. HCS and True Stop

Strong primary/Reflection support:

- Reflection R-65: HCS refinement is a retest of a TRUE STOP and sits above ordinary FU retest in hierarchy.
- Reflection R-108: True Stop is a contextual Main POI where all 10m+ TFS factors align; LTF HCS/negation follows after respect plus final liquidity calculation.
- Primary Q&A states that true-stop quality depends on formation strength, timeframe, session timing, zones, major-liquidity reasoning and TFS placement.

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

Reflection R-145 adds LTF execution sequence:

retail liquidity manipulation -> LTF LAOL taken -> 1m negation or 3m HCS+negation trigger.

Primary Price Action Reflection also shows:

- established 1m HCS can act as entry when broader direction and major targets are already aligned;
- waiting can produce additional 5m + 1m HCS confirmation;
- 15m HCS after liquidity is taken can support an aggressive setup when zone retest and timeframe strength agree;
- repeated HCS reactions can create re-entry opportunities while broader liquidity context remains valid.

Thus HCS entry is contextual, not pattern-only.

## 10. Aggressive vs confirmed use

Aggressive HCS/FU entries may exist, but only when stronger context is already aligned.

Candidate gate:

- liquidity/LAOL context known;
- prevalent TFS direction known;
- relevant zone known;
- True Stop respected or equivalent contextual support;
- opposite-side/target liquidity supports the trade;
- forming HCS/FU may be used only as provisional context until its required confirmation event occurs.

This preserves the future distinction:

`LIVE_PROVISIONAL` vs `CONFIRMED_IMMUTABLE`.

## 11. Certification blockers

The module is NOT VERIFIED until the following are resolved with labelled primary examples:

1. exact grammar separating plain FU retest from HCS;
2. exact extended-HCS component combinations and their minimum requirements;
3. exact mechanics of "left FU retested first" for HCS establishment;
4. retest validity geometry versus retest quality geometry;
5. exact HCS invalidation/break criterion;
6. exact quantitative strength boundaries, if any;
7. whether the 30m HCS = 1h FU equivalence generalizes;
8. positive, negative and edge examples for plain FU retest;
9. positive, negative and edge examples for Attempted-FU retest;
10. positive, negative and edge examples for HCS formation and HCS establishment;
11. examples distinguishing aggressive HCS use from confirmed HCS entry.

Until those gates pass, ambiguous observations produce `NOT_CERTIFIED / NO_TRADE` in any deterministic implementation.

## 12. Implementation contract for later Python/MQL5

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
- hcs_grammar
- hcs_state
- hcs_strength
- true_stop_ref
- laol_ref
- tfs_state_ref
- confirmation_timestamp
- provisional_or_confirmed
- provenance_refs

The strategy definition must be finalized before any implementation helper is allowed to map these fields.