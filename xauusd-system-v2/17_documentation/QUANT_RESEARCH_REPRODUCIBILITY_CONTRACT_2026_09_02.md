# XAUUSD V2 — Quantitative Research Reproducibility Contract

Date: 2026-09-02
Status: ENGINEERING CONTRACT READY / NO PERFORMANCE EVIDENCE

## Purpose

This contract prevents a backtest or statistical study from being treated as reproducible when its strategy code, market data, parameters or execution-cost assumptions are not pinned to immutable identities.

It does not certify strategy truth, define unresolved strategy rules, select production risk, prove profitability or authorize live execution.

## Required experiment identity

Every admissible `ResearchExperimentSpec` must provide:
- non-empty experiment ID;
- non-empty strategy version;
- exact 40-character hexadecimal Git commit SHA for the strategy implementation;
- immutable XAUUSD data snapshot reference in `sha256:<64-hex>` form;
- immutable parameter-set reference in `sha256:<64-hex>` form;
- immutable execution-cost-model reference in `sha256:<64-hex>` form;
- canonical symbol `XAUUSD`;
- positive timeframe in seconds.

Human-friendly aliases such as `latest`, `params-v1`, `costs-v1`, a short Git SHA or an un-hashed file name are not sufficient reproducibility identities.

## Historical-data constraints

Research may use confirmed/closed historical bars only.

The immutable data snapshot must:
- match the experiment's exact `data_snapshot_ref`;
- be canonical XAUUSD;
- match the declared timeframe;
- match the validated bar count;
- contain no provisional bar when performance research is requested;
- cover the full train-to-test interval.

The data layer reuses the content-addressed snapshot and tamper-detection contracts from the MT5/replay infrastructure.

## Train / validation / test constraints

All research windows must use timezone-aware datetimes.

Canonical order:
1. train;
2. validation;
3. locked test.

Train may not overlap validation. Validation may not overlap test.

Contiguous windows are currently allowed but produce a warning because they contain no purge gap. This warning must not be silently dropped from an experiment report.

The test set must remain locked until final evaluation. An experiment that declares the test set unlocked is rejected before backtesting.

## Content-addressed parameter set

`parameter_set_ref` identifies the exact bytes of the parameter artifact used by the experiment.

This identity requirement does not itself define what strategy parameters are valid. Unresolved strategy boundaries remain unresolved and may not be invented merely to construct a parameter file.

## Content-addressed cost model

`cost_model_ref` identifies the exact bytes of the execution-cost assumptions used by the experiment.

The current research gate requires immutable identity for this artifact but does **not** yet claim that real broker spread, slippage or commission assumptions have been supplied. A hash proves which artifact was used, not that its economic assumptions are correct.

Therefore:
- an empty cost reference is rejected;
- a vague alias such as `costs-v1` is rejected;
- a valid SHA-256 reference is necessary for reproducibility;
- real broker-quality cost assumptions remain an external/data requirement before performance conclusions are credible.

## Readiness states

`prepare_research_runtime()` can produce:
- `BLOCKED` — research design or data contract is incomplete/inconsistent;
- `DATA_READY` — immutable data and research design are admissible, but strategy certification is not ready;
- `BACKTEST_READY` — data/design gates and the supplied strategy-certification gate are ready for a research run.

`BACKTEST_READY` is not a profitability result, strategy verification, production approval or live authorization.

## Authority boundary

The Quantitative Research Agent explicitly has no authority to:
- modify strategy truth;
- fill unresolved strategy definitions;
- choose production risk;
- authorize a trade;
- promote knowledge/rules to VERIFIED.

## Current real-world status

As of 2026-09-02:
- real broker XAUUSD dataset in the evidence path = 0;
- real broker-aligned replay episodes = 0;
- real content-addressed production parameter artifact = not yet established;
- real broker-quality execution-cost artifact = not yet established;
- real OOS / walk-forward / cost-and-slippage performance evidence = 0;
- performance claims allowed = false.

The engineering contract is ready; the external evidence needed to use it meaningfully is not yet complete.

## Relevant implementation

- `src/xauusd_v2/agents/quant_agent.py`
- `src/xauusd_v2/research_runtime.py`
- `src/xauusd_v2/data_snapshot.py`
- `15_tests/test_quant_research_agent.py`
- `15_tests/test_data_snapshot_research_runtime.py`
- `17_documentation/MT5_TO_REPLAY_READINESS_RUNBOOK.md`
