# XAUUSD V2 — Current Checkpoint — 2026-09-03 21:07 Europe/Athens

## Current diagnostic boundary

The governed March FU-criteria gap remains non-certified.

For the source-labelled `1975` HCS re-entry, the critical `2023-03-30T12:31:00Z` M1 bar has:
- exact retest of the latest basic-FU proxy wick,
- conditional Reflection `attempted_fu_form_2` geometry,
- no FU semantic certification because parent M1 OHLC cannot prove liquidity-take -> opposite-direction intrabar ordering.

No strategy truth, performance, promotion, or live-execution authorization changed.

## Python MT5 tick API result

The local research probe returned:

`MT5_PYTHON_API_UNAVAILABLE_NOT_CERTIFIED`

with error:

`MetaTrader5 Python integration is unavailable: No module named 'MetaTrader5'`

Interpretation: no broker historical-tick availability conclusion can be drawn from that run. The request did not reach the MT5 Python integration layer. Do not install or infer a substitute data source from this result.

## Terminal-native fallback implemented

A research-only MT5 terminal exporter now exists:

`18_tools/mt5/XAUUSD_V2_March_HCS_Tick_Export.mq5`

It requests `COPY_TICKS_ALL` using `CopyTicksRange` for exactly these inclusive millisecond windows:

1. `buy_1975_hcs_candidate_2023_03_30_1231`
   - start `1680179460000`
   - end `1680179519999`
   - equivalent to `2023-03-30T12:31:00.000Z` through `12:31:59.999Z`
2. `sell_1986_hcs_control_2023_03_31_1236`
   - start `1680266160000`
   - end `1680266219999`
   - equivalent to `2023-03-31T12:36:00.000Z` through `12:36:59.999Z`

The exporter writes status records plus raw `MqlTick` evidence fields and does not classify FU/HCS.

## Governed importer implemented

Files:
- `src/xauusd_v2/march_mt5_terminal_tick_import.py`
- `src/xauusd_v2/march_mt5_terminal_tick_import_cli.py`
- `15_tests/test_march_mt5_terminal_tick_import.py`

CLI:

`xauusd-v2-march-mt5-terminal-tick-import`

The importer re-verifies the persisted MT5 M1 snapshot, requires the exact broker symbol and exact governed millisecond windows, validates `copy_result` against tick rows, rejects out-of-range/tampered exports, preserves price values as decimal strings, and persists raw export + normalized tick JSONL + report immutably/content-addressed.

Possible top-level import states:
- `MARCH_MT5_TERMINAL_TICKS_IMPORTED_NOT_CERTIFIED`
- `MARCH_MT5_TERMINAL_TICK_IMPORT_PARTIAL_OR_UNAVAILABLE_NOT_CERTIFIED`
- `MT5_TERMINAL_TICK_IMPORT_BLOCKED_NOT_CERTIFIED`

All semantic/performance/promotion/live flags remain false.

## CI state before this checkpoint

Implementation head before checkpoint documentation:

`85d25b9552a21146767108fbd203f2dd75a18c6a`

Workflow:
- `XAUUSD V2 Tests`
- run `#520`
- conclusion `success`

## Next action

Do not install the MetaTrader5 Python module as a workaround.

Next action is to place/compile/run `XAUUSD_V2_March_HCS_Tick_Export.mq5` in the connected Exclusive Markets MT5 terminal, obtain `xauusd_v2_march_hcs_ticks.csv`, and pass that exact file through the governed terminal-tick importer.

If historical ticks are present, inspect ordered `time_msc` evidence for the 1975 `12:31` bar without inventing a liquidity reference or FU threshold. If the terminal reports zero/unavailable history, record that broker-data boundary and do not infer FU semantics from M1 OHLC.
