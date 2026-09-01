# Entry / Re-entry Models — Certification Draft v0.1

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01

Purpose: formalize entry and re-entry families only after top-down, liquidity, TFS and True-Stop context exists. This module must never turn a pattern into an automatic trade.

## 1. Universal pre-entry gate

Current primary/top-priority sources support the following order before a normal confirmed entry can be evaluated:

1. directional/top-down context is resolved;
2. liquidity calculation is resolved first;
3. relevant TFS is established / prevalent direction is confirmed;
4. relevant POI/zone context is known;
5. True Stop is established where required by the setup;
6. True Stop is respected/retested where required;
7. core LTF liquidity / LAOL execution condition is satisfied;
8. approved LTF entry model appears;
9. later deterministic risk engine approves.

Important source gate: Reflection R-95 says minimum 10m+ TS must be ESTABLISHED, not merely forming, for the normal entry-resolution path.

Therefore:

`PATTERN_FOUND != ENTRY_ALLOWED`

and

`BIAS_RESOLVED != ENTRY_ALLOWED`.

## 2. Confirmed True-Stop retest entry

Sources: Reflection R-108, R-182, R-95, primary Q&A.

Candidate conditions:

- prevalent TFS established;
- entry occurs on retest of established TFS / relevant True Stop POI;
- liquidity calculation agrees;
- minimum required 10m+ TS is established;
- final LTF HCS/negation refinement confirms execution.

Candidate state:

`ENTRY_MODEL = CONFIRMED_TS_RETEST`

Invalid:
- TS only forming when confirmed path requires established;
- no liquidity agreement;
- no LTF manipulated sequence where required;
- opposing HTF authority unresolved.

## 3. HCS entry model

Sources: Reflection R-221/R-65, primary Price Action Reflection.

HCS entry model is not merely an HCS candle pattern. It combines:

- liquidity manipulation;
- refinement point;
- reaction / True-Stop retest;
- alignment within the active POI / prevalent direction.

Candidate model:

`ENTRY_MODEL = HCS_TS_REFINEMENT`

A valid HCS entry must reference:
- `true_stop_ref`
- `tfs_ref`
- `laol_or_core_liquidity_ref`
- `zone_or_poi_ref`
- `confirmation_timestamp`

HCS without those contextual links remains price-action information only.

## 4. LTF execution sequence — 1m negation or 3m HCS+negation

Source: Reflection R-145 + primary notebook.

Candidate process:

`retail liquidity manipulated`
-> `LTF LAOL taken`
-> trigger through either:
  - `1m negation`, or
  - `3m HCS + negation`.

Candidate model:

`ENTRY_MODEL = LTF_LAOL_NEGATION`

or

`ENTRY_MODEL = LTF_HCS_NEGATION`.

This is an execution layer. It must not create the HTF direction itself.

## 5. Advanced FU-retest entry

Primary Price Action Reflection:

After direction is already established:
- 5m Attempted-FU retest
- plus strong 1m FU close
is shown as an advanced optimal entry.

Candidate model:

`ENTRY_MODEL = ADVANCED_ATT_FU_RETEST_PLUS_1M_STRONG_FU`

Hard restriction:

This model is invalid as a direction-discovery signal. Direction must already be established.

Open blockers:
- exact Strong-FU quantitative threshold;
- exact FU-break criterion;
- exact 5m retest quality boundary where entry remains valid.

Therefore it stays DRAFT even though the model family is source-supported.

## 6. HCS re-entry

Primary Price Action Reflection states that after the advanced FU-retest entry, a later 1m HCS can provide an easier re-entry once direction is more established.

It also shows that a previous HCS area can react again and form a new HCS, creating another entry/re-entry opportunity while broader liquidity context remains valid.

Candidate model:

`ENTRY_MODEL = HCS_REENTRY`

Required context:
- original prevalent direction still valid;
- active target/liquidity thesis unchanged or appropriately updated;
- prior TS/TFS context not invalidated;
- new HCS is formed/established according to the certified HCS grammar;
- entry occurs at a valid refined location, not anywhere after the first trade.

## 7. Established 1m HCS entry around high-impact timing

Primary Price Action Reflection shows an established 1m HCS before a high-impact event supporting entry when:
- buys are already prevalent;
- major targets remain above.

Waiting can produce additional 5m and 1m HCS confirmation.

Candidate interpretation:

The event/timing does not create direction; it is a volatility/execution window inside already-established context.

Candidate state:

`ENTRY_MODEL = ESTABLISHED_1M_HCS_TIMING_CONTEXT`.

Do not turn news timing into an unconditional entry trigger.

## 8. Aggressive AS_FORMING entry

Primary Price Action Reflection + Q&A + Reflection R-145 support an aggressive mode only under unusually complete surrounding context.

Candidate prerequisites include combinations of:
- zone of manipulation / prior FU-retest-zone reaction;
- liquidity left behind / extreme opposite-side liquidity;
- respected True Stop or active TS build;
- prevalent TFS and higher-TF confirmation;
- major target liquidity;
- broken opposing TS where the source example requires it;
- 10m TS forming in the Reflection aggressive sequence.

Candidate model:

`ENTRY_MODEL = AGGRESSIVE_AS_FORMING`

Mandatory software treatment:
- `provisional_or_confirmed = LIVE_PROVISIONAL`
- never store the forming state as confirmed historical truth;
- aggressive mode cannot bypass risk limits.

This model must remain separate from the normal confirmed-entry path.

## 9. Sole 1m FU forming — narrow aggressive exception

Primary Q&A says sole 1m FU forming may sometimes be used aggressively only when:
- reacting from a prior FU retest / zone;
- extreme liquidity exists on the opposite side;
- placement / low-liquidity move / TS potential agree.

Candidate model:

`ENTRY_MODEL = SOLE_1M_FU_AGGRESSIVE_EXCEPTION`.

This is an exception, not baseline entry logic.

Current blockers:
- exact FU validity geometry;
- SFU/close-quality threshold;
- exact minimum contextual requirements across chart examples.

## 10. 15m HCS aggressive setup after liquidity taken

Primary Price Action Reflection describes:
- 15m doji + big-wick liquidity taken;
- 15m HCS downside;
- zone retest + TFS alignment;
-> aggressive setup candidate.

Candidate model:

`ENTRY_MODEL = 15M_HCS_POST_LIQUIDITY_AGGRESSIVE`.

Again: liquidity is taken first; HCS is not the first decision in the chain.

## 11. NO-ENTRY conditions — source-supported candidate set

Entry must be rejected / remain unevaluated when:

- analysis is confused or doubtful;
- liquidity calculation is unresolved;
- required TS is only forming when confirmed path requires established;
- no minimum 1m manipulated TS build sequence exists in a setup requiring it;
- a pattern is outside the approved trading plan/model family;
- LTF signal conflicts with prevalent HTF state without sufficient negation authority;
- HCS/FU retest is visible but not located inside valid POI/TS/liquidity context;
- target/LAOL relationship is unresolved;
- the relevant zone is inactive/expired when the model depends on it.

Output:

`ENTRY_NOT_ALLOWED`.

## 12. Entry versus re-entry object model

Future engine should not overwrite the first entry with later opportunities.

Each opportunity object should include:
- `entry_model_id`
- `entry_family`
- `is_reentry`
- `parent_trade_or_setup_id`
- `direction`
- `entry_tf`
- `prevalent_tfs_ref`
- `true_stop_ref`
- `zone_ref`
- `laol_ref`
- `core_liquidity_ref`
- `trigger_pattern_refs`
- `timing_context`
- `confirmation_timestamp`
- `provisional_or_confirmed`
- `invalidated_by`
- `provenance_refs`.

## 13. Certification test matrix

### Confirmed TS retest
- positive: established TFS + established/respected TS + liquidity agreement + LTF trigger;
- negative: same-looking POI but TS only forming / absent sequence;
- edge: TS respected by wick but body/close geometry unresolved.

### HCS entry
- positive: HCS at certified TS refinement with aligned liquidity;
- negative: isolated HCS outside valid context;
- edge: near-wick HCS tolerance / competing HCS strength.

### Advanced FU retest
- positive: established direction + 5m ATT-FU retest + strong 1m FU close;
- negative: same structure while direction unresolved;
- edge: weak versus stronger retest quality.

### Re-entry
- positive: prior context remains valid + new established HCS reaction;
- negative: previous target/TS invalidated before re-entry;
- edge: new HCS forms while HTF transition is developing.

### Aggressive
- positive: full supporting context + provisional trigger;
- negative: sole forming signal without required context;
- edge: context aligned but TS establishment timing incomplete.

## 14. What is NOT yet allowed

Do not implement:
- market order from any detected FU/HCS alone;
- auto-entry from a zone touch;
- auto-entry from a LAOL touch;
- auto-entry from a 1m signal that contradicts HTF prevalent state;
- automatic aggressive mode when data is incomplete;
- numeric entry score invented from pattern counts.

## 15. Current status

Source-supported entry families now identified:

1. confirmed TS/TFS retest entry;
2. HCS/TS refinement entry;
3. 1m negation execution;
4. 3m HCS+negation execution;
5. advanced 5m ATT-FU retest + strong 1m FU;
6. HCS re-entry;
7. established 1m HCS timing-context entry;
8. aggressive as-forming mode;
9. narrow sole-1m-FU aggressive exception;
10. 15m HCS post-liquidity aggressive setup.

None is VERIFIED for production yet.

Remaining main blockers:
- exact FU/SFU mechanics;
- exact TS respect geometry;
- exact HCS boundary/tolerance mechanics;
- labelled positive/negative/edge cases for each entry family;
- independent validation and historical reproducibility;
- later deterministic risk gate.

Failure-safe:

`AMBIGUOUS -> ENTRY_NOT_ALLOWED -> NO_TRADE`.
