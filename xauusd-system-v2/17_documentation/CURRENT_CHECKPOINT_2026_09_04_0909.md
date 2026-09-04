# XAUUSD V2 Checkpoint — 2026-09-04 09:09 Europe/Athens

## Scope
Only `xauusd-system-v2/` was touched. No Supabase writes. No production/live/promotion claim.

## Real operator-run data used
Verified persisted MT5 snapshot:
- broker: Exclusive Markets Ltd.
- symbol: `XAUUSD!`
- normalized SHA256: `ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`
- source/reference alignment: `FOREXCOM:XAUUSD = REQUIRED / DEFERRED / NOT ALIGNED`

The operator ran the M1 source-level probe against the pre-fix replay head. Observed results before the fidelity correction:

### 1973 source role: strongest 1m FU closure
- exact level-touch bars: 20
- strong marker touch bars: 2
- attempted marker touch bars: 4
- dual-marker touch bars: 1
- BETA HCS touch bars: 2
- source-marker HCS proxy touch bars: 2
- notable candidate: 2023-03-30T12:30:00Z had Strong bullish plus Attempted bearish under the old replay output

### 1975 source role: easy 1m HCS re-entry
- exact level-touch bars: 4
- Strong: 0
- Attempted: 0
- BETA HCS: 0
- source-marker HCS proxy: 0
- therefore Exclusive Markets + current supplied Casino_v7 helper does not reproduce a marker HCS on any exact 1975 touch in this probe
- this does NOT invalidate the source narrative because source occurrence timestamp is not certified and canonical `FOREXCOM:XAUUSD` alignment remains deferred

### 1986 source role: clearest 1m HCS sell entry
- exact level-touch bars: 8
- Strong: 0
- Attempted: 3
- BETA HCS: 0
- source-marker HCS proxy: 1
- observed chain: 2023-03-31T12:35:00Z Attempted bullish -> 2023-03-31T12:36:00Z Attempted bearish with exact latest-marker wick retest
- this is implementation-level observational alignment only, not source-semantic certification

## Fidelity bug discovered from the real replay
The supplied `Casino_v7.txt` defaults `useBearBull = true` and explicitly removes:
- bearish ATT from a bullish candle
- bullish ATT from a bearish candle

The historical runner and source-marker HCS proxy had replayed the core FU/ATT branches plus current-candle doji filter, but had omitted this default directional ATT filter. This allowed impossible default-visible dual marker combinations such as Strong bullish + Attempted bearish on a bullish candle.

## Fix implemented
New helper path:
- `apply_casino_v7_default_visible_filters(...)`
- preserves the existing current-candle doji behavior
- applies the supplied default `useBearBull=true` directional ATT filter
- does not enable optional MA or leading-doji gates (their supplied defaults are false)

Updated consumers:
- `casino_historical_event_runner.py`
- `casino_source_hcs_candidate.py`

Tests added for both directional ATT removals.

## Validation
Head after code/tests:
`312fecc5330d43d8afc3123539c81f09504998a6`

GitHub Actions check completed successfully on that head.

## Important consequence
The pre-fix M15/M1 visible-marker counts and source-marker HCS proxy counts are now **superseded for fidelity purposes** and must be rerun on the corrected head before being used for further conclusions.

The BETA HCS state itself is separate and was not changed by this fix.

## Next exact step
Rerun the verified M1 source-level probe on the corrected head, then compare:
1. 1973 candidate markers after dual-direction cleanup,
2. whether 1975 remains a complete marker miss,
3. whether the 1986 ATT->ATT exact-retest HCS proxy survives,
4. corrected full M15 marker/HCS-proxy counts if needed.

Do not modify production HCS semantics based on the pre-fix counts.
