# XAUUSD V2 — CURRENT CHECKPOINT — 2026-09-03 18:23 Europe/Athens

## Scope lock

- Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
- Branch: `xauusd-v2-foundation`
- Project root: `xauusd-system-v2/`
- Do not modify any non-XAUUSD project or unrelated repository content.
- This checkpoint supersedes `CURRENT_CHECKPOINT_2026_09_03_1809.*` for continuation order only. Older checkpoints remain historical evidence and must not be overwritten.

## Continuation chain

Read in this order when resuming:

1. `START_HERE_NEW_CHAT.md`
2. `17_documentation/PROJECT_STATE_CURRENT_2026_09_03.md`
3. `17_documentation/PROJECT_STATE_CURRENT_2026_09_03.json`
4. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1734.md/.json`
5. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1809.md/.json`
6. `17_documentation/CURRENT_CHECKPOINT_2026_09_03_1823.md/.json`
7. Verify live branch head and latest `XAUUSD V2 Tests` CI before changing code.

# 1. User decision: FOREXCOM reference validation is deferred, not resolved

The user explicitly chose not to purchase an expensive TradingView plan solely to obtain the historical `FOREXCOM:XAUUSD` M1 sample for March 2023.

Governed decision:

- do **not** require TradingView Premium now;
- do **not** treat `FOREXCOM:XAUUSD` alignment as satisfied;
- do **not** remove or weaken the reference-feed requirement;
- keep the already-implemented `xauusd-v2-march-reference-feed` comparator ready for later use;
- when a valid historical `FOREXCOM:XAUUSD` M1 sample becomes economically/easily available, resume the exact-time, zero-tolerance comparison;
- until then, any feed-sensitive geometry remains explicitly unresolved/deferred.

This is a cost/access deferral only. It is not evidence that the Exclusive Markets feed equals the canonical visual/reference feed.

Reference-feed state:

`FOREXCOM:XAUUSD = REQUIRED / DEFERRED / NOT ALIGNED`

# 2. Important correction to the interpretation of the March 0/0 correspondence result

The completed March bundle remains valid and immutable. However, the earlier exact-bar correspondence statistic must be interpreted narrowly.

The source-fidelity fixtures were built primarily as ordered market-path/price anchors. They mix semantic roles, including:

- True Stop price areas,
- HCS/re-entry areas,
- imbalance areas/targets,
- liquidity/re-entry areas,
- minimum targets.

They were **not** a clean set of source-labelled FU/HCS event bars.

Therefore:

`0 exact-bar basic-FU correspondence` and `0 exact-bar HCS correspondence`

mean only that the generic source-fidelity anchor bars selected by the ordered path replay did not coincide with the current narrow raw primitive candidate timestamps.

They must **not** be upgraded into the stronger claim:

`the FU/HCS detector failed on all explicitly source-labelled FU/HCS examples`.

That stronger claim had not actually been tested by the generic bridge.

# 3. Explicit source-labelled semantic roles now isolated

The approved primary March narrative explicitly contains these M1 semantic labels:

1. Buy side: strongest `1m FU closure` around `1973`.
2. Buy side: easier `1m HCS re-entry` around `1975`.
3. Sell side: `1m HCS at 1986` described as the clearest sell entry in the stated manipulation zone/context.

These are materially better probes for the current narrow FU/HCS primitive grammar than generic target, liquidity or True Stop anchors.

The preserved narrative does **not** expose certified exact occurrence timestamps for these three labels. Therefore no exact source-event bar timestamp may be invented.

# 4. New governed role-aware March semantic probe

New fixture:

`06_examples/MARCH_SOURCE_SEMANTIC_PROBES.json`

It contains exactly three governed probes:

- `buy_1973_strongest_1m_fu_closure` — family `FU`, level `1973.00`
- `buy_1975_1m_hcs_reentry` — family `HCS`, level `1975.00`
- `sell_1986_1m_hcs_entry` — family `HCS`, level `1986.00`

New implementation:

- `src/xauusd_v2/march_semantic_probe.py`
- `src/xauusd_v2/march_semantic_probe_cli.py`
- `15_tests/test_march_semantic_probe.py`

New CLI:

`xauusd-v2-march-semantic-probe`

Registered in `pyproject.toml`.

## Probe rules

For each explicit source-labelled level, the tool:

1. re-verifies the persisted M1 MT5 snapshot;
2. scans only the governed March day window;
3. finds **every closed M1 bar whose OHLC range contains the exact source level**;
4. evaluates the current narrow raw FU/HCS primitive state on those exact level-touch bars;
5. does not choose a convenient single touch;
6. does not infer a missing source occurrence timestamp;
7. does not use nearest-bar substitution;
8. does not apply price tolerance;
9. preserves data-gap/closed-bar boundaries;
10. returns diagnostic raw correspondence only;
11. writes an immutable content-addressed report under `research-bundles/march-2023-semantic-probes/<sha>/report.json`;
12. always leaves FU/HCS certification, strategy truth, performance, promotion and live execution false.

Expected top-level status:

`MARCH_SOURCE_SEMANTIC_PROBE_COMPLETE_NOT_CERTIFIED`

# 5. Engineering state before this checkpoint document

Code/test head:

`23decb178cba93a5a47051dcd97663f7860be979`

Relevant new commits:

- `1ab63363567c3cfb36c1556fb319d02763d182fe` — `Add governed March semantic probes`
- `e9ff4ad21a4d0a85efbfdd8b4cfc5c1e933a1fdf` — `Add role-aware March semantic probes`
- `a41f1b51b77c97121beeaed83844ce664309b3de` — `Expose March semantic probe CLI`
- `17718548d785660903a63ec60a6b4f04567dda44` — `Register March semantic probe command`
- `23decb178cba93a5a47051dcd97663f7860be979` — `Test March semantic probe boundaries`

Verified CI:

- Workflow: `XAUUSD V2 Tests`
- Run: `#487`
- Run id: `33772177116`
- Job id: `100704910006`
- Head SHA: `23decb178cba93a5a47051dcd97663f7860be979`
- Conclusion: `SUCCESS`
- Exact ending: `Ran 822 tests in 0.711s` / `OK`

New boundary tests cover:

- semantic fixture uses explicit FU/HCS roles rather than generic path anchors;
- all exact level touches are preserved;
- adjacent/nearest candidate cannot substitute for a level-touch bar;
- HCS correspondence must exist on the same level-touch bar;
- fixture cannot enable certification or promotion.

# 6. March consolidated replay remains unchanged

Previously completed real local replay remains authoritative as observational evidence:

- status: `MARCH_2023_REPLAY_BUNDLE_BUILT_NOT_CERTIFIED`
- bundle SHA-256: `f1bf8cb5a9e58d90279d4a38d7273b28d594716a1d0dd2642f9e5fcef4c4ddf6`
- persisted normalized snapshot SHA-256: `ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`

30 March BUY:

- source path: `3/3` anchors matched
- raw basic FU candidates: `189`
- raw source-style HCS candidates: `728`
- generic anchor exact-bar FU correspondence: `0`
- generic anchor exact-bar HCS correspondence: `0`

31 March SELL:

- source path: `5/5` anchors matched
- raw basic FU candidates: `186`
- raw source-style HCS candidates: `1234`
- generic anchor exact-bar FU correspondence: `0`
- generic anchor exact-bar HCS correspondence: `0`

The new semantic probe does not alter, replace or invalidate this bundle. It answers a narrower and more appropriate diagnostic question.

# 7. Governance remains fail-closed

Nothing in this tranche certifies or authorizes:

- FU
- HCS
- True Stop
- TFS
- six-stage R-143 automation
- strategy profitability
- expected return
- performance validity
- promotion
- production risk readiness
- live trading

Open blockers remain open, including B-01 through B-08 and the deferred `FOREXCOM:XAUUSD` alignment.

Do not tune thresholds or add tolerance merely to make the March examples fit.

# 8. Single next action

Run the new role-aware semantic probe **once locally** against the already-persisted March M1 snapshot.

No new market data is required.

Inspect for each of the three explicit source-labelled probes:

- `level_touch_bar_count`
- `raw_requested_family_match_bar_count`
- `diagnostic`

Interpretation after the real run:

- if raw matches exist on one or more explicit source-labelled levels, the earlier generic `0/0` result was at least partly a role-alignment limitation of the old diagnostic;
- if no raw match exists, inspect the detailed per-touch basic-FU/HCS observations to identify the exact primitive condition that blocks correspondence before changing any rule;
- in either case, no semantic certification follows automatically;
- `FOREXCOM:XAUUSD` stays deferred/unresolved until a valid reference dataset is later available.

# 9. Local command after pulling this checkpoint

Use the existing persisted ingestion manifest:

`$HOME/.xauusd-v2/mt5/ingestions/691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0--ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24.json`

Refresh the editable install after pulling because the new console script was registered after the user's previous local install.

# 10. Communication rule

For the local run, explain in Greek:

`τι κάνουμε -> γιατί -> τι περιμένουμε -> τι σημαίνει`

Keep manual work to one copy-paste command and ask only for the returned JSON output.
