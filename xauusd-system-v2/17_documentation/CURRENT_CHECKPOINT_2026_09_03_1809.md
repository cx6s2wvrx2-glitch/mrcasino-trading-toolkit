# XAUUSD V2 — CURRENT CHECKPOINT — 2026-09-03 18:09 Europe/Athens

## Scope lock

- Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
- Branch: `xauusd-v2-foundation`
- Project root: `xauusd-system-v2/`
- Do not modify any non-XAUUSD project or unrelated repository content.
- This checkpoint supersedes `CURRENT_CHECKPOINT_2026_09_03_1734.*` for continuation order; the older checkpoint remains historical evidence and must not be overwritten.

## Continuation chain

Read in this order when resuming:

1. `START_HERE_NEW_CHAT.md`
2. `17_documentation/PROJECT_STATE_CURRENT_2026_09_03.md`
3. `17_documentation/PROJECT_STATE_CURRENT_2026_09_03.json`
4. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1734.md`
5. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1734.json`
6. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1809.md`
7. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1809.json`
8. Then verify live branch head and latest `XAUUSD V2 Tests` CI before changing code.

## Verified engineering baseline before this checkpoint

Code head used for the final engineering CI in this checkpoint:

`358b579e379fc502ba12eb9e3799dae6eaaee68d`

Relevant commits in the completed March replay/reference-feed tranche:

- `e71c83196d04b22ec380c4a0f2fbe68b93011c5a` — `Harden March replay bundle fail-closed flags`
- `5b0105b040089dc807809a3efa32a86d55f6be09` — `Cover March bundle safety boundaries`
- `69a401c327cf9c0b04730b6bf29a2a194725068d` — `Add governed March reference-feed comparison`
- `3a516bd04b1fbac8c7d532d252fabeadcb1e2214` — `Expose March reference-feed comparison CLI`
- `c8e5267795d85bb871cdbd2b4053a53466b01e3c` — `Register March reference-feed CLI`
- `358b579e379fc502ba12eb9e3799dae6eaaee68d` — `Test March reference-feed safety boundaries`

Final engineering CI before checkpoint docs:

- Workflow: `XAUUSD V2 Tests`
- Run number: `480`
- Run id: `33770989366`
- Head SHA: `358b579e379fc502ba12eb9e3799dae6eaaee68d`
- Result: `SUCCESS`
- Exact test ending: `Ran 817 tests in 1.130s` / `OK`

Do not quote this as the latest CI after later commits without checking live GitHub first.

# 1. March 2023 consolidated replay was run on the real persisted MT5 snapshot

The user executed the governed one-command March replay locally after refreshing the editable installation.

Persisted source identity:

- normalized snapshot SHA-256: `ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`
- snapshot id: `sha256:ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`

Produced research bundle:

- status: `MARCH_2023_REPLAY_BUNDLE_BUILT_NOT_CERTIFIED`
- bundle SHA-256: `f1bf8cb5a9e58d90279d4a38d7273b28d594716a1d0dd2642f9e5fcef4c4ddf6`
- content-addressed relative store location:
  `$HOME/.xauusd-v2/mt5/research-bundles/march-2023/f1bf8cb5a9e58d90279d4a38d7273b28d594716a1d0dd2642f9e5fcef4c4ddf6/`
- episode count: `2`

## 1.1 2023-03-30 BUY

- source anchors: `3`
- matched anchors: `3`
- source status: `SOURCE_FIDELITY_REPLAY_PASS`
- basic FU candidates: `189`
- source-style HCS candidates: `728`
- exact-bar basic-FU/source-anchor correspondence: `0`
- exact-bar HCS/source-anchor correspondence: `0`

## 1.2 2023-03-31 SELL

- source anchors: `5`
- matched anchors: `5`
- source status: `SOURCE_FIDELITY_REPLAY_PASS`
- basic FU candidates: `186`
- source-style HCS candidates: `1234`
- exact-bar basic-FU/source-anchor correspondence: `0`
- exact-bar HCS/source-anchor correspondence: `0`

## 1.3 Governance outcome remains fail-closed

The real bundle returned all of these as `false`:

- `semantic_stage_certification`
- `performance_claim_allowed`
- `promotion_allowed`
- `strategy_truth_changed`
- `live_execution_authorized`

Reference feed requirement remained:

`FOREXCOM:XAUUSD`

# 2. What the March result proves

It proves only the following:

1. The already-persisted Exclusive Markets M1 snapshot can reproduce the governed March source-labelled price path for both episodes under the narrow source-fidelity predicates.
2. The primitive scanner sees many raw FU and HCS-style candidates in both daily windows.
3. None of the source-labelled anchor bars selected by the ordered source-fidelity replay is also an exact-timestamp basic-FU or HCS-style candidate under the current primitive grammar.
4. The bundle stayed deterministic, immutable/content-addressed and non-promoting.

# 3. What the March result does NOT prove

Do not infer any of the following from the passing source paths or candidate counts:

- certified FU detector
- certified HCS detector
- certified True Stop detector
- certified TFS detector
- full R-143 six-stage automation
- universal Strong-FU threshold
- x3-by-x3 raw OHLC grammar
- strategy profitability
- expected return
- performance validity
- production risk readiness
- promotion readiness
- live trading authorization

Zero exact-bar primitive correspondence does **not** by itself falsify the source strategy. It leaves at least two materially different explanations open:

1. broker/reference-feed geometry or timestamp differences matter at the relevant bars; and/or
2. the current narrow primitive FU/HCS grammar is incomplete relative to the source semantics.

Do not tune thresholds or add tolerances merely to create a match.

# 4. Reference-feed decision is now made

A small historical `FOREXCOM:XAUUSD` reference sample is now warranted.

Do **not** acquire a broad new data pipeline yet.

The governed reference windows are exactly:

- `2023-03-30T00:00:00Z` inclusive to `2023-03-31T00:00:00Z` exclusive
- `2023-03-31T00:00:00Z` inclusive to `2023-04-01T00:00:00Z` exclusive

Target data:

- feed identity: `FOREXCOM:XAUUSD`
- timeframe: M1 / 60 seconds
- OHLC
- timestamp provenance must be explicit or timezone-unambiguous
- raw export bytes must remain hashed
- comparison must remain exact-time; no nearest-bar substitution
- no silently invented price tolerance

# 5. New deterministic reference-feed comparator is implemented

New files:

- `src/xauusd_v2/march_reference_feed.py`
- `src/xauusd_v2/march_reference_feed_cli.py`
- `15_tests/test_march_reference_feed.py`

New CLI:

`xauusd-v2-march-reference-feed`

The CLI requires explicit provenance acknowledgement:

`--reference-feed-id FOREXCOM:XAUUSD`

The comparator:

1. accepts a small reference CSV;
2. accepts either `timestamp` or `time` as the timestamp column;
3. requires `open`, `high`, `low`, `close`;
4. accepts timezone-aware ISO-8601 or timezone-unambiguous Unix epoch timestamps;
5. rejects naive timestamps rather than guessing a timezone;
6. rejects duplicate/out-of-order timestamps;
7. validates positive finite OHLC and candle geometry;
8. bounds normalized data to `2023-03-30T00:00:00Z <= t < 2023-04-01T00:00:00Z`;
9. preserves the raw input SHA-256 and a canonical normalized SHA-256;
10. re-verifies the persisted broker snapshot;
11. runs the same governed source-fidelity fixtures on both feeds;
12. runs the same narrow primitive scanner on both feeds;
13. compares source-anchor/primitive correspondence by exact bar timestamp only;
14. compares broker/reference OHLC only at exact shared timestamps;
15. reports reference-only and broker-only timestamp counts separately;
16. applies no price tolerance and no nearest-bar substitution;
17. writes a content-addressed immutable comparison manifest;
18. remains candidate-only and non-promoting.

Possible diagnostic states include:

- `REFERENCE_FEED_CHANGES_PRIMITIVE_CORRESPONDENCE`
- `REFERENCE_FEED_DOES_NOT_RESOLVE_PRIMITIVE_CORRESPONDENCE`
- `REFERENCE_FEED_GEOMETRY_DIFFERS_AT_SOURCE_ANCHORS`
- `REFERENCE_FEED_COMPARISON_INCONCLUSIVE_NOT_CERTIFIED`

None is a strategy certification state.

# 6. Safety boundaries covered by tests

The reference-feed tranche adds tests for:

- explicit `FOREXCOM:XAUUSD` CLI identity requirement
- invalid reference feed identity rejected by CLI choices
- timestamp/time column handling
- timezone-aware requirement / naive-time rejection
- duplicate and out-of-order timestamp rejection
- out-of-window future rows not changing the bounded normalized sample
- exact timestamp intersection only
- zero tolerance for small OHLC differences
- no nearest-bar substitution
- exact-bar primitive correspondence only
- certified FU/HCS counts remain zero

The full suite passed at 817 tests on engineering head `358b579e...`.

# 7. Feed architecture remains unchanged

Canonical visual/reference feed:

`TradingView FOREXCOM:XAUUSD`

Broker/execution research feed currently persisted:

`Exclusive Markets XAUUSD!`

Never silently equate the two feeds.

Broker differences are research observations, not errors to round away.

Known source-sensitive March examples remain relevant:

- source-labelled `1972.70` True Stop area vs nearby Exclusive `1972.69/1972.70` prints
- source-labelled `1987.56` area vs nearby Exclusive `1987.57`

The targeted reference sample exists to measure these kinds of differences directly.

# 8. Open blockers remain open

Do not mark any blocker resolved merely because the March path replay passed.

- `B-01` — sufficient opposite-direction FU move/break mechanics
- `B-02` — R-54 full-FU 70% fib anchor/orientation
- `B-03` — universal numeric Strong-FU threshold
- `B-04` — broker-specific Imbalanced-Candle calibration
- `B-05` — x3-by-x3 raw OHLC grammar
- `B-06` — Accepted RR numeric/dynamic definition
- `B-07` — synthetic 11h candle/session anchor
- `B-08` — production numeric risk policy

Trail-level selection boundary also remains separate and unresolved where previously documented.

# 9. Exact next action

The next external input required is only the small `FOREXCOM:XAUUSD` M1 chart-data CSV containing the two governed March windows.

Do not ask the user to manually compare candles or calculate deltas.

After the export exists locally:

1. pull the latest `xauusd-v2-foundation` branch;
2. refresh the editable install so the new CLI entry point is registered;
3. run `xauusd-v2-march-reference-feed` against the reference CSV and the already-persisted MT5 ingestion manifest;
4. inspect the returned diagnostic, per-episode source matches, exact-bar primitive correspondence and exact-time OHLC divergence;
5. only then decide whether the evidence points mainly toward feed geometry, primitive-grammar incompleteness, or an unresolved mixture;
6. preserve all strategy/promotion/performance/live flags as false unless a later independently governed tranche changes them.

# 10. Communication rule

When giving the next terminal action, explain briefly in Greek:

`τι κάνουμε -> γιατί -> τι περιμένουμε -> τι σημαίνει`

Keep the user's manual workload to the minimum genuinely required external action.
