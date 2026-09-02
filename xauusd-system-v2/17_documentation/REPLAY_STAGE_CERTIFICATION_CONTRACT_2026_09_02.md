# XAUUSD V2 — R-143 Replay Stage Timestamp Certification Contract

Date: 2026-09-02  
Scope: XAUUSD V2 only  
Status: infrastructure contract / NOT strategy verification / NOT performance evidence / NOT live authorization

## Purpose

Historical replay requires more than an aligned source chart and more than an analyst asserting that the six R-143 stages happened.

The V2 replay path therefore separates:

1. immutable broker-data verification;
2. source-chart alignment;
3. stage-by-stage timestamp evidence;
4. lookahead-safe component replay;
5. historical replay evaluation;
6. strategy/performance certification, which remains a later and separate process.

A bare boolean such as `stage_timestamps_certified=true` is not an admissible unlock mechanism in the production-facing replay-readiness CLI.

## Required evidence chain

A stage certification artifact is admissible only when it is bound to all of the following:

- one registered replay candidate;
- the exact primary-source `source_id` and `source_locator` for that candidate;
- one already-verified persisted MT5 snapshot;
- the exact content-addressed snapshot identity and normalized SHA-256;
- explicit broker name;
- explicit broker symbol;
- canonical symbol `XAUUSD`;
- explicit timeframe;
- an already successful source-chart alignment against that same snapshot;
- all six canonical R-143 stages.

The certification loader reopens the canonical snapshot bytes and reproduces the snapshot metadata before accepting any stage mapping.

## Canonical R-143 stage order

The artifact must contain exactly these six stages, in this order:

1. `HCS_ZONE_REACTION`
2. `TFS`
3. `LAOL_MET`
4. `TRUE_STOP_RESPECTED`
5. `TEN_MIN_TRUE_STOP_ESTABLISHED`
6. `TARGETS_AND_TIMING`

Missing, duplicated, reordered or unknown stages fail closed.

## Per-stage fields

Each stage records:

- `stage` — canonical R-143 stage name;
- `occurred_at` — when the event occurred;
- `available_at` — when the evidence was actually available to a historical decision process;
- `broker_bar_open` — exact open timestamp of the referenced broker candle;
- `source_ref` — non-empty provenance reference for the stage evidence;
- `evidence_kind` — currently fixed to `primary_source_label_aligned_to_closed_broker_bar`.

All timestamps must be timezone-aware.

## Closed-bar and no-lookahead requirements

The referenced `broker_bar_open` must identify a real closed candle inside the exact verified MT5 snapshot.

For every stage:

- `occurred_at` must lie inside the referenced broker candle;
- `available_at >= occurred_at`;
- evidence anchored to that candle is not usable before the candle's close;
- therefore `available_at` must be at or after the referenced candle close;
- `available_at` must remain inside verified snapshot coverage.

Across stages:

- `occurred_at` cannot move backward in canonical R-143 order;
- `available_at` cannot move backward;
- referenced broker bars cannot move backward.

These restrictions are deliberately conservative. They prevent a chart annotation visible in hindsight from becoming earlier historical knowledge.

## What successful certification means

A valid artifact proves only that:

- the six stage labels have a complete provenance-bearing timestamp mapping;
- the mapping is tied to exact immutable broker data;
- the timestamps pass the V2 closed-bar/no-lookahead contract.

It does **not** by itself prove that:

- the analyst's semantic stage label is universally correct;
- the underlying strategy rule is VERIFIED;
- the setup is profitable;
- the replay is sufficient for performance research;
- live trading is allowed.

The artifact itself must contain:

- `promotion_allowed=false`;
- `strategy_verified=false`;
- `performance_claim_allowed=false`.

Any attempt to set those claims to true is rejected.

## Replay-readiness CLI behavior

`xauusd-v2-replay-readiness` now accepts an optional:

```text
--stage-certification /path/to/r143-stage-certification.json
```

Without a valid artifact, exact broker/chart alignment alone remains `BLOCKED_STAGE_TIMESTAMPS`.

With both:

- exact source-chart alignment; and
- a valid six-stage certification artifact bound to the same immutable snapshot,

the registered episode may reach `READY_CANDIDATE` / `replay_ready=true` at the replay-readiness layer.

That state still reports:

- `promotion_allowed=false`;
- `strategy_verified=false`;
- `performance_claim_allowed=false`.

`READY_CANDIDATE` is therefore a data/replay admissibility state, not a strategy certification result.

## Current real-data status

As of 2026-09-02:

- the MT5 ingestion, persistence, reload and alignment infrastructure exists;
- the strict R-143 stage-certification path exists and is regression-tested;
- no real broker-quality XAUUSD MT5 export has yet been ingested into the project;
- no real six-stage certification artifact has yet been created from broker-aligned primary evidence;
- real replay READY count remains 0;
- no real backtest/performance claim is available.

Synthetic test fixtures validate the contract only. They are not market evidence.

## Candidate implications

- `RC-001` remains timestamp-blocked unless its source stages can be proven against admissible raw data.
- `RC-002` is `CONTEXT_ONLY` and cannot be upgraded by a stage artifact.
- `RC-003` remains raw-data blocked until real immutable broker alignment exists; once aligned, it additionally requires a valid six-stage timestamp artifact before replay readiness.

## Governance

This contract does not mutate Supabase disagreement rows, does not promote knowledge/rules, and does not resolve B-01 through B-08.

Live execution remains disabled.
