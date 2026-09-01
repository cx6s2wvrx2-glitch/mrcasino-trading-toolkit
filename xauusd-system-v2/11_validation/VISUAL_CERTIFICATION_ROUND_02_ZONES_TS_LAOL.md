# Visual Certification Round 02 — Zones / True Stop / LAOL

Status: ACTIVE / ALL LABELS UNVERIFIED
Date: 2026-09-01
Primary evidence: Mr Casino `casinonotes.excalidraw` + top-priority Reflection.

Purpose: turn the later zone engine, True-Stop build/respect logic and LAOL nesting into explicit positive/invalid/edge tests. No item in this file is automatically VERIFIED.

## 1. Zone lifecycle — primary visual tests

### Z-VC-01 — Broken FU wick zone activation
Embedded notebook file: `8ac53dc9378f9c568c27f49a080bb772c960d94a`
Label: VALID candidate.

Casino annotations explicitly state:
- the zone was broken with a BODY CLOSURE and becomes active only at that point;
- it holds for one main true-move reaction on the SAME TF;
- it can hold for two, but only the first is confirmed and matters most.

Certification use: positive test for `NOT_ACTIVE -> BODY_CLOSE_BREAK -> ACTIVE -> REACTION_1`.

Still open: exact marginal body-close tolerance at the zone edge.

### Z-VC-02 — Broken HCS reaction quota
Embedded notebook file: `a46bf1c244bec9d82ae6bf6559b507d46e1707cd`
Label: VALID candidate.

Casino annotations:
- two main same-TF reactions are confirmed;
- a third may occur but is weaker/non-core.

Certification use: positive lifecycle test for reaction quota.

### Z-VC-03 — HCS placement, expansion and explicit exception
Embedded notebook file: `7c144a2d92d0376a13fbea41caf17161affdc763`
Label: EDGE candidate.

Casino visual rules:
1. better HCS zone does not start from an exact pivot high/low by default;
2. existing HCS zone can expand with a new HCS reaction; full range matters and large zones are refined internally;
3. on 50m+, even a small weak ATT-FU wick reaction from where HCS would form can suffice as a hidden zone, creating an explicit exception to rule 1.

Certification consequence: zone-boundary logic cannot be reduced to `always use pivot` or `never use pivot`.

### Z-VC-04 — True Orderblock geometry
Embedded notebook file: `6002c168895b3ff94bfff2f40d00dd7bc6a39146`
Label: VALID candidate.

Casino annotation: candle BODY inside the wick of the previous or following candle forms a True Orderblock candidate / bank-order clump, but it is not necessarily the most accurate reaction point.

Certification consequence: geometry and reaction precision are separate fields.

### Z-VC-05 — Weakest ATT-FU / failed-FU zone TF gate
Embedded notebook file: `66685ec90725d4e70cdfff8f440fdbbb80dc0d78`
Label: EDGE candidate.

Casino annotations:
- weakest ATT-FU wick can count as a zone;
- one main reaction only;
- relevant on 3h+ swing TFs;
- can be classed as failed FU.

Certification consequence: this zone family must fail on lower TFs unless another explicitly certified rule applies.

### Z-VC-06 — 1m final zone geometry
Embedded notebook file: `04b836f9afeeb4440d00f771dcec7a1d8dea7426`
Label: VALID candidate.

Casino annotation: mark the whole Strong FU candle for the 1m zone; then wait for retest or break-and-retest.

Certification consequence: 1m final zone is not represented by body-only generic OB logic.

## 2. True Stop — build, weakness and respect

### TS-VC-01 — Minimum manipulated sequence for TS build
Embedded notebook file: `907e1816bce48502ddfd3d32076cbebcb7b1d8ed`
Label: VALID candidate.

Casino annotations:
- look for new LTF TS build in the main timing hour;
- higher-TF/POI backing accompanies the build;
- banks are in only with a minimum 1m manipulated SEQUENCE.

Candidate implementation gate:
`TS_BUILD_SEQUENCE_PRESENT = true` before strong execution authority is allowed.

### TS-VC-02 — No sequence = weaker TS / wait
Embedded notebook files: `7db77b4d14096bd2dc23358147eda91bdac09139`, `95b7205bc49506c7f397e0678a45f07556ce105b`
Label: INVALID / NO-ENTRY candidate.

Casino annotations:
- trade only with the minimal 1m TS build-up sequence;
- NO SEQUENCE = weaker TS to note in bias;
- if no 1m true-stop HCS/negation/x3 formation exists, wait for the correct sequence showing bank entry.

Certification consequence: visible POI/liquidity alone does not pass the TS execution gate.

### TS-VC-03 — HCS/TS retest preserves stronger side
Embedded notebook file: `7db77b4d14096bd2dc23358147eda91bdac09139`
Label: EDGE candidate.

Casino annotation: HCS/TS retest confirms the previous stronger buy TS while the opposing sell TS is weaker; buys remain in play.

Certification consequence: competing True Stops require relative strength/context, not last-signal-wins logic.

### TS-VC-04 — Explicit TS respect check
Embedded notebook file: `15c886c8b7ca732cfa33ab5767dd4191dd4f3294`
Label: VALID candidate.

Casino annotations:
- TS marked in zone around 7m x3-negation high + 1m manipulated doji;
- evaluate whether the new 1m x3 negation RESPECTS the previous TS;
- resolution is framed around the 1m sequence.

Candidate state transition:
`TS_ESTABLISHED -> NEW_LTF_SEQUENCE -> RESPECT_CHECK -> RESPECTED | FAILED/UNRESOLVED`.

Still open: exact candle-level respect geometry (wick penetration, body penetration, closure threshold) must be certified before coding.

### TS-VC-05 — Aggressive use does not erase sequence requirement
Embedded notebook file: `60904c92ce38a7cffab0678edf352e5906c3cb73`
Label: EDGE candidate.

Casino annotation: a more aggressive entry can be considered while structure forms when TFS POI is respected and sell side is weak through liquidity + TS build, while opposite management still requires the full sequence.

Certification consequence: `AGGRESSIVE` is a mode inside established context, not permission to bypass TS/liquidity gates.

## 3. LAOL — nested priority rather than one flat target

### LAOL-VC-01 — LAOL belongs inside the reversal POI
Notebook annotation + Reflection R-214.
Label: STRUCTURAL candidate.

Cross-source support:
- notebook: LAOL should be inside a POI, close to a relevant True Stop;
- Reflection R-214: LAOL = last area of liquidity inside the reversal POI; core liquidity is the liquidity that must be taken/manipulated significantly first.

Candidate consequence: `major_liquidity`, `core_liquidity`, `LAOL`, and `POI/TS` must be stored as linked but distinct objects.

### LAOL-VC-02 — Intraday LAOL versus trail to swing
Embedded notebook file: `e1c26acf9711eeff11a99f6b8d3f3473ba3fdad3`
Label: EDGE candidate.

The chart explicitly marks an `Intraday LAOL` separately from `LAOL 2 - trail to swing`, while a 10m x3-negation/TS respect-establishment process remains active.

Certification consequence: LAOL is timeframe/TFS-setting specific; one global LAOL variable is invalid architecture.

### LAOL-VC-03 — Breakout LAOL can be deferred by nearer important POI/TS
Embedded notebook file: `9ac21863ede5494d6d5e712945cae90b45c48581`
Label: EDGE candidate.

Casino annotation: breakout LAOL is an extended possibility, but an important POI/TS must be refined closer first.

Certification consequence: the presence of a farther LAOL target does not automatically authorize immediate continuation; nearer POI/TS structure can control the next decision.

### LAOL-VC-04 — Opposite side overpowers after LAOL context changes
Embedded notebook file: `8a834788ba82de06ab966f8f0cf00b261f9a8219`
Label: EDGE candidate.

The chart frames an extended LAOL that may be left for a future swing buy once the opposite side overpowers.

Certification consequence: an identified LAOL can remain structurally relevant without being the current immediate target.

## 4. What Round 02 materially clarifies

1. Zone activation by body closure now has direct primary visual support, not only extracted text.
2. Broken FU and Broken HCS reaction quotas have direct visual examples.
3. Zone placement contains explicit exceptions, so a simplistic pivot-based detector would be wrong.
4. True Stop build requires a manipulated sequence; absence of sequence is an explicit weakness/no-entry condition.
5. `TS respected` is a real state in primary material, not an invented software state.
6. Competing TS structures are hierarchical/contextual.
7. LAOL is nested by timeframe/POI and can be deferred by nearer TS/POI logic.

## 5. Remaining blockers after Round 02

Still NOT mechanically certified:

- exact TS `RESPECTED` geometry: wick/body/close thresholds;
- exact marginal body-close rule at a zone boundary;
- exact lower/upper boundary formula for every zone subtype;
- complete parent-child zone expansion algorithm;
- exact LAOL boundary selection when multiple LTF candidates exist inside one POI;
- exact priority/tie-break rule between competing intraday and swing LAOLs;
- FU-retest 70% fib anchor/orientation;
- imbalance geometry conflict.

## 6. Promotion status

`VERIFIED promotions = 0`.

All examples remain `unverified` until independent relabelling and historical reproducibility gates are passed.

Failure-safe remains:

`AMBIGUOUS -> NOT_CERTIFIED -> NO_TRADE`.
