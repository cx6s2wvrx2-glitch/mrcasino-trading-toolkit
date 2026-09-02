# XAUUSD V2 — Open Boundary Reconciliation

Date: 2026-09-02
Scope: XAUUSD V2 only
Governance state: documentation/reconciliation only; no VERIFIED promotion; no `resolved_by_user` mutation

## Purpose

The live `v2_disagreements` table currently contains 14 records with `resolved_by_user=false`. These records are not 14 independent broken strategy components. Some are duplicate manifestations of the same unresolved boundary; some are source-evolution or geometry conflicts that already have a source-backed operational interpretation but still remain formally unverified.

This document consolidates them without guessing, deleting provenance, changing user-resolution state, or promoting any rule.

## Canonical unresolved blocker set

### B-01 — FU sufficient opposite-direction move / break criterion

Related DB records:
- `66a9f8fb-2579-44cd-9a17-6fffc0ba2ffd`
- `928a1381-b0d2-4905-a971-0fc311d6b105`

Current source-backed state:
- liquidity must be taken;
- the qualifying opposite-direction move belongs to the same FU event/candle;
- V2 records raw liquidity interaction, intrabar ordering and exact parent/child reconstruction without inventing a universal BOS formula.

Still unresolved:
- whether the sufficient break is mechanically wick breach, body close, another context-dependent condition, or a source-defined combination.

Fail-closed action:
- do not certify a raw FU detector from an invented close-through/pip/body-colour threshold.

### B-02 — R-54 numeric 70% Fibonacci anchor/orientation

Related DB record:
- `712b253e-c9ba-48f3-a6b8-55d9b54e1498`

Current source-backed state:
- retest validity and retest quality are separate concepts;
- body/close-enough retest may be valid;
- source grades wick interaction more strongly and references a numeric 70% branch.

Still unresolved:
- exact Fibonacci 0/100 anchor and orientation needed to reproduce the numeric 70% boundary.

Fail-closed action:
- retain qualitative wick-touch grading; block numeric 70% grading unless the anchor is explicitly proven.

### B-03 — Universal Strong-FU quantitative threshold

Related DB record:
- `39a7c1ef-06de-465e-abeb-94638c8b53ef`

Current source-backed state:
- stronger FU is associated with strong close and little/no rejection;
- V2 exposes threshold-free quality metrics;
- one 1m-scoped structural Strong-FU feature exists in Reflection evidence.

Still unresolved:
- no universal numeric candle-shape threshold is certified.

Fail-closed action:
- never invent a universal SFU body/wick/rejection percentage.

### B-04 — Broker-specific Imbalanced-Candle classifier calibration

Related DB record:
- `b332f762-21e8-4e60-bbe8-3a6243157c73`

Current source-backed state:
- H1 Imbalanced Candle and M5 Classic Imbalance are separate constructs;
- exact OHLC equality/distance observables are implemented;
- source says the imbalance should be read from broker data rather than TradingView.

Still unresolved:
- exact broker-specific classifier geometry/tolerance for canonical Imbalanced Candle detection.

Fail-closed action:
- helper equality logic remains shadow evidence/raw observable only until labelled broker-quality fixtures exist.

### B-05 — x3-by-x3 raw grammar

Related DB record:
- `167aa018-4d6d-45e4-aa07-ca935c0855b3`

Current source-backed state:
- preserve explicit `x3 by x3` source labels as opaque context.

Still unresolved:
- standalone raw-candle grammar/detector definition.

Fail-closed action:
- no detector or strategy gate may infer what x3-by-x3 means from the name alone.

### B-06 — Accepted RR numeric/dynamic definition

Related DB record:
- `5c71cac8-ce92-4ecb-8cd1-e585fa66987a`

Current source-backed state:
- `Accepted RR` is an approved-source concept in the advanced x3 entry model.

Still unresolved:
- no numeric threshold, formula or dynamic acceptance rule is defined.

Fail-closed action:
- no fixed RR threshold may be inserted into the strategy gate.

### B-07 — 11h candle construction anchor

Related DB record:
- `9f1b1bc0-5767-473a-a194-737b70d4b240`

Current source-backed state:
- native/provenance-backed 11h evidence may be consumed as context.

Still unresolved:
- anchor/session origin required to synthesize reproducible 11h bars from lower-timeframe broker data.

Fail-closed action:
- synthetic 11h construction remains blocked.

### B-08 — Production risk policy

Related DB record:
- `7f77aa6b-ef30-470b-817a-d7cef9f016de`

Current source-backed state:
- deterministic risk engine exists and can enforce a supplied policy.

Still unresolved:
- historical source conflict between 3% maximum and conditional up-to-5% language;
- no production risk percentage has been approved for V2.

Fail-closed action:
- do not hard-code production 3% or 5% as canonical V2 policy.

## Operationally reconciled but still formally unverified/governance-open

These records should not be counted as separate active semantic blockers, although their database rows remain `resolved_by_user=false` and no rule is VERIFIED.

### R-01 — HCS source wording evolution

DB record: `543b8f52-46ed-407e-81bb-7cd9fdd69507`

Operational reconciliation:
- HCS is treated as an eligible new FU/manipulation form created on retest of the prior FU wick;
- exact wick or explicitly source-confirmed near-enough tolerance can count;
- unknown distance fails closed;
- only source-explicit strength rankings are ranked.

Remaining governance state: formal VERIFIED promotion pending.

### R-02 — Liquidity taxonomy source evolution

DB record: `e0dfa8f4-5949-4c8b-9867-3a2a16e3669f`

Operational reconciliation:
- Reflection R-207 scope is explicit and does not erase older broader lists;
- older and newer taxonomies are preserved by source/context rather than auto-merged.

Remaining governance state: formal VERIFIED promotion pending.

### R-03 — Secondary-source authority boundary

DB record: `6d143f13-6abc-4422-acb6-6b961c920653`

Operational reconciliation:
- `BASICSTOINSTITUTIONALTRADING.pptx` remains secondary instructional evidence and cannot silently become canonical strategy authority.

Remaining governance state: explicit user authority decision would be required for any promotion beyond secondary evidence.

### R-04 — Orderblock/body-vs-wick geometry conflict

DB record: `db53242b-c544-4d64-a0a0-acc06db734e7`

Operational reconciliation:
- the apparent conflict is represented as distinct source-backed geometries rather than one arbitrary optional boundary switch;
- True Orderblock body-in-wick geometry, 1m Strong-FU full-candle zone, and full-range refinement remain separate primitives.

Remaining governance state: formal VERIFIED promotion pending.

### R-05 — Reflection R-label numbering collision

DB record: `715fd692-7f17-47ee-9212-bc55a45d8e9b`

Operational reconciliation:
- source label alone is not a unique identifier;
- page/section/occurrence plus unique internal V2 identity must be preserved.

Remaining governance state: canonical renumbering may happen later, but no strategy ambiguity should be created by the source-number collision itself.

### R-06 — FU retest validity vs quality distinction

DB record: `712b253e-c9ba-48f3-a6b8-55d9b54e1498`

Operational reconciliation:
- validity and quality are distinct;
- the conceptual ambiguity is closed operationally.

Remaining blocker is B-02 only: numeric R-54 70% fib anchor/orientation.

### R-07 — Imbalanced Candle vs Classic Imbalance concept separation

DB record: `b332f762-21e8-4e60-bbe8-3a6243157c73`

Operational reconciliation:
- the two constructs are separate and should not be collapsed.

Remaining blocker is B-04 only: broker-specific raw classifier calibration.

## Consolidated status

Live unresolved DB rows: **14**

Canonical genuinely unresolved blocker families after consolidation: **8**

Operationally reconciled source/governance items: **7 views across 5 standalone rows plus partial reconciliation of the R-54 and Imbalance rows**

Important:
- the count reduction from 14 rows to 8 blocker families is deduplication/reconciliation, not rule promotion;
- `resolved_by_user=false` remains untouched;
- VERIFIED knowledge remains 0;
- VERIFIED rules remain 0;
- live execution remains disabled.

## Next certification implications

1. Do not spend future source-review time treating duplicate FU records as separate blockers; resolve them through B-01.
2. Search already-indexed primary visual evidence specifically for B-01/B-02/B-03/B-04 before asking for new source material.
3. B-05/B-06/B-07 remain explicit-source-definition problems; absence of a definition is itself a fail-closed boundary.
4. B-08 requires a production policy decision and must not be inferred from historical source conflict.
5. Independent Agent-06 validation and broker-history ingestion can proceed in parallel; neither is allowed to auto-promote these boundaries.
