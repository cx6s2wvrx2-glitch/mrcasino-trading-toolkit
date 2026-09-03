# Agent-06 Semantic Protocol Triage — 2026-09-03

## Status

The completed Anthropic `claude-sonnet-5` Agent-06 run `agent06-anthropic-20260903T040444Z` remains a technically valid external blind execution. Its frozen artifacts passed corrected artifact/isolation audit and must not be modified.

The original post-run comparison reported:

- 173 total vectors
- 144 exact single-label agreements
- 19 single-label disagreements
- 10 abstentions / ambiguous outcomes
- promotion disabled

These counts are preserved as the historical output of the original comparison. They are **not** to be represented as a clean semantic-accuracy score until the benchmark-collision analysis below is completed.

## Confirmed benchmark design issue

The original blind case schema contains only:

- `vector_id`
- `source_locator`

Agent-06 then receives the source evidence plus the batch-wide taxonomy and is asked to choose one exact label or abstain. It does not receive a target proposition or any other answer-free indication of which concept inside a multi-concept source is being tested.

This becomes under-specified when the ground-truth corpus assigns more than one legitimate expected label to the exact same source locator.

Confirmed examples include:

- Round 09: GT-R09-001, GT-R09-002 and GT-R09-003 all use the exact same source image but have three different expected labels.
- Round 10: GT-R10-001/002, GT-R10-003/004, GT-R10-007/008 and GT-R10-012/013 are examples where one exact image is intentionally used for more than one ground-truth concept.

Therefore a provider can select a concept that is ground-truth-supported by the exact same image and still be marked `DISAGREE` against the particular vector's single expected label. That is a benchmark collision, not source contradiction.

## What the technical audit does and does not prove

`AUDIT_PASS` proves the completed external run's artifact integrity and isolation properties, including the frozen prediction/runtime hashes, provider/model identity, ground-truth isolation during the blind stage, and disabled promotion.

It does **not** prove that the benchmark task itself is semantically well-posed. Artifact integrity and semantic benchmark validity are separate gates.

## Collision-aware salvage of the paid run

The deterministic `agent06_locator_set_review_cli` re-evaluates the already-frozen predictions without any provider call.

For each vector it constructs the set of every ground-truth label attached to the exact same source locator across the selected rounds and assigns one of four review states:

- `EXACT_AGREE`: prediction equals the vector's expected label.
- `LOCATOR_SET_AGREE`: prediction differs from the vector's expected label but is another ground-truth label attached to the exact same source locator.
- `UNRESOLVED_DISAGREE`: prediction is not among any ground-truth labels attached to that locator.
- `ABSTAIN`: provider returned no label.

`LOCATOR_SET_AGREE` does not rewrite the historical comparison and does not promote strategy truth. It records that the original single-label disagreement was caused by an under-specified multi-label source locator.

## Required next protocol revision

No new full paid Agent-06 run should be started using the original one-label-per-vector task as a semantic-accuracy benchmark.

A future protocol must make the adjudication target well-posed while keeping the expected verdict hidden. Two acceptable directions are:

1. candidate-claim adjudication: supply the exact claim being tested but hide the expected verdict; return `SUPPORTED`, `CONTRADICTED`, or `INSUFFICIENT`, with negative-control claims included in the benchmark; or
2. locator-level multi-label adjudication: collapse identical locators and allow the validator to return the complete supported-label set, scored using set-based metrics.

The current paid run should first be salvaged with the collision-aware locator-set review before deciding whether any new provider run is justified.

## Authority and promotion

This triage changes no strategy rule, ground-truth label, source authority, VERIFIED state, or production permission.

- strategy truth changed: false
- promotion allowed: false
- live execution authorized: false
