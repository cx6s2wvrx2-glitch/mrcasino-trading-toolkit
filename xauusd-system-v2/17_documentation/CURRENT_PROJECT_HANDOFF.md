# XAUUSD V2 — Current Project Handoff

Updated: 2026-09-02
Branch: `xauusd-v2-foundation`
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
Project root: `xauusd-system-v2/`
Supabase project: `mr-casino` (`wuhrhlzabiuudswktcvk`)

## Non-negotiable scope

- This handoff is ONLY for the XAUUSD V2 project.
- Do not touch gym / Flowstate / LUMOS / THRV / unrelated repos or data.
- Clean-room V2: legacy strategy content is invalid unless the user explicitly re-approves a specific item.
- Source authority order: approved primary Mr Casino material > approved secondary/corroborative material > implementation helpers.
- Helper code never becomes strategy truth by itself.
- Ambiguity = fail closed / NO TRADE / NOT CERTIFIED.
- No LLM has live execution authority.
- Do not bypass connector safety blocks.

## Current verified technical checkpoint

Latest verified GitHub Actions run on `xauusd-v2-foundation`:
- run id: `33636554573`
- job id: `100268762626`
- head commit: `8d8282fe1415d2e76835c11f591f5c203860ffca`
- Python: 3.12
- result: **507 / 507 tests PASS**

Live Supabase snapshot checked on 2026-09-02:
- **29** active approved sources
- **195** knowledge claims
- **23** V2 rules
- **215** examples
- **32** agent runs
- **14** disagreement/certification records with `resolved_by_user=false`
- **0 VERIFIED knowledge claims**
- **0 VERIFIED rules**

Do not interpret the 14 open records as 14 broken strategy components. Several are deliberate fail-closed boundaries for concepts the source has not defined precisely enough.

## Architecture implemented

Canonical agent roles:
1. Knowledge Agent
2. Strategy Formalization Agent
3. XAUUSD Data Agent
4. Market State / Context Agent
5. Quant Research / Backtesting Agent
6. Independent Validation Agent
7. Deterministic Risk Engine
8. Continuous Improvement Agent

All eight have v0.1 foundation code. Critical strategy/research/execution gates consume evidence-bearing reports rather than free boolean bypasses.

## Strategy / research modules already implemented at semantic or candidate level

- FU semantic criteria and marked-liquidity bridge
- FU raw observables
- Complete FU / ATT FU Form 1 / ATT FU Form 2
- FU intrabar evidence reconstruction
- FU quality metrics without invented Strong-FU threshold
- FU retest quality with R-54 fail-closed fib-anchor boundary
- `Casino_v7` / `BETA 1 + LAOL` shadow comparison
- liquidity interaction + R-207 scoped taxonomy
- doji-liquidity semantics
- zone lifecycle and separate zone geometries
- True Orderblock body-in-wick geometry
- HCS semantics / establishment
- negation semantics
- final x3 semantic definition
- x3-by-x3 explicit-source-only boundary
- TFS forming / established / retest states
- 10m+ establishment floor
- True Stop semantic gate
- LAOL / target hierarchy candidate semantics
- R-143 official backtest-sequence state machine
- R-145 LTF execution candidate logic
- Accepted-RR safeguard: no invented numeric threshold
- 11h safeguard: native/provenance-backed 11h may be used; synthetic construction blocked until anchor is known
- deterministic Risk Engine with no hardcoded production 3%/5% choice
- broker precision / tick-size / digits
- immutable historical-data snapshots
- parent-child candle alignment
- source-chart ↔ immutable broker-bar alignment
- component replay / lookahead protection
- blind-validation packet / runner / comparator / runtime

## Known unresolved boundaries — DO NOT GUESS

- R-54 exact Fibonacci 0/100 anchor/orientation for numeric 70% grading
- universal numeric Strong-FU threshold
- exact broker-specific Imbalanced-Candle geometry/tolerance
- x3-by-x3 standalone raw grammar
- Accepted RR numeric definition
- 11h candle construction/anchor
- trail-level selection rule
- production risk policy, including historical 3% vs 5% conflict

## Source restrictions still active

The original first-10 approval did NOT include:
- `True Stop Loss`
- `Entries`
- `Attempted FU`

Do not use those as formal strategy authority unless the user explicitly approves them later.

Approved helper policy:
- `Casino_v7.txt`: implementation evidence; useful FU/ATT-FU decision tree; known duplicate/unreachable branches.
- `BETA 1 + LAOL.txt`: implementation prototype; user reports repaint; provisional states are never historical truth.
- `MMB_AFU_v1.ex5`: AFU = Attempted FU; compiled black box.
- `MMB_SFU_v1.ex5`: SFU = Strong FU; compiled black box.

Comparison direction is always:
`approved source -> canonical rule -> labelled example -> helper behavior comparison`.
Never reverse this direction.

## Blind-validation corpus

Persisted canonical blind corpus currently covers **Rounds 02–13 = 173 cases**.

Round sizes used by the current test suite:
- R02: 20
- R03: 7
- R04: 6
- R05: 5
- R06: 8
- R07: 10
- R08: 10
- R09: 4
- R10: 20
- R11: 30
- R12: 24
- R13: 29
- total: **173**

Agent 06 receives only `vector_id + source_locator` plus a shared taxonomy. Expected answers/evidence are excluded from the blind packet. Even 173/173 agreement cannot auto-promote a rule.

No real independent-provider validation run is allowed to be described as completed unless an actual model/provider run is executed and logged.

## Primary top-down archive — exhausted

Source: `top down analysis (1).zip`
Authority: primary Mr Casino visual ground truth.

Current source-exhaustion state:
- **188 / 188 real chart images inspected**
- **29 / 29 dated sequences inspected**
- **28 XAUUSD sequences**
- **1 GBPJPY sequence (`2021-11-30`) inspected and explicitly excluded from XAUUSD ground truth**

Canonical persisted rounds include the processed sequences through Round 13.

The final **47 XAUUSD charts** from:
- 2023-07-10
- 2023-08-21
- 2024-07-16
- 2024-07-24
- 2024-07-29
- 2024-07-30

were visually inspected and dominant candidate labels/blockers were prepared. During that pass a connector safety block prevented persisting the detailed trading-rule labels to GitHub. The block was not bypassed. Therefore these charts are source-exhausted but are NOT claimed as persisted canonical ground truth, blind-validation inputs, VERIFIED knowledge/rules, or certified detectors.

Canonical source-exhaustion reference:
`01_sources/TOPDOWN_PRIMARY_SEQUENCE_INDEX.md`.

## Other visual corpus exhaustion already completed

Recent branch history confirms these already-approved corpora were also inspected/indexed:

- **Price Action Reflection visual cutoff** through 2023-05-31: fully inspected/indexed.
- **Student Swing-low archive**: fully inspected/indexed; secondary student evidence only, never primary authority.
- **Student handwritten notes archive**: fully inspected/indexed; secondary student evidence only.
- **Casino Notes text annotations**: indexed.

Do not confuse `inspected/exhausted` with `verified` or `canonical detector-certified`.

## Reflection policy

Reflection Master is TOP PRIORITY and final Master state supersedes stale page-1 progress text. Final Master says Reflection extraction is complete. Source R-labels are not unique because numbering collisions exist; always identify by source label + page/section/occurrence + unique internal V2 ID.

Evidence classes:
- `[C]` = source-confirmed / system-unverified
- `[I]` = inference / unverified
- `[U]` = ambiguous
- `[E]` = experimental / unverified

Never automatically promote `[C]` to V2 VERIFIED.

## Current strategic status

The project is NOT strategy-verified and NOT live-ready.

Current facts:
- semantic/candidate engine foundation is substantial;
- source visual exhaustion is much further advanced than early handoffs indicated;
- 173 persisted blind cases exist;
- 507 regression tests pass;
- VERIFIED knowledge = 0;
- VERIFIED rules = 0;
- no performance claim is certified;
- live execution remains disabled.

## Immediate next work

Continue without waiting for the large Discord channel. User will send its photos gradually.

Priority order:
1. Reconcile/consolidate the now-exhausted approved corpora and identify which ambiguities can be closed from already-indexed primary evidence without invention.
2. Continue certification of the **173 persisted blind cases** and prepare a real independent Agent-06 provider run; do not simulate or call a self-comparison independent validation.
3. Build/connect broker-quality XAUUSD historical data ingestion and immutable snapshots suitable for source-chart alignment and historical replay.
4. Turn source-backed replay candidates READY only when broker/time/timestamp alignment is proven; never invent timestamps.
5. Use helper code only as shadow implementation evidence against approved labelled cases.
6. Keep the connector-blocked Round-14/15 candidate material noncanonical unless a compliant persistence path becomes available; do not bypass safety controls.
7. Continue ingesting new Discord photos gradually when the user provides them, preserving chronology and source authority.
8. Only after sufficient strategy certification: OOS -> walk-forward -> costs/slippage -> sensitivity -> Monte Carlo -> paper/demo -> shadow -> tiny live -> production.

## Workflow discipline

For every new source or candidate:
1. verify authority and approval,
2. preserve provenance,
3. distinguish source statement from inference,
4. create valid/invalid/edge cases only when justified,
5. name implementation blockers honestly,
6. keep outputs unverified/draft by default,
7. never auto-promote,
8. run CI after code/data-contract changes,
9. do not claim success if a connector blocks persistence,
10. never touch unrelated projects.

## How to resume in a fresh ChatGPT chat

User can paste:

`Συνέχισε το XAUUSD V2 από xauusd-system-v2/17_documentation/CURRENT_PROJECT_HANDOFF.md στο branch xauusd-v2-foundation. Διάβασε πρώτα το handoff, έλεγξε live GitHub/Supabase και το τελευταίο CI, και συνέχισε από το πραγματικό current state. Μην αγγίξεις τίποτα εκτός του XAUUSD project.`

The assistant should fetch this file first, then verify live branch head, `01_sources/TOPDOWN_PRIMARY_SEQUENCE_INDEX.md`, Supabase counts/status and latest CI before modifying anything.
