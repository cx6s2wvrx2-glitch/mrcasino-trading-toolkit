# XAUUSD V2 — Current Project Handoff

Updated: 2026-09-02
Branch: `xauusd-v2-foundation`
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
Project root: `xauusd-system-v2/`
Supabase: `mr-casino` (`wuhrhlzabiuudswktcvk`)

## Non-negotiable governance

- Work only inside `xauusd-system-v2/` and strictly necessary XAUUSD-specific workflow files.
- Never touch Flowstate, LUMOS, THRV, gym or unrelated projects.
- V2 is clean-room. Legacy strategy content has no authority unless explicitly re-approved.
- Authority order: approved primary Mr Casino > approved secondary/corroborative evidence > implementation helpers.
- Helpers never define strategy truth.
- Ambiguity = fail closed / NO TRADE / NOT CERTIFIED.
- No LLM has live execution authority.
- Tests, source recovery, helper agreement, blind-model agreement and audit success never auto-promote strategy truth.
- Live execution remains disabled.

## Latest fully tested engineering checkpoint

- commit `beef2f22d61ea4db8c98ad3d3a195a653dbef23e`;
- GitHub Actions run `33682358511`;
- job `100421674594`;
- Python 3.12;
- **690 / 690 tests PASS**.

This checkpoint includes:
- Agent-06 per-case checkpoint/resume and one-command resume coverage;
- successful audit coverage for a completed resumed Agent-06 run;
- MT5 non-persisting `--dry-run` validation;
- strict, default-free production-risk policy contract and CLI;
- quantitative-research hardening requiring immutable strategy/data/parameter/cost identities.

A previous integration run failed after the research hardening because old fixtures still used short/vague references. That failure was investigated and fixed rather than ignored; the full suite then returned to 690/690 PASS.

Later documentation commits may advance the branch head. Verify the live branch and CI before new substantive code changes.

## Supabase truth

Known checked inventory:
- 29 user-approved source rows stored with `status='review'`;
- 16 source rows with non-null `storage_path`;
- 195 knowledge claims;
- 23 V2 rules;
- 215 examples;
- 32 agent runs;
- 14 unresolved disagreement/certification rows (`resolved_by_user=false`);
- VERIFIED knowledge = 0;
- VERIFIED rules = 0.

The 14 unresolved rows consolidate into 8 canonical blocker families. Reconciliation does not resolve database rows or promote anything.

## Canonical blocker families

- B-01 — exact sufficient opposite-direction move/break mechanics for FU.
- B-02 — exact R-54 70% Fibonacci 0/100 anchor/orientation.
- B-03 — universal numeric Strong-FU threshold, if one exists. Timeframe scope itself is already clarified by the user: Strong FU / ATT FU use the same primitive logic on every timeframe.
- B-04 — broker-specific Imbalanced-Candle calibration.
- B-05 — raw OHLC grammar for x3-by-x3.
- B-06 — exact numeric/dynamic Accepted RR rule.
- B-07 — synthetic 11h candle/session anchor.
- B-08 — explicit user-approved production risk policy.

Do not guess any of these closed.

Canonical audits:
- `17_documentation/OPEN_BOUNDARY_RECONCILIATION_2026_09_02.md`
- `17_documentation/PRIMARY_BLOCKER_AUDIT_B01_B04_2026_09_02.md`
- `17_documentation/PRIMARY_BLOCKER_AUDIT_B05_B08_2026_09_02.md`

## User clarification — Strong FU / ATT FU timeframe scope

Explicit user clarification on 2026-09-02:
- Strong FU / ATT FU use the same primitive logic on every timeframe;
- the primitive concept is fractal/timeframe-invariant;
- timeframe changes authority, top-down weighting and downstream application, not the primitive definition;
- a 1m-specific Strong-FU zone construction is a 1m application, not the universal Strong-FU definition.

Canonical record:
`01_sources/USER_CLARIFICATION_FU_TIMEFRAME_SCOPE_2026_09_02.md`.

## Architecture

Canonical agents:
1. Knowledge;
2. Strategy Formalization;
3. XAUUSD Data;
4. Market State / Context;
5. Quant Research / Backtesting;
6. Independent Validation;
7. Deterministic Risk Engine;
8. Continuous Improvement.

All have foundation code. Critical gates consume evidence-bearing reports instead of unrestricted booleans.

## Blind corpus

Persisted R02-R13 corpus = **173 cases**:
R02 20, R03 7, R04 6, R05 5, R06 8, R07 10, R08 10, R09 4, R10 20, R11 30, R12 24, R13 29.

Frozen packet SHA-256:
`e9dd198f166dc7d4d22d1f921b00c4a84c02e36a3d7e5ec734b7703379e5ab4f`

Per-case expected answers/evidence are not exposed to Agent-06. Even 173/173 agreement cannot auto-promote.

## Agent-06 infrastructure

Implemented and tested:
- strict answer-free packet;
- exact PDF/top-down/Excalidraw primary-context resolution;
- private multimodal evidence bundle with pinned hashes;
- readiness before provider calls;
- isolated provider run with no ground-truth loading;
- separate deterministic comparison;
- frozen output hashes before comparison;
- strict post-run audit;
- safe provider-error classification;
- Anthropic structured-output compatibility;
- compact `L001`...`L173` taxonomy transport;
- fail-closed abstention for malformed/out-of-range provider taxonomy codes;
- per-case progress output;
- atomic checkpoint after every completed case;
- resume without re-calling checkpointed cases;
- resume bound to exact run ID, provider, model, Git commit, packet, taxonomy and primary evidence fingerprints;
- one-command resume via `xauusd-v2-agent06-local --resume-run-id <run-id>`;
- post-run auditor explicitly regression-tested against a legitimate completed resumed run;
- `promotion_allowed=false` throughout.

Runbook:
`17_documentation/AGENT06_RUN_AND_RESUME_RUNBOOK_2026_09_02.md`.

### Current real provider run

A real Anthropic `claude-sonnet-5` run is currently executing on the user's Mac from local commit:
`69a55ad9deb5f3e00dba85a576c3f1081587ea4c`.

It reached the isolated 173-case provider stage and an Anthropic child process was observed alive. No completion or failure has yet been reported in this conversation.

That local run predates the new checkpoint/resume code. New remote commits do not affect it. **Do not tell the user to pull, reinstall, restart or interrupt that running process.**

Current certification truth:
- completed 173-case external validation = NO;
- audited completed external validation = NO;
- automatic promotion = NOT ALLOWED.

If the current old run succeeds, inspect/freeze/audit its actual artifacts before making any independent-validation claim. If it fails, wait for the process to exit, then pull the newer branch and start a fresh checkpoint-enabled run.

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
- strict MT5 history parsing/validation;
- explicit broker, broker symbol, source timezone and timeframe provenance;
- `xauusd-v2-ingest-mt5 --dry-run` to validate/fingerprint without persistence;
- source and normalized SHA-256, snapshot identity, coverage, bar count, closed-only and gap diagnostics;
- immutable raw + normalized content-addressed persistence;
- tamper-detecting reload;
- source-chart and parent/child alignment;
- replay candidate registry;
- lookahead-safe `occurred_at` / `available_at` model;
- strict six-stage R-143 timestamp certification against exact closed broker bars;
- replay-readiness CLI and fail-closed artifact contracts.

Operational order:
`original broker export -> dry-run -> inspect -> persist -> align -> six-stage evidence -> replay admissibility`.

Runbook:
`17_documentation/MT5_TO_REPLAY_READINESS_RUNBOOK.md`.

Real-data truth:
- real XAUUSD MT5 export ingested = 0;
- real broker-aligned replay episodes = 0;
- real R-143 six-stage certification artifacts = 0;
- real historical performance/backtest evidence = 0;
- performance claims allowed = false.

## B-08 production risk policy

Engineering capture is ready but policy is not approved.

Strict layer:
- `src/xauusd_v2/risk_policy_io.py`;
- `src/xauusd_v2/risk_policy_cli.py`;
- CLI `xauusd-v2-risk-policy-check`;
- contract `17_documentation/PRODUCTION_RISK_POLICY_CONTRACT_2026_09_02.md`.

A real policy must explicitly provide all four limits:
- maximum per-trade risk fraction;
- maximum daily-loss fraction;
- maximum total-open-risk fraction;
- maximum concurrent positions.

Missing/extra fields are rejected. Strategy authority, live-execution authority and promotion authority must remain false. Historical 3%/5% statements and unit-test values are not production defaults.

B-08 remains UNRESOLVED until the user explicitly approves the actual numeric production-safety values.

## Quantitative research reproducibility

The research gate now requires immutable identities rather than human aliases:
- `strategy_commit_sha` = exact 40-character hexadecimal Git commit;
- `data_snapshot_ref` = `sha256:<64-hex>`;
- `parameter_set_ref` = `sha256:<64-hex>`;
- `cost_model_ref` = `sha256:<64-hex>`.

Research also requires canonical XAUUSD, positive timeframe, confirmed bars only, timezone-aware non-overlapping train/validation/test windows and a locked test set. Contiguous windows are allowed only with an explicit warning about no purge gap.

This prevents vague references such as `latest`, `params-v1` or `costs-v1` from being presented as reproducible inputs.

A hash proves artifact identity, not correctness of its economics. Real broker-quality spread/slippage/commission assumptions have not yet been established, so there is still no credible performance evidence.

Contract:
`17_documentation/QUANT_RESEARCH_REPRODUCIBILITY_CONTRACT_2026_09_02.md`.

## Critical path still remaining

1. Complete and audit one real 173-case Agent-06 run.
2. Persist truthful provider/model/comparison metadata only after audit; never persist API secrets and never auto-promote.
3. Obtain a real broker XAUUSD MT5 export; dry-run validate before immutable persistence.
4. Align primary charts and produce actual six-stage R-143 evidence against broker bars.
5. Resolve B-04 with broker-quality labelled OHLC evidence.
6. Resolve B-01/B-02/B-03/B-05/B-06/B-07 only from explicit primary evidence or explicit user clarification.
7. Explicitly approve and validate B-08 production risk limits.
8. Establish real content-addressed parameter and broker-quality cost artifacts.
9. Run lookahead-safe replay, OOS, walk-forward, spread/slippage/cost research only after upstream gates are sufficiently closed.
10. Run a separate certification/promotion process. VERIFIED remains 0 until that process genuinely occurs.
11. Keep live execution disabled until certification, risk policy, operational safeguards and explicit authorization are complete.

## Bottom line

Software plumbing is now advanced. The dominant remaining work is real external validation, real broker data, unresolved strategy definitions, real research inputs and explicit production policy.

Current truth:
- blind corpus: 173 ready cases;
- future Agent-06 runs: checkpoint/resume ready;
- current pre-checkpoint live Agent-06 run: outcome pending;
- completed/audited real Agent-06 validation: NO;
- MT5/replay infrastructure: ready;
- real MT5 dataset: NO;
- real replay-ready episodes: 0;
- quant reproducibility identity gate: ready;
- real parameter/cost artifacts: not yet established;
- B-08 capture contract: ready, numeric policy unapproved;
- unresolved canonical blocker families: 8;
- VERIFIED knowledge/rules: 0 / 0;
- live trading: DISABLED.
