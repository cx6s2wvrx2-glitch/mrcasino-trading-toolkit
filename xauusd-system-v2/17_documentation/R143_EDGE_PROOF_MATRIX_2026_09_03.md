# R-143 Edge Proof Matrix — 2026-09-03

Status: ACTIVE PROOF PROGRAM
Strategy premise: user states the Mr Casino strategy has edge; this program is designed to demonstrate and quantify that edge without changing the strategy to fit results.
Strategy truth changed: no
Promotion allowed: no
Live execution authorized: no

## What is already proven at the engineering/data layer

1. Exclusive Markets XAUUSD! M1 history is immutable and content-addressed from 2021-01-04 through 2026-09-03.
2. Broker server-time provenance is explicitly confirmed as GMT+2 winter / GMT+3 summer and ingested DST-aware.
3. M1-derived H1/H4/H8/D1 candles were compared against native MT5 exports: 5,708 / 5,708 exact OHLC matches, 0 missing timestamps, 0 mismatches.
4. The first real broker replay slice for the 2023-11-01 Casino episode is immutable: 13,665 M1 bars, SHA-256 `eefa2503777b576394f926e3e22555eb0b9dd4e194a24dae8ac6dcab5ed04399`.
5. The source-labelled 1975 condition level exists exactly in that broker history and its 2023-11-01 path has been measured without semantic guessing.

These results prove the replay/data machinery is reproducing the broker chart correctly. They are not yet the edge proof itself.

## Source-defined edge hypothesis to prove

The primary/top-priority Reflection source gives the official R-143 sequence:

1. HCS zone reaction
2. TFS
3. LAOL met
4. True Stop respected
5. 10min True Stop established
6. core + major + opposite LAOL target / timing

Supporting primary-source mechanics include:

- TS respected -> LAOL taken -> new 10min HCS TS for established direction.
- TFS can confirm LAOL/refined POI through stacked negations across 4h/11h, 3h/5h and 7h in the illustrated example.
- LTF LAOL taken can start the 10min TS build.
- 1min HCS x3 / x3 negation can build 10min HCS establishment.
- Core breakout liquidity is described as the minimum target after the opposite LAOL/POI is respected.

Open definitions remain fail-closed where the source does not give enough raw geometry, notably B-01, B-02, B-03 numeric threshold, B-04, B-05, B-06, B-07 and B-08.

## Candidate roles

### RC-001 — semantic gold-standard sequence

Source: `GIANNO_CASINO_REFLECTION_MASTER.pdf#pages:35-37#section:Delta3-Delta6`

What it gives:
- explicit six-stage R-143 sequence,
- explicit TS/LAOL/10min establishment ladder,
- explicit target hierarchy context,
- multi-timeframe TFS example.

What it does not yet give:
- machine-reliable occurrence/availability timestamps for every stage.

Role in proof program:
- canonical semantic template for what the historical engine must reproduce.
- not yet a timestamp-certified trade fixture.

### RC-003 — real market-alignment episode

Source: `top down analysis (1).zip#sequence:2023-11-01`

What is now available:
- immutable broker M1 replay slice,
- source-labelled 1975 condition-level alignment,
- exact 2023-11-01 broker path around 1975,
- top-down source context from Monthly through intraday/2h imagery.

Measured 1975 path on 2023-11-01:
- first strict low below 1975 at `2023-11-01T16:44:00Z`,
- first M1 close below 1975 at `2023-11-01T18:41:00Z`,
- four separate touch clusters that day,
- later return/retest around 1975.

What is still missing:
- certified source capture time,
- complete explicit mapping of all six R-143 stages in this episode.

Role in proof program:
- proves source-labelled context can be tied to real immutable market history,
- must not be forced into a full R-143 example if the source does not show the six-stage chain.

## Stage evidence matrix

| R-143 stage | RC-001 semantic source | RC-003 2023-11-01 broker replay | Current proof state |
|---|---|---|---|
| HCS zone reaction | Explicit in official sequence | 4H HCS retest POI/source condition exists; 1975 path measured | SOURCE_SUPPORTED + MARKET_CONTEXT_MEASURED, not stage-timed |
| TFS | Explicit and multi-TF example shown | HTF context present, but exact event-stage timestamp not certified | SOURCE_SUPPORTED, TIMESTAMP_BLOCKED |
| LAOL met | Explicit in official sequence | Not safely mapped in RC-003 | NOT_YET_MAPPED |
| True Stop respected | Explicit in official sequence | Not safely mapped in RC-003 | NOT_YET_MAPPED |
| 10min TS established | Explicit ladder and LTF build described | Not safely mapped in RC-003 | NOT_YET_MAPPED |
| targets/timing | Core + major + LAOL explicit | Not safely mapped in RC-003 | NOT_YET_MAPPED |

## Proof standard

The edge proof will not be accepted because one chart looks correct. It will require:

- deterministic detection/replay of the source-defined sequence without future bars,
- exact evidence availability times,
- a frozen rule/version commit,
- a frozen data snapshot,
- historical samples not used to alter the rules,
- locked out-of-sample / walk-forward evaluation,
- spread/slippage/cost sensitivity,
- feed-robustness comparison while preserving `FOREXCOM:XAUUSD` as the Casino visual/reference feed and broker feeds as execution research feeds.

No losing sample is permission to rewrite the strategy after seeing the result. Any unresolved source mechanic remains unresolved until primary evidence or explicit user clarification resolves it.

## Immediate next path

1. Use RC-001 as the six-stage semantic target.
2. Continue searching primary material for a fully timestampable instance of that exact sequence rather than forcing RC-003 to be one.
3. Keep RC-003 as the first source-to-real-market alignment proof and use it to validate top-down/context geometry.
4. Add the `FOREXCOM:XAUUSD` historical reference feed when exact source-chart geometry/custom-timeframe anchor validation becomes the binding dependency.
5. Once one six-stage fixture has certified timestamps, run it through the existing `replay_stage_certification.py` contract, which requires real closed broker bars and lookahead-safe availability times.
