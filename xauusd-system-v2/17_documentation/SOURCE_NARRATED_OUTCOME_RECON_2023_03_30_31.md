# Source-Narrated Outcome Reconstruction — 30–31 March 2023

Status: RETROSPECTIVE SOURCE-TO-BROKER RECONSTRUCTION
Purpose: demonstrate that the primary Mr Casino narrated price story can be located in the immutable user-supplied broker history before using the episode for detector/component validation.
Performance claim: not allowed from this artifact alone
Strategy truth changed: no
Promotion allowed: no
Live execution authorized: no

## Evidence inputs

Primary narrative:
- approved Price Action Reflection / Discord material paired to the 2023-04-02 visual episode,
- retrospective messages posted 3 April 2023 reviewing `Thursday the 30th` and `Friday the 31st`.

Broker history:
- Exclusive Markets Ltd. `XAUUSD!` M1 raw export,
- source SHA-256 `691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0`,
- broker timezone converted with the confirmed GMT+2/GMT+3 DST-aware provenance.

## Reconstruction A — source-described buy sequence

Primary narrative states, in the buy-establishment discussion:

- 45min HCS / manipulation context around 1972,
- `1972.19` liquidity left behind,
- `1972.70` True Stop respected,
- strongest 1min FU closure around `1973`,
- easy 1min HCS re-entry around `1975`,
- `1984.19` as clear imbalance / upside target context.

Exclusive Markets observations on Thursday 30 March:

1. `2023-03-30T15:52:00Z`: M1 low `1972.69`.
2. `2023-03-30T15:53:00Z`: the only M1 low exactly equal to `1972.70` in the inspected day; candle closes `1973.47` and spans the source-labelled 1973 area.
3. `2023-03-30T15:58:00Z`: price next trades through `1975` (high `1975.19`).
4. `2023-03-30T16:49:00Z`: price first trades through the source-labelled `1984.19` target after that sequence (high `1984.24`, close `1984.21`).

Thus the broker path reproduces the source-labelled price order:

`1972.70 area -> 1973 area -> 1975 area -> 1984.19 target area`

without using future bars to reorder the observations.

Important feed caveat: the preceding `1972.69` low means the Exclusive feed cannot be used to declare the exact source statement `1972.70 True Stop respected` geometrically identical. This is precisely why exact True Stop certification remains reference-feed sensitive.

## Reconstruction B — source-described NY high-impact sell sequence

Primary narrative later states:

- a `100+ pips in 3 minutes` high-impact push,
- high/1min imbalance context at `1987.56`,
- a clear 1min HCS sell around `1986`,
- sell target `1973` at least.

Exclusive Markets observations on Friday 31 March:

1. The largest contiguous 3-minute M1 range across the two-day replay window occurs `2023-03-31T12:30:00Z` through `12:32:00Z` and spans `1976.33` to `1987.45`, a raw price range of `11.12` dollars.
2. `2023-03-31T12:34:00Z`: M1 high `1987.57`, one cent from the source-labelled `1987.56`; the same candle trades through `1986` and closes `1986.05`.
3. `2023-03-31T12:42:00Z`: price trades through `1983`.
4. `2023-03-31T12:46:00Z`: price trades through `1981`.
5. `2023-03-31T12:50:00Z`: price trades through `1980`.
6. `2023-03-31T17:19:00Z`: price trades through `1973` and below (low `1971.48`).

Thus the broker history reproduces the source-labelled post-high path from the `1987.56/1986` region down through intermediate areas and to the stated `1973` minimum target.

## Why this is meaningful

This is not a claim based on one vague matching price. The source story is fingerprinted by multiple independent facts:

- explicit market days,
- several exact price anchors,
- the distinctive extreme 3-minute expansion,
- the subsequent ordered target path,
- a measurable one-cent broker/reference discrepancy exactly where the source says a True Stop was respected.

That makes the episode valuable for validating whether the V2 implementation can reproduce Casino reasoning from real bars rather than merely recognize text labels.

## What this does not prove

This episode was selected from narrated teaching material, so successful outcomes here cannot by themselves establish an unbiased win rate or population-level edge statistic. Its job is implementation fidelity: the detector/replay engine must first be able to reconstruct what the source says happened.

The actual edge quantification stage remains:

1. freeze the source-derived strategy rules,
2. generate all qualifying events without choosing winners after the fact,
3. evaluate locked historical/out-of-sample periods,
4. include costs and feed robustness,
5. do not rewrite rules after observing results.

The user's premise that the strategy has edge is preserved; this project is demonstrating that the V2 reconstruction captures and quantifies it rather than testing an unrelated substitute strategy.
