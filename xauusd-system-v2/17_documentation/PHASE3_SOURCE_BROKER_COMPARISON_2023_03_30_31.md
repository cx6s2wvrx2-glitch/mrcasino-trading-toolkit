# XAUUSD V2 — Phase 3 Source vs Broker Comparison — 30–31 March 2023

Date: 2026-09-04
Scope: `xauusd-system-v2/` only
Status: RESEARCH COMPARISON / NOT STRATEGY-CERTIFIED

## Core rule

This comparison keeps three different questions separate:

1. What does the primary source explicitly label?
2. Does the Exclusive Markets broker path contain a related price/path observation?
3. Is the actual semantic strategy stage machine-certified?

A matching price or ordered path is **not** a semantic certification.

Canonical source-feed equivalence additionally requires explicit `FOREXCOM:XAUUSD` reference alignment. That alignment is currently false/deferred.

## Evidence packets

Source packets:

- `06_examples/R143_SOURCE_EVIDENCE_2023_03_30_BUY.json`
- `06_examples/R143_SOURCE_EVIDENCE_2023_03_31_SELL.json`

Broker packets:

- `06_examples/PHASE3_BROKER_STAGE_EVIDENCE_2023_03_30_BUY.json`
- `06_examples/PHASE3_BROKER_STAGE_EVIDENCE_2023_03_31_SELL.json`

Broker reconstruction authority:

- `17_documentation/SOURCE_NARRATED_OUTCOME_RECON_2023_03_30_31.md`

The real March source/broker packets are regression-tested by:

- `15_tests/test_phase3_march_stage_comparison_fixtures.py`

## 2023-03-30 BUY

| R-143 stage | Primary source | Exclusive price/path | Broker semantic | Canonical equivalence |
|---|---|---|---|---|
| HCS zone reaction | OBSERVED / explicit | YES — source-described 1972 manipulation area is reached | BLOCKED | NO |
| TFS | OBSERVED / explicit | not independently represented as a path fact | BLOCKED | NO |
| LAOL met | BLOCKED / unresolved | not enough to establish canonical LAOL | BLOCKED | NO |
| True Stop respected | OBSERVED / explicit at 1972.70 | YES — exact 1972.70 low appears, but 1972.69 appears immediately before | BLOCKED | NO |
| 10m True Stop established | BLOCKED / unresolved | no certified 10m event | BLOCKED | NO |
| Targets/timing | BLOCKED / partial | YES — later trades through 1984.19 | BLOCKED | NO |

### Meaning

The broker reproduces a highly useful ordered price fingerprint:

`1972.70 area -> 1973 area -> 1975 area -> 1984.19 target area`

but this does not transform those price interactions into machine-certified R-143 stages.

The most important example is the True Stop:

- source explicitly says `1972.70 True Stop respected`;
- Exclusive does print `1972.70`;
- however the immediately preceding `1972.69` low means exact source-feed semantic equivalence is not established.

Therefore:

`SOURCE TRUE STOP LABEL = OBSERVED`

but

`BROKER TRUE STOP SEMANTIC = BLOCKED`.

The official R-143 source packet itself still stops first at unresolved `LAOL_MET`.

## 2023-03-31 SELL

| R-143 stage | Primary source | Exclusive price/path | Broker semantic | Canonical equivalence |
|---|---|---|---|---|
| HCS zone reaction | OBSERVED / explicit around 1986 | YES — 1987.57/1986 region is reproduced | BLOCKED | NO |
| TFS | BLOCKED / partial | no independently certified establishment event | BLOCKED | NO |
| LAOL met | BLOCKED / unresolved | downside path exists, canonical LAOL does not | BLOCKED | NO |
| True Stop respected | BLOCKED / unresolved | no certified broker TS-respect event | BLOCKED | NO |
| 10m True Stop established | BLOCKED / unresolved | no certified 10m event | BLOCKED | NO |
| Targets/timing | BLOCKED / partial | YES — later trades through stated 1973 minimum target | BLOCKED | NO |

### Meaning

The Exclusive path strongly fingerprints the narrated sell episode:

- extreme three-minute expansion;
- 1987.57 high versus source 1987.56;
- price through 1986;
- subsequent path through 1983 / 1981 / 1980;
- later trade through 1973.

That makes the episode useful for implementation fidelity.

It still does **not** mean the broker has machine-certified the source HCS at 1986, TFS, LAOL, True Stop, or the complete R-143 sequence.

The source sell packet itself stops first at `TFS` because the preserved source evidence is only partial for that stage.

## Why this matters for the strategy build

This is the first Phase-3 layer that prevents a very common false positive:

> same price / similar chart geometry = same semantic strategy event

V2 now refuses that shortcut.

The comparison model explicitly separates:

- source explicit evidence;
- broker price/path fingerprint;
- broker semantic certification;
- canonical reference-feed alignment.

Only if source semantic evidence and broker semantic evidence are both observed **and** reference-feed alignment is explicitly established can canonical stage equivalence become eligible.

## March semantic boundaries remain unchanged

- `1973`: useful clean supplied-helper Strong-FU observation.
- `1975`: unresolved; do not force-match or tune the detector to fit.
- `1986`: useful source-labelled/control HCS context and broker-path fingerprint; not universal HCS certification.
- 12:31 + 12:32 must not be merged into one staged HCS without primary-source authority.

## What this comparison does not claim

It does not certify:

- FU;
- HCS;
- TFS;
- LAOL;
- True Stop;
- R-143;
- R-145;
- entry validity;
- profitability / expected return;
- production risk readiness;
- promotion;
- live execution.

`FOREXCOM:XAUUSD` remains `REQUIRED / DEFERRED / NOT ALIGNED`.

## Next Phase-3 step

Move from episode-level stage comparison into **timed evidence reconstruction**:

- attach actual broker timestamps/timeframes to the stages that can be observed without semantic invention;
- preserve unresolved semantic stages as `BLOCKED`;
- then build the final human visual timeline showing source label, broker event, semantic state and unresolved boundary side-by-side.

No detector tuning is allowed merely to improve source/broker agreement.
