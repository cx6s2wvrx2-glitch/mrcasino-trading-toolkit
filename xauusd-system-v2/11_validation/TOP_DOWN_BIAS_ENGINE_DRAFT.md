# Top-Down Bias Engine — Certification Draft v0.1

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01

Purpose: formalize the directional/top-down decision process from approved Mr Casino sources without inventing a numeric scoring system. This layer consumes certified/candidate outputs from Zones, TFS, Liquidity/LAOL and True Stop. It does NOT generate entries by itself.

## 1. Core principle

The engine must reproduce the source hierarchy:

`HTF context commands -> lower TF refines -> liquidity decides priority -> TS/LAOL establish actionable context -> LTF sequence executes`

Source-supported principles already in the corpus:

- HTF confirmation defines the larger picture; LTF alone does not create HTF direction.
- `The LTF builds the HTF but HTF commands the LTF` (Reflection R-216).
- TFS ESTABLISHED and AS_FORMING are different states (R-217).
- Directional outlook requires Zones + HTF TFS + EST TFS + major liquidity taken + major liquidity to target; entries add core LTF liquidity + advanced entry-model TS (R-209).
- Official backtest order: HCS-zone reaction -> TFS -> LAOL met -> TS respected -> 10m TS established -> core/major/LAOL target + timing (R-143).
- No entry when analysis remains confused/doubtful; unresolved context is an explicit NO TRADE state.

## 2. Output states

Do NOT output a fake confidence percentage yet.

Allowed directional states:

- `BULLISH_PREVALENT`
- `BEARISH_PREVALENT`
- `TRANSITIONAL_BULL_TO_BEAR`
- `TRANSITIONAL_BEAR_TO_BULL`
- `MIXED_UNRESOLVED`
- `NO_TRADE`

Separate execution readiness:

- `CONTEXT_ONLY`
- `REFINEMENT_ALLOWED`
- `ENTRY_EVALUATION_ALLOWED`
- `ENTRY_NOT_ALLOWED`

A bullish/bearish prevalent state is not equivalent to permission to enter.

## 3. Required input objects

The top-down layer must consume references, not redraw concepts independently:

### 3.1 Zone map

For each relevant TF:
- active zones
- not-active zones
- reaction count / quota
- refined parent-child relationships
- expired/deactive zones
- nearest meaningful zone above/below

### 3.2 TFS map

Per TFS setting / timeframe group:
- direction
- state: `FORMING_PROVISIONAL | ESTABLISHED | RETESTED | NEGATED`
- confirmation timestamp
- supporting same-TF zone reference

### 3.3 Liquidity map

Both sides must be represented:
- core liquidity
- major liquidity candidates
- manipulated/taken liquidity
- downgraded/lower-priority liquidity
- active target candidates
- unresolved competition between sides

### 3.4 LAOL map

LAOL must be stored by context/setting, not as one global variable:
- intraday LAOL
- swing LAOL / trail
- LAOL within reversal POI
- LAOL target status: active / deferred / taken / unresolved

### 3.5 True Stop map

- TS candidate
- TS established
- TS retested
- TS respected
- TS broken/failed
- TS build sequence present/absent
- relative strength when competing TS structures exist

## 4. Directional decision ladder

### Gate A — HTF prevalent state

Start with the highest relevant established directional context.

Candidate behavior:
- established HTF TFS/HCS/x3 authority persists until comparable source-supported opposite authority develops;
- a lower-TF counter-signal is provisional/refinement information by default;
- forming HTF negation is a transition warning, not automatically a confirmed reversal.

If no stable HTF state exists:
`MIXED_UNRESOLVED`.

### Gate B — Zone context

Determine:
- which HTF zones remain active/relevant;
- which have completed their reaction quota or are no longer active;
- where meaningful refinement exists.

A zone cannot independently set direction. It narrows the areas where directional evidence is evaluated.

### Gate C — Liquidity comparison

Evaluate both sides:
- which liquidity has already been manipulated/taken;
- which remaining liquidity is more important;
- which visible liquidity has been downgraded by later manipulation;
- whether core/major target logic agrees with the prevalent HTF state.

If strong unresolved liquidity exists on both sides and no source-supported tie-break resolves it:
`MIXED_UNRESOLVED -> NO_TRADE`.

### Gate D — TFS establishment / transition

Require the relevant TFS layer to be explicit:
- `ESTABLISHED` supports prevalent direction;
- `AS_FORMING` may create a power-POI only on top of an already established prevalent TFS;
- an opposing forming state alone cannot erase established HTF authority.

### Gate E — LAOL / True Stop relationship

Before entry readiness, determine:
- relevant LAOL within/refined toward the current reversal POI;
- whether nearer POI/TS refinement supersedes a farther breakout LAOL for the immediate decision;
- whether TS is established and respected;
- whether the minimum manipulated TS build sequence exists.

No valid TS sequence / no respect evidence:
`ENTRY_NOT_ALLOWED`.

### Gate F — LTF execution readiness

Only after the prior gates agree:
- core LTF liquidity manipulated/taken;
- LTF LAOL condition satisfied where required;
- valid HCS/negation/x3 sequence or approved entry model appears;
- timing/session requirement is valid;
- risk engine later approves.

Then:
`ENTRY_EVALUATION_ALLOWED`.

The top-down engine itself still does not place an order.

## 5. First end-to-end primary test — 2023-11-01

Source: `top down analysis (1).zip`, primary Mr Casino.
Sequence: 12 screenshots.

### Observed hierarchy

1. **Monthly** — x3 manipulation closure + monthly HCS strength supports strongest buys entering the new month, while Mr Casino explicitly distinguishes outlook from final establishment.
2. **Monthly refinement** — a weaker HCS reaction is not enough to negate previous buys; intraday perspective is still needed for extraction bias.
3. **3-week** — forming negation high at monthly x3 area creates possible TS/retracement scenario, but buys remain prevalent until clearer HTF negation develops.
4. **2-week** — key untested HCS zone is mapped for the week ahead.
5. **1-week** — a previous area is explicitly marked no longer active after reaction, showing zone lifecycle matters to current bias.
6. **11-day** — refinement is retained while a previous weekly zone is marked for removal; not every prior zone remains equally relevant.
7. **4-day** — x3 becomes the first major sign for possibility of longer sells; this is transition evidence, not automatic replacement of all higher context.
8. **Daily** — Daily HCS + strong x3 appears while weekly-doji/monthly-high structures remain major targets; the annotation still says the immediate task is zone reading before close.
9. **12h** — concentrated zone remains relevant for refinement and the annotation states liquidity has the final say.
10. **4h** — HCS retest POI + 4h HCS zone becomes explicit context for LTF entries.

### What the sequence tests

A valid engine must be able to preserve all of these simultaneously:
- HTF prevalent buys;
- developing longer-sell transition evidence;
- active/deactive zone state;
- target/liquidity competition;
- lower-TF refinement without prematurely flipping the global bias.

A one-variable `bullish/bearish` model would fail this sequence.

## 6. Candidate state transition logic

Example high-level transition:

`BULLISH_PREVALENT`
-> opposing HTF evidence forms
-> `TRANSITIONAL_BULL_TO_BEAR`
-> if HTF opposite evidence becomes established AND liquidity/TS/LAOL confirm
-> `BEARISH_PREVALENT`

But:

`BULLISH_PREVALENT`
-> isolated LTF sell/HCS/FU
-> remain `BULLISH_PREVALENT` or `CONTEXT_ONLY`
unless sufficient higher/contextual authority is certified.

The mirror logic applies for bearish-to-bullish transition.

## 7. Hard NO-TRADE conditions — current candidate set

- HTF direction unresolved and competing signals cannot be reconciled;
- liquidity calculation unresolved between both sides;
- relevant TS build sequence absent;
- TS respect/establishment required by the setup but unresolved;
- only forming/provisional evidence attempts to create direction from zero context;
- lower-TF signal conflicts with active HTF state without sufficient negation authority;
- required zone is not active or has expired/deactivated;
- LAOL/POI relationship is ambiguous enough that immediate target direction is not defensible.

## 8. What must NOT be implemented yet

Do not create:
- weighted points for FU/HCS/x3;
- arbitrary 0–100 bias confidence;
- automatic tie-breaks between timeframes;
- a universal fixed TF ladder for every setup;
- `last signal wins` logic;
- automatic reversal on LAOL touch;
- automatic entry on zone touch.

## 9. Next certification tests

### Positive sequences
- established HTF + aligned zones/liquidity + established TS + LTF execution.

### Negative sequences
- strong-looking LTF reversal that fails to negate HTF prevalent state;
- correct zone but no TS sequence;
- visible major liquidity but wrong/immediate LAOL interpretation.

### Edge sequences
- HTF prevalent state with genuine forming transition;
- competing strong liquidity both sides;
- active intraday LAOL while swing LAOL remains deferred;
- deactivated parent zone while refined child remains relevant.

At least several dated Mr Casino sequences must reproduce the same decision ladder before promotion.

## 10. Promotion gates

Before this module can become VERIFIED:

1. label multiple full Mr Casino top-down sequences, not only 2023-11-01;
2. independently relabel them without using the formalization output;
3. demonstrate deterministic ordering of evidence;
4. resolve remaining TS respect geometry and LAOL tie-break rules;
5. prove historical reproducibility without future candles;
6. user/certified process approves promotion.

Current status remains:

`DRAFT / UNVERIFIED / NO LIVE AUTHORITY`.
