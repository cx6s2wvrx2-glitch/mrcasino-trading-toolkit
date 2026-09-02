# XAUUSD V2 — System Readiness Snapshot

Date: 2026-09-02
Status: STRATEGY ENGINE FOUNDATION ACTIVE / NOT STRATEGY-VERIFIED / NOT LIVE-READY

## Governance baseline

XAUUSD V2 remains clean-room and fail-closed.

Hard constraints:
- no legacy strategy rule becomes authority unless re-approved;
- approved primary Mr Casino evidence outranks secondary/corroborative material and implementation helpers;
- helper behavior cannot define strategy truth;
- ambiguity means NOT CERTIFIED / NO TRADE;
- no LLM has live execution authority;
- no independent-provider claim exists until a real external run completes and its frozen outputs are audited;
- no blind-validation result can auto-promote knowledge or rules to VERIFIED;
- live execution remains disabled.

## Supabase inventory snapshot

Known live Supabase state on 2026-09-02:
- 29 user-approved source records currently stored with `status='review'` — do not describe these rows as database `ACTIVE`;
- 16 source records with non-null `storage_path`;
- 195 knowledge claims;
- 23 V2 rules;
- 215 examples;
- 32 agent runs;
- 14 disagreement/certification rows with `resolved_by_user=false`;
- 0 VERIFIED knowledge claims;
- 0 VERIFIED rules.

The 14 unresolved rows consolidate into 8 genuinely unresolved blocker families. Deduplication/reconciliation does not mutate `resolved_by_user` and does not promote anything.

Canonical blocker registry:
- B-01 FU sufficient opposite-direction move / break mechanic;
- B-02 R-54 70% fib 0/100 anchor/orientation;
- B-03 universal numeric Strong-FU threshold, if one exists;
- B-04 broker-specific Imbalanced-Candle calibration;
- B-05 x3-by-x3 raw detector grammar;
- B-06 Accepted RR numeric/dynamic decision rule;
- B-07 synthetic 11h candle anchor/session origin;
- B-08 user-approved production risk policy.

Detailed audits:
- `17_documentation/PRIMARY_BLOCKER_AUDIT_B01_B04_2026_09_02.md`
- `17_documentation/PRIMARY_BLOCKER_AUDIT_B05_B08_2026_09_02.md`
- `17_documentation/OPEN_BOUNDARY_RECONCILIATION_2026_09_02.md`

## User clarification — FU-family timeframe scope

Explicit user clarification on 2026-09-02 establishes:
- Strong FU / ATT FU use the same primitive logic on every timeframe;
- the concept is fractal/timeframe-invariant;
- timeframe changes authority, top-down weighting, move scale and downstream application, not the primitive definition;
- a source-specific 1m Strong-FU zone construction is a 1m application and must not be promoted into the universal Strong-FU definition.

Canonical record:
`01_sources/USER_CLARIFICATION_FU_TIMEFRAME_SCOPE_2026_09_02.md`

## Agent and orchestration state

All 8 canonical agent roles have foundations:
1. Knowledge;
2. Strategy Formalization;
3. XAUUSD Data;
4. Market State / Context;
5. Quant Research / Backtesting;
6. Independent Validation;
7. Deterministic Risk Engine;
8. Continuous Improvement.

Current orchestrator requires evidence-bearing reports rather than free booleans.

A strategy candidate cannot bypass:
`validated data + unambiguous context + ordered strategy sequence + LTF execution gate + independent validation report + historical replay report + risk gate`.

Execution consumes the actual upstream strategy/risk reports. A blocked report cannot be relabelled ready downstream. `live_execution_authorized=false` remains a hard boundary.

## Strategy implementation state

Source-backed/candidate layers currently cover:
- FU semantic criteria and observables;
- Complete FU / ATT FU forms;
- intrabar FU evidence and parent/child reconstruction;
- threshold-free FU quality observables;
- FU retest quality including fail-closed R-54 numeric branch;
- Casino_v7/BETA helper shadow comparison without helper authority;
- liquidity interaction and taxonomy;
- doji/liquidity semantic edge cases;
- classic zone confirmation and later Reflection zone lifecycle/geometries;
- HCS semantics;
- negation window and x3 exception;
- x3 semantic primitive and x3-by-x3 source-label boundary;
- TFS establishment/as-forming and research scale;
- True Stop semantic gate;
- R-143 ordered strategy sequence;
- R-145 LTF execution candidate logic;
- Accepted RR fail-closed boundary;
- 11h context/synthesis boundary;
- structural target hierarchy with unresolved trail selection kept explicit;
- deterministic risk engine without hard-coded 3%/5% production policy;
- broker precision;
- immutable data snapshots and research-runtime gates.

Implementation coverage is not VERIFIED strategy truth and is not performance evidence.

## Blind ground-truth corpus — R02 to R13

Persisted blind corpus:
- R02: 20 cases;
- R03: 7 cases;
- R04: 6 cases;
- R05: 5 cases;
- R06: 8 cases;
- R07: 10 cases;
- R08: 10 cases;
- R09: 4 cases;
- R10: 20 cases;
- R11: 30 cases;
- R12: 24 cases;
- R13: 29 cases.

Total: **173 persisted blind cases**.

Each Agent-06 case exposes only its blind identity/locator plus the shared batch-wide taxonomy. Per-case expected labels, analyst evidence and forbidden-inference notes are excluded from the provider packet.

Even 173/173 agreement remains non-promotional.

## Agent-06 independent validation infrastructure

Implemented:
- strict answer-free packet schema with recursive forbidden-field rejection;
- frozen packet builder for R02–R13;
- primary evidence resolver for PDFs, top-down images, Excalidraw images/text and exact locators;
- private evidence bundle with pinned bundle and manifest SHA-256;
- readiness gate before any provider call;
- isolated provider process that does not load ground truth;
- strict blind prediction loader;
- separate deterministic post-run comparison process;
- packet fingerprint / locator / taxonomy verification before ground truth is loaded;
- external command adapter preserving provider command flags;
- Anthropic multimodal wrapper with image SHA/MIME/size verification;
- provider-compatible structured-output schema and local confidence validation;
- sanitized safe provider error codes without API-key/response-body leakage;
- bounded validator response verbosity;
- configurable Anthropic output-token cap;
- frozen output hashes before post-run comparison;
- strict post-run audit CLI;
- explicit `api_key_written_to_disk=false`, `blind_process_loaded_ground_truth=false`, `promotion_allowed=false` contracts.

### Post-run audit gate

CLI: `xauusd-v2-agent06-audit`

The audit process is separate from the blind provider execution and verifies the completed persisted run only after the provider/comparison pipeline is finished.

It fail-closes on:
- missing required artifacts;
- wrong run/provider/model/case metadata;
- wrong private bundle or primary-context manifest hashes;
- mutated prediction/runtime files after freeze;
- comparison not recorded after blind execution;
- any promotion flag set true;
- blind ground-truth loading;
- mismatched packet/taxonomy/vector IDs/source locators;
- inconsistent AGREE/DISAGREE/AMBIGUOUS totals;
- runtime abstention-count mismatch;
- runtime/readiness image-case mismatch;
- invalid text/image evidence SHA-256 metadata;
- invalid image MIME or byte size;
- path-like local evidence fields in the persisted runtime manifest;
- a runtime case without any persisted evidence fingerprint.

`AUDIT_PASS` means the external run is internally coherent/auditable. It still does not promote strategy truth.

Real-provider status:
- a real Anthropic `claude-sonnet-5` local run is currently executing on the user's machine;
- earlier failed attempts exposed and fixed parser/schema/output-cap issues;
- **until that run reaches `LOCAL_AGENT06_PIPELINE_COMPLETE` and its frozen artifacts pass inspection/audit, no completed external independent validation is claimed**.

Do not ask the user to pull the newer GitHub branch while that local process is still running.

## Primary Agent-06 evidence bundle

Private bundle remains outside the public repository.

Pinned identifiers:
- bundle SHA-256: `6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf`;
- manifest SHA-256: `e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37`;
- 477 resolver entries;
- 219 unique image assets;
- 1 text asset;
- 222 ZIP members including the canonical `primary_context_bundle.json`.

Proprietary source binaries must never be committed to the public repository.

## Historical replay and MT5 infrastructure

Implemented:
- strict machine-readable replay-session loader;
- lookahead-safe component replay with separate `occurred_at` / `available_at`;
- historical replay batch gate;
- source-backed replay candidate registry;
- source-chart alignment checks;
- broker/symbol/timeframe/window/grid alignment;
- parent/child bar alignment;
- MT5 history ingestion for supported CSV/tab exports;
- explicit source timezone handling — never inferred;
- OHLC/time-order/spacing validation;
- immutable raw + canonical snapshot persistence by SHA-256;
- tamper-detecting snapshot reload;
- replay-readiness CLI that re-verifies the persisted snapshot before alignment;
- strict six-stage R-143 timestamp/evidence certification tied to the exact immutable broker snapshot;
- historical replay dataset schema that rejects extra fields, lookahead and `promotion_allowed=true`.

### R-143 stage timestamp certification

Module: `src/xauusd_v2/replay_stage_certification.py`

Contract: `17_documentation/REPLAY_STAGE_CERTIFICATION_CONTRACT_2026_09_02.md`

A bare `stage_timestamps_certified=true` cannot unlock the production-facing readiness path.

A valid artifact must bind:
- registered replay candidate;
- primary source ID + locator;
- exact verified persisted MT5 snapshot identity + normalized SHA-256;
- broker + broker symbol + timeframe;
- an already successful source-chart alignment against the same snapshot;
- all six canonical R-143 stages in order.

Canonical stages:
1. HCS zone reaction;
2. TFS;
3. LAOL met;
4. True Stop respected;
5. 10m True Stop established;
6. targets and timing.

For each stage the system verifies timezone-aware `occurred_at`, `available_at`, exact `broker_bar_open`, source reference and evidence class. The referenced broker candle must exist and be closed in the exact snapshot. Evidence is conservatively unavailable before that candle closes, and stage times/bar references cannot move backward.

The artifact itself must explicitly deny promotion, strategy verification and performance claims.

`xauusd-v2-replay-readiness` accepts `--stage-certification <path>`. Exact alignment without a valid artifact remains `BLOCKED_STAGE_TIMESTAMPS`. Exact alignment plus a valid six-stage artifact may become `READY_CANDIDATE` only at the replay-admissibility layer.

Current real-data state:
- no real broker XAUUSD MT5 export has been ingested yet;
- no real six-stage stage-certification artifact exists;
- no real broker-aligned historical replay has been certified;
- no performance/backtest claim exists;
- real replay READY count remains **0**.

Current candidates:
- RC-001 remains timestamp-blocked unless source stages can be proven against admissible raw data;
- RC-002 remains CONTEXT_ONLY and cannot be upgraded by a stage artifact;
- RC-003 remains raw-data blocked until real immutable broker alignment, then still requires a valid six-stage artifact.

Runbook:
`17_documentation/MT5_TO_REPLAY_READINESS_RUNBOOK.md`

## Source recovery / provenance state

Recovered primary evidence includes:
- full top-down archive with 188 real chart images, 29 date groups and explicit exclusion of the 2021-11-30 GBPJPY sequence from XAUUSD scope;
- Price Action Reflection source material;
- large Excalidraw notebook with exact embedded/text locators;
- approved primary PDFs mapped to private Library source records;
- corrected physical-page provenance for blind rounds where needed.

Source recovery is provenance infrastructure, not automatic strategy certification.

## Latest regression state

Latest fully verified code regression:
- commit `268cca7bf35a001ec52b95bf23f4e5d307e6fbf1`;
- GitHub Actions run `33675613850`;
- job `100399431199`;
- Python 3.12;
- **656/656 tests PASS**.

The subsequent replay-contract documentation commit `6c542b98183e6ae7acd37f16eed5cdf4f8522b89` also completed GitHub Actions successfully in run `33675694172`.

The GitHub Actions Node deprecation warning is infrastructure noise and is not a strategy/certification blocker.

## What is genuinely waiting on external evidence or user policy

External/provider/data dependencies:
- completion and audit of the real 173-case Agent-06 provider run;
- real broker XAUUSD MT5 history for immutable alignment/replay;
- real six-stage R-143 timestamp evidence for replay candidates;
- broker-quality labelled OHLC fixtures for B-04 calibration;
- any genuinely new primary material that explicitly defines B-01/B-02/B-03/B-05/B-06/B-07 remaining boundaries.

User/governance dependency:
- B-08 production risk policy must be explicitly user-approved; it must not be inferred from conflicting historical 3%/5% source statements.

## Current next work

1. Let the real Agent-06 blind run complete without modifying its local checkout mid-run.
2. On completion, preserve and inspect its six persisted artifacts before pulling newer code.
3. Pull/reinstall the editable package only after the live run finishes, then run the strict post-run auditor against the commit recorded by that run itself.
4. Persist truthful provider/model/comparison metadata only after audit; never persist the API secret and never auto-promote.
5. Obtain and ingest a real MT5 XAUUSD history export, then run immutable snapshot reload and source-chart/replay readiness checks.
6. Build six-stage timestamp artifacts only when primary source evidence and immutable broker bars prove each stage and its availability time.
7. Use broker-aligned data to attack B-04 and historical replay rather than approximating from TradingView.
8. Keep B-01/B-02/B-03/B-05/B-06/B-07 fail-closed at only their narrowed unresolved layers.
9. Define B-08 later as an explicit deterministic production safety policy, separately from strategy truth.
10. Only after certification and replay/data gates are sufficiently resolved, begin serious OOS/walk-forward/cost/slippage performance research.

## Bottom line

The V2 foundation is substantially implemented and heavily regression-tested, but it is deliberately **not strategy-verified and not live-ready**.

Current truth:
- 173-case blind corpus exists;
- real independent-provider validation is executing but not yet verified complete;
- strict post-run Agent-06 audit path exists;
- strict R-143 replay timestamp certification path exists;
- real broker dataset is absent;
- real replay-ready episodes = 0;
- real performance evidence is absent;
- 8 canonical blocker families remain explicit;
- VERIFIED knowledge = 0;
- VERIFIED rules = 0;
- live execution = disabled.