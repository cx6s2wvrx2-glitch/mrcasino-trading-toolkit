# XAUUSD V2 — Current Project Handoff

Updated: 2026-09-02
Branch: `xauusd-v2-foundation`
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
Project root: `xauusd-system-v2/`
Supabase project: `mr-casino` (`wuhrhlzabiuudswktcvk`)

## Non-negotiable scope and governance

- Work only inside `xauusd-system-v2/` and strictly necessary XAUUSD-specific workflow files.
- Never touch Flowstate, LUMOS, THRV, gym or unrelated projects.
- V2 is clean-room: legacy strategy content has no authority unless explicitly re-approved.
- Authority order: approved primary Mr Casino > approved secondary/corroborative evidence > implementation helpers.
- Helpers never define strategy truth.
- Ambiguity = fail closed / NO TRADE / NOT CERTIFIED.
- No LLM has live execution authority.
- No blind result, test pass, helper agreement or source recovery auto-promotes strategy knowledge/rules.
- Live execution remains disabled.

## Current engineering checkpoint

Latest code checkpoint before this documentation refresh:
- commit `c0ba4ad7a4c0deb59e898be0a3eb1f1cfbf2878c`;
- GitHub Actions run `33679713826`;
- full regression suite **669 / 669 PASS**.

The branch may advance through documentation-only commits after that checkpoint. Always verify the live head and latest XAUUSD V2 CI before substantive continuation.

## Supabase truth

Known checked state:
- 29 user-approved source rows stored with `status='review'`;
- 16 source rows with non-null `storage_path`;
- 195 knowledge claims;
- 23 V2 rules;
- 215 examples;
- 32 agent runs;
- 14 unresolved disagreement/certification rows (`resolved_by_user=false`);
- VERIFIED knowledge = 0;
- VERIFIED rules = 0.

The 14 rows consolidate into 8 canonical blocker families. Reconciliation does not resolve database rows and does not promote anything.

## Canonical blocker families

- **B-01** — exact sufficient opposite-direction move/break mechanics for FU.
- **B-02** — R-54 70% Fibonacci exact 0/100 anchor/orientation.
- **B-03** — universal numeric Strong-FU threshold, if such a threshold exists. The timeframe-scope question itself is closed by user clarification: Strong FU / ATT FU use the same primitive logic on every timeframe.
- **B-04** — broker-specific Imbalanced-Candle calibration.
- **B-05** — raw OHLC grammar for x3-by-x3.
- **B-06** — exact numeric/dynamic Accepted RR rule.
- **B-07** — synthetic 11h candle/session anchor.
- **B-08** — explicit user-approved production risk policy.

Detailed audits:
- `17_documentation/PRIMARY_BLOCKER_AUDIT_B01_B04_2026_09_02.md`
- `17_documentation/PRIMARY_BLOCKER_AUDIT_B05_B08_2026_09_02.md`
- `17_documentation/OPEN_BOUNDARY_RECONCILIATION_2026_09_02.md`

## User clarification — Strong FU / ATT FU

Explicit user clarification on 2026-09-02:
- Strong FU / ATT FU use the same primitive logic on every timeframe;
- the concept is fractal/timeframe-invariant;
- timeframe changes authority, top-down weighting and downstream application, not the primitive definition;
- a 1m-specific Strong-FU zone rule is an application, not the universal Strong-FU definition.

Canonical record:
`01_sources/USER_CLARIFICATION_FU_TIMEFRAME_SCOPE_2026_09_02.md`.

## Agent architecture

Canonical roles:
1. Knowledge Agent;
2. Strategy Formalization Agent;
3. XAUUSD Data Agent;
4. Market State / Context Agent;
5. Quant Research / Backtesting Agent;
6. Independent Validation Agent;
7. Deterministic Risk Engine;
8. Continuous Improvement Agent.

All have foundation code. Critical gates consume evidence-bearing reports instead of unrestricted booleans.

## Blind corpus

Persisted R02-R13 blind corpus = **173 cases**:
R02 20, R03 7, R04 6, R05 5, R06 8, R07 10, R08 10, R09 4, R10 20, R11 30, R12 24, R13 29.

Frozen packet SHA-256:
`e9dd198f166dc7d4d22d1f921b00c4a84c02e36a3d7e5ec734b7703379e5ab4f`

Per-case expected answers/evidence are not exposed to Agent-06. Even 173/173 agreement cannot auto-promote.

## Agent-06 — current infrastructure

Implemented and regression-tested:
- strict answer-free packet schema;
- exact primary-context resolver for PDFs/top-down/Excalidraw;
- private multimodal bundle with pinned hashes;
- readiness gate before provider calls;
- isolated blind provider process with no ground-truth loading;
- separate deterministic post-run comparison;
- frozen output hashes before comparison;
- strict post-run auditor;
- safe provider error classification;
- Anthropic structured-output compatibility;
- default Anthropic output budget 16384 tokens;
- compact taxonomy transport that does not place all 173 labels in the JSON-schema grammar;
- explicit provider codes `L001` ... `L173` mapped deterministically to the frozen taxonomy;
- malformed/out-of-range provider taxonomy code becomes a fail-closed per-case abstention instead of crashing the whole batch;
- per-case progress output;
- atomic private checkpoint after every successful case;
- safe resume of interrupted runs without re-calling already checkpointed cases;
- resume is bound to the exact run ID, provider, model, Git commit, packet SHA, taxonomy SHA and primary text/image fingerprints;
- all persisted blind/checkpoint/final artifacts keep `promotion_allowed=false`.

Run/resume contract:
`17_documentation/AGENT06_RUN_AND_RESUME_RUNBOOK_2026_09_02.md`.

### Important current live-provider truth

Several real local Anthropic attempts reached `claude-sonnet-5`, but all posted attempts so far failed before completing all 173 cases. They exposed and led to fixes for:
- provider command parsing;
- unsupported structured-output schema constraints;
- max-token truncation;
- invented/concatenated labels;
- over-complex 173-label enum schema;
- out-of-range numeric taxonomy index.

**No end-to-end real external Agent-06 validation has yet been completed or audited.**

The next fresh live run after pulling the checkpoint-enabled code will preserve every successfully completed case. Older failed runs cannot be resumed because they predate the checkpoint contract.

A completed real run must reach:
`LOCAL_AGENT06_PIPELINE_COMPLETE`

and then pass the separate `xauusd-v2-agent06-audit` artifact audit before any independent-validation completion claim is made.

## Agent-06 private evidence identity

Keep outside public GitHub.

- bundle SHA-256: `6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf`;
- manifest SHA-256: `e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37`;
- 477 resolver entries;
- 219 unique image assets;
- 1 text asset;
- 222 ZIP members.

Never commit proprietary source binaries.

## MT5 / replay infrastructure

Implemented:
- strict MT5 history parsing and ingestion;
- explicit source timezone, never inferred;
- broker/symbol/timeframe/OHLC/order/spacing validation;
- immutable raw + normalized content-addressed snapshots;
- tamper-detecting snapshot reload;
- source-chart alignment;
- parent/child bar alignment;
- replay candidate registry;
- lookahead-safe `occurred_at` / `available_at` replay model;
- historical replay gate;
- `xauusd-v2-replay-readiness`;
- strict R-143 six-stage timestamp certification bound to the exact verified broker snapshot;
- replay loaders reject extra hidden fields and `promotion_allowed=true`.

R-143 six-stage order:
1. HCS zone reaction;
2. TFS;
3. LAOL met;
4. True Stop respected;
5. 10m True Stop established;
6. targets and timing.

A replay episode may become `READY_CANDIDATE` only when exact chart/broker alignment and valid six-stage evidence are both present. This never means strategy verification or performance proof.

### Real-data truth

- real XAUUSD MT5 broker export ingested = 0;
- real immutable broker-aligned replay episodes = 0;
- real six-stage R-143 certification artifacts = 0;
- real historical performance/backtest evidence = 0;
- performance claims allowed = false.

## What is already substantially finished

Engineering/foundation work is largely in place for:
- source provenance and private evidence resolution;
- FU/ATT FU semantics and observables;
- intrabar evidence;
- FU quality/retest boundaries;
- liquidity/doji semantics;
- zones/HCS/negation/x3/TFS/True Stop candidate layers;
- R-143 ordered sequence and R-145 LTF execution candidate;
- targets/LAOL boundaries;
- deterministic risk engine foundation;
- immutable MT5 data layer;
- replay anti-lookahead infrastructure;
- 173-case blind validation infrastructure;
- strict independent-validation audit path;
- safe checkpoint/resume for expensive live provider runs.

Implementation coverage is not strategy verification.

## Critical path still remaining

1. **Complete one real 173-case Agent-06 Anthropic run** on one fixed tested commit.
2. **Audit its frozen artifacts** and record truthful agree/disagree/ambiguous/abstention counts; no promotion.
3. **Persist truthful run metadata to Supabase** only after artifact verification; never persist the API secret.
4. **Obtain real broker XAUUSD MT5 history** and ingest it into immutable snapshots.
5. **Use real broker data to align primary charts and certify R-143 stage timestamps**, then create actual replay-ready candidates.
6. **Resolve B-04 with broker-quality labelled OHLC evidence**, not TradingView approximation.
7. **Resolve B-01/B-02/B-03/B-05/B-06/B-07 only from explicit evidence or user clarification**, never invention.
8. **Define B-08 production risk policy with explicit user approval** as a deterministic safety policy separate from strategy truth.
9. **Run historical replay / OOS / walk-forward / cost-and-slippage research** only after strategy/data gates are sufficiently closed.
10. **Separate certification/promotion process** after evidence and performance research. VERIFIED remains 0 until that process genuinely occurs.
11. **Live execution stays disabled** until certification, risk policy, operational safeguards and explicit authorization are complete.

## Current bottom line

The project is no longer blocked mainly by missing software plumbing. The main remaining work is now **real external evidence, broker data, unresolved strategy definitions and explicit production policy**.

Current truth:
- 173-case blind corpus: ready;
- Agent-06 provider infrastructure: ready with checkpoint/resume;
- completed/audited real Agent-06 run: **NO**;
- MT5/replay infrastructure: ready;
- real MT5 dataset: **NO**;
- real replay-ready episodes: **0**;
- canonical unresolved blocker families: **8**;
- VERIFIED knowledge/rules: **0 / 0**;
- live trading: **DISABLED**.
