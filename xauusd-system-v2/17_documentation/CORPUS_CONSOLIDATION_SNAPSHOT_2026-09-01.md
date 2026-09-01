# XAUUSD V2 — Corpus Consolidation Snapshot

Date: 2026-09-01
Status: ACTIVE CONSOLIDATION — strategy corpus not complete

## Current database snapshot

- Sources: 29
- Knowledge claims: 159
- Glossary terms: 18
- Draft rules in DB: 23
- Examples: 24
- Agent runs: 7
- Knowledge verification status: 159/159 UNVERIFIED
- Rule status: 23/23 DRAFT
- Human-resolved disagreements: 0
- Open disagreements/ambiguities by governance rule (`resolved_by_user=false`): 9

Important: a disagreement row is NOT considered resolved merely because its `resolution` field contains a note such as "pending review". Only `resolved_by_user=true` or an approved certification process may close it.

## Source authority hierarchy for consolidation

### Tier A — top-priority / primary Mr Casino evidence

1. GIANNO_CASINO_REFLECTION_MASTER — top-priority master compilation.
2. Reflection ground-truth/backtest exercises.
3. Mr Casino top-down visual archive — 188 screenshots / 29 dated sequences.
4. Mr Casino Q&A March–April 2024 — direct answers only; student questions are context.
5. PRICE ACTION REFLECTION text through 2023-05-31 — direct Mr Casino text only.
6. PRICE ACTION REFLECTION visuals through 2023-05-31 — 124 images / 12 dated episodes, paired to text where available.
7. User-approved direct Mr Casino books/PDF instructional material where provenance supports primary use.

### Tier B — important corroborating / secondary evidence

- High-value videos from a serious Mr Casino student.
- Student swing-analysis archive.
- Student handwritten notes.
- Irving Santiago presentation / other secondary instructional material.
- MrDomino visual breakdown used as case-study evidence unless direct authority is separately established.

Secondary material may corroborate, illustrate or raise hypotheses. It may not independently override conflicting primary Mr Casino evidence or self-promote a rule to VERIFIED.

### Tier C — implementation references only

- Casino_v7 Pine reference.
- BETA 1 + LAOL repainting Pine prototype.
- MMB_AFU_v1.ex5 (Attempted FU) black-box MT5 indicator.
- MMB_SFU_v1.ex5 (Strong FU) black-box MT5 indicator.

Implementation code may suggest detectors, state machines, event models and test cases. It may never define strategy truth by itself.

## Open governance issues — 9

1. Major-liquidity source evolution: older big-wick list vs later definitive imbalanced-candle list.
2. HCS definition conflict: simplified FU→retest annotation vs direct HCS definitions/extensions.
3. FU break criterion ambiguity: previous-candle high/low clarified, but wick breach vs close remains unresolved.
4. Risk conflict: max 3% vs allowance up to 5% for small accounts in another source.
5. Imbalance geometry conflict: close-to-open vs wick-to-wick marking.
6. Orderblock boundary conflict: body-only vs optional wick inclusion / exceptions.
7. Secondary-source authority issue for the Irving Santiago presentation.
8. Reflection numbering collision: R-152 through R-180 reused; never merge by source label alone.
9. FU retest validity vs quality: body retest may be valid, while wick/50%-wick grading may define stronger entry quality.

## Certification order

The consolidation process will proceed concept-by-concept, not source-by-source:

1. Liquidity / major liquidity / Last Area of Liquidity / low-liquidity move
2. Timeframe Strength / True Stop / HTF-LTF hierarchy
3. FU / Strong FU / Attempted FU / negation / x3
4. FU retest / establishment / entry-quality grading
5. HCS / multiple HCS / HCS retest
6. Zones / orderblocks / zone of manipulation
7. Imbalances
8. Top-down analysis and bias construction
9. Entry models / aggressive vs confirmed entry / re-entry
10. Targets / trade management / risk

For each concept the required certification object is:

`definition → deterministic conditions → invalidation → positive example → negative example → edge case → source provenance`

If any required component is ambiguous, the production state remains `NO TRADE / NOT CERTIFIED`.

## Visual-data handling

- Dated screenshot sequences are preserved as episodes, not shuffled into isolated images.
- Text and chart evidence are linked where sequence/context is known.
- A chart does not create a canonical rule by itself; it certifies or challenges a textual/formal interpretation.
- Student visuals begin as secondary/unverified.
- Primary Mr Casino visuals begin as primary evidence but still require rule/example certification before becoming automated ground truth.

## Repaint handling

The BETA 1 + LAOL prototype uses provisional/forming multi-timeframe states. These are useful for realtime architecture but may change before candle close. V2 will separate:

- `PROVISIONAL_LIVE` — may update until the relevant candle/event is confirmed.
- `CONFIRMED_IMMUTABLE` — reproducible historical state used for certification and backtests.

No provisional/repainting output may be used as historical truth.

## Promotion rule

No AI agent may self-promote knowledge or rules.

Promotion path:

`UNVERIFIED claim → reviewed interpretation → deterministic draft rule → certified examples → historical validation → OOS/walk-forward/cost tests → paper/shadow → tiny live → production`

Strategy ingestion remains open: future yearly Discord image batches can be added gradually without blocking current consolidation.
