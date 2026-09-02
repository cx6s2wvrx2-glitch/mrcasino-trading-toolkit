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

Latest fully exercised code checkpoint before the subsequent documentation-only refreshes:
- commit `0bd5a662e392771e9ca40f3beacde38a2dbf1604`;
- GitHub Actions run `33681442520`;
- job `100418712032`;
- Python 3.12;
- full regression suite **685 / 685 PASS**.

The later MT5 runbook documentation commit `08b0429fd4a568517ff56d9a9b79affd5ec748e7` also completed GitHub Actions successfully in run `33681531038`.

The branch may advance through later documentation commits. Always verify the live head and latest XAUUSD V2 CI before substantive continuation.

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

B-08 engineering contract:
- `17_documentation/PRODUCTION_RISK_POLICY_CONTRACT_2026_09_02.md`

The B-08 software contract is ready, but the blocker remains unresolved because no real production numeric limits have yet been explicitly user-approved.

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
- compact taxonomy transport using provider codes `L001` ... `L173` mapped deterministically to the frozen taxonomy;
- malformed/out-of-range provider taxonomy code becomes a fail-closed per-case abstention instead of crashing the whole batch;
- per-case progress output for checkpoint-enabled runs;
- atomic private checkpoint after every successful case;
- safe resume without re-calling already checkpointed cases;
- resume bound to exact run ID, provider, model, Git commit, packet SHA, taxonomy SHA and primary text/image fingerprints;
- one-command resume through `xauusd-v2-agent06-local --resume-run-id <run-id>`;
- full-orchestrator regression verifies that resume reuses the exact run and passes `--resume-existing` rather than creating a second run;
- all persisted blind/checkpoint/final artifacts keep `promotion_allowed=false`.

Run/resume contract:
`17_documentation/AGENT06_RUN_AND_RESUME_RUNBOOK_2026_09_02.md`.

### Current live-provider truth

A real local Anthropic `claude-sonnet-5` run is currently executing on the user's Mac from the older local commit:
`69a55ad9deb5f3e00dba85a576c3f1081587ea4c`.

It reached the isolated 173-case provider stage and its Anthropic child process was observed alive. It has not yet been reported complete or failed in the conversation.

That currently executing run predates the new per-case checkpoint/resume contract, so the newer remote commits do not affect it and it must **not** be interrupted or updated mid-run. Do not ask the user to `git pull` until that process exits.

Earlier real attempts exposed and led to fixes for provider command parsing, structured-output schema compatibility and other provider-boundary issues. None of those failed attempts counts as completed external validation.

**Current certification truth: no end-to-end real external Agent-06 validation has yet been completed and audited.**

A completed real run must reach `LOCAL_AGENT06_PIPELINE_COMPLETE` and then pass the separate `xauusd-v2-agent06-audit` artifact audit before any independent-validation completion claim is made.

If the current pre-checkpoint run fails, it cannot be resumed. After it exits, pull the newer checkpoint-enabled branch and start a fresh run; any later interruption can then safely resume from the last completed case on the same commit.

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
- new `--dry-run` mode that validates and fingerprints an export without persisting anything;
- dry-run returns source/normalized hashes, snapshot identity, coverage timestamps, bar count, closed-only state and gap diagnostics;
- persist mode requires an explicit store root;
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

Canonical operational order is now:
`original broker export -> dry-run validation -> inspect diagnostics -> immutable persist -> source/chart alignment -> six-stage R-143 evidence -> replay admissibility`.

Runbook:
`17_documentation/MT5_TO_REPLAY_READINESS_RUNBOOK.md`.

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

## B-08 production risk policy engineering state

The deterministic Risk Engine still contains no production risk defaults.

New strict policy layer:
- `src/xauusd_v2/risk_policy_io.py`;
- `src/xauusd_v2/risk_policy_cli.py`;
- CLI `xauusd-v2-risk-policy-check`.

A policy document must explicitly provide all four limits:
- maximum per-trade risk fraction;
- maximum daily-loss fraction;
- maximum total-open-risk fraction;
- maximum concurrent positions.

The contract rejects missing limits, extra hidden fields and any attempt to set strategy authority, live execution authority or promotion authority to true.

No historical 3%/5% statement and no test-fixture number is treated as production policy. Numeric B-08 policy remains pending explicit user approval.

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
- deterministic risk engine foundation plus strict no-default policy contract;
- immutable MT5 data layer plus non-persisting dry-run validation;
- replay anti-lookahead infrastructure;
- 173-case blind validation infrastructure;
- strict independent-validation audit path;
- safe per-case checkpoint/resume and one-command local resume for future expensive provider runs.

Implementation coverage is not strategy verification.

## Critical path still remaining

1. Complete and audit one real 173-case Agent-06 Anthropic run.
2. Persist truthful provider/model/comparison metadata only after artifact verification; never persist the API secret and never auto-promote.
3. Obtain a real broker XAUUSD MT5 export, first dry-run validate it, then persist it immutably.
4. Use real broker data to align primary charts and certify R-143 stage timestamps, creating actual replay-admissible candidates.
5. Resolve B-04 with broker-quality labelled OHLC evidence, not TradingView approximation.
6. Resolve B-01/B-02/B-03/B-05/B-06/B-07 only from explicit evidence or user clarification, never invention.
7. Obtain explicit user-approved numeric values for B-08 through the strict production-risk policy contract.
8. Run historical replay / OOS / walk-forward / cost-and-slippage research only after strategy/data gates are sufficiently closed.
9. Run a separate certification/promotion process after evidence and performance research. VERIFIED remains 0 until that process genuinely occurs.
10. Keep live execution disabled until certification, risk policy, operational safeguards and explicit authorization are complete.

## Current bottom line

The project is no longer blocked mainly by missing software plumbing. The main remaining work is now real external evidence, broker data, unresolved strategy definitions and explicit production policy.

Current truth:
- 173-case blind corpus: ready;
- Agent-06 provider infrastructure: ready with one-command checkpoint/resume for future runs;
- currently executing legacy/pre-checkpoint Agent-06 run: outcome pending;
- completed/audited real Agent-06 run: **NO**;
- MT5/replay infrastructure including dry-run: ready;
- real MT5 dataset: **NO**;
- real replay-ready episodes: **0**;
- B-08 policy contract: ready, numeric user policy not approved;
- canonical unresolved blocker families: **8**;
- VERIFIED knowledge/rules: **0 / 0**;
- live trading: **DISABLED**.
