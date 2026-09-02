# XAUUSD V2 — System Readiness Snapshot

Date: 2026-09-02
Status: FOUNDATION ADVANCED / NOT STRATEGY-VERIFIED / NOT LIVE-READY

## Governance

- Clean-room V2 only.
- Approved primary Mr Casino evidence outranks secondary/corroborative material and implementation helpers.
- Helpers never define strategy truth.
- Ambiguity = NOT CERTIFIED / NO TRADE.
- No LLM has live execution authority.
- Tests, source recovery, helper agreement, blind-model agreement and audit success do not auto-promote rules or knowledge.
- Live execution remains disabled.

## Latest fully tested engineering checkpoint

- commit `beef2f22d61ea4db8c98ad3d3a195a653dbef23e`;
- GitHub Actions run `33682358511`;
- job `100421674594`;
- Python 3.12;
- **690 / 690 tests PASS**.

The checkpoint includes:
- Agent-06 one-command checkpoint/resume regression coverage;
- audit compatibility with completed resumed runs;
- MT5 non-persisting `--dry-run` validation;
- strict default-free production-risk policy contract/CLI;
- quantitative research requiring immutable commit/data/parameter/cost identities.

One preceding integration run failed because old research-runtime fixtures still used legacy short/vague identifiers. The failure was inspected and corrected, after which the complete suite returned to 690/690 PASS.

Later documentation commits may advance the branch head without changing this tested code checkpoint.

## Supabase inventory

Known checked state:
- 29 user-approved sources stored with `status='review'`;
- 16 source rows with non-null storage path;
- 195 knowledge claims;
- 23 V2 rules;
- 215 examples;
- 32 agent runs;
- 14 unresolved disagreement/certification rows;
- VERIFIED knowledge = 0;
- VERIFIED rules = 0.

The 14 rows consolidate into 8 canonical blocker families without mutating `resolved_by_user`.

## Open blocker families

1. B-01 — FU sufficient opposite-direction move/break mechanics.
2. B-02 — exact R-54 70% Fibonacci anchor/orientation.
3. B-03 — universal numeric Strong-FU threshold, if one exists. Timeframe scope itself is already clarified by the user as timeframe-invariant primitive logic.
4. B-04 — broker-specific Imbalanced-Candle calibration.
5. B-05 — raw x3-by-x3 OHLC grammar.
6. B-06 — exact Accepted RR numeric/dynamic rule.
7. B-07 — synthetic 11h candle/session anchor.
8. B-08 — explicit user-approved deterministic production risk policy.

No blocker is to be guessed closed.

## Architecture readiness

All 8 canonical agent roles have foundation code:
Knowledge, Strategy Formalization, XAUUSD Data, Market State/Context, Quant Research/Backtesting, Independent Validation, Deterministic Risk, Continuous Improvement.

Critical downstream gates consume evidence-bearing reports. Blocked upstream state cannot be relabelled ready downstream.

## Strategy/component implementation coverage

Substantial candidate/fail-closed implementations exist for FU/ATT FU, intrabar evidence, FU quality/retests, liquidity/doji, zones, HCS, negation/x3, TFS, True Stop, R-143, R-145, LAOL/targets, Accepted RR boundary, 11h boundary, deterministic risk, broker precision and immutable data snapshots.

Implementation coverage is not VERIFIED strategy truth.

## Blind validation

Persisted R02-R13 blind corpus = **173 cases**.

Frozen packet SHA-256:
`e9dd198f166dc7d4d22d1f921b00c4a84c02e36a3d7e5ec734b7703379e5ab4f`.

Agent-06 receives no per-case expected answer/evidence. Even perfect agreement remains non-promotional.

### Agent-06 infrastructure

Ready for future runs:
- answer-free packet;
- exact multimodal evidence resolver;
- readiness gate;
- isolated provider process with no ground truth;
- separate comparison;
- frozen hashes;
- strict post-run audit;
- Anthropic-compatible structured outputs and compact `L001`...`L173` taxonomy;
- safe provider-error handling;
- per-case progress and atomic checkpoint;
- exact same-commit resume without re-calling completed cases;
- one-command `--resume-run-id` path;
- explicit regression that a legitimate completed resumed run passes final artifact audit;
- promotion disabled throughout.

Runbook:
`17_documentation/AGENT06_RUN_AND_RESUME_RUNBOOK_2026_09_02.md`.

### Current real provider status

A real `claude-sonnet-5` run is currently executing on the user's Mac from pre-checkpoint commit:
`69a55ad9deb5f3e00dba85a576c3f1081587ea4c`.

It reached the isolated 173-case provider stage and has not yet been reported complete or failed in the conversation.

Do not update, pull, reinstall, restart or interrupt that local process. Newer checkpoint/resume code does not retroactively apply to it.

Current truth:
- completed 173-case external validation = NO;
- audited completed external validation = NO;
- external-validation auto-promotion = NOT ALLOWED.

## Private Agent-06 evidence

- bundle SHA-256: `6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf`;
- manifest SHA-256: `e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37`;
- 477 resolver entries;
- 219 unique images;
- 1 text asset.

Private source binaries remain outside public GitHub.

## MT5 / historical replay readiness

Infrastructure:
- strict MT5 parsing/validation;
- explicit broker/symbol/timezone/timeframe provenance;
- `--dry-run` validation/fingerprinting without persistence;
- source and normalized hashes, snapshot identity, coverage/bar/gap diagnostics;
- immutable raw + normalized snapshots;
- tamper-detecting reload;
- source-chart and parent/child alignment;
- replay candidate registry;
- lookahead-safe evidence timing;
- strict six-stage R-143 evidence certification against closed broker bars;
- replay-readiness CLI.

Operational order:
`broker export -> dry-run -> inspect -> persist -> align -> certify R-143 stages -> replay admissibility`.

Runbook:
`17_documentation/MT5_TO_REPLAY_READINESS_RUNBOOK.md`.

Real-data state:
- real broker XAUUSD export ingested = 0;
- real broker-aligned replay episodes = 0;
- real six-stage R-143 artifacts = 0;
- real historical performance/backtest evidence = 0;
- performance claims allowed = false.

## Production risk policy — B-08

Engineering capture is ready and contains no production defaults:
- `risk_policy_io.py`;
- `risk_policy_cli.py`;
- `xauusd-v2-risk-policy-check`;
- `17_documentation/PRODUCTION_RISK_POLICY_CONTRACT_2026_09_02.md`.

A real policy must explicitly provide per-trade max risk, daily-loss max, total-open-risk max, concurrent-position max and non-empty approval provenance. Missing/extra fields are rejected. Strategy authority, live authority and promotion authority must remain false.

Historical 3%/5% statements and test values are not production defaults.

B-08 policy = NOT CONFIGURED until explicit user numeric approval.

## Quantitative research reproducibility

Research identity is now fail-closed and content-addressed:
- strategy implementation = exact 40-character Git SHA;
- market data = `sha256:<64-hex>` snapshot;
- parameter set = `sha256:<64-hex>` artifact;
- execution-cost model = `sha256:<64-hex>` artifact.

Aliases such as `latest`, short Git SHAs, `params-v1` or `costs-v1` are not reproducible inputs.

Other required research boundaries:
- canonical XAUUSD only;
- positive timeframe;
- confirmed bars only;
- timezone-aware train/validation/test windows;
- no train/validation or validation/test overlap;
- test set locked until final evaluation;
- contiguous windows produce an explicit no-purge-gap warning.

Contract:
`17_documentation/QUANT_RESEARCH_REPRODUCIBILITY_CONTRACT_2026_09_02.md`.

This identity hardening does not create real cost assumptions. No broker-quality spread/slippage/commission artifact or real production parameter artifact is yet established, so performance research remains externally/data gated.

## Remaining critical path

1. Complete and audit one real 173-case Anthropic Agent-06 run.
2. Persist truthful validation metadata after artifact audit, without secrets or promotion.
3. Obtain a real XAUUSD MT5 broker export; dry-run before immutable persistence.
4. Align primary charts and build real six-stage R-143 evidence against broker bars.
5. Use real broker OHLC evidence to attack B-04 and other raw-geometry boundaries where appropriate.
6. Resolve B-01/B-02/B-03/B-05/B-06/B-07 only from explicit primary evidence or explicit user clarification.
7. Obtain explicit user-approved B-08 production-safety values and validate the policy contract.
8. Establish immutable parameter and real broker-quality execution-cost artifacts.
9. Run lookahead-safe replay, OOS, walk-forward and cost/slippage research only after upstream gates are sufficiently closed.
10. Run separate certification/promotion. Research success is not VERIFIED truth.
11. Keep live execution disabled until certification, risk policy, operational safeguards and explicit authorization are complete.

## Bottom line

The software foundation is advanced. Remaining critical work is dominated by real evidence, real broker data and explicit decisions rather than missing basic plumbing.

Current truth:
- 173 blind cases: ready;
- Agent-06 future checkpoint/resume path: ready;
- current old live Agent-06 run: outcome pending;
- completed/audited external validation: NO;
- MT5/replay infrastructure: ready;
- real MT5 dataset: NO;
- real replay-ready episodes: 0;
- quant reproducibility gate: ready;
- real parameter/cost artifacts: not established;
- B-08 contract: ready, policy unapproved;
- unresolved blocker families: 8;
- VERIFIED knowledge/rules: 0 / 0;
- live execution: DISABLED.
