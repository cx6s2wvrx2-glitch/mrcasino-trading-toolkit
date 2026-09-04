# XAUUSD V2 — Canonical Agent Status

Status date: 2026-09-04

This file is the current short-form operational status. Detailed audit: `17_documentation/AGENT_REALITY_AUDIT_2026_09_04.md`. Machine-readable audit: `06_examples/AGENT_REALITY_AUDIT_2026_09_04.json`.

## Critical interpretation

Eight agent foundations are implemented, but **eight autonomous agents are not continuously running in the background**. The project contains deterministic engines, provider-dependent agents, explicit run pipelines and a deterministic orchestrator. Runs occur when invoked; stored `agent_runs` rows are history, not active processes.

| ID | Agent | Implementation | Runtime reality | Authority boundary / current frontier |
|---|---|---|---|---|
| 01 | Knowledge / Understanding | `KnowledgeAgent` v0.1.0 | provider-dependent; live DB run history exists; no background runtime observed | Approved sources only; claims start UNVERIFIED; 195 knowledge claims, 0 VERIFIED |
| 02 | Strategy Formalization | `RulesAgent` v0.1.0 | provider-dependent; live DB run history exists; no background runtime observed | DRAFT rules only; 23 rules, 0 VERIFIED; cannot promote |
| 03 | XAUUSD Data | `XAUUSDDataAgent` v0.1.0 + broader MT5/replay layer | deterministic validator; real Exclusive Markets March broker evidence/replay infrastructure exists; no background runtime observed | Data/provenance only; `FOREXCOM:XAUUSD` reference alignment remains incomplete |
| 04 | Market State / Context | `MarketStateAgent` v0.1.0 | deterministic consistency gate; no background runtime observed | aligned/conflicting/ambiguous only; does not create primitives; unresolved TFS must remain ambiguous |
| 05 | Quant Research / Backtesting | `QuantitativeResearchAgent` v0.2.0 | deterministic reproducibility/design gate; no background runtime observed | Cannot modify strategy or authorize trades; credible performance research remains upstream-blocked |
| 06 | Independent Validation | `IndependentValidationAgent` v0.3.0 + blind/audit runtime | provider-dependent; 173-case blind corpus; checkpoint/resume/audit/multimodal infrastructure; no background runtime observed | No currently observed completed+audited full external 173-case result; never auto-promotes |
| 07 | Deterministic Risk Engine | `DeterministicRiskEngine` v0.2.0 | deterministic hard-veto gate; no background runtime observed | No default production percentages; B-08 numeric policy unapproved; cannot create signals or directly authorize execution |
| 08 | Continuous Improvement | `ContinuousImprovementAgent` v0.1.0 | deterministic governance/proposal gate; no background runtime observed | PROPOSAL_ONLY / rejected incomplete; no self-modification or direct promotion |

## Orchestration

Current orchestrator: **`AgentPipelineCoordinator` v0.6.0**.

Strategy-candidate readiness consumes actual evidence-bearing reports for:
- market data;
- market context;
- R-143 sequence;
- R-145 LTF execution;
- blind independent validation;
- historical replay reproducibility.

Research readiness additionally requires provenance-bearing source approval, strategy freeze, ground truth and a reproducible research design.

Execution-candidate readiness additionally requires a clean deterministic risk decision.

`live_execution_authorized` remains **false by construction**.

## Strategy/evidence implementation

- FU: source semantic criteria, conservative observables/candidates, Complete/ATT classification, threshold-free quality measurements, helper/code shadow comparisons and intrabar evidence tooling.
- Liquidity: explicit marked-level interaction, 30m+ core taxonomy and doji-liquidity semantics without invented thresholds.
- HCS / negation: source-backed node grammar with fail-closed temporal/co-location and certification boundaries; March `12:31 + 12:32` staged merge remains forbidden without authority.
- Zones / POI: dedicated geometry/lifecycle layers; source evolution and helper implementations remain separate.
- TFS / True Stop / R-143 / R-145: explicit fail-closed semantic and sequence gates.
- Imbalanced candle: raw observables exist; no universal broker-independent canonical classifier has been invented.
- Broker precision: source/broker identity, digits and tick size remain explicit; no silent rounding/equivalence.
- Replay: lookahead-safe `occurred_at` / `available_at` model and immutable broker snapshots/bundles.

## Real March Phase-3 state

### 2023-03-30 BUY
- source semantic frontier: **LAOL**;
- broker semantic frontier: **Zone/POI/HCS stage**;
- distinctive Exclusive Markets path exists;
- `1975` remains unresolved rather than force-matched.

### 2023-03-31 SELL
- source semantic frontier: **TFS**;
- broker semantic frontier: **Zone/POI/HCS stage**;
- `1986` remains useful source-labelled/control context and broker path fingerprint, not universal HCS certification.

Reference state for both:

`FOREXCOM:XAUUSD = REQUIRED / DEFERRED / NOT ALIGNED`

Exclusive Markets `XAUUSD!` is broker/execution research geometry and must not be silently treated as canonical source geometry.

## Blind validation

Persisted blind corpus R02–R13: **173 cases**.

Per-case expected answers and analyst evidence are hidden from Agent 06. Primary source text/image context is resolved separately. The pipeline supports strict taxonomy transport, abstention, checkpoint/resume, immutable/frozen outputs, deterministic post-run comparison and post-run audit.

Current connected-state truth:
- infrastructure implemented: YES;
- full 173-case corpus: YES;
- canonical Agent-06 DB row: `needs_review`, provider `none`, model `not_connected`;
- currently observed completed and audited full external 173-case provider run: **NO**;
- auto-promotion: **FORBIDDEN**.

## Live Supabase snapshot — 2026-09-04 read-only check

- 29 user-approved sources;
- 215 examples;
- 195 knowledge claims;
- 23 rules;
- 14 unresolved disagreement/certification rows;
- 32 stored agent/support runs;
- 0 VERIFIED knowledge claims;
- 0 VERIFIED rules.

Stored run rows are historical records. They are not proof of active background workers.

## Test status

Latest confirmed full regression before this status refresh:
- workflow: `XAUUSD V2 Tests`;
- run id: `33863854316`;
- run number: `670`;
- head: `99553aa65872ba16b9ace93812218ca1edabc28a`;
- Python 3.12;
- **1044 tests / OK**.

Documentation/status commits after that checkpoint trigger their own CI and must be checked on the final head before claiming a newer green checkpoint.

## Open canonical blocker families

- B-01 — exact sufficient opposite-direction move/break mechanics for FU.
- B-02 — exact R-54 70% Fibonacci anchor/orientation.
- B-03 — universal numeric Strong-FU threshold, if one exists.
- B-04 — broker-specific Imbalanced-Candle calibration.
- B-05 — raw OHLC grammar for x3-by-x3.
- B-06 — exact numeric/dynamic Accepted RR definition.
- B-07 — synthetic 11h candle/session anchor.
- B-08 — explicit user-approved production risk policy.

Additional current semantic frontiers:
- March BUY exact `LAOL met` meaning/application;
- March SELL exact pre-entry `TFS` establishment evidence;
- HCS temporal/co-location boundary;
- canonical `FOREXCOM:XAUUSD` alignment;
- trail-level selection boundary.

## Non-negotiable rules

1. No agent self-promotes strategy truth.
2. Ambiguity is fail-closed.
3. Provisional bars cannot satisfy confirmed conditions.
4. Agent 06 never receives expected case answers or analyst-authored ground-truth evidence.
5. Helper code is implementation evidence only, never strategy authority.
6. R-143 stage order cannot be skipped.
7. A broker price/path observation is not automatically a source semantic event.
8. `LAOL respected`, `LAOL taken`, `liquidity left behind` and `LAOL met` are not silently interchangeable.
9. Forming FU / general timeframe-strength context is not silently promoted to established TFS.
10. Later evidence cannot retroactively certify an earlier decision point.
11. Research requires frozen/versioned strategy, clean immutable data, explicit parameters/costs and proper time splits.
12. Risk veto outranks strategy readiness; production risk requires explicit approved policy.
13. No LLM is permitted in the latency-critical live order path.
14. No profitability, production readiness, promotion or live-execution claim is allowed from the current state.
