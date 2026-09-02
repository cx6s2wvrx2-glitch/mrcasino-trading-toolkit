# XAUUSD V2 — Ground Truth Coverage Round 02

Status: IMPLEMENTATION COVERAGE ONLY / NOT VERIFIED / NO PROMOTION AUTHORITY
Date: 2026-09-02

This report maps every primary-labelled `GT-R02-*` case to the current deterministic/semantic implementation layer. Coverage means the code has a component capable of representing the source-backed rule or gate. It does **not** mean the strategy rule is VERIFIED and it does not authorize a trade.

## Coverage snapshot

- Total labelled cases: **20**
- Executable semantic/deterministic coverage: **12**
- Partial coverage with an explicit unresolved boundary: **7**
- Context-only / not yet raw end-to-end fixture: **1**
- VERIFIED promotions caused by this mapping: **0**

## Executable cases

`GT-R02-001, 002, 005, 007, 008, 009, 010, 011, 013, 015, 016, 018`

Implemented components include True Stop gates, R-143 sequence, R-145 LTF execution, HCS/TFS establishment, x3 semantic state, zone lifecycle, True Orderblock geometry and the 3h+ weakest-ATT-FU zone gate.

## Partial cases — blockers preserved

- `GT-R02-003`: no universal numeric True-Stop strength score.
- `GT-R02-004`: no certified fixed distance between LAOL and True Stop.
- `GT-R02-006`: active-vs-deferred LAOL priority remains contextual.
- `GT-R02-012`: HCS `near enough` tolerance is source-confirmed but not numeric.
- `GT-R02-014`: zone expansion/refinement still requires contextual zone identity.
- `GT-R02-017`: the 1m full Strong-FU zone is implemented, but universal Strong-FU calibration is not certified.
- `GT-R02-019`: True-Stop respect is represented semantically, but exact raw wick/body respect geometry is not certified.

## Context-only case

- `GT-R02-020`: the 2023-11-01 full top-down sequence is usable as an end-to-end context reference, but one session is not sufficient to define a universal raw top-down detector.

## Governance

The machine-readable registry lives in `src/xauusd_v2/certification_coverage.py` and is tested against `15_tests/ground_truth_round_02.json` so that every current Round-02 case must have an explicit implementation status.

No entry may move from PARTIAL/CONTEXT_ONLY to EXECUTABLE merely because code exists. The missing primary/certification evidence must be supplied and the relevant ground-truth tests must be expanded first.
