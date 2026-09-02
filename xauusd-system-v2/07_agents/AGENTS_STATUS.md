# XAUUSD V2 — Canonical Agent Status

Status date: 2026-09-02

| ID | Agent | Current state | Connection | Authority boundary |
|---|---|---|---|---|
| 01 | Knowledge / Understanding | IMPLEMENTED v0.1 | provider-neutral; no production model adapter | Approved sources only; output starts UNVERIFIED |
| 02 | Strategy Formalization | IMPLEMENTED v0.1 | provider-neutral | DRAFT/candidate rules only; cannot promote |
| 03 | XAUUSD Data | IMPLEMENTED v0.1 | immutable snapshots + broker precision; no MT5 yet | Validates data/provenance/time; no trade authority |
| 04 | Market State / Context | IMPLEMENTED v0.1 | consumes confirmed/provisional semantic context | aligned/conflicting/ambiguous only; no trade authority |
| 05 | Quant Research | IMPLEMENTED v0.1 | reproducible research gate; R-143/R-215 layers available | Cannot change strategy or authorize trades |
| 06 | Independent Validation | IMPLEMENTED infrastructure v0.2 | 38-case multi-round leakage-safe packet + primary-context resolver + downstream comparison; no production independent provider yet | Never sees case answers/evidence; may abstain; cannot promote |
| 07 | Risk Engine | IMPLEMENTED v0.1 | no broker/account connection; production policy unset | Hard veto; no default 3%/5%; cannot create signals |
| 08 | Continuous Improvement | IMPLEMENTED v0.1 | proposal/governance foundation | Propose only; every change re-enters certification |

## Strategy/evidence implementation

- FU: semantic criteria, conservative raw candidate, Complete/ATT classification, threshold-free quality metrics, Casino_v7/BETA shadow comparison.
- Liquidity: marked-level interaction + R-207 30m+ core taxonomy + threshold-free doji-liquidity semantics.
- Doji liquidity: unmanipulated/core vs manipulated/not-core vs outside-previous-wick Attempted-FU context, without inventing a doji body-ratio threshold.
- Zones: later Reflection lifecycle/geometry remains separate from the older classic-zone confirmation model; source evolution is not silently collapsed.
- HCS, negation, final R-213 x3, TFS established/as-forming, True Stop, R-145 LTF execution, R-143 sequence and target hierarchy use fail-closed gates.
- Imbalanced-candle observables remain separate from classic imbalance/FVG; no canonical `is_imbalance` classifier yet.
- Broker precision requires explicit broker/source symbol, digits and tick size.
- Historical component replay distinguishes `occurred_at` from `available_at`; future evidence is hidden.
- Replay candidate registry currently has 0 READY sessions: Reflection sequence is timestamp-blocked, top-down sequence is raw-data-blocked, exercise protocol is context-only.

## Ground truth

- Round 02: 20 primary-labelled cases — 12 EXECUTABLE, 7 PARTIAL, 1 CONTEXT_ONLY.
- Round 03: 7 explicit primary visual labels — 6 PARTIAL, 1 RAW_BLOCKED.
- Round 04: 6 explicit FU-retest/zone primary cases — 6 PARTIAL with preserved cross-version/raw blockers.
- Round 05: 5 primary negative/edge cases — 5 semantic EXECUTABLE, 0 VERIFIED.
- Total R02–R05: **38 labelled cases** — **17 EXECUTABLE, 19 PARTIAL, 1 RAW_BLOCKED, 1 CONTEXT_ONLY**.
- Supabase examples: **71**.
- VERIFIED promotions from these datasets: **0**.

## Blind validation

Agent 06 can now receive one multi-round R02–R05 packet containing 38 cases.

Per case, the packet schema is only:
- `vector_id`
- `source_locator`

Expected label, expected class, analyst evidence and forbidden-inference notes are not present. A shared multi-option taxonomy is batch-wide only. Duplicate vector IDs across rounds are rejected before the run; missing predictions become AMBIGUOUS; all-agree still cannot promote.

A real independent production provider/model validation run has not yet occurred.

## Orchestration

Current orchestrator: **v0.5**.

Critical gates do not accept free readiness booleans:
- strategy candidate consumes actual blind-validation and historical-replay reports;
- research reruns the full strategy evidence gate;
- execution consumes the actual strategy readiness report;
- a blocked report cannot be relabelled ready downstream;
- live execution authorization remains false by construction.

Canonical specification: `07_agents/PIPELINE_ORCHESTRATION_V0_5.md`.

## Live Supabase snapshot

- 29 active user-approved sources
- 71 examples
- 195 knowledge claims
- 23 rules
- 11 open disagreement/certification records
- 32 agent runs
- 0 VERIFIED knowledge claims
- 0 VERIFIED rules

## Test status

Latest confirmed GitHub Actions full regression: **347/347 PASS** on Python 3.12, run `33592412316`, job `100128924887`, commit `75fa69afcc5369d474bfd5b53646cd9a1ade7d9c`.

## Non-negotiable rules

1. No agent self-promotes strategy truth.
2. Ambiguity is fail-closed.
3. Provisional bars cannot satisfy confirmed conditions.
4. Agent 06 never receives the expected case answer or analyst-authored evidence.
5. Actual primary context must be available for blind validation; no summary fallback.
6. Helper code is implementation evidence only, never strategy authority.
7. R-143 stage order cannot be skipped.
8. Research requires frozen/versioned strategy, clean data, explicit costs and proper time splits.
9. Risk veto outranks strategy readiness.
10. Production risk limits require explicit approved policy.
11. No LLM is permitted in the latency-critical live order path.
12. EXECUTABLE coverage means implementation coverage only; it is not raw-OHLC certification and never means VERIFIED.
