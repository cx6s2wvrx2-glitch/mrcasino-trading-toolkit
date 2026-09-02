# XAUUSD V2 — Current Project Handoff

Updated: 2026-09-02
Branch: `xauusd-v2-foundation`
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
Project root: `xauusd-system-v2/`
Supabase project: `mr-casino` (`wuhrhlzabiuudswktcvk`)

## Non-negotiable scope

- Work ONLY inside `xauusd-system-v2/` and, when strictly necessary, XAUUSD-specific GitHub workflow files.
- Do not touch gym / Flowstate / LUMOS / THRV / unrelated repos, tables, files or data.
- Clean-room V2: legacy strategy content is invalid unless the user explicitly re-approves a specific item.
- Source authority: approved primary Mr Casino > approved secondary/corroborative material > implementation helpers.
- Helper code never becomes strategy truth by itself.
- Ambiguity = fail closed / NO TRADE / NOT CERTIFIED.
- No LLM has live execution authority.
- Never call source recovery, implementation coverage, blind-model agreement, test success or helper agreement a VERIFIED strategy promotion.
- Never describe independent validation as completed unless an actual external provider/model run reaches completion and its frozen outputs are audited.
- Live execution remains disabled.

## Current GitHub checkpoint

Latest fully verified code checkpoint:
- commit `268cca7bf35a001ec52b95bf23f4e5d307e6fbf1`;
- GitHub Actions run `33675613850`;
- job `100399431199`;
- Python 3.12;
- **656 / 656 tests PASS**.

The next documentation-only commit:
- `6c542b98183e6ae7acd37f16eed5cdf4f8522b89` — R-143 replay stage certification contract;
- GitHub Actions run `33675694172` — SUCCESS.

This handoff refresh is a later documentation commit and may have its own newer CI run. Always verify live branch head and latest XAUUSD V2 CI on continuation.

## Live Supabase snapshot

Known state checked 2026-09-02:
- 29 approved-by-user source records with database `status='review'`;
- 16 source records with non-null `storage_path`;
- 195 knowledge claims;
- 23 V2 rules;
- 215 examples;
- 32 agent runs;
- 14 disagreement/certification rows with `resolved_by_user=false`;
- 0 VERIFIED knowledge;
- 0 VERIFIED rules.

Do not describe the 29 approved source rows as database `ACTIVE`; the factual state is approved-by-user + `review`.

## Canonical blocker set

The 14 open database rows consolidate into 8 blocker families:
- B-01 FU sufficient opposite-direction move/break mechanic;
- B-02 R-54 70% fib 0/100 anchor/orientation;
- B-03 universal numeric Strong-FU threshold, if one exists;
- B-04 broker-specific Imbalanced-Candle calibration;
- B-05 x3-by-x3 raw detector grammar;
- B-06 Accepted RR numeric/dynamic decision rule;
- B-07 synthetic 11h candle anchor/session origin;
- B-08 explicit user-approved production risk policy.

Canonical documentation:
- `17_documentation/OPEN_BOUNDARY_RECONCILIATION_2026_09_02.md`
- `17_documentation/PRIMARY_BLOCKER_AUDIT_B01_B04_2026_09_02.md`
- `17_documentation/PRIMARY_BLOCKER_AUDIT_B05_B08_2026_09_02.md`

No database row was resolved and no rule was promoted by these audits.

## User clarification — Strong FU / ATT FU timeframe scope

Explicit user clarification on 2026-09-02:
- Strong FU / ATT FU use the same primitive logic on every timeframe;
- the primitive concept is fractal/timeframe-invariant;
- timeframe changes authority/context/downstream application, not the definition;
- the Reflection 1m Strong-FU zone rule is a 1m-specific application and not the universal definition of Strong FU.

Canonical record:
`01_sources/USER_CLARIFICATION_FU_TIMEFRAME_SCOPE_2026_09_02.md`.

Do not re-open this timeframe-scope question unless the user explicitly changes the clarification.

## Architecture

Canonical roles:
1. Knowledge Agent;
2. Strategy Formalization Agent;
3. XAUUSD Data Agent;
4. Market State / Context Agent;
5. Quant Research / Backtesting Agent;
6. Independent Validation Agent;
7. Deterministic Risk Engine;
8. Continuous Improvement Agent.

All eight have foundation code. Critical strategy/research/execution gates consume evidence-bearing reports rather than free booleans.

## Blind corpus

Canonical persisted blind corpus R02–R13 = **173 cases**:
- R02 20;
- R03 7;
- R04 6;
- R05 5;
- R06 8;
- R07 10;
- R08 10;
- R09 4;
- R10 20;
- R11 30;
- R12 24;
- R13 29.

Agent-06 receives per case only blind identity/source locator plus the shared batch-wide taxonomy. Expected answers/evidence are excluded. 173/173 agreement cannot auto-promote.

## Agent-06 infrastructure

Implemented:
- strict answer-free packet schema;
- frozen R02–R13 packet builder;
- primary-context evidence resolver;
- PDF-page, top-down, Excalidraw image/text support;
- readiness gate before provider calls;
- isolated blind provider process that does not load ground truth;
- strict prediction loader;
- separate post-run comparator;
- packet fingerprint, vector-ID, locator and taxonomy verification;
- provider-neutral external command boundary;
- direct Anthropic Messages API multimodal wrapper;
- verified image MIME/size/SHA checks;
- provider-compatible structured-output schema;
- local confidence validation;
- safe allowlisted provider error codes without response-body/API-key leakage;
- frozen output hashes before comparison;
- one-command secure local orchestration outside the public repo;
- strict post-run artifact auditor;
- `promotion_allowed=false` throughout.

Important provider fixes already landed:
1. `python -m` provider-command flags are preserved with argparse remainder handling;
2. unsupported numeric `minimum`/`maximum` constraints were removed from the Anthropic raw JSON schema while 0..1 validation remains local;
3. provider errors are reduced to safe codes such as HTTP/auth/billing/max-token classes;
4. Agent-06 response verbosity is bounded to prevent unnecessary output truncation;
5. Anthropic max output tokens are configurable through `XAUUSD_AGENT06_ANTHROPIC_MAX_TOKENS`.

## Real Agent-06 run — current live state

A real user-controlled Anthropic run has been started locally with model `claude-sonnet-5`.

Earlier attempts failed closed and exposed implementation issues before a full batch completed:
- CLI provider-command parsing;
- Anthropic structured-output schema incompatibility;
- output truncation at the previous 2048-token cap.

Those issues were corrected and regression-tested.

The current rerun uses the bounded validator prompt and a larger local provider output cap (`XAUUSD_AGENT06_ANTHROPIC_MAX_TOKENS=8192`).

**Current truth:** the rerun is executing, but it has not yet been verified complete. Do not claim external independent validation until the terminal reaches `LOCAL_AGENT06_PIPELINE_COMPLETE` and the frozen run artifacts are inspected/audited.

While this local run is executing, do not tell the user to `git pull` in that same running checkout/process. GitHub can continue to advance remotely; pull only after the local run is finished.

Expected successful stages:
1. build frozen answer-free packet;
2. execute 173-case isolated blind provider run;
3. freeze/hash blind outputs;
4. deterministic post-run ground-truth comparison.

Expected run root:
`~/.xauusd-agent06/runs/<run-id>/`.

Required artifacts after success:
- `agent06_local_pipeline_summary.json`;
- `agent06_frozen_output_hashes.json`;
- `agent06_blind_predictions.json`;
- `agent06_runtime_manifest.json`;
- `agent06_readiness.json`;
- `agent06_comparison.json`.

## Agent-06 post-run audit

New production-independent audit CLI:
`xauusd-v2-agent06-audit`.

Relevant file:
`src/xauusd_v2/agent06_audit_cli.py`.

The auditor is deliberately **post-run only**. It does not participate in the blind provider process and cannot expose ground truth to the model.

It requires all six persisted run artifacts and verifies, fail-closed:
- local pipeline status is complete;
- run ID and optional exact expected Git commit;
- provider/model metadata;
- pinned private bundle SHA-256;
- pinned primary-context manifest SHA-256;
- actual predictions/runtime bytes against frozen hashes;
- output freeze occurred before ground-truth comparison;
- API key was not written to disk;
- blind process did not load ground truth;
- prediction/runtime/readiness/comparison packet identities agree;
- exactly the expected case count;
- runtime vector IDs, source locators, labels and abstentions match frozen predictions;
- runtime abstention count matches the frozen prediction batch;
- runtime image-case count matches per-case evidence metadata and readiness;
- text evidence fingerprints are valid SHA-256 digests when present;
- image evidence metadata has valid MIME, SHA-256 and positive byte size;
- path-like local evidence fields are rejected from the runtime manifest;
- every runtime case has a persisted text or image evidence fingerprint;
- readiness was `READY_TO_RUN` and resolved all cases;
- comparison occurred after the blind run;
- AGREE/DISAGREE/AMBIGUOUS counts sum correctly;
- `promotion_allowed=false` throughout.

Even `AUDIT_PASS` means the external run is internally coherent and auditable. It does not auto-promote strategy knowledge/rules.

After the current local run has fully finished, first preserve/inspect its outputs. Only then pull the newer branch. Because the audit console entry point was added after the current local run started, safest local refresh after completion is:

```bash
python3 -m pip install -e ./xauusd-system-v2
```

Then audit the completed run with the **repo commit recorded inside that run's artifacts**, not the newer GitHub branch head:

```bash
xauusd-v2-agent06-audit \
  --run-root "$HOME/.xauusd-agent06/runs/<run-id>" \
  --provider anthropic \
  --model claude-sonnet-5 \
  --case-count 173 \
  --expected-repo-commit <commit-recorded-inside-run>
```

Do not run these refresh/audit steps until the currently executing Agent-06 process is finished.

## Private Agent-06 evidence bundle

Keep outside the public repository.

Canonical private bundle:
- Library path: `/XAUUSD V2/Agent06/xauusd_agent06_primary_bundle_2026_09_02.zip`;
- size: 17,623,961 bytes;
- ZIP SHA-256: `6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf`;
- manifest SHA-256: `e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37`;
- 477 resolver entries;
- 219 unique image assets;
- 1 text asset;
- 222 ZIP members.

Never commit proprietary source binaries to public GitHub.

## Primary evidence recovery

Recovered exact originals include:
- `top down analysis (1).zip`;
- `PRICE ACTION REFLECTION.zip`;
- `casinonotes.excalidraw`;
- approved primary PDFs mapped to private Library records.

Top-down scope:
- 188 real chart images;
- 188 unique basenames;
- 29 date groups;
- 28 XAUUSD sequences / 186 XAUUSD images;
- exact 2021-11-30 GBPJPY sequence excluded from XAUUSD scope.

Excalidraw:
- 2518 elements;
- 679 embedded files;
- canonical R02 image/text locators resolved fail-closed.

Corrected physical-page provenance for R03/R04/R05 is pinned by tests.

## MT5 / historical replay state

Implemented:
- strict MT5 history parsing;
- explicit source timezone — never inferred;
- broker/symbol/timeframe/OHLC/order/spacing validation;
- provisional final-bar preservation;
- raw-source and canonical SHA-256;
- immutable content-addressed snapshot store;
- tamper-detecting snapshot reload;
- source-chart alignment;
- parent/child bar alignment;
- replay-candidate registry;
- lookahead-safe replay sessions with `occurred_at` / `available_at`;
- historical replay gate;
- replay-readiness CLI;
- strict six-stage R-143 timestamp/evidence certification bound to immutable broker data;
- replay dataset schema rejects hidden extra fields and `promotion_allowed=true`.

Relevant CLIs:
- `xauusd-v2-ingest-mt5`;
- `xauusd-v2-replay-readiness`.

Runbooks/contracts:
- `17_documentation/MT5_TO_REPLAY_READINESS_RUNBOOK.md`;
- `17_documentation/REPLAY_STAGE_CERTIFICATION_CONTRACT_2026_09_02.md`.

### R-143 stage timestamp certification

New module:
`src/xauusd_v2/replay_stage_certification.py`.

A bare `stage_timestamps_certified=true` is not an admissible production-facing unlock.

A valid stage artifact must be bound to:
- one registered replay candidate;
- exact primary source ID and locator;
- one verified persisted MT5 snapshot;
- exact snapshot identity + normalized SHA-256;
- broker name and broker symbol;
- canonical XAUUSD;
- exact timeframe;
- already successful source-chart alignment against the same snapshot;
- all six R-143 stages in canonical order.

Canonical six-stage order:
1. `HCS_ZONE_REACTION`;
2. `TFS`;
3. `LAOL_MET`;
4. `TRUE_STOP_RESPECTED`;
5. `TEN_MIN_TRUE_STOP_ESTABLISHED`;
6. `TARGETS_AND_TIMING`.

Each stage must identify:
- `occurred_at`;
- `available_at`;
- exact `broker_bar_open`;
- non-empty source reference;
- fixed evidence class `primary_source_label_aligned_to_closed_broker_bar`.

The loader reopens the exact canonical snapshot bytes and verifies every referenced broker bar is real and closed. Evidence is conservatively unavailable before that bar closes. Stage occurrence, availability and referenced-bar order cannot move backward.

The artifact itself must keep:
- `promotion_allowed=false`;
- `strategy_verified=false`;
- `performance_claim_allowed=false`.

The replay-readiness CLI now accepts:

```text
--stage-certification /path/to/r143-stage-certification.json
```

Exact broker/chart alignment alone remains stage-timestamp blocked. Exact alignment + a valid six-stage artifact may reach `READY_CANDIDATE` / `replay_ready=true` at the replay admissibility layer only. That still does not mean strategy verification or performance evidence.

Real-data truth:
- no real broker XAUUSD MT5 export has been ingested yet;
- no real six-stage R-143 certification artifact exists yet;
- real replay READY count = 0;
- no real backtest/performance data exists;
- no performance claim is allowed.

Current candidate implications:
- `RC-001` remains timestamp blocked unless its source stages can be proven against admissible raw data;
- `RC-002` is `CONTEXT_ONLY` and cannot be upgraded by a stage artifact;
- `RC-003` remains raw-data blocked until real immutable broker alignment exists, and then still requires a valid six-stage artifact.

## B-05 to B-08 narrowed state

B-05:
- applied x3-by-x3 relational role is source-backed;
- raw OHLC grammar remains unresolved.

B-06:
- Accepted RR is source-confirmed in advanced x3 entry context;
- no threshold/formula is defined.

B-07:
- 11h strategic context and lower-TF confirmation relationship are source-backed;
- synthetic bar anchor/session origin remains unresolved.

B-08:
- historical 3% and conditional up-to-5% statements remain source evidence;
- production account risk is a separate deterministic user-approved safety policy;
- do not select 3% or 5% automatically.

## Immediate next actions

1. Let the current real Agent-06 run complete without modifying its local process or pulling the newer branch.
2. When it completes, inspect/preserve the six actual run artifacts and terminal result.
3. Only after completion, pull the newer GitHub state and refresh the editable package installation so the new `xauusd-v2-agent06-audit` CLI is available.
4. Audit the completed Agent-06 run against the commit recorded by that run itself; do not substitute the latest branch head.
5. Persist only truthful provider/model/run/comparison metadata after the audit; never persist the API secret and never auto-promote.
6. Obtain a real XAUUSD MT5 history export from the intended broker and ingest it through the immutable snapshot path.
7. Use broker-aligned data for B-04 calibration and historical replay; do not approximate from TradingView.
8. Build real R-143 stage timestamp artifacts only where primary evidence + immutable broker bars prove every stage and availability time.
9. Keep B-01/B-02/B-03/B-05/B-06/B-07 fail-closed only at their narrowed remaining unknowns.
10. Define B-08 later as explicit production safety policy, separately from strategy truth.
11. Only after certification/replay/data gates are sufficiently resolved, begin serious OOS/walk-forward/cost/slippage performance research.

## Truthful current status

- V2 foundation: substantially implemented;
- blind corpus: 173 cases;
- latest verified code regression: 656/656 PASS;
- real external Agent-06 run: executing, not yet verified complete;
- post-run audit path: implemented and regression-tested;
- real broker MT5 dataset: absent;
- real replay-ready episodes: 0;
- real performance evidence: absent;
- canonical blocker families: 8;
- VERIFIED knowledge: 0;
- VERIFIED rules: 0;
- live execution: disabled.

## Fresh-chat continuation instruction

`Συνέχισε το XAUUSD V2 από xauusd-system-v2/17_documentation/CURRENT_PROJECT_HANDOFF.md στο branch xauusd-v2-foundation. Διάβασε πρώτα το handoff, έλεγξε live GitHub/Supabase και το τελευταίο CI, και συνέχισε από το πραγματικό current state. Μην αγγίξεις τίποτα εκτός του XAUUSD project.`

In a fresh chat, fetch this file first, then verify live branch head, Supabase snapshot and latest CI before modifying anything.