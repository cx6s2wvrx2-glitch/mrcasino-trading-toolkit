# XAUUSD V2 — Current Project Handoff

Updated: 2026-09-02
Branch: `xauusd-v2-foundation`
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
Supabase project: `mr-casino` (`wuhrhlzabiuudswktcvk`)

## Non-negotiable scope

- This handoff is ONLY for the XAUUSD V2 project.
- Do not touch gym / Flowstate / LUMOS / THRV / unrelated repos or data.
- Clean-room V2: legacy strategy content is invalid unless the user explicitly re-approves a specific item.
- Source authority order: approved primary Mr Casino material > approved secondary/corroborative material > implementation helpers.
- Helper code never becomes strategy truth by itself.
- Ambiguity = fail closed / NO TRADE / NOT CERTIFIED.
- No LLM has live execution authority.

## Architecture already implemented

Canonical agent roles:
1. Knowledge Agent
2. Strategy Formalization Agent
3. XAUUSD Data Agent
4. Market State / Context Agent
5. Quant Research / Backtesting Agent
6. Independent Validation Agent
7. Deterministic Risk Engine
8. Continuous Improvement Agent

All eight have v0.1 foundation code. The orchestrator uses evidence-bearing reports rather than free boolean bypasses for critical strategy/research/execution gates.

## Strategy modules already implemented at semantic/candidate level

- FU semantic criteria and marked-liquidity bridge
- FU raw observables
- Complete FU / ATT FU Form 1 / ATT FU Form 2
- FU intrabar evidence reconstruction
- FU quality metrics without invented Strong-FU threshold
- FU retest quality with R-54 fail-closed fib-anchor boundary
- Helper shadow comparison for `Casino_v7` and `BETA 1 + LAOL`
- Liquidity interaction and R-207 scoped taxonomy
- Doji liquidity semantics
- Zone lifecycle and separate zone geometries
- True Orderblock geometry
- HCS semantics and establishment
- Negation semantics
- x3 semantic definition
- x3-by-x3 explicit-source-only boundary
- TFS semantics / establishment / forming state
- True Stop semantics
- Official R-143 backtest sequence state machine
- R-145 LTF execution gate
- Target hierarchy with trail-selection blocker preserved
- 11h safeguard: native/provenance-backed 11h usable; synthetic aggregation blocked until anchor is known
- Accepted-RR safeguard: no invented numeric RR threshold
- Broker precision, immutable data snapshots, parent-child bar alignment, source-chart alignment, replay gates
- Blind-validation packet/runner/comparator/runtime

## Critical unresolved boundaries — DO NOT GUESS

- R-54 full-FU fib 0/100 anchor/orientation
- universal numeric Strong-FU threshold
- canonical broker-specific Imbalanced-Candle tolerance/geometry (`open==low/high` remains helper evidence, not primary truth)
- x3-by-x3 raw candle grammar
- Accepted RR numeric definition
- 11h candle anchor/construction
- trail-level selection rule
- production risk policy (including old 3% vs 5% conflict)

## Helper-code policy

Approved implementation helpers:
- `Casino_v7.txt`: useful FU/ATT-FU decision-tree reference; contains known duplicate/unreachable branches.
- `BETA 1 + LAOL.txt`: valuable repainting beta/prototype; provisional MTF states must never become historical ground truth.
- `MMB_AFU_v1.ex5`: AFU = Attempted FU; compiled black box.
- `MMB_SFU_v1.ex5`: SFU = Strong FU; compiled black box.

Comparison direction is always:
`approved source -> canonical rule -> labelled example -> helper behavior comparison`.
Never reverse this direction.

## Source restrictions still active

Earlier PDFs 11–13 were NOT approved in the original first-10 batch:
- True Stop Loss
- Entries
- Attempted FU
Do not use them as strategy authority unless the user explicitly approves them later.

The large remaining Discord channel (~2000 images) is NOT required right now. User will send images gradually. Continue exhausting already-approved material first.

## Ground-truth / top-down archive progress

Primary top-down archive: `top down analysis (1).zip`
- 188 real chart images
- 29 dated sequences
- one sequence `2021-11-30` is GBPJPY and is explicitly excluded from XAUUSD ground truth

Completed and fully checkpointed before current Round 11 work:
- 2023-11-01 -> Round 06
- 2023-11-06 -> Round 07
- 2023-11-08 -> Round 09
- 2023-11-20 -> Round 08
- 2021-11-21 / 2021-11-28 / 2021-12-06 / 2021-12-12 -> Round 10 (`2021_method_state`)
- 2021-11-30 -> inspected but excluded (GBPJPY)

Round 10 state:
- 20/20 Supabase rows
- all `unverified`
- all `promotion_allowed=false`
- all marked `2021_method_state`
- blind corpus through R10 = 90 cases
- latest fully verified CI checkpoint through Round 10 = **471/471 PASS**

Source-exhaustion index at the last fully committed checkpoint:
- 58/188 images accounted for
- 9/29 sequences accounted for, including the excluded GBPJPY sequence

## CURRENT EXACT CHECKPOINT — resume here

The 2022 tranche has been visually inspected across all 30 XAUUSD charts from:
- 2022-01-10 (4)
- 2022-03-14 (4)
- 2022-04-03 (5)
- 2022-07-30 (5)
- 2022-10-10 (7)
- 2022-11-20 (5)

Round 11 has STARTED and these files have already been committed on `xauusd-v2-foundation`:
- `15_tests/ground_truth_round_11.json` — 30 cases, one per 2022 chart
- `15_tests/test_ground_truth_round_11.py`
- `11_validation/CERTIFICATION_COVERAGE_ROUND_11.json`

Round 11 is deliberately temporal `2022_method_state`, not automatically canonical over later Reflection-era material.

IMPORTANT: Round 11 is NOT finished yet. At this checkpoint, do NOT claim it is in Supabase, in the blind corpus, or green in CI until those are actually completed and verified.

## Immediate next steps

1. Add/verify Round 11 coverage tests.
2. Insert all 30 Round-11 examples into Supabase as `unverified`, `promotion_allowed=false`, with `temporal_scope=2022_method_state`.
3. Update top-down sequence index so all six 2022 sequences become processed only after the above is complete.
4. Extend Agent-06 multi-round blind corpus from 90 -> 120 cases.
5. Run full GitHub Actions CI and record exact pass count.
6. Only after green CI, begin remaining 2023 top-down sequences chronologically:
   - 2023-05-18
   - 2023-05-19
   - 2023-05-22
   - 2023-05-30
   - 2023-06-06
   - 2023-06-20
   - 2023-06-21
   - 2023-06-26
   - 2023-07-10
   - 2023-08-21
7. Then process 2024 sequences until top-down archive reaches 188/188.
8. After top-down exhaustion, continue the same disciplined pass over the remaining already-approved visual corpora (including Price Action Reflection visuals and other approved chart batches), preserving chronology and source authority.

## Workflow discipline

For every dated visual sequence:
1. inspect every real chart,
2. preserve exact date/file provenance,
3. extract only explicit or tightly-supported Casino claims,
4. create valid / invalid / edge cases only when justified,
5. record honest implementation coverage/blockers,
6. keep `unverified` and `promotion_allowed=false`,
7. insert into Supabase,
8. extend blind-validation corpus,
9. require green CI,
10. then move to the next sequence.

Do not inflate case counts. Do not infer labels merely from how a chart looks. Preserve temporal evolution rather than collapsing older and newer method states into one rule.

## How to resume in a new ChatGPT chat

Tell ChatGPT:
`Continue the XAUUSD V2 project from xauusd-system-v2/17_documentation/CURRENT_PROJECT_HANDOFF.md on branch xauusd-v2-foundation. Read that file first, verify the current repo/Supabase state, and resume from the CURRENT EXACT CHECKPOINT. Touch nothing outside this XAUUSD project.`
