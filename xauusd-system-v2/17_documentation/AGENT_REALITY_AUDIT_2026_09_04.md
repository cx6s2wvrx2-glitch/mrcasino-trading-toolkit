# XAUUSD V2 — Agent Reality Audit

Date: 2026-09-04

Scope: only `xauusd-system-v2/` on `xauusd-v2-foundation`.

## Why this audit exists

The project contains eight named agents, but the phrase “eight agents” can easily create the wrong impression that eight autonomous processes are continuously analysing the market in the background. That is not the current system.

The accurate statement is:

> Eight agent foundations are implemented. Some are deterministic engines, some require a model/provider, and all are bounded by fail-closed governance. No continuously running eight-agent background swarm was observed in the live project state.

The deterministic orchestrator connects evidence-bearing outputs when explicitly invoked. It never grants live execution authority.

## Current live engineering snapshot

Before this audit, the live branch head was `99553aa65872ba16b9ace93812218ca1edabc28a`.

Latest observed `XAUUSD V2 Tests` run:

- run id: `33863854316`;
- run number: `670`;
- head: `99553aa65872ba16b9ace93812218ca1edabc28a`;
- conclusion: `success`;
- Python 3.12 full suite: **1044 tests, OK**.

Live Supabase read-only snapshot:

- 29 user-approved sources;
- 215 examples;
- 195 knowledge claims;
- 0 VERIFIED knowledge claims;
- 23 rules;
- 0 VERIFIED rules;
- 14 unresolved disagreement/certification rows;
- 32 recorded agent/support runs.

These counts describe stored project evidence. They do not mean 32 active processes.

## Agent 01 — Knowledge / Understanding

**Implementation:** `KnowledgeAgent` v0.1.0.

What it actually does:
- accepts only a user-approved source;
- sends source content to a configured structured model client;
- extracts source-scoped claims with provenance;
- forces every extracted claim to start as `UNVERIFIED`;
- always routes output to review.

What it does not do:
- it cannot verify its own interpretation;
- it cannot promote a rule;
- it cannot authorize a trade.

Observed live DB history: six canonical Agent-01 rows, all `needs_review`, across GPT-5.6 Sol and a clean-room extractor.

Current frontier: **195 stored knowledge claims, 0 VERIFIED**.

## Agent 02 — Strategy Formalization

**Implementation:** `RulesAgent` v0.1.0.

What it actually does:
- converts source-backed claims into structured strategy-rule drafts;
- keeps source provenance explicit;
- accepts one source at a time in v0.1;
- rejects any model output that attempts to promote a rule above `DRAFT`.

What it does not do:
- it does not decide that a draft is strategy truth;
- it does not close ambiguous definitions;
- it cannot authorize trading.

Observed live DB history: one canonical Agent-02 `needs_review` row.

Current frontier: **23 rules exist, 0 VERIFIED**.

## Agent 03 — XAUUSD Data

**Implementation:** `XAUUSDDataAgent` v0.1.0 plus a much larger dedicated MT5/snapshot/replay data layer elsewhere in V2.

The Agent-03 class itself is a deterministic validation gate. It checks:
- canonical XAUUSD scope;
- timezone-aware timestamps;
- ordered/unique bars;
- OHLC validity;
- closed vs provisional state;
- explicit data-source and broker-symbol provenance.

It does not directly log into MT5. The broader project now contains MT5 ingestion, immutable snapshots, MTF handling, source/broker alignment tooling and real March Exclusive Markets broker evidence.

The important boundary remains:

`Exclusive Markets XAUUSD! broker geometry != FOREXCOM:XAUUSD canonical reference geometry`

Current frontier: broker research data exists, but **FOREXCOM reference alignment is still REQUIRED / DEFERRED / NOT ALIGNED**.

## Agent 04 — Market State / Context

**Implementation:** `MarketStateAgent` v0.1.0.

This is a deterministic consistency engine. It consumes already-established inputs such as:
- prevalent HTF direction;
- established TFS direction;
- major liquidity-target direction;
- active-zone direction.

It returns aligned bullish, aligned bearish, conflicting, ambiguous or no-context.

If a required input is provisional or unresolved, it deliberately returns `AMBIGUOUS`.

Critical limitation: it **does not invent or discover the strategy primitives itself**. If TFS is unresolved upstream, Agent 04 must remain blocked/ambiguous rather than manufacture TFS.

Current March SELL frontier: the source-side TFS before the 1986 decision remains unresolved.

## Agent 05 — Quant Research / Backtesting

**Implementation:** `QuantitativeResearchAgent` v0.2.0.

This is currently a research-design and reproducibility gate, not a money-making backtest engine.

It requires:
- exact full Git strategy commit SHA;
- content-addressed data snapshot;
- content-addressed parameter set;
- content-addressed cost model;
- canonical XAUUSD;
- confirmed bars only;
- timezone-aware train/validation/test windows;
- non-overlapping windows;
- locked final test set.

It cannot modify strategy, choose live risk or authorize a trade.

Current frontier: we are **not yet entitled to make credible profitability claims** because upstream strategy semantics, canonical reference alignment and real cost/parameter artifacts are not sufficiently closed.

## Agent 06 — Independent Validation

**Implementation:** `IndependentValidationAgent` v0.3.0 plus the strongest surrounding infrastructure of the eight-agent architecture.

Implemented surrounding controls include:
- 173-case blind corpus (Rounds 02–13);
- answer-free packets;
- exact primary-source context resolution;
- text and image evidence support;
- isolated provider stage;
- taxonomy constraints;
- abstention support;
- checkpoint/resume;
- frozen output hashes;
- separate deterministic comparison;
- post-run audit;
- no automatic promotion.

Important reality check:

The live canonical Agent-06 database row currently records `needs_review` with provider `none` / model `not_connected`. Supporting independent-validation infrastructure and earlier validation rows exist, but in the currently observed connected state there is **no completed and audited full external 173-case provider result that can be claimed as finished validation**.

Therefore:
- Agent 06 exists;
- it can be run through the prepared pipeline when the provider/runtime is actually invoked;
- it is not silently running in the background;
- even 173/173 agreement would still not auto-promote strategy truth.

## Agent 07 — Deterministic Risk Engine

**Implementation:** `DeterministicRiskEngine` v0.2.0.

It is a hard-veto layer.

It requires:
- a complete explicit production risk policy;
- a provenance-bearing strategy-candidate gate;
- a provenance-bearing market-context gate;
- valid account/risk snapshot values.

It intentionally contains **no default production percentages**.

It can return `NOT_CONFIGURED`, `VETO`, or `APPROVE_CANDIDATE`, but it cannot create a strategy signal or directly authorize execution.

Current frontier: **B-08 remains unresolved** because the real production numerical policy has not been explicitly approved.

## Agent 08 — Continuous Improvement

**Implementation:** `ContinuousImprovementAgent` v0.1.0.

It is a governance layer for proposed changes. A valid proposal must include:
- affected rules;
- evidence references;
- observed failure modes;
- proposed change;
- validation plan;
- rollback criteria.

It can only return a proposal/review state. Direct promotion is rejected.

This is **not autonomous self-learning or self-modifying strategy code**. Every proposed change must re-enter the validation/certification ladder.

## Orchestrator — what ties the agents together

`AgentPipelineCoordinator` is currently v0.6.0.

It accepts actual evidence-bearing reports rather than free caller booleans.

Strategy-candidate readiness requires, among other things:
- valid market data;
- non-ambiguous market context;
- complete-candidate R-143 sequence;
- LTF entry candidate;
- clean blind-validation comparison;
- historically reproducible replay.

Research readiness adds source approval, strategy freeze, ground truth and reproducible research design.

Execution-candidate readiness adds a clean risk decision.

In all paths:

`live_execution_authorized = false`

So the orchestrator is a deterministic gatekeeper, not a live trading daemon.

## Current March truth

The two real March episodes remain useful validation specimens.

### 2023-03-30 BUY

- source semantic frontier: **LAOL**;
- broker semantic frontier: **Zone/POI/HCS stage**;
- canonical FOREXCOM equivalence: not established.

### 2023-03-31 SELL

- source semantic frontier: **TFS**;
- broker semantic frontier: **Zone/POI/HCS stage**;
- canonical FOREXCOM equivalence: not established.

This means the broker can reproduce meaningful price-path observations without those observations being silently promoted to source-semantic truth.

## Bottom line

The eight-agent architecture is real software, not a presentation mock-up. But it is also not eight autonomous traders working continuously behind the scenes.

Today the accurate status is:

- **8/8 agent foundations implemented**;
- deterministic and provider-dependent responsibilities are separated;
- 173-case independent-validation corpus exists;
- real broker/replay engineering exists;
- full regression is green;
- evidence/provenance boundaries are materially stronger than at project start;
- no agent may self-promote strategy truth;
- VERIFIED knowledge/rules remain **0 / 0**;
- canonical FOREXCOM alignment remains incomplete;
- production risk policy remains unapproved;
- performance/profitability claims remain forbidden;
- live execution remains disabled.

The next engineering objective is not to add more impressive agent names. It is to close the actual semantic/data frontiers, then let these existing agents operate on a frozen strategy definition and reproducible data.
