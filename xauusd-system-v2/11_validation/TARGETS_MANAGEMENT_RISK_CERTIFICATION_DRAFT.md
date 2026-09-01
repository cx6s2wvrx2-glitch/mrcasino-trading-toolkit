# Targets / Trade Management / Risk — Certification Draft

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01

This module separates strategy target logic from position management and from production risk policy. Source claims are preserved as evidence; no percentage, RR threshold, trail rule, partial rule or target distance is promoted merely because it appears in one source.

## 1. Mandatory separation

The future engine must keep three independent layers:

1. `TARGET_LOGIC` — where price is structurally expected to move based on liquidity / LAOL / TFS / zones / True Stop.
2. `TRADE_MANAGEMENT` — how an already-open position is reduced, protected, trailed or held.
3. `RISK_POLICY` — how much account risk is permitted and what hard vetoes apply.

A target is not a risk rule. A source example of 100/250/350+ pips is not an automatic TP. A book suggestion to move to break-even is not a universal management command. A source risk percentage is not automatically production policy.

## 2. Target selection — strongest current source support

### C-TGT-001 — Liquidity target first

Cross-source support:
- major/core liquidity and LAOL are central target structures;
- Reflection R-209 requires major liquidity taken + major liquidity to target in the directional checklist;
- Reflection R-111 says final HTF major-liquidity targeting is refined down to 1m reasoning for final execution/target context;
- the official backtest sequence R-143 ends in `core + major + LAOL target/timing`.

Candidate output:

`target_candidate = liquidity_object | LAOL | unresolved`

Hard restriction:

Do not use arbitrary fixed pip TP when an active structural target is available and certified.

### C-TGT-002 — Major target priority is contextual

A visible liquidity object does not automatically become the active target.

Priority depends on:
- prevalent move / TFS;
- which side has already been manipulated;
- relative importance of remaining liquidity;
- zone / True Stop context;
- LAOL placement;
- timeframe authority.

Therefore target selection must be a contextual ranking problem, not `nearest_liquidity = target`.

### C-TGT-003 — LTF target alone may be insufficient

Earlier imbalance material states that a sole 1m imbalance is not sufficient by itself as target, while higher-TF major imbalances may be valid targets.

Primary Price Action Reflection similarly shows that a 1m DB/doji/IMB may be downgraded when later manipulation demonstrates that a more important target remains elsewhere.

Candidate state:

`target_priority = major | secondary | trail | invalidated | unresolved`

## 3. LAOL and target relationship

Reflection R-208/R-214 support:
- LAOL is the last area of liquidity within the reversal POI / the target of the liquidity grab that started the move;
- core liquidity is the liquidity that must be significantly manipulated/taken first;
- LAOL is refined lower as required.

Candidate architecture:

`core_liquidity -> target_path -> LAOL / refined target`

Do not collapse `major_liquidity`, `core_liquidity`, `LAOL` and `trail_liquidity` into one field.

## 4. TFS scale — classification aid, not fixed TP

Reflection R-215 records a source scale:
- 1–5m = LTF / minimum scalp;
- 7–30m = scalp / intraday move;
- 30m–3h = intraday, source claim 100+ pips;
- 3h–7h = swing, source claim 250+ pips;
- 7h–4D+ = long-term swing, source claim 350+ pips;
- source notes expansion on news days.

V2 handling:

These ranges are `SOURCE CLAIMS FOR EMPIRICAL TESTING`, not production TP constants.

Future backtests must measure actual conditional distributions before any pip threshold is promoted.

## 5. Hold / extraction logic

### C-MGMT-001 — Do not automatically hold to opposite swing

Reflection R-222: intermediate intraday moves are continuation; extraction should focus on the active swing + minimum negation and the most ripe area rather than automatically holding until the opposite swing.

Candidate implications:
- hold horizon depends on active TFS category;
- a structural target may justify exit before an opposite macro swing;
- `maximum theoretical target` and `planned extraction target` are different fields.

### C-MGMT-002 — Swing holding requires stronger backing

Primary Q&A says daily extraction/LTF mastery comes before swing holding. 3h+ alignment is described as a basic intraday template; 7–11h+ backing supports longer multi-day swing potential. Holding also depends on target, liquidity trail, TFS and formation strength.

Candidate output:

`hold_mode = scalp | intraday | swing | long_swing | unresolved`

No hold mode may be selected from timeframe alone.

## 6. Break-even / partials / scaling

Primary Q&A states that a complete trading plan needs mechanical definitions for:
- targets;
- partials;
- breakeven;
- scaling;
- risk per trade/day;
- scenario-specific liquidity calculation.

A secondary book suggests:
- move to break-even early when possible;
- take partial profit / pay oneself;
- adapt management to trade potential.

V2 handling:

This is sufficient to establish that management must be explicitly specified, but NOT enough to certify a universal BE trigger, partial percentage, scale-in rule or trail distance.

Required future fields:
- `be_trigger_type`
- `partial_trigger_type`
- `partial_fraction`
- `scale_rule`
- `trail_rule`
- `management_reason`
- `provenance_refs`

All remain `UNSPECIFIED` until primary evidence or empirical policy selection resolves them.

## 7. Risk policy — source claims versus production choice

### Historical source claim

`03_Analysis_Basics_.pdf` states max 3% risk per trade and 1–3% depending on RR/confluence.

### Known conflict

The corpus also contains a separate 3% versus 5% risk disagreement.

Therefore:

`source_risk_claim != production_risk_policy`

V2 must not auto-select 3% or 5%.

The deterministic Risk Engine will eventually own:
- max risk per trade;
- max daily loss;
- max concurrent exposure;
- max correlated exposure;
- spread/slippage veto;
- duplicate-position veto;
- data-quality veto;
- session/news constraints if chosen;
- hard account protection.

The Risk Engine outranks strategy output.

## 8. RR claims

Some earlier material contains aggressive RR/readiness thresholds (e.g. source claims around 1:15+ and very high RR expectations). These are preserved as source statements only.

No production minimum RR is certified yet.

Future empirical evaluation must compare:
- structural target distance;
- true invalidation distance;
- spread/commission/slippage;
- realized MAE/MFE;
- target hit rate;
- partial/BE effects.

Only then can a production RR gate be chosen.

## 9. Stop-loss placement versus True Stop

Do not confuse:
- `True Stop` as strategy/context Main POI;
- broker order `stop_loss_price` as deterministic risk/execution protection.

A trade's protective SL must eventually be derived from a certified invalidation model plus risk sizing. It cannot simply equal every True Stop by definition unless primary certification proves that mapping.

## 10. Candidate management state machine

`PLANNED`
→ `OPEN`
→ optional `PARTIAL_TAKEN`
→ optional `BE_PROTECTED`
→ optional `TRAILING`
→ `TARGET_EXIT | INVALIDATION_EXIT | RISK_VETO_EXIT | MANUAL_TEST_EXIT`

Historical testing must preserve which management decision was knowable at each timestamp.

## 11. Certification blockers

Before VERIFIED status:

1. exact primary target-priority algorithm when multiple liquidity objects coexist;
2. exact LAOL/core/major/trail hierarchy in competing TFs;
3. empirical validation of R-215 pip scales;
4. exact trail-level selection — Reflection keeps this unresolved;
5. exact Accepted RR — Reflection keeps this unresolved;
6. primary/canonical break-even trigger;
7. primary/canonical partial-profit trigger and size;
8. scale-in / add-on rules;
9. exact protective SL / invalidation relationship;
10. production max risk per trade/day;
11. 3% versus 5% source disagreement;
12. costs/slippage-aware RR testing.

Until these are resolved, the system may identify structural targets but must not claim a certified live money-management policy.

## 12. Promotion standard

Targets may be certified separately from management and risk.

Possible future statuses:
- `TARGET_LOGIC_VERIFIED`
- `MANAGEMENT_POLICY_EXPERIMENTAL`
- `RISK_POLICY_USER_APPROVED`

This separation is intentional: strategy truth should not be contaminated by arbitrary account-risk preferences, and production risk must remain a deterministic veto layer.