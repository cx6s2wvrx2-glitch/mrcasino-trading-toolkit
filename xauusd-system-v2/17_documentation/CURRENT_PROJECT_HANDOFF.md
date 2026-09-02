# XAUUSD V2 — Current Project Handoff

Updated: 2026-09-02
Branch: `xauusd-v2-foundation`
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
Project root: `xauusd-system-v2/`
Supabase project: `mr-casino` (`wuhrhlzabiuudswktcvk`)

## Non-negotiable scope

- ONLY the XAUUSD V2 project.
- Do not touch gym / Flowstate / LUMOS / THRV / unrelated repos or data.
- Clean-room V2: legacy strategy content is invalid unless the user explicitly re-approves a specific item.
- Source authority: approved primary Mr Casino > approved secondary/corroborative > implementation helpers.
- Helper code never becomes strategy truth by itself.
- Ambiguity = fail closed / NO TRADE / NOT CERTIFIED.
- No LLM has live execution authority.
- Never bypass connector safety blocks.

## Current verified technical checkpoint

Latest fully verified code checkpoint before this documentation update:
- GitHub Actions run: `33639681595`
- job: `100279310183`
- head commit: `606113cb6f1a2cb7386fb1672b34a108572f4be6`
- Python: 3.12
- result: **540 / 540 tests PASS**

Live Supabase snapshot checked 2026-09-02:
- **29** active approved sources
- **195** knowledge claims
- **23** V2 rules
- **215** examples
- **32** agent runs
- **14** open disagreement/certification records
- **0 VERIFIED knowledge**
- **0 VERIFIED rules**

The 14 open records are not 14 broken strategy components. Canonical engineering classification is in:
`17_documentation/CERTIFICATION_OPEN_RECORDS_MATRIX.md`.

## Architecture

Canonical roles:
1. Knowledge Agent
2. Strategy Formalization Agent
3. XAUUSD Data Agent
4. Market State / Context Agent
5. Quant Research / Backtesting Agent
6. Independent Validation Agent
7. Deterministic Risk Engine
8. Continuous Improvement Agent

All eight have foundation code. Critical strategy/research/execution gates consume evidence-bearing reports, not free booleans.

Agent 06 is now **v0.2.0** and has a multimodal blind-validation path.

## Agent 06 — current state

Implemented:
- blind packet excludes expected label/class/evidence per case;
- text-only external model command adapter;
- multimodal external model command contract;
- original primary images travel as file evidence with MIME + SHA-256 + byte size;
- image mutation is detected before model call;
- text-only client cannot silently validate an image case;
- multimodal runtime audit manifest stores source hashes/metadata and prediction/abstention, but no ground-truth answer and no local image path;
- primary-context filesystem bundle resolver;
- bundle rejects duplicate locators, answer-leakage fields and path traversal;
- Agent-06 readiness gate;
- CLI returns `READY_TO_RUN` only when the full blind packet has resolvable primary evidence and model metadata/capability; otherwise `NOT_READY` with explicit blockers.

Relevant code:
- `src/xauusd_v2/primary_context_payload.py`
- `src/xauusd_v2/primary_context_bundle.py`
- `src/xauusd_v2/structured_model_clients.py`
- `src/xauusd_v2/agents/validation_agent.py`
- `src/xauusd_v2/blind_validation_multimodal_runtime.py`
- `src/xauusd_v2/agent06_readiness.py`
- `src/xauusd_v2/agent06_readiness_cli.py`

A **real independent-provider validation run has NOT yet been executed**. Never describe it as completed until an actual provider/model is run and logged.

### Current real Agent-06 blocker

Most approved primary source records in `v2_sources` still have `storage_path = null`. The external runtime therefore does not yet have a persistent source store containing the original approved PDFs/charts/notebook assets for all 173 locators.

Do NOT substitute analyst summaries, evidence strings, model memory or candidate labels for missing primary context.

The current Supabase connector available in ChatGPT exposes database SQL/docs but no binary Storage-upload action. GitHub connector handles UTF-8 text, not the source binary corpus. Therefore source persistence is still an infrastructure dependency, not something to fake through SQL/base64 or summaries.

## Strategy / research modules already implemented at semantic or candidate level

- FU semantic criteria + marked-liquidity bridge
- FU raw observables
- Complete FU / ATT FU Form 1 / Form 2
- FU intrabar evidence reconstruction
- FU quality metrics without invented Strong-FU threshold
- FU retest quality with R-54 fail-closed fib-anchor boundary
- `Casino_v7` / `BETA 1 + LAOL` shadow comparison
- liquidity interaction + R-207 scoped taxonomy
- doji-liquidity semantics
- zone lifecycle + separate zone geometries
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
- Accepted-RR safeguard
- 11h safeguard
- deterministic Risk Engine with no hardcoded 3%/5%
- broker precision / tick-size / digits
- immutable historical-data snapshots
- parent-child candle alignment
- source-chart ↔ immutable broker-bar alignment
- component replay / lookahead protection
- blind-validation packet / runner / comparator / text runtime / multimodal runtime

## Real source/calibration unknowns — DO NOT GUESS

- FU: exact source-backed sufficiency for the opposite-direction move after liquidity take
- R-54 exact Fibonacci 0/100 orientation for numeric 70% grading
- universal numeric Strong-FU threshold, if one exists
- exact broker-specific Imbalanced-Candle geometry/tolerance
- x3-by-x3 standalone raw grammar
- Accepted RR numeric/dynamic definition
- 11h candle construction/session anchor
- trail-level selection rule
- final production risk policy, including historical 3% vs 5% conflict

Operationally handled but not formally VERIFIED: liquidity-list evolution, HCS evolution, zone/orderblock geometry split, secondary PPT authority, Reflection numbering collisions.

## Source restrictions still active

The original first-10 approval did NOT include:
- `True Stop Loss`
- `Entries`
- `Attempted FU`

Do not use them as formal authority unless explicitly approved later.

Helper policy:
- `Casino_v7.txt`: implementation evidence only; known duplicate/unreachable FU/ATT branches.
- `BETA 1 + LAOL.txt`: implementation prototype; user reports repaint; provisional states are never historical truth.
- `MMB_AFU_v1.ex5`: AFU = Attempted FU; compiled black box.
- `MMB_SFU_v1.ex5`: SFU = Strong FU; compiled black box.

Direction is always:
`approved source -> canonical rule -> labelled example -> helper behavior comparison`.

## Blind-validation corpus

Persisted canonical blind corpus: **Rounds 02–13 = 173 cases**.

- R02 20
- R03 7
- R04 6
- R05 5
- R06 8
- R07 10
- R08 10
- R09 4
- R10 20
- R11 30
- R12 24
- R13 29

Agent 06 sees only `vector_id + source_locator` plus a batch-wide taxonomy before source-context resolution. Even 173/173 agreement cannot auto-promote strategy rules.

## Primary top-down archive — exhausted

`top down analysis (1).zip`:
- **188 / 188** real chart images inspected
- **29 / 29** dated sequences inspected
- **28 XAUUSD** sequences
- **1 GBPJPY (`2021-11-30`)** inspected and explicitly excluded from XAUUSD ground truth

Canonical reference:
`01_sources/TOPDOWN_PRIMARY_SEQUENCE_INDEX.md`.

The final 47 XAUUSD charts from 2023-07-10, 2023-08-21 and July-2024 sequences were visually exhausted but their detailed candidate labels were connector-blocked from canonical persistence. Do not treat them as persisted blind cases or VERIFIED evidence.

Other already-exhausted/indexed corpora:
- Price Action Reflection visuals through 2023-05-31
- student Swing-low archive — secondary only
- student handwritten notes — secondary only
- Casino Notes text annotations

Inspected/exhausted != VERIFIED.

## Reflection policy

Reflection Master is TOP PRIORITY. Final Master state supersedes stale page-1 progress text. R-label collisions exist; use source label + page/section/occurrence + unique V2 ID.

Evidence classes:
- `[C]` source-confirmed / system-unverified
- `[I]` inference / unverified
- `[U]` ambiguous
- `[E]` experimental / unverified

Never auto-promote `[C]` to VERIFIED.

## Current strategic status

NOT strategy-verified. NOT performance-certified. NOT live-ready.

Facts:
- substantial semantic/candidate engine exists;
- approved visual source exhaustion is advanced;
- 173 persisted blind cases exist;
- **540 regression tests pass at the latest verified code checkpoint**;
- VERIFIED knowledge = 0;
- VERIFIED rules = 0;
- no performance claim is certified;
- live execution remains disabled.

## Immediate next work

Continue without waiting for the huge Discord channel; user will provide that gradually.

Priority:
1. Make the 173-case Agent-06 primary-context bundle persistently resolvable from original approved text/images; do not use summaries as substitute.
2. Configure a genuinely independent external multimodal provider/wrapper and run Agent 06 only after `agent06_readiness` says `READY_TO_RUN`.
3. Compare real blind predictions deterministically against ground truth; disagreement/abstention stays unverified.
4. Build/connect broker-quality XAUUSD historical-data ingestion and immutable snapshots for replay/source-chart alignment.
5. Turn replay candidates READY only with proven broker/time/timestamp alignment.
6. Keep helpers in shadow mode only.
7. Keep connector-blocked candidate material noncanonical unless a compliant persistence path appears.
8. Ingest future Discord photos gradually with chronology/source authority preserved.
9. After sufficient certification: OOS -> walk-forward -> costs/slippage -> sensitivity -> Monte Carlo -> paper/demo -> shadow -> tiny live -> production.

## Workflow discipline

For every new source/candidate:
1. verify authority + approval,
2. preserve provenance,
3. separate source statement from inference,
4. create valid/invalid/edge cases only when justified,
5. name blockers honestly,
6. keep unverified/draft by default,
7. never auto-promote,
8. run CI after code/data-contract changes,
9. do not claim persistence if connector blocks it,
10. never touch unrelated projects.

## Fresh-chat resume prompt

`Συνέχισε το XAUUSD V2 από xauusd-system-v2/17_documentation/CURRENT_PROJECT_HANDOFF.md στο branch xauusd-v2-foundation. Διάβασε πρώτα το handoff, έλεγξε live GitHub/Supabase και το τελευταίο CI, και συνέχισε από το πραγματικό current state. Μην αγγίξεις τίποτα εκτός του XAUUSD project.`

In a fresh chat, fetch this file first, then verify live branch head, `01_sources/TOPDOWN_PRIMARY_SEQUENCE_INDEX.md`, Supabase snapshot and latest CI before modifying anything.
