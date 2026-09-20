# Primary Narrated Replay Episode — 2023-03-30 / 2023-03-31

Status: REPLAY PREPARATION / HIGH-VALUE NARRATED EPISODE
Authority: approved primary Mr Casino Price Action Reflection material
Visual source ID: `221336f1-a2f8-44d7-8506-e15ec580c7dd`
Visual archive: `PRICE ACTION REFLECTION.zip`
Strategy truth changed: no
Promotion allowed: no
Live execution authorized: no

## Why this episode matters

This episode is materially stronger for historical reconstruction than a chart with only an approximate date because the primary Discord narrative explicitly identifies the market days being reviewed:

- it starts with `Thursday the 30th`,
- the later post says it is reviewing `Friday the 31st`,
- the Discord messages carrying the review are dated 3 April 2023,
- the source gives multiple exact price labels and an explicit chronological story rather than only drawn chart geometry.

The Price Action Reflection visual index already records the 2023-04-02 visual episode as `paired_with_primary_text_dataset`. This file treats the underlying market story as the 30–31 March 2023 replay episode; it does not treat the 3 April retrospective post time as a live signal time.

## Primary-source narrative anchors

The source explicitly names the following prices/roles within the narrative:

- `1972` — untested 45min HCS zone of manipulation / major liquidity context.
- `1972.19` — liquidity being left behind.
- `1972.70` — True Stop described as respected in the buy-establishment recap.
- `1973` — strongest 1min FU closure used for an advanced buy entry after buys were established.
- `1975` — easy 1min HCS re-entry after stronger manipulation/low-liquidity context around 1973.
- `1984` / `1984.19` — major/clear IMB upside target context.
- `1987` / `1987.56` — higher zone / 1min IMB context after the NY high-impact move.

The same narrative says the NY high-impact move produced `100+ pips in 3 minutes` before the later sell-side analysis.

## Independent broker-data reconnaissance already performed

The exact user-supplied Exclusive Markets raw M1 export (source SHA-256 `691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0`) was inspected without altering the persisted snapshot.

On the Exclusive Markets feed:

### Thursday 30 March 2023

- the 1972 area is present repeatedly,
- at `2023-03-30T15:52:00Z` the M1 low is `1972.69`,
- at `2023-03-30T15:53:00Z` the M1 low is exactly `1972.70`,
- the subsequent move reaches `1984.24` at `2023-03-30T16:49:00Z`.

This is an important feed-sensitive observation: the primary narrative says `1972.70 true stop respected`, while this broker feed prints one M1 low one cent below that price immediately before an exact `1972.70` low. No tolerance is invented. Exact True Stop geometry therefore remains a reference-feed question until `FOREXCOM:XAUUSD` is aligned.

### Friday 31 March 2023

- the largest observed three-minute range in the relevant high-impact burst is `11.12` dollars, from `1976.33` to `1987.45`, across `2023-03-31T12:30:00Z` through `12:32:00Z`,
- the source-labelled `1987.56` level is reached to within one cent on this broker feed: M1 high `1987.57` at `2023-03-31T12:34:00Z`,
- this strongly fingerprints the source's `100+ pips in 3 minutes` + `1987.56` narrative against the real historical market path without claiming the two feeds are identical.

## What this establishes

This episode supplies a high-information source-to-market fingerprint:

1. explicit market days,
2. multiple exact source-labelled prices,
3. a distinctive three-minute high-impact burst,
4. source-described HCS / FU / True Stop / liquidity / target relationships,
5. real broker history that reproduces the same broad chronological price story with measurable feed differences.

It is therefore a strong candidate for component-level historical replay and for later cross-feed validation against the canonical `FOREXCOM:XAUUSD` reference feed.

## What it does NOT establish yet

- The one-cent `1972.69` Exclusive Markets print is not silently rounded into `1972.70 respected`.
- No broker-vs-reference tolerance is invented.
- The retrospective Discord post time is not treated as the stage occurrence time.
- This episode is not automatically declared a complete six-stage R-143 fixture unless every R-143 stage can be source-labelled and tied to closed bars without hindsight.
- B-01 through B-08 remain governed exactly as before.

## Deterministic replay window

Use broker-market window:

- start inclusive: `2023-03-30T00:00:00Z`
- end exclusive: `2023-04-01T00:00:00Z`

This window is an engineering replay boundary around the explicitly narrated Thursday/Friday market days, not a strategy rule.

## Next step

Use the machine-readable anchor set `PRIMARY_REPLAY_EPISODE_2023_03_30_31_ANCHORS.json` to build one immutable broker replay slice and measure every source-labelled price against it. Then evaluate which source-described components can be tied to closed bars deterministically. Exact True Stop certification remains dependent on the canonical `FOREXCOM:XAUUSD` reference geometry where the broker differs.
