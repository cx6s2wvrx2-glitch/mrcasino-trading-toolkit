# XAUUSD V2 — CANONICAL PROJECT STATE / NEW-CHAT HANDOFF

Date: 2026-09-03
Status: ACTIVE RESEARCH / STRATEGY RECONSTRUCTION / HISTORICAL REPLAY
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
Branch: `xauusd-v2-foundation`
Project root: `xauusd-system-v2/`

This file exists so a fresh conversation can continue without losing project state. It is a continuity artifact, not strategy truth and not a live-trading authorization.

---

## 1. SCOPE AND GOVERNANCE

Only work inside `xauusd-system-v2/` plus necessary XAUUSD-specific workflows.
Never touch Flowstate, LUMOS, THRV, gym, or unrelated repository content.

Authority hierarchy:

1. approved primary Mr Casino source;
2. approved secondary/corroborative source;
3. helpers/beta code only as engineering references.

Core safety rules:

- V2 is clean-room.
- Helpers never become strategy truth.
- Ambiguity => fail closed / `NO TRADE` / `NOT CERTIFIED` / `BLOCKED`.
- No LLM live authority.
- No auto-promotion.
- Live execution disabled.
- Reflection evidence `[C]/[I]/[U]/[E]` never auto-promotes.
- Do not invent numeric thresholds, tolerances, anchors, expiry rules, RR definitions, or session rules.
- Do not rewrite rules after seeing historical outcomes to make a backtest look better.

Canonical agents remain:

- Knowledge
- Strategy Formalization
- XAUUSD Data
- Market State/Context
- Quant Research/Backtesting
- Independent Validation
- Deterministic Risk
- Continuous Improvement

User research premise: the strategy has edge; the project objective is to reconstruct it faithfully, demonstrate that the implementation captures it, and quantify it. Do not substitute a different strategy and call that a test of Casino.

---

## 2. CANONICAL OPEN BLOCKERS

Keep these open unless a primary source or explicit user instruction resolves them:

- `B-01` — FU sufficient opposite-direction move/break mechanics.
- `B-02` — R-54 numeric 70% full-FU Fib anchor/orientation.
- `B-03` — universal numeric Strong-FU threshold only. Timeframe scope itself is resolved: Strong FU / ATT FU primitive logic is the same concept on every timeframe.
- `B-04` — broker-specific Imbalanced-Candle calibration.
- `B-05` — x3-by-x3 raw OHLC grammar.
- `B-06` — Accepted RR numeric/dynamic definition.
- `B-07` — synthetic 11h candle/session anchor.
- `B-08` — production risk policy numeric values.

Separate known boundary: Reflection R-150 gives Trail-level ordering/context but no certified Trail selector.

Never resolve any of the above by convenience or optimization.

---

## 3. USER CLARIFICATIONS THAT MUST BE PRESERVED

### 3.1 FU / ATT FU timeframe scope

User clarification:

> strong fu - att fu ειναι η ιδια νοοτροπια σε ολα και καθε timeframe οχι μονο στο 1m

Operational meaning:

- Strong FU / ATT FU primitive concept is timeframe-neutral/fractal.
- 1m is not a special primitive definition.
- Timeframe changes authority, context, scale, top-down weighting and use.
- A specific 1m-only zone construction can remain 1m-scoped without making Strong FU itself 1m-only.

Canonical source record:
`01_sources/USER_CLARIFICATION_FU_TIMEFRAME_SCOPE_2026_09_02.md`

### 3.2 TradingView feed

User reported Casino instruction:

> when looking at TradingView use only Forex.com because the others are not good.

Primary-source feed guidance also prioritizes IC Markets / Forex.com and explicitly acknowledges broker candle differences.

Operational architecture:

- TradingView canonical visual/reference feed: `FOREXCOM:XAUUSD`.
- Broker feeds: execution/broker-specific research, spread/cost/robustness.
- Exclusive Markets `XAUUSD!` is NOT silently treated as identical to Forex.com.
- Feed disagreements are measured, never rounded away to manufacture agreement.

Canonical record:
`01_sources/PRIMARY_FEED_GUIDANCE_2024_04_28.md`

### 3.3 Common higher timeframes observed by user

User reports that in the group he sees these used frequently:

`1h / 2h / 3h / 5h / 7h / 11h`

This is preserved as observational priority metadata, not automatic strategy truth or a mandatory set.

Canonical record:
`01_sources/USER_OBSERVATION_COMMON_HTF_USAGE_2026_09_03.md`

---

## 4. AGENT-06 — CLOSED, DO NOT RERUN

Agent-06 external paid validation is complete and closed.
Do not call Anthropic/Claude again for Agent-06 closure and do not ask the user for an API key.

### V1 provider run

- Run ID: `agent06-anthropic-20260903T040444Z`
- Provider: Anthropic
- Model: `claude-sonnet-5`
- Repo commit: `50f9a434bcc678a7b04494ff457ed4fd980f8e8f`
- Full packet SHA: `e9dd198f166dc7d4d22d1f921b00c4a84c02e36a3d7e5ec734b7703379e5ab4f`
- Bundle SHA: `6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf`
- Context manifest SHA: `e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37`
- Predictions SHA: `fd2d3584ecde9d5b1b1804a8566d764057587297b53bdcbe0297e602e2b7ce0f`
- Runtime manifest SHA: `d7c0aab96b7ed71852fd583018933e129471b7dc87ba8e6d902ce0ddedf7ff89`
- 173/173 completed.
- 10 provider abstentions.

Collision-aware V1 result:

- 144 EXACT_AGREE
- 6 LOCATOR_SET_AGREE
- 13 UNRESOLVED_DISAGREE
- 10 ABSTAIN

Collision-neutral IDs:
`GT-R09-002, GT-R09-003, GT-R10-002, GT-R10-004, GT-R10-007, GT-R10-012`

### Focused V2 run

- Run ID: `agent06-focus-anthropic-20260903T084504Z`
- Repo commit: `1a19818559230d9452783caea7a59d0a424a0882`
- Packet SHA: `696df8f457c03854bc4d3445d9b9cebb23cb3b4625f9a6a9b96bbf827ed9e635`
- Predictions SHA: `4db60c6dc0b0e76e488fdcaa9ce868464b15de109557bffd29b78d7f0c9eba14`
- Runtime manifest SHA: `251e1f66c4509d51ba0ea6a809d11058ffffd64b51e971a048c684d16ed074db`
- Source review SHA: `26ff679f827ba4ffdcf5d41a8900642f51d10c3202d06731b879eb6992edf565`
- 23/23 complete.
- 19 SUPPORTED
- 0 CONTRADICTED
- 4 INSUFFICIENT

Four evidence-open cases:

- `GT-R02-020`
- `GT-R13-002`
- `GT-R13-006`
- `GT-R13-026`

Final closure status:
`AGENT06_EXTERNAL_VALIDATION_CLOSED_WITH_UNRESOLVED_EVIDENCE`

Finalizer invariants:

- all cases accounted for = true
- artifact integrity passed = true
- blockers = []
- paid provider work complete = true
- no further provider calls required for Agent-06 closure = true
- provider calls performed by finalizer = false
- promotion allowed = false
- independent validation auto-promoted = false
- live execution authorized = false
- strategy truth changed = false

Local closure report previously produced:
`~/agent06_final_closure.json`

---

## 5. EXCLUSIVE MARKETS MT5 DATA — COMPLETED FOUNDATION

The user runs MetaTrader 5 under Wine on Mac.
Current usable broker account for dataset provenance: Exclusive Markets demo, Standard Plus account type, server `ExclusiveMarkets-Demo`, symbol `XAUUSD!`, description `Gold 100oz (Spot)`.

Do not use the deleted/invalid old FTMO account as canonical data.

### 5.1 Full M1 export

Original user file:
`XAUUSD!_M1_202101040100_202609031251.csv`

Source properties:

- exact rows: `1,999,671`
- source SHA-256: `691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0`
- normalized SHA-256: `ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`
- snapshot ID: `sha256:ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`
- actual delimiter: TAB despite `.csv`
- first raw server timestamp: `2021-01-04 01:00:00`
- last raw server timestamp: `2026-09-03 12:51:00`
- first UTC: `2021-01-03T23:00:00+00:00`
- last UTC: `2026-09-03T09:51:00+00:00`
- duplicates: 0
- out-of-order: 0
- invalid/nonfinite OHLC: 0
- source gap count: 1,604
- gaps are preserved, never filled.

### 5.2 Timezone provenance

Exclusive Markets support explicitly confirmed:

- winter GMT+2
- summer GMT+3
- DST-aware

Technical ingestion timezone: `EET` through Python zoneinfo.

Canonical record:
`17_documentation/EXCLUSIVE_MARKETS_MT5_TIMEZONE_CONFIRMATION_2026_09_03.md`

### 5.3 Persisted local store

User successfully persisted the immutable snapshot under:

- raw source: `/Users/nikolaosgiannopoulos/.xauusd-v2/mt5/raw/691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0/source.mt5.txt`
- canonical snapshot: `/Users/nikolaosgiannopoulos/.xauusd-v2/mt5/snapshots/ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24/xauusd_ohlc.csv`
- ingestion manifest: `/Users/nikolaosgiannopoulos/.xauusd-v2/mt5/ingestions/691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0--ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24.json`

Do not ask for a second full M1 export.

Canonical snapshot record:
`17_documentation/EXCLUSIVE_MARKETS_MT5_SNAPSHOT_2026_09_03.md`

---

## 6. MULTI-TIMEFRAME DATA — COMPLETED BROKER VALIDATION

Deterministic derived broker timeframes currently governed:

`M5, M10, M15, M30, H1, H4, H8, D1`

M1 remains the raw base. No need for duplicate full-history exports for each timeframe.

Derived build result from 1,999,671 M1 bars:

- M5: 400,019 bars
- M10: 200,163
- M15: 133,448
- M30: 66,737
- H1: 33,385
- H4: 8,741
- H8: 4,374
- D1: 1,458

No gaps were filled. `partial_omitted=1` on each derived series at the frozen source horizon was expected.

### Native MT5 validation

Representative native samples for H1/H4/H8/D1 passed exactly against deterministic M1 aggregation:

- H1: 3,976/3,976 exact OHLC matches, 0 missing, 0 mismatch.
- H4: 1,039/1,039 exact, 0 missing, 0 mismatch.
- H8: 520/520 exact, 0 missing, 0 mismatch.
- D1: 173/173 exact, 0 missing, 0 mismatch.

Total exact comparisons: `5,708 / 5,708`.

Canonical record:
`17_documentation/EXCLUSIVE_MARKETS_NATIVE_MTF_VALIDATION_2026_09_03.md`

Do not rerun these exports or comparisons unless the code contract itself changes materially.

---

## 7. TIMEFRAME UNIVERSE / MULTI-CONFIRMATION

The old beta helper literally configures 25 minute-based timeframes:

`1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,20,30,35,40,45,50,55,60,90,100` minutes.

This is helper/beta evidence only, not strategy truth.

Primary source material also adds higher/custom layers such as:

`4D, D1, 18h, 15/14h, 12h, 11h, 7h, 5h, 4h, 3h, 1h, 50m`

and multi-horizon TFS concepts (macro/scalp/intraday/swing/extreme swing).

The user additionally reports frequent group usage of:
`1h, 2h, 3h, 5h, 7h, 11h`.

Governed registry:
`src/xauusd_v2/timeframe_registry.py`

Important:

- Do not freeze V2 to only 8 derived TFs or only the beta 25.
- Do not assume all custom TF candle anchors.
- 11h synthesis remains fail-closed under `B-07` until the correct session/anchor is certified.

Canonical inventory:
`17_documentation/MULTI_TIMEFRAME_SOURCE_INVENTORY_2026_09_03.md`

---

## 8. HISTORICAL REPLAY — FIRST IMMUTABLE EPISODE

Primary source episode:
`top down analysis (1).zip#sequence:2023-11-01`

Replay slice created from the immutable Exclusive M1 snapshot:

- status: `REPLAY_MARKET_SLICE_BUILT`
- episode ID: `casino-2023-11-01`
- bars: 13,665
- first UTC: `2023-10-23T00:00:00Z`
- last UTC: `2023-11-03T20:59:00Z`
- gap count: 11
- low: 1953.43
- high: 2009.37
- slice SHA: `eefa2503777b576394f926e3e22555eb0b9dd4e194a24dae8ac6dcab5ed04399`

Local slice paths:

- CSV: `/Users/nikolaosgiannopoulos/.xauusd-v2/mt5/replay-slices/ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24/casino-2023-11-01/eefa2503777b576394f926e3e22555eb0b9dd4e194a24dae8ac6dcab5ed04399/m1.csv`
- manifest: same directory, `manifest.json`

Source-price anchor alignment for `1975.00` passed:

- within replay range: true
- touched: true
- closest distance: 0
- 177 M1 touch bars over the broad replay window.

Within `2023-11-01` UTC specifically:

- touch clusters: 4
- first strict low below 1975: `16:44Z`
- first close below 1975: `18:41Z`

This episode remains source-timestamp blocked for exact stage certification. Do not infer screenshot market time from filenames or chart pixels.

Relevant files:

- `06_examples/PRIMARY_REPLAY_EPISODE_2023_11_01.md`
- `06_examples/PRIMARY_REPLAY_EPISODE_2023_11_01_ANCHORS.json`
- `src/xauusd_v2/replay_slice.py`
- `src/xauusd_v2/replay_alignment.py`
- `src/xauusd_v2/replay_anchor_path.py`
- `src/xauusd_v2/replay_stage_certification.py`
- `src/xauusd_v2/replay_candidate_registry.py`

---

## 9. CURRENT HIGH-VALUE REPLAY EPISODE — 30–31 MARCH 2023

This is the current main implementation-fidelity episode because the primary narrative supplies a distinctive ordered sequence with multiple explicit price anchors.

Canonical primary narrative record:
`01_sources/PRIMARY_NARRATIVE_2023_03_30_31.md`

Retrospective source-to-broker reconstruction record:
`17_documentation/SOURCE_NARRATED_OUTCOME_RECON_2023_03_30_31.md`

### 9.1 Buy sequence — source narrative

Primary narrative includes:

- 45m HCS / manipulation context around 1972
- liquidity at `1972.19`
- `1972.70` True Stop respected
- strongest 1m FU closure around `1973`
- 5m ATT FU retest / advanced entry context
- easy 1m HCS re-entry around `1975`
- `1984.19` clear imbalance / upside target context

Exclusive Markets observations already located:

- `2023-03-30T15:52:00Z`: M1 low `1972.69`
- `2023-03-30T15:53:00Z`: M1 low exactly `1972.70`, close `1973.47`
- `2023-03-30T15:58:00Z`: trades through `1975`, high `1975.19`
- `2023-03-30T16:49:00Z`: first trades through `1984.19`, high `1984.24`, close `1984.21`

Observed ordered path:
`1972.70 area -> 1973 area -> 1975 area -> 1984.19 target area`

Feed caveat is critical: Exclusive prints `1972.69` one bar before exact `1972.70`. Therefore broker geometry cannot certify the exact Forex.com/source True Stop statement. This is a real cross-feed test case, not a rounding problem to hide.

### 9.2 Sell sequence — source narrative

Primary narrative includes:

- `100+ pips in 3 minutes`
- major liquidity left below
- right place to form daily FU downside
- 1m imbalance at `1987.56`
- clear 1m HCS sell around `1986`
- target at least `1973`
- later 15m doji/big-wick and 15m HCS re-entry context

Exclusive Markets observations already located:

- largest contiguous 3-minute range across the two-day window: `2023-03-31T12:30Z` through `12:32Z`, roughly `1976.33 -> 1987.45`, raw range $11.12
- `12:34Z`: high `1987.57`, one cent from source `1987.56`, same candle trades through 1986 and closes `1986.05`
- `12:42Z`: through 1983
- `12:46Z`: through 1981
- `12:50Z`: through 1980
- `17:19Z`: through 1973 and below, low `1971.48`

This is a distinctive source fingerprint and is the current best component-replay case.

---

## 10. NEW SOURCE-FIDELITY REPLAY LAYER — IMPLEMENTED

Files added:

- `06_examples/SOURCE_FIDELITY_2023_03_30_BUY.json`
- `06_examples/SOURCE_FIDELITY_2023_03_31_SELL.json`
- `src/xauusd_v2/source_fidelity_replay.py`
- `src/xauusd_v2/source_fidelity_replay_cli.py`
- `15_tests/test_source_fidelity_replay.py`

CLI:
`xauusd-v2-source-fidelity-replay`

Purpose:

- measure whether explicit source-narrated anchors occur in the required chronological order in the immutable broker snapshot;
- measure distinctive expansion windows such as the 3-minute March 31 burst;
- reject duplicate anchor IDs, unknown predicates, noncontiguous expansion probes, same-bar cheating for ordered anchors, timeframe mismatch, and promotion flags;
- preserve broker/reference differences instead of inventing tolerance;
- never certify strategy truth or performance by itself.

The source-fidelity layer is implementation-fidelity evidence, not an unbiased edge statistic.

---

## 11. NEW PRIMITIVE REPLAY SCAN — IMPLEMENTED AND CURRENT

Files:

- `src/xauusd_v2/primitive_replay_scan.py`
- `src/xauusd_v2/primitive_replay_scan_cli.py`
- `15_tests/test_primitive_replay_scan.py`

CLI:
`xauusd-v2-primitive-scan`

Current contract:

- scans an explicit finite window of a verified immutable MT5 snapshot;
- classifies only the narrow existing **basic FU candidate**: one-sided previous-candle liquidity sweep + opposite candle direction;
- both-side sweeps remain `AMBIGUOUS` and are not silently assigned to an FU side;
- records the swept-side wick interval objectively;
- records later closed-bar wick interactions;
- if a later interaction bar is itself a basic FU candidate, marks a **source-style HCS candidate**;
- accepts both continuation-form and negation-form candidate pairs;
- does not certify FU or HCS;
- does not invent near-enough tolerance, Strong-FU threshold, 70% fib anchor, x3 grammar, doji threshold, or expiry;
- skips classification across noncontiguous parent bars / market-data gaps and reports `adjacency_gap_pairs_skipped`;
- no intrabar ordering is inferred from OHLC.

Current output invariants:

- `certified_fu_count = 0`
- `certified_hcs_count = 0`
- `strategy_truth_changed = false`
- `promotion_allowed = false`
- `live_execution_authorized = false`
- blockers preserved: `B-01`, `B-02`, `B-03`, `B-05`

Important recent engineering history:

- initial primitive-scan tests exposed that some synthetic fixtures accidentally swept both sides while expecting one-sided FU candidates;
- fixtures were corrected instead of weakening the fail-closed classifier;
- provisional-bar removal is now correctly treated as a data gap, so nonadjacent closed bars are not pretended to be consecutive candles;
- CLI now exposes the gap diagnostic.

Current green baseline before this handoff artifact:

- commit: `5b0397a59460f8586d72d9c8154b1351f309efec`
- workflow: `XAUUSD V2 Tests`
- run number: 454
- run ID: `33765119945`
- result: `success`

A fresh chat must fetch the current branch head because the handoff-document commits themselves may be newer than this baseline.

---

## 12. EXISTING SEMANTIC COMPONENTS THAT MUST NOT BE DUPLICATED

Before adding new detectors, inspect and reuse the existing modules:

- `fu_basic_candidate.py`
- `fu_observables.py`
- `fu_completion.py`
- `fu_criteria.py`
- `fu_intrabar_evidence.py`
- `fu_liquidity_bridge.py`
- `fu_retest_quality.py`
- `hcs_semantic.py`
- `negation_semantic.py`
- `x3_semantic.py`
- `x3_by_x3_boundary.py`
- `tfs_semantic.py`
- `tfs_research_scale.py`
- `true_stop_semantic.py`
- `liquidity_taxonomy.py`
- `doji_liquidity_semantic.py`
- `zone_geometry.py`
- `candidate_detectors.py`
- `target_semantic.py`
- `ltf_execution.py`
- `backtest_sequence.py`
- `component_replay.py`
- `component_replay_dataset.py`
- `historical_replay_gate.py`
- `historical_reproducibility.py`

Do not build parallel competing definitions when an existing semantic boundary already exists.

---

## 13. R-143 SIX-STAGE REPLAY TARGET

The current canonical end-to-end sequence is:

1. HCS zone reaction
2. TFS
3. LAOL met/taken
4. True Stop respected
5. 10m True Stop established
6. targets/timing

Current architecture already enforces ordered, lookahead-safe stage availability through `component_replay.py` and related replay certification code.

The project must eventually be able to say at historical time T:

> using only evidence legitimately available by T, the system sees these confirmations and returns BUY / SELL / NO TRADE candidate state.

No stage may use a later candle before it closed.

---

## 14. CURRENT RESEARCH INTERPRETATION OF SOURCE MATERIAL

Primary HCS wording preserved in the corpus:

> HCS — price forms a new FU retesting last FU wick.

Do not restrict the second FU to only same-direction continuation. Source material contains continuation and negation-form HCS concepts. HCS validity is tied to the new manipulation occurring on the retest; direction characterizes the form.

Primary True Stop / TFS relationship preserved:

- TFS is confirmed prevalent direction, evaluated after candle close.
- refined entries require 10/15m+ confirmation context.
- each wave of true price action is based on 10m+ HCS/negation manipulation.
- Main HTF True Stop is the low/high alignment of required 10m+ TFS factors; it must be respected before LTF HCS/negation entry upon final liquidity calculation.

Primary liquidity/target relationship preserved:

- 30m+ core liquidity marking prioritizes big wick to fill and unmanipulated doji;
- breakout liquidity is optional/advanced;
- ATT-FU liquidity is refinement/concentrated-area context under the later R-207 workflow;
- major liquidity + HTF manipulation and subsequent strong FU/HCS can support a hold toward the opposite last area;
- rapid move between concentrated liquidity areas is source-supported context, but do not invent a numeric speed/expiry rule.

---

## 15. WHAT IS ALREADY PROVEN VS WHAT IS NOT

Already demonstrated:

- the Exclusive Markets full M1 history is reproducible, immutable and content-addressed;
- timezone provenance is explicit and DST-aware;
- deterministic M1 -> H1/H4/H8/D1 reconstruction matches native MT5 exactly on 5,708 representative candles;
- source-labelled historical price stories can be located in the immutable broker history;
- March 30–31 2023 provides multiple ordered source anchors and a distinctive expansion fingerprint;
- the codebase has lookahead-safe replay primitives and fail-closed semantic gates;
- independent Agent-06 source validation is closed without auto-promotion.

Not yet demonstrated/completed:

- exact raw-market certified FU detector under full Casino criteria (`B-01` remains important);
- certified universal Strong-FU numeric threshold (`B-03`);
- exact Forex.com reference-feed geometry for feed-sensitive March 2023 True Stop / imbalance details;
- certified custom timeframe candle anchors for all Casino-used TFs, especially 11h (`B-07`);
- complete automatic R-143 stage extraction from raw bars;
- unbiased all-event population backtest with frozen rules;
- locked OOS / walk-forward performance;
- spread/slippage/cost sensitivity across broker feeds;
- production numeric risk policy (`B-08`);
- paper/shadow live verification;
- live execution authorization.

---

## 16. NEXT ACTION — CONTINUE HERE

Do not restart from source collection or MT5 setup.

### Immediate engineering/research next steps

1. **Use the March 30–31 source-fidelity fixtures against the user's already-persisted immutable M1 snapshot and freeze the generated reports/hashes.**
   This is the next local-data execution step when the user is needed.

2. **Run the primitive replay scanner over narrow March 30 and March 31 windows** around the source-described sequences.
   Goal: measure whether the source-labelled 1973 / 1975 / 1986 areas line up with raw basic-FU and wick-retest candidate observations without pretending those candidates are certified FU/HCS.

3. **Build a deterministic bridge report** that compares:
   - source narrative labels,
   - source-fidelity anchor path,
   - primitive raw candidates,
   - existing semantic component gates,
   while explicitly naming which R-143 stages are source-labelled only, raw-observable, semantically executable, or still blocker-bound.

4. **Do not resolve B-01/B-03 by optimizing March 2023.**
   Use the episode for implementation fidelity, not to tune an arbitrary threshold to one winner.

5. **Acquire a small historical `FOREXCOM:XAUUSD` reference sample only when needed** for feed-sensitive exact geometry around 30–31 March 2023. Do not replace the Exclusive execution dataset. The user should be asked only when the code/reference-feed stage genuinely requires it.

6. After the March component replay is stable, expand to additional primary source episodes and then freeze rules before population-level backtesting.

7. Then perform locked OOS / walk-forward / cost and broker robustness research.

### Current user involvement

At the moment of this handoff, no additional full MT5 data export is needed.
The next likely user-needed input is a small Forex.com historical reference sample or a local command run against the already-persisted snapshot, not a repeat of setup.

---

## 17. NEW-CHAT OPERATING INSTRUCTION

In a fresh chat:

1. Read `START_HERE_NEW_CHAT.md` and this file.
2. Read `PROJECT_STATE_CURRENT_2026_09_03.json` for machine-readable exact identifiers.
3. Fetch current branch head and latest `XAUUSD V2 Tests` status.
4. Search the repo before creating any module to avoid duplication.
5. Continue from Section 16.
6. Do not ask the user to re-explain the project, resend the full MT5 file, rerun Agent-06, or repeat native MTF validation.

The desired communication style with the user is simple Greek. Before any command that the user must run, explain in plain language: **τι κάνουμε -> γιατί -> τι αποτέλεσμα περιμένουμε -> τι σημαίνει**. Avoid turning the user into a blind terminal operator.
