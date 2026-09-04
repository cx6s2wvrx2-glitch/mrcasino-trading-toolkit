# XAUUSD V2 — Phase 3 Strategy Sequence Architecture

Date: 2026-09-04
Scope: `xauusd-system-v2/` only
Status: PHASE 3 STARTED / RESEARCH ARCHITECTURE / NOT STRATEGY-CERTIFIED

## 1. Purpose

Phase 3 stops treating Strong FU / ATT / HCS / Negation as isolated chart events and begins composing them inside the strategy context.

The target is not a buy/sell generator. The target is a traceable reconstruction of the strategy path with no future leakage and no invented rule filling.

Human-facing status vocabulary:

- `OBSERVED` = the required evidence was actually observed and has provenance;
- `MISSING` = the stage was evaluated but the required evidence is not present yet;
- `BLOCKED` = the system cannot decide the strategy truth because source/data/semantic authority is unresolved.

`BLOCKED` must never be silently converted to false or true.

## 2. Why Phase 3 is NOT one invented universal linear chain

The primary corpus contains several related but distinct strategy sequences and entry families. V2 must preserve them rather than force them into one synthetic master rule.

Three layers are therefore kept separate:

1. universal context gate;
2. source-defined sequence scaffolds such as R-143;
3. entry-family-specific execution logic such as R-145 or confirmed True-Stop retest.

This prevents a rule from one entry family from becoming mandatory for every other family without source authority.

## 3. Universal context gate

Before an entry model is even reviewed, current source-supported drafts require at minimum:

1. directional / top-down context resolved;
2. liquidity calculation resolved;
3. relevant POI / zone context known.

Output is only:

`READY_FOR_MODEL_REVIEW | WAIT | BLOCKED`

It is deliberately NOT `ENTRY_ALLOWED`.

A detected FU/HCS/Negation cannot bypass this gate.

## 4. Official R-143 reconstruction scaffold

The existing `backtest_sequence.py` preserves the official source order:

`HCS zone reaction`
→ `TFS`
→ `LAOL met`
→ `True Stop respected`
→ `10m True Stop established`
→ `Core + Major + LAOL target/timing`

Phase 3 now wraps those stages in provenance-bearing evidence records through `strategy_evidence_sequence.py`.

The wrapper does not redefine R-143. It only adds:

- evidence/source reference;
- optional event time;
- optional timeframe;
- explicit observed/missing/blocked state.

A later stage cannot repair a missing earlier R-143 stage.

## 5. Liquidity / LAOL layer

Current source-supported architecture keeps the following distinctions:

- liquidity comes before final entry logic;
- major liquidity is not automatically LAOL;
- visible LTF liquidity is not automatically the active target;
- 30m+ operational marking and broad major-liquidity taxonomy remain separate source layers;
- no certified numeric scoring formula exists for competing liquidity candidates;
- unresolved liquidity comparison remains fail-closed.

Current deterministic components can evaluate interaction with an already-authorized marked level, but they do not invent which level is the correct active liquidity/LAOL.

## 6. TFS layer

Current semantic implementation preserves:

- TFS = confirmed prevalent direction;
- closed 10m+ evidence is required for established TFS in the conservative semantic gate;
- sub-10m evidence may refine but cannot establish the main TFS by itself;
- `AS_FORMING` cannot create independent direction from zero context;
- entry on a TFS retest remains only an entry candidate with downstream gates still required.

TFS must remain stateful and timeframe/setting-aware rather than one global bullish/bearish switch.

## 7. True Stop layer

Current semantic implementation preserves:

- True Stop is a contextual Main POI, not an arbitrary swing high/low and not a fixed stop-loss rule;
- a True Stop candidate requires aligned 10m+ TFS factors plus 10m+ HCS/Negation manipulation evidence;
- existence of the Main POI is separate from later `respected` behavior;
- LTF HCS/Negation entry refinement is allowed only after True Stop respect plus final liquidity calculation;
- exact deterministic True-Stop creation and respect geometry remain partially unresolved.

Therefore Phase 3 can carry TS evidence, but must not fabricate the missing raw boundary rules.

## 8. R-145 LTF execution layer

Existing `ltf_execution.py` preserves the source sequence:

`retail liquidity manipulated`
→ `LTF LAOL taken`
→ `1m negation OR 3m HCS+negation`

Confirmed mode additionally requires an established 10m True Stop.

Aggressive mode is kept separate and requires explicit fuller context including 10m TS forming + full TFS factors. It cannot silently downgrade into normal confirmed execution.

No LTF trigger creates HTF direction by itself.

## 9. Targets

Existing target semantics preserve these source-supported classes:

- Core Breakout Liquidity;
- Major Liquidity;
- opposite LAOL;
- trail level.

Core Breakout Liquidity is treated as the minimum eligible target only after the relevant opposite LAOL/POI respect and target identification prerequisites are present.

Trail-level selection remains unresolved and must stay fail-closed.

No target module currently makes a profitability claim.

## 10. Phase-3 evidence object

Implemented in:

`src/xauusd_v2/strategy_evidence_sequence.py`

Each record contains:

- strategy stage;
- `OBSERVED | MISSING | BLOCKED`;
- evidence provenance reference;
- source reference where applicable;
- timestamp where applicable;
- timeframe where applicable;
- note.

An `OBSERVED` record is rejected if it has no provenance.

Duplicate records for the same stage in one evaluation packet are rejected rather than silently overwritten.

## 11. Current Phase-3 adapters

### Universal pre-entry context

Implemented:

`evaluate_pre_entry_context(...)`

This returns only readiness for entry-model review.

### R-143

Implemented:

`evaluate_r143_evidence(...)`

This converts evidence states into the existing R-143 evaluator without changing its semantics:

- `OBSERVED -> True`
- `MISSING -> False`
- `BLOCKED / absent -> None`

Therefore an unresolved source boundary remains `NOT_CERTIFIED` rather than being treated as an ordinary missing stage.

## 12. March evidence role

The March 2023 material remains a validation specimen, not the definition of the strategy.

Current handling remains:

- `1973`: useful clean supplied-helper Strong-FU observation;
- `1975`: unresolved source-vs-broker geometry / FU-criteria boundary; do not force-match;
- `1986`: useful HCS-style control geometry but not proof of universal HCS semantics;
- 12:31 + 12:32 must not be merged into a staged HCS without source authority.

Phase 3 will later ask a harder question than “did an HCS appear?”:

“What context existed before it, what state changed after it, what liquidity/TS/TFS relationship was active, and was the sequence reconstructable without future information?”

## 13. What is still blocked

Phase 3 must remain fail-closed on at least:

- full FU semantic certification / B-01 intrabar opposite-move evidence;
- exact Strong-FU quantitative threshold;
- exact True-Stop raw creation and respect geometry;
- exact deterministic liquidity priority when several candidates compete;
- exact LAOL refinement when multiple timeframe candidates coexist;
- x3 / x3-by-x3 raw grammar;
- Accepted RR numeric/dynamic definition;
- synthetic 11h session anchor;
- trail-level target selection;
- production risk policy;
- exact `FOREXCOM:XAUUSD` historical reference alignment.

## 14. Next engineering milestones

Phase 3 continues in this order:

1. add traceable R-145 execution evidence adapter;
2. add True-Stop/TFS evidence composition without inventing raw geometry;
3. build one human-readable strategy-sequence report from the evidence ledger;
4. reconstruct known source episodes in order;
5. replay the same composition on real broker history without future leakage;
6. produce the final Greek visual/PDF validation artifact;
7. only after user validation of strategy understanding, move toward broad historical performance backtesting.

## 15. Hard boundary

A complete evidence path means only:

`SOURCE-SEQUENCE CANDIDATE RECONSTRUCTED`

It does NOT mean:

- profitable;
- strategy-certified;
- risk-ready;
- production-ready;
- live execution authorized.
