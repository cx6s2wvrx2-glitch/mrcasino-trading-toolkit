# XAUUSD V2 — Open Boundary Reconciliation

Date: 2026-09-02
Scope: XAUUSD V2 only
Governance state: documentation/reconciliation only; no VERIFIED promotion; no `resolved_by_user` mutation

## Purpose

The live `v2_disagreements` table currently contains 14 records with `resolved_by_user=false`. These records are not 14 independent broken strategy components. Some are duplicate manifestations of the same unresolved boundary; some are source-evolution or geometry conflicts that already have a source-backed operational interpretation but still remain formally unverified.

This document consolidates them without guessing, deleting provenance, changing user-resolution state, or promoting any rule.

Detailed primary-evidence audits:
- `17_documentation/PRIMARY_BLOCKER_AUDIT_B01_B04_2026_09_02.md`
- `17_documentation/PRIMARY_BLOCKER_AUDIT_B05_B08_2026_09_02.md`

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
- the R-54 quality ordering is established: beyond 70% of full FU without wick touch is the weak branch, wick touch is stronger, and 50% of the FU wick is strongest.

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
- explicit user clarification dated 2026-09-02 establishes that Strong FU / ATT FU use the same primitive logic on every timeframe;
- a specific 1m Strong-FU zone application exists in Reflection, but that application is not the definition of Strong FU.

Still unresolved:
- no universal numeric candle-shape threshold is certified; it remains unknown whether a universal body/wick/rejection percentage is intended at all.

Fail-closed action:
- never invent a universal SFU body/wick/rejection percentage;
- do not re-open timeframe scope: the primitive logic is timeframe-invariant, while timeframe changes context/authority/downstream application.

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
- Reflection contains an applied establishment sequence where 1m HCS x3 and a following 1m x3 negation labelled `x3 by x3` contribute to 10m HCS establishment;
- pure x3 negation and self-negating x3 are distinct concepts;
- explicit `x3 by x3` source labels may be preserved as context.

Still unresolved:
- standalone raw-candle grammar/detector definition for autonomously identifying x3-by-x3 from OHLC.

Fail-closed action:
- no detector or strategy gate may infer x3-by-x3 from the name, visual similarity, or helper behavior alone.

### B-06 — Accepted RR numeric/dynamic definition

Related DB record:
- `5c71cac8-ce92-4ecb-8cd1-e585fa66987a`

Current source-backed state:
- `Accepted RR` is an approved-source concept in the advanced x3 entry model;
- it appears together with complete liquidity calculation and multi-timeframe alignment for advanced exact-entry context.

Still unresolved:
- no numeric threshold, formula or dynamic acceptance rule is defined;
- historical RR examples do not define `Accepted RR`.

Fail-closed action:
- no fixed RR threshold may be inserted into the strategy gate unless separately certified or explicitly adopted later as a production/research policy rather than attributed to the source.

### B-07 — 11h candle construction anchor

Related DB record:
- `9f1b1bc0-5767-473a-a194-737b70d4b240`

Current source-backed state:
- 11h is repeatedly used as a genuine swing/context timeframe;
- a forming 11h HCS+negation can be confirmed by aligned established lower-TF evidence in the cited sequence;
- native/provenance-backed 11h evidence may be consumed as context.

Still unresolved:
- anchor/session origin required to synthesize reproducible 11h bars from lower-timeframe broker data, including broker/server-time and DST implications.

Fail-closed action:
- synthetic 11h construction remains blocked until its anchor is proven;
- do not treat the strategic role of 11h itself as unresolved.

### B-08 — Production risk policy

Related DB record:
- `7f77aa6b-ef30-470b-817a-d7cef9f016de`

Current source-backed state:
- deterministic risk engine exists and can enforce a supplied complete policy;
- historical material contains 3% guidance and separate conditional up-to-5% language in another context;
- source risk claims and production account-risk policy are intentionally separate layers.

Still unresolved:
- no production risk policy has been explicitly approved for V2, including per-trade, aggregate-open and daily-loss limits.

Fail-closed action:
- do not hard-code production 3% or 5% as canonical V2 policy;
- B-08 is a future user-approved deterministic safety/governance decision, not a strategy-source truth contest.

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

1. Use `PRIMARY_BLOCKER_AUDIT_B01_B04_2026_09_02.md` for the narrowed mechanical/data unknowns B-01 through B-04.
2. Use `PRIMARY_BLOCKER_AUDIT_B05_B08_2026_09_02.md` for the narrowed definition/governance unknowns B-05 through B-08.
3. B-05/B-06/B-07 remain explicit-definition problems only at their unresolved layers; do not discard their already source-backed applied semantics.
4. B-08 requires an explicit production safety-policy decision and must not be inferred from historical source conflict.
5. Independent Agent-06 validation and broker-history ingestion can proceed in parallel; neither is allowed to auto-promote these boundaries.
6. No future review should re-open the user-confirmed Strong FU / ATT FU timeframe-invariant primitive scope unless the user explicitly changes that clarification.