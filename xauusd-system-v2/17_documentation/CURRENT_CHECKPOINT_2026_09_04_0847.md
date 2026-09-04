# XAUUSD V2 Current Checkpoint — 2026-09-04 08:47 Europe/Athens

## Scope

XAUUSD project only. No unrelated repository area, Supabase object, Flowstate, THRV or gym material was modified.

## Live code state before this checkpoint

- Branch: `xauusd-v2-foundation`
- Code head: `1f8096064e5a4ab57ecb9fb78ecf4c156bd537f3`
- `XAUUSD V2 Tests` run #582: `completed / success`
- Reference feed: `FOREXCOM:XAUUSD = REQUIRED / DEFERRED / NOT ALIGNED`
- No strategy-semantic certification, performance claim, promotion or live execution authorization.

## What now exists

### 1. Sequential supplied-indicator history runner

`src/xauusd_v2/casino_historical_event_runner.py`

Historical closed bars are processed left-to-right. The runner combines:

- supplied Casino_v7 Strong/ATT marker branches;
- supplied Casino_v7 current-candle doji filter;
- supplied BETA broad FU/SN candidate behavior;
- supplied BETA tracked-box HCS X1/X2/... counter behavior;
- supplied BETA 50/60-minute HCS-zone retest behavior where applicable;
- common `CasinoIndicatorEventFrame` output.

The final provisional bar cannot emit confirmed events.

### 2. Verified persisted-MT5 history report

`src/xauusd_v2/casino_history_report.py`

The report:

- re-verifies the persisted MT5 snapshot;
- supports M1 or governed broker-local derived timeframes;
- seeds replay state from all closed history available before the requested end time;
- clips returned events to the requested window;
- records gap-affected derived bars rather than silently hiding them.

### 3. Narrow source-style HCS marker proxy

`src/xauusd_v2/casino_source_hcs_candidate.py`

This is a separate diagnostic lane, not the BETA HCS implementation and not certified HCS truth.

It operationalizes only the currently supplied Casino Strong/ATT marker output:

- latest prior marker bar only;
- directional wick of the prior marker;
- exact OHLC range intersection only;
- no arbitrary tolerance;
- no same-direction requirement;
- Strong+Strong -> `L3_PROXY`;
- Strong+ATT -> `L2_PROXY`;
- ATT+ATT -> `L1_PROXY`;
- FU-negation nodes are not integrated;
- source-confirmed near-enough retest is not integrated.

This follows the governed source concept that HCS is formed by two FU-family nodes retesting each other while preserving unresolved boundaries instead of inventing them.

### 4. BETA-vs-source-proxy comparison

The verified history report now exposes:

- BETA HCS event bars;
- source-style marker-proxy candidate bars;
- overlap bars;
- BETA-only bars;
- source-proxy-only bars;
- source-proxy counts by form;
- whether any reported events/candidates sit on gap-affected derived bars.

This comparison is observability only and is explicitly not strategy certification.

### 5. Concise CLI output

`xauusd-v2-indicator-history` now supports:

- `--summary`
- `--marker-limit N`

The summary prints the useful March-analysis surface directly, so no extra shell-side JSON parsing is required.

## Tests

New/extended tests cover:

- Strong and ATT historical marker emission;
- doji filtering;
- BETA HCS X1 -> X2 state progression;
- provisional-bar exclusion;
- source-style Strong+Strong exact latest-wick proxy;
- opposite-direction Strong+ATT observability without silently applying a direction filter;
- latest-prior-marker behavior that refuses to reach back to an older marker wick;
- concise comparison summary formatting.

Latest code CI: #582 `success` at head `1f8096064e5a4ab57ecb9fb78ecf4c156bd537f3`.

## March evidence already preserved

Existing M1 governed diagnostics remain unchanged, including:

- 1975 source-level touch at `2023-03-30T12:31:00Z`: exact latest basic-FU-proxy wick retest exists; basic-FU second node absent; conditional Attempted-FU Form 2 remains blocked by uncertified FU criteria.
- 1986 source-level touch at `2023-03-31T12:36:00Z`: strict latest-wick basic-HCS proxy remains present, still non-certified.

No old content-addressed replay artifact was rewritten.

## Current blocker requiring the user's machine

The verified MT5 snapshot and ingestion manifest live under the user's local `$HOME/.xauusd-v2/mt5` store and are not available to GitHub Actions or this remote connector.

Therefore the next irreducible step is one local real-data run over the persisted March snapshot. The required run is now simpler because the CLI itself produces the concise comparison summary.

Target first run:

- timeframe: M15
- window: `2023-03-30T00:00:00Z <= t < 2023-04-01T00:00:00Z`
- output focus: Strong/ATT counts, BETA HCS bars, source-style HCS marker-proxy candidates, overlap/BETA-only/source-only bars, gap diagnostics.

After that output is available, continue directly into mismatch localization and then M1/M5 follow-up where justified by the real result.

## Governance remains unchanged

Still blocked/unresolved unless separately proven:

- B-01 opposite-direction FU move/break mechanics
- B-02 full-FU 70% fib anchor/orientation
- B-03 universal numeric Strong-FU threshold
- B-04 broker-specific Imbalanced-Candle calibration
- B-05 x3-by-x3 raw OHLC grammar
- B-06 Accepted RR numeric/dynamic definition
- B-07 synthetic 11h candle/session anchor
- B-08 production numeric risk policy
- trail-level selection boundary
- exact `FOREXCOM:XAUUSD` reference alignment

No profitability, expected-return, production-risk-readiness or live-trading claim is authorized.
