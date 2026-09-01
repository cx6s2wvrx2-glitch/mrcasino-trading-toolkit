# Deterministic Detector Round 01

Status: CANDIDATE / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01

## Purpose

Start deterministic implementation only where the current corpus supports clear semantic state transitions, while refusing to invent unresolved raw-OHLC geometry.

## Implemented candidate components

### 1. Zone lifecycle evaluator

Implemented in `src/xauusd_v2/candidate_detectors.py`.

Inputs are already-recognized semantic facts, not raw candle detection:

- zone type;
- body-close break status;
- main same-timeframe reaction count;
- governing timeframe where required.

Current candidate mechanics:

- Broken FU-wick zone: inactive until body-close break; 1 main confirmed same-TF reaction quota.
- Broken HCS zone: inactive until body-close break; 2 main confirmed same-TF reaction quota.
- Weakest ATT-FU zone: 3h+ only; 1 main reaction quota.
- Untested FU-wick zone: 1 main reaction quota.

Fail-closed behavior:

- missing activation evidence => `NOT_CERTIFIED`;
- broken zone without body close => `INACTIVE`;
- consumed main reaction quota => `EXPIRED`.

This code does NOT yet detect zone geometry from OHLC.

### 2. Standard entry semantic gate

Implemented in `src/xauusd_v2/candidate_detectors.py`.

Required semantic inputs:

- liquidity calculation resolved;
- LTF LAOL taken;
- 10m True Stop established;
- True Stop respected;
- HTF context aligned;
- approved LTF trigger present.

Outputs:

- any missing input => `NOT_CERTIFIED`;
- any required gate false => `WAIT`;
- all gates true => `READY_CANDIDATE` only.

`READY_CANDIDATE` is explicitly NOT a live-trading authorization. It still requires independent certification, historical reproducibility, and deterministic risk veto.

## Ground-truth expansion

`15_tests/ground_truth_round_02.json` contains 20 candidate vectors from primary Mr Casino sources:

- valid examples;
- invalid examples;
- edge cases;
- one full top-down sequence.

The dataset remains `promotion_allowed=false`.

## Provenance schema improvement

Ground-truth vectors now accept a general `source_locator`, with backward compatibility for Round 01 `image_file` fields. This allows Excalidraw embedded charts/text and ZIP sequences to retain exact provenance instead of pretending every example is a standalone image file.

## Tests

Local test pass for the newly added detector/data-contract tests: 8/8.

Additional backward-compatibility check confirms the Round 01 `image_file` shape still loads into the new `source_locator` model.

## Explicitly NOT implemented yet

No raw-OHLC detector is implemented yet for:

- FU / AFU / SFU;
- exact FU break criterion;
- FU-retest 70% fib anchor;
- HCS raw geometry/tolerance;
- True Stop raw geometry/respect boundary;
- imbalance geometry;
- LAOL automatic target ranking.

These remain blocked by certification questions and visual boundary cases.

## Promotion rule

No code in this round is VERIFIED or production-ready.

Ambiguous or missing evidence must fail closed to `NOT_CERTIFIED`, `INACTIVE`, or `WAIT` rather than being guessed.
