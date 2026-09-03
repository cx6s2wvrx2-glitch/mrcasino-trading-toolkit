# XAUUSD V2 — CURRENT CHECKPOINT — 2026-09-03 20:18 Europe/Athens

## Scope lock

- Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
- Branch: `xauusd-v2-foundation`
- Project root: `xauusd-system-v2/`
- Do not modify any non-XAUUSD project or unrelated repository content.
- Older checkpoints remain immutable historical evidence.

## Continuation order

1. `START_HERE_NEW_CHAT.md`
2. `17_documentation/PROJECT_STATE_CURRENT_2026_09_03.md/.json`
3. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1734.md/.json`
4. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1809.md/.json`
5. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1823.md/.json`
6. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1859.md/.json`
7. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1907.md/.json`
8. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_2018.md/.json`
9. Verify live branch head and latest `XAUUSD V2 Tests` CI before changing code.

# 1. Reference feed remains unresolved

`FOREXCOM:XAUUSD = REQUIRED / DEFERRED / NOT ALIGNED`

This remains an access/cost deferral only. No broker/reference-feed equivalence is inferred.

# 2. New FU-criteria-gap diagnostic completed on real March snapshot

Governed broker snapshot:

- normalized SHA-256: `ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`
- snapshot id: `sha256:ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`

Report:

- status: `MARCH_HCS_FU_CRITERIA_GAP_DIAGNOSTIC_COMPLETE_NOT_CERTIFIED`
- report SHA-256: `870db1f5f0dc77ea5d3bce2c0f6f81b6379df8b834e16d8bccf68c79038948e7`
- report root: `~/.xauusd-v2/mt5/research-bundles/march-2023-hcs-fu-criteria-gap/870db1f5f0dc77ea5d3bce2c0f6f81b6379df8b834e16d8bccf68c79038948e7`
- `fu_criteria_certified = false`
- `semantic_stage_certification = false`
- `performance_claim_allowed = false`
- `promotion_allowed = false`
- `live_execution_authorized = false`
- `strategy_truth_changed = false`

## 1975 HCS re-entry

Aggregate:

- source-level touches: `4`
- exact latest-basic-FU-proxy-wick retests: `1`
- conditional Attempted-FU Form 2 on exact retest: `1`
- conditional Complete FU on exact retest: `0`
- diagnostic: `EXACT_RETEST_HAS_CONDITIONAL_ATTEMPTED_FU_FORM_2_BLOCKED_BY_FU_CRITERIA`

Critical bar:

- `2023-03-30T12:31:00Z`
- OHLC: `1974.24 / 1975.35 / 1973.12 / 1975.06`
- latest prior basic-FU proxy: `2023-03-30T12:28:00Z`, bullish
- prior proxy wick: `1973.34` to `1973.75`
- exact latest-basic-FU-proxy wick retest: `true`
- observed Reflection completion: `not_certified`
- counterfactual completion only if FU criteria later become certified: `attempted_fu_form_2`
- raw observables: bullish, previous high swept, previous low not swept, close above previous body, close not within previous body
- liquidity taken / opposite-direction move / same-candle semantic sequence: all unresolved from parent M1 OHLC
- HCS remains not certified.

The adjacent `12:32` bar is Reflection `attempted_fu_form_1`, but it does not exact-retest the latest basic-FU-proxy wick. Do not merge `12:31 + 12:32` into a permissive two-candle HCS.

Governed interpretation:

The immediate `1975` mismatch is no longer a generic HCS-geometry failure. The strict retest geometry is present. If the source-required FU criteria were independently certified for the same `12:31` candle, its Reflection completion geometry would be Attempted FU Form 2. The remaining immediate semantic blocker is therefore FU-criteria evidence for that same candle, not permission for a `+1 candle` HCS rule.

# 3. 1986 control result

Aggregate:

- source-level touches: `8`
- exact latest-basic-FU-proxy-wick retests: `4`
- conditional Attempted-FU Form 2 on exact retest: `4`
- conditional Complete FU on exact retest: `0`
- FU criteria remain not certified.

At the previously strict-positive `2023-03-31T12:36:00Z` bar:

- exact latest-basic-FU-proxy wick retest: `true`
- latest prior basic-FU proxy: `12:35`, bullish, wick `1984.25` to `1986.09`
- counterfactual Reflection completion if FU criteria were met: `attempted_fu_form_2`
- observed Reflection completion remains `not_certified`.

This confirms that the raw `basic-FU proxy` family and the source Reflection completion classes are not interchangeable.

# 4. Source-liquidity boundary around 1975

Primary March narrative explicitly identifies `1974.91` as a broker 1m double-bottom liquidity feature and says the 1975 HCS closed after liquidity/manipulation. However the governed `12:30` M1 bar already traded down to `1972.94`, below `1974.91`, before the `12:31` candidate opened.

Therefore `1974.91` must not be silently assigned as the liquidity first taken by the `12:31` FU candidate. It is valid contextual source evidence, not a certified per-candle FU liquidity reference.

# 5. Existing intrabar architecture

`fu_intrabar_evidence.py` already provides a fail-closed ordered-path extractor:

- requires a supplied `MarkedLiquidityReference`;
- identifies the first child-bar take;
- reports ordered post-take path evidence;
- does not invent a minimum reversal distance;
- does not classify FU itself.

The existing MT5 history adapter is bar-export ingestion only. Tick volume is supplemental candle metadata and is not historical tick path evidence.

# 6. New research-only MT5 tick availability layer

New files:

- `src/xauusd_v2/march_mt5_tick_availability.py`
- `src/xauusd_v2/march_mt5_tick_availability_cli.py`
- `15_tests/test_march_mt5_tick_availability.py`

Registered CLI:

`xauusd-v2-march-mt5-tick-availability`

Purpose:

- query only two exact Exclusive-Markets broker windows using MT5 `copy_ticks_range` with UTC datetimes:
  - `2023-03-30T12:31:00Z <= t < 2023-03-30T12:32:00Z`
  - `2023-03-31T12:36:00Z <= t < 2023-03-31T12:37:00Z`
- require `time_msc` for sub-second ordering;
- preserve bid/ask/last/flags and optional volume fields;
- normalize to a strict half-open UTC range;
- persist available ticks content-addressed under the existing XAUUSD MT5 store;
- record empty/failed historical ranges without treating them as schema success;
- never infer a marked liquidity reference;
- never certify FU/HCS, strategy truth, performance, promotion or live execution.

Implementation commits after `85d4af24c7c5b3639967cfe3e3bf1f842741b221`:

- `1aec5666656b76d91809dc495eef53213991f371` — Add governed March MT5 tick availability probe
- `28380c365d4daf0a70e3f42b6805d13cb3958be6` — Expose March MT5 tick availability probe
- `037b5780a08974361a4524491c7bf413a65ff114` — Test March MT5 tick availability governance
- `effe8be55f51be212b1369376ec0b4a579afeb0e` — Register March MT5 tick availability CLI
- `8c12c8780ac599abee7ce0efef6ef659a90e8111` — Handle empty MT5 tick history fail closed
- `bb995af2b5bfc40cc5eb6403a271302e93b13074` — Cover unavailable historical MT5 ticks

Verified CI before this checkpoint write:

- workflow: `XAUUSD V2 Tests`
- run number: `513`
- run id: `33783735004`
- head: `bb995af2b5bfc40cc5eb6403a271302e93b13074`
- conclusion: `success`

# 7. Next governed action

Run the MT5 tick-availability probe against the same verified ingestion manifest.

Interpretation order:

1. `MT5_PYTHON_API_UNAVAILABLE_NOT_CERTIFIED` -> native Mac Python cannot access MT5 integration; do not install random substitutes. Move to an MT5-terminal-native export/script fallback.
2. `MT5_TICK_API_INITIALIZE_FAILED_NOT_CERTIFIED` -> terminal/API integration exists but is not connected/initialised; inspect exact MT5 error only.
3. `MARCH_MT5_TICK_AVAILABILITY_PARTIAL_OR_UNAVAILABLE_NOT_CERTIFIED` -> broker does not expose one or both old tick ranges; preserve that availability boundary and use only source/manual broker evidence if obtainable.
4. `MARCH_MT5_TICKS_AVAILABLE_NOT_CERTIFIED` -> persist exact ticks, then build a separate path-facts diagnostic for low/high ordering. Do not certify FU until a source-backed marked liquidity reference is supplied.

# 8. Open blockers remain

- B-01 sufficient opposite-direction FU move/break mechanics
- B-02 R-54 full-FU 70% fib anchor/orientation
- B-03 universal numeric Strong-FU threshold
- B-04 broker-specific Imbalanced-Candle calibration
- B-05 x3-by-x3 raw OHLC grammar
- B-06 Accepted RR numeric/dynamic definition
- B-07 synthetic 11h candle/session anchor
- B-08 production numeric risk policy
- trail-level selection boundary remains separate
- exact `FOREXCOM:XAUUSD` reference alignment remains required/deferred/not aligned

No blocker is silently waived by the March diagnostics or tick availability work.
