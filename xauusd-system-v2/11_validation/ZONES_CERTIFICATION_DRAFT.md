# Zones — Certification Draft

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01

This module uses the currently approved corpus, with priority given to the later Reflection zone engine over older generic orderblock descriptions when the later source explicitly provides operational mechanics.

## 1. Core role

Zones are contextual/order-power structures, not standalone trade signals. Earlier source material already states that zones confirm rather than outrank liquidity/manipulation. Later Reflection makes the zone process more mechanical and places zones at the front of the official sequence before TFS/LAOL/True Stop refinement.

Operational interpretation:

`ZONE -> context/order power -> refinement -> reaction evidence`

not

`ZONE -> automatic entry`.

## 2. Zone families currently supported

The Reflection zone engine supports distinct zone families, including:

- broken FU wick zone;
- broken HCS zone;
- weakest ATT FU / failed-FU zone on higher TF only;
- untested FU wick zone;
- HCS-derived zones/refinements;
- body-in-wick True Orderblock refinement;
- 1min final zone built from the whole Strong FU candle.

These must remain separate types in implementation.

## 3. Activation

Strong source-confirmed rule:

- a zone is NOT active merely because the source pattern exists;
- activation occurs only after the required break;
- Reflection explicitly states BODY CLOSURE for broken-zone activation;
- wick penetration alone does not satisfy the source-confirmed broken-zone activation rule.

Candidate state transition:

`FORMED -> NOT_ACTIVE -> BODY_CLOSE_BREAK -> ACTIVE`

## 4. Reaction quota / lifecycle

Source-confirmed lifecycle mechanics:

- Broken FU wick zone: one main confirmed same-TF reaction; a second may occur but is not equally confirmed.
- Broken HCS zone: two main confirmed same-TF reactions; possible third is weaker/non-core.
- Weakest ATT FU / failed-FU zone: one reaction then expires.
- Untested FU wick zone: one reaction.
- Completed reaction quota -> EXPIRED/DEACTIVE.
- A broader zone may be faded/deleted once its refined zone has been met.
- Deactive zones can remain visible as historical/context reference.

Candidate states:

`NOT_ACTIVE | ACTIVE | REACTION_1 | REACTION_2 | EXPIRED | DEACTIVE | REFINED_REPLACED`

## 5. True Orderblock / body-in-wick refinement

Later Reflection provides a more specific candidate than older generic OB language:

- candle BODY lies inside the wick of the previous or next candle;
- interpreted as a manipulated candle / bank-order clump;
- useful but not necessarily the most precise reaction point;
- within full zone refinement, FU wick remains the main refinement while body-in-wick OB is extra refinement with limited reaction life.

This later rule must be tested visually before replacing every earlier orderblock definition.

## 6. HCS zone boundaries and expansion

Current Reflection support:

- prime HCS zone is not defined from the exact obvious retail pivot by default;
- HCS zone can expand when a new HCS reaction adds meaningful range;
- the entire FU candle can belong to an HCS zone in the later refinement framework;
- a main HTF zone can expand to include an LTF HCS refinement;
- Broken HCS zone already includes the broken FU wick, so the FU-wick zone must not be duplicated;
- when refinement belongs to an existing HTF zone, expand the existing zone rather than create redundant layers.

## 7. Anti-duplication / overlap control

Source-confirmed:

- do not double-mark broken HCS + contained broken FU wick;
- expand existing HTF zone for nested refinement where appropriate;
- overlap ceiling: maximum 4, ideally 3;
- avoid over-refinement when the picture is already encapsulated.

Future detector must expose parent/child zone references rather than drawing every observed candidate as an independent zone.

## 8. Timeframe rules

Reflection zone-building protocol provides a custom top-down sequence and timeframe restrictions.

Important currently supported points:

- HTF zone scan proceeds from high custom TFs downward;
- HCS zones in the specified zone-building protocol are restricted to 1h/50min at that layer;
- 7/10/15m use analogous zone logic without the weakest/failed type;
- weakest ATT FU / failed-FU zones are 3h+ only;
- sole 1m HCS zone is final refinement inside an HTF zone, never standalone confirmation;
- 1min final bank-orderblock zone uses the whole Strong FU candle and then waits for retest or break-and-retest.

These timeframe rules need labelled chart certification before code promotion.

## 9. Same-TF reaction principle

Reflection repeatedly ties zone reaction counts to the zone's own timeframe. Earlier sources also use same-TF confirmation language.

Candidate rule:

`zone_reaction_valid_for_quota` should be evaluated on the zone's governing TF unless an explicit refinement rule reassigns authority.

Exact edge handling remains to be tested.

## 10. Zone workflow

Current candidate workflow:

1. locate zone candidate;
2. determine source type and governing TF;
3. verify activation condition;
4. avoid duplication with parent HTF zone;
5. refine internally only where justified;
6. wait for true reaction rather than predict from the zone alone;
7. update reaction count/lifecycle;
8. map each confirmed true-move reaction back to its source zone in post-session review.

## 11. Open blockers

This module is not VERIFIED until primary visual certification resolves:

1. exact boundary grammar for each zone type;
2. interaction between full FU candle, FU wick and body-in-wick OB boundaries;
3. older body-only OB marking versus later optional/full-range refinements;
4. exact same-TF reaction qualification;
5. marginal body-close cases near zone edge;
6. precise parent-child expansion rules;
7. exact handling of overlapping zones at the max-4 threshold;
8. positive/negative/edge examples for every zone type;
9. examples of inactive vs active zone;
10. examples of expired/deactive vs still-valid zone.

Until those gates pass, ambiguous zones remain `NOT_CERTIFIED` and cannot independently authorize a trade.

## 12. Future implementation fields

- zone_id
- zone_type
- source_pattern_id
- governing_timeframe
- parent_zone_id
- child_refinement_ids
- lower_bound
- upper_bound
- boundary_basis
- formation_timestamp
- activation_timestamp
- activation_type
- reaction_count
- reaction_quota
- lifecycle_state
- expired_timestamp
- deactive_reason
- provisional_or_confirmed
- provenance_refs