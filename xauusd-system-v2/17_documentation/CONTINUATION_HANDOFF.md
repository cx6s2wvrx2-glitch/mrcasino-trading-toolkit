# XAUUSD V2 — Continuation Handoff

Last updated: 2026-09-02
Branch: `xauusd-v2-foundation`
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
Project root: `xauusd-system-v2/`
Supabase project: `mr-casino` (`wuhrhlzabiuudswktcvk`)

## Purpose

This file is the durable handoff for continuing the XAUUSD V2 project in a new ChatGPT conversation if the current conversation reaches its maximum length. Do not rely on chat memory as the source of truth. Re-read this file plus the canonical status/source files and query Supabase before continuing.

## Non-negotiable project boundary

Only modify resources clearly related to this XAUUSD V2 trading project. Do NOT touch gym, Flowstate, LUMOS, THRV, or any unrelated repository/project/content unless the user explicitly requests it.

## Clean-room strategy policy

- All legacy strategy material is invalid unless the user explicitly approves a specific item.
- Existing GitHub/Supabase are infrastructure only.
- Only explicitly approved sources may become V2 sources.
- No invention; ambiguity = NO TRADE / NOT CERTIFIED.
- AI outputs start unverified/draft.
- Provenance everywhere.
- No auto-promotion to VERIFIED.
- Deterministic risk veto outranks strategy.
- No LLM live-execution authority.

## Source authority rules

- Primary Mr Casino material: highest strategy authority among approved sources.
- High-value serious student material: secondary corroboration only; cannot independently override/promote primary rules.
- Student charts/notes: secondary examples/hypotheses only.
- Implementation helpers (`Casino_v7`, `BETA 1 + LAOL`, compiled AFU/SFU): implementation evidence only, never strategy authority by themselves.
- PDFs 12 `Entries` and 13 `Attempted FU` remain unapproved for formal source ingestion unless the user explicitly approves them.
- `AFU = Attempted FU`; `SFU = Strong FU` confirmed by user.

## Architecture

Canonical 8 roles:
1. Knowledge Agent
2. Strategy Formalization Agent
3. XAUUSD Data Agent
4. Market State / Context Agent
5. Quantitative Research / Backtesting Agent
6. Independent Validation Agent
7. Deterministic Risk Engine
8. Continuous Improvement Agent

Orchestrator is fail-closed and evidence-report based. Critical strategy/research/execution gates do not accept free boolean bypasses.

## Current technical checkpoint

Last fully confirmed CI checkpoint before Round 11 completion work:
- `471/471` tests PASS on GitHub Actions.
- Blind-validation corpus: `90` cases (Rounds 02–10).
- No VERIFIED rules or VERIFIED knowledge.
- Live execution remains disabled; `EXECUTION_CANDIDATE` is not a live order.

Important data safeguards already implemented:
- no future/lookahead bars,
- provisional != confirmed,
- broker/symbol/timeframe provenance,
- broker tick-size/digits precision,
- parent/child candle reconstruction,
- source-chart ↔ immutable broker-bar alignment contract,
- intrabar FU evidence path,
- historical replay availability timestamps,
- immutable data snapshots and checksums.

## Strategy components already implemented at semantic/candidate level

- FU semantic criteria and raw observables
- Complete FU / Attempted FU Form 1 / Attempted FU Form 2
- FU quality metrics (no invented universal Strong-FU threshold)
- FU retest qualitative grading with R-54 fail-closed numeric branch
- helper shadow comparison: `Casino_v7` vs `BETA` vs Reflection
- liquidity interaction + R-207 scope taxonomy
- doji liquidity semantics
- zone lifecycle and separate zone geometries
- True Orderblock body-in-wick geometry
- HCS semantic grammar / strength hierarchy where source supports it
- negation window and x3 exception
- x3 final semantic definition
- x3-by-x3 explicit-label-only safety boundary
- TFS forming/established/retest states
- 10m+ minimum establishment floor
- True Stop semantic gate
- LAOL / target hierarchy candidate semantics
- R-143 official backtest sequence state machine
- R-145 LTF execution candidate logic
- Accepted-RR no-invented-number safeguard
- 11h no-synthetic-construction-without-anchor safeguard
- deterministic risk engine with no hardcoded 3%/5% production choice

## Known unresolved boundaries — do not invent

- R-54 exact Fibonacci 0/100 anchor/orientation for numeric 70% grading
- universal numeric Strong-FU threshold (source is qualitative)
- exact broker-specific Imbalanced-Candle geometry/tolerance
- x3-by-x3 standalone raw grammar (R-149)
- Accepted RR numeric definition (R-116)
- 11h candle construction/anchor (R-118)
- trail-level selection rule (R-150)
- production risk policy (including historical 3% vs 5% conflict)

## Top-down primary archive exhaustion

Source: `top down analysis (1).zip`
Authority: primary Mr Casino visual ground truth
Archive size: 188 real chart images across 29 dated sequences.

Processed/closed before current Round 11 work:
- 2021-11-21 — XAUUSD — Round 10 temporal 2021
- 2021-11-28 — XAUUSD — Round 10 temporal 2021
- 2021-11-30 — GBPJPY — inspected and explicitly excluded from XAUUSD corpus
- 2021-12-06 — XAUUSD — Round 10 temporal 2021
- 2021-12-12 — XAUUSD — Round 10 temporal 2021
- 2023-11-01 — Round 06
- 2023-11-06 — Round 07
- 2023-11-08 — Round 09
- 2023-11-20 — Round 08

Last indexed closed state before Round 11: `58/188 images`, `9/29 sequences` inspected/closed including the excluded GBPJPY sequence.

### Round 11 — CURRENT WORK IN PROGRESS

Temporal scope: `2022_method_state`.
All 30 charts from these 6 XAUUSD sequences have been visually reviewed:
- 2022-01-10 — 4 charts
- 2022-03-14 — 4 charts
- 2022-04-03 — 5 charts
- 2022-07-30 — 5 charts
- 2022-10-10 — 7 charts
- 2022-11-20 — 5 charts

Round 11 files already created on branch:
- `15_tests/ground_truth_round_11.json` — 30 cases / 30 charts (commit `a4d2849e...`)
- `15_tests/test_ground_truth_round_11.py` (commit `bf2acd67...`)
- Round-11 implementation coverage file was just created (commit `1dab7c23...`). Verify its exact path/content before editing.

Round 11 is NOT YET CLOSED. The next conversation/task must continue from here in this exact order:
1. verify the Round-11 coverage file and its exact blockers,
2. add/update Round-11 coverage tests if still missing,
3. insert all 30 Round-11 cases into Supabase as `unverified`, `promotion_allowed=false`, with `temporal_scope=2022_method_state`,
4. extend the blind-validation multi-round corpus from 90 to 120 cases,
5. update `TOPDOWN_PRIMARY_SEQUENCE_INDEX.md` to mark all six 2022 sequences processed,
6. run full GitHub Actions CI and record the exact new total test count,
7. only if CI is green, start the remaining 2023 sequences chronologically.

Do not claim Round 11 completed until all seven steps above are done.

## Key 2022 methodological observations already extracted

Use these only as temporal 2022 primary cases unless later sources confirm them:
- stronger emphasis on zone refinement and avoiding excessive/overlapping zones,
- manipulation required before choosing direction from a zone,
- liquidity can delay/veto an otherwise attractive FU/ATT-FU setup,
- HTF zones and LTF execution zones have different authority,
- FU-wick POI retest can be conditional on significant target liquidity,
- minor ATT-FU liquidity can be explicitly insufficient as a target,
- bias may remain prevalent when no meaningful opposite-side target exists,
- do not convert qualitative distance/strength words into invented numeric thresholds.

## Other already-approved visual corpora still to exhaust after top-down archive

- `PRICE ACTION REFLECTION.zip`: 124 included XAUUSD screenshots through 2023-05-31, grouped into 12 chronological episodes. Some episodes already represented in Supabase, but not all images are deeply annotated.
- `Swing low analysis XAU.zip`: 34 student charts, secondary only.
- `trading_notes_jpg_exports(1).zip`: 20 student handwritten-note images, secondary only.
- Reflection Master + Backtest Exercises: TOP PRIORITY; use final Master state, not stale page-1 progress text.
- Large remaining Discord page (~2000 images): not currently available in full. User will provide photos gradually. Do not block current work waiting for it.

## Reflection Master critical policy

Final Master says Reflection is fully extracted: 159/159 images + texts. The Master replaces/supersedes DISCORD_03 and DISCORD_04 for active Reflection use. Source R-labels are not unique because there are numbering collisions; always use source label + page/section/occurrence + internal V2 ID.

Evidence labels:
- `[C]` = source-confirmed / system-unverified
- `[I]` = inference/unverified
- `[U]` = ambiguous
- `[E]` = experimental/unverified
Never automatically promote `[C]` to V2 VERIFIED.

## How to resume in a new chat

User can say simply:

`Συνέχισε το XAUUSD V2 από το CONTINUATION_HANDOFF.md στο repo.`

Then the assistant should:
1. fetch this file from branch `xauusd-v2-foundation`,
2. fetch `01_sources/TOPDOWN_PRIMARY_SEQUENCE_INDEX.md`,
3. fetch canonical agent/readiness status files,
4. query Supabase live counts/status before quoting numbers,
5. inspect current branch head / latest CI,
6. resume the exact pending step instead of rebuilding or asking the user to repeat history.

## User communication preference for this project

Explain progress in simple Greek: what was found, what it means for the strategy, whether it is verified, and whether the user needs to decide anything. Do the technical work directly; do not make the user repeatedly say `πάμε` to continue a clearly agreed sequence.
