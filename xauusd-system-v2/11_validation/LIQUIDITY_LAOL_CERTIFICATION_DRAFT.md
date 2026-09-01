# Liquidity / Major Liquidity / LAOL — Certification Draft

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01
Round: 01 — mechanical decomposition started

This document consolidates only approved V2 sources. It does not create new strategy truth and does not resolve conflicts automatically.

## 1. Core concept — strong cross-source support

Current approved sources repeatedly place liquidity first in analysis. A single pattern, zone, FU or HCS is not sufficient context by itself.

Current source-supported core:

- Liquidity = obvious/concentrated retail stop-loss areas.
- Major Liquidity != Last Area of Liquidity (LAOL).
- Liquidity left behind is not automatically taken immediately.
- A visible liquidity point can be downgraded when later manipulation shows price is comfortable leaving it behind.
- Liquidity calculation compares the prevalent move, which side has already been manipulated more, and which side carries the more important remaining liquidity.
- Entry logic comes after liquidity/LAOL context, not before it.

## 2. Taxonomy versus operational marking

Two source layers must be kept separate rather than blended:

### 2.1 General major-liquidity taxonomy

Later Last Areas material + primary Mr Casino Q&A support four main categories:

1. unmanipulated doji
2. perfect double top / double bottom
3. perfect trendline
4. imbalanced candle / IMB

The Q&A independently repeats the same four categories and says doji/IMB liquidity is most prevalent.

### 2.2 Reflection operational marking on 30m+

Reflection later gives a narrower operational marking instruction:

- R-207: on 30m+, core marking = unfilled big-wick-to-fill + unmanipulated dojis; breakout liquidity optional/advanced.
- R-62 earlier in Reflection lists unmanipulated doji, big wick to fill, ATT FU and breakout.

These statements are not automatically merged. V2 must preserve the distinction between:

`liquidity_taxonomy`

and

`operational_marking_set_by_timeframe`

The source-evolution issue remains open until certified visually / by user where needed.

## 3. Mechanical candidate rules — Round 01

These are candidate rules for certification. None is VERIFIED yet.

### C-LIQ-001 — Core doji eligibility

Source: Reflection R-83.

Candidate condition:

- candle is inside the previous wick context;
- candle does not manipulate the last low/high.

Candidate output:

`liquidity_type = core_unmanipulated_doji`

Invalid / non-core candidate:

- the candle itself manipulates the last low/high;
- geometry falls outside the source-defined core-doji structure.

Open: exact programmatic geometry of "inside previous wick" still requires labelled chart tests.

### C-LIQ-002 — Four-type major-liquidity taxonomy

Sources: Last Areas Liquidity + primary Q&A 2024.

Candidate categories:

- `unmanipulated_doji`
- `perfect_double_top_bottom`
- `perfect_trendline`
- `imbalanced_candle`

Output:

`liquidity_class = major_candidate`

Important: category membership alone does NOT prove that the level is the active target, LAOL, or immediate reversal point.

### C-LIQ-003 — Perfect trendline threshold

Source: Last Areas Liquidity.

Candidate condition:

- >= 3 perfect rejection points => major-liquidity candidate.
- 2 points => low-liquidity candidate.

Open: exact numerical tolerance for "perfect" is still not defined mechanically.

### C-LIQ-004 — Lower-timeframe liquidity is not automatically decisive

Sources: primary Price Action Reflection + Q&A.

Candidate logic:

A visible LTF DB/doji/liquidity point must NOT automatically become the active target merely because it exists.

Downgrade evidence includes:

- stronger HCS/manipulation forms after or around the liquidity;
- price leaves the liquidity behind while stronger opposite-side context remains active;
- HTF/TFS/zone context supports the opposite target.

Output candidate:

`liquidity_priority = lower_priority`

This rule is contextual and is not yet reducible to a single candle test.

### C-LIQ-005 — Doji/liquidity hold gate

Source: Reflection R-92.

Candidate rule:

A doji/liquidity is allowed to be treated as holding live only when BOTH are present:

1. opposite-side liquidity overpowers;
2. the liquidity is inside HCS or HCS forms after it.

Output:

`hold_candidate = true`

If either condition is missing:

`hold_candidate = false_or_unconfirmed`

This is one of the strongest current candidates for later deterministic testing.

### C-LIQ-006 — Liquidity calculation comparison frame

Sources: primary Price Action Reflection + Q&A + Reflection.

Candidate comparison fields:

1. `prevalent_move`
2. `side_more_manipulated`
3. `remaining_liquidity_importance_buyside`
4. `remaining_liquidity_importance_sellside`
5. `HTF_TFS_context`
6. `zone_context`
7. `true_stop_context`

Output:

`direction_candidate = buy | sell | unresolved`

Hard gate:

If the evidence does not resolve the comparison => `NO_TRADE / unresolved`.

Open: no certified numeric scoring formula exists yet. Do not invent one.

### C-LIQ-007 — 30m+ operational marking set

Primary source: Reflection R-207, with historical comparison to R-62.

Current later-source candidate for 30m+ core marking:

- unfilled big wick to fill
- unmanipulated doji

Optional/advanced:

- breakout liquidity

Open source-evolution item:

- ATT FU appears in earlier R-62 but not the later core R-207 wording.

V2 action now:

Store `marking_mode = core | advanced | historical_candidate`; do not silently delete ATT FU or promote it into core.

### C-LIQ-008 — Liquidity first entry gate

Sources: Reflection R-95/R-143/R-145 + primary Q&A.

Candidate gate:

- liquidity calculation precedes final entry logic;
- sole x3/FU/HCS/zone pattern is insufficient without compatible liquidity context;
- visible liquidity alone is also insufficient for entry.

Output:

`entry_evaluation_allowed = true` only after liquidity/LAOL context has been established sufficiently for the current setup.

## 4. LAOL mechanical candidates — Round 01

### C-LAOL-001 — Practical LAOL definition

Source: Reflection R-208.

Candidate definition:

LAOL = the target of the liquidity grab that started the move, refined lower as needed.

Important:

`major_liquidity != LAOL`

A level may be major liquidity without being the active LAOL of the current move.

### C-LAOL-002 — Instant-taken doji rule

Source: Reflection R-90.

Candidate rule:

If a doji is taken immediately / inside the liquidity grab, classify it as:

`LAOL_of_its_timeframe = true`

Open: exact temporal boundary for "immediately" must be labelled from source examples.

### C-LAOL-003 — LAOL-to-LAOL reversal model

Source: Reflection R-60.

Candidate structural model:

`true_reversal(TFS_setting) = active_LAOL -> opposite_active_LAOL`

This must be applied separately per TFS setting; do not merge scalp/intraday/swing LAOL state blindly.

### C-LAOL-004 — LAOL refinement by timeframe

Sources: Reflection R-208/R-111.

Candidate process:

- broader HTF liquidity provides context/target candidate;
- active target is progressively refined;
- 1m liquidity reasoning is part of final target/entry refinement when the source requires it.

No fixed TF ladder is VERIFIED yet beyond explicit source statements.

### C-LAOL-005 — LAOL reaction is contextual, not automatic

Sources: Last Areas Liquidity + Price Action Reflection.

Candidate gate for reaction/reversal expectation:

- candidate LAOL present;
- major target exists in opposite direction;
- manipulation / TS / TFS / zone context supports reaction.

No standalone `touch LAOL => reverse` rule is permitted.

## 5. First-pass visual evidence review

Primary visual set currently available:

- Price Action Reflection: 12 dated episodes / 124 images through 2023-05-31.
- 2023-04-02 episode: 22 images with matching primary Casino text available.
- Reflection Exercise 1: Doji Liquidity + Big Wicks + HCS, top-down 4H→1H→15m→5m→1m.
- Reflection Exercise 3: official liquidity backtest protocol.
- 188 primary Mr Casino top-down screenshots remain sequence-level ground-truth material for later labelled conversion.

First visual pass on the 2023-04-02 episode supports using it as a multi-step evidence sequence rather than isolated screenshots. It contains repeated HTF/LTF zones, liquidity references, HCS reactions, target transitions and re-entry context that align with the paired text narrative.

Do NOT yet promote individual frames to VERIFIED positive/negative examples until frame-level labels are written.

## 6. Certification test matrix to build next

Required labelled cases:

### Core doji

- positive: satisfies R-83 geometry and remains unmanipulated;
- negative: manipulates last high/low;
- edge: borderline previous-wick geometry.

### Perfect DT/DB

- positive: source-certified perfect level;
- negative: visibly non-perfect rejection;
- edge: broker-data discrepancy / tiny price difference.

### Perfect trendline

- positive: 3+ perfect rejection points;
- negative: only 2 points;
- edge: 3 points with one tolerance dispute.

### IMB

- positive: source-certified major IMB target;
- negative: balanced candle / already materially filled structure;
- edge: partially filled IMB.

### Liquidity priority

- positive major: remains active in broader context;
- downgraded: HCS/manipulation demonstrates price can leave it behind;
- edge: competing strong liquidity on both sides.

### LAOL

- positive: source identifies the active last area / liquidity-grab origin relationship;
- negative: major liquidity that is NOT active LAOL;
- edge: multiple LAOL candidates across TFs.

## 7. Open questions after Round 01

Do not ask the user yet unless the existing primary visual corpus cannot resolve them.

1. Exact numerical tolerance for a "perfect" double top/bottom.
2. Exact numerical tolerance for a "perfect" trendline rejection.
3. Exact temporal definition of R-90 "taken instantly".
4. Exact deterministic priority function when several major-liquidity candidates coexist.
5. ATT FU status inside 30m+ operational marking after R-207 narrowing.
6. Exact machine geometry for big-wick-to-fill.
7. Exact mapping from HTF candidate liquidity to final 1m target when several LTF candidates exist.

## 8. Current certification state

Strong enough to proceed to labelled-example construction:

- liquidity-first analysis principle;
- four-category general taxonomy candidate;
- core doji candidate definition;
- perfect trendline 3+ threshold candidate;
- major liquidity != LAOL;
- R-90 doji→LAOL candidate;
- R-92 hold gate candidate;
- LAOL→LAOL per TFS model candidate;
- contextual downgrade of visible LTF liquidity.

NOT ready for VERIFIED / production:

- numeric tolerances;
- full priority scoring;
- complete 30m+ historical-vs-later marking reconciliation;
- frame-level positive/negative/edge certification.

Ambiguous cases remain `NO_TRADE / NOT_CERTIFIED`.