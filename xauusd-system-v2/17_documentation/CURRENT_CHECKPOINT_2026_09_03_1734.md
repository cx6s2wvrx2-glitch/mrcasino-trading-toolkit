# XAUUSD V2 — CURRENT CHECKPOINT — 2026-09-03 17:34 Greece time

This is the newest continuity delta on top of `PROJECT_STATE_CURRENT_2026_09_03.md`.

## Canonical continuation chain
In a new chat read, in order:
1. `xauusd-system-v2/START_HERE_NEW_CHAT.md`
2. `xauusd-system-v2/17_documentation/PROJECT_STATE_CURRENT_2026_09_03.md`
3. `xauusd-system-v2/17_documentation/PROJECT_STATE_CURRENT_2026_09_03.json`
4. `xauusd-system-v2/17_documentation/CURRENT_CHECKPOINT_2026_09_03_1734.md`
5. `xauusd-system-v2/17_documentation/CURRENT_CHECKPOINT_2026_09_03_1734.json`
Then fetch the current branch head and latest `XAUUSD V2 Tests` workflow before doing more work.

## Repository / branch / scope
- Repo: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
- Canonical working branch: `xauusd-v2-foundation`
- Project root: `xauusd-system-v2/`
- Never modify Flowstate, LUMOS, THRV, gym, or any unrelated project.
- V2 clean-room, fail-closed, no auto-promotion, live execution disabled.

## Latest verified branch checkpoint before this continuity commit
- Head: `160d4ac383a70658e5c4093c431ef8381eb4947d`
- Commit: `Test governed R-143 source evidence maps`
- GitHub Actions `XAUUSD V2 Tests` run `33766967657`: `success`.

## New work completed after the original project-state handoff
The codebase now contains the next research bridge layers that were only listed as future work in Section 16 of `PROJECT_STATE_CURRENT_2026_09_03.md`:

### 1. March 2023 source-fidelity fixtures
- `06_examples/SOURCE_FIDELITY_2023_03_30_BUY.json`
- corresponding March 31 sell fixture in the same example family.
- deterministic source-fidelity replay code/CLI already exists.

These fixtures preserve ordered source-labelled price facts only. They do not certify strategy semantics and do not make performance claims.

### 2. Primitive replay scanner
- `src/xauusd_v2/primitive_replay_scan.py`
- `src/xauusd_v2/primitive_replay_scan_cli.py`
- `15_tests/test_primitive_replay_scan.py`
- `15_tests/test_march_2023_primitive_boundaries.py`

Purpose: scan exact closed M1 bars for raw basic-FU candidates and source-style wick-retest/HCS candidate observations. Output remains `NOT CERTIFIED`; `certified_fu_count=0`, `certified_hcs_count=0`. Data gaps are fail-closed and adjacency across gaps is skipped.

### 3. Source-to-primitive bridge
- `src/xauusd_v2/source_primitive_bridge.py`
- `src/xauusd_v2/source_primitive_bridge_cli.py`
- `15_tests/test_source_primitive_bridge.py`

Purpose: join source-labelled anchor bars to primitive observations by exact timestamp only. No nearest-event fitting, no price-tolerance optimization, no semantic promotion.

### 4. Governed R-143 source evidence maps
- `06_examples/R143_SOURCE_EVIDENCE_2023_03_30_BUY.json`
- `06_examples/R143_SOURCE_EVIDENCE_2023_03_31_SELL.json`
- `src/xauusd_v2/r143_source_evidence.py`
- `15_tests/test_r143_source_evidence.py`

These maps explicitly distinguish what the primary source narrates from what is not yet automatically certified from raw bars. They are evidence maps, not trade labels and not backtest results.

## Primary March 2023 source facts already grounded
Primary narrative for 30 March describes, in order/context:
- 45m HCS/manipulation area around 1972;
- 1972.19 liquidity left behind;
- 1972.70 True Stop respected;
- strongest 1m FU closure around 1973;
- 1m HCS re-entry around 1975;
- 1984.19 imbalance/upside target context.

Exclusive Markets immutable M1 reconnaissance reproduces the ordered broker path:
`1972.70 area -> 1973 area -> 1975 area -> 1984.19 target area`.
Important feed-sensitive discrepancy remains: Exclusive prints `1972.69` immediately before a bar with exact low `1972.70`; do not convert that into a tolerance rule.

Primary narrative for 31 March describes:
- 100+ pips in 3 minutes;
- 1m imbalance/high around 1987.56;
- clear 1m HCS sell around 1986;
- target 1973 at least;
- later 15m doji/big-wick and 15m HCS re-entry context.

Exclusive Markets reproduces the distinctive 3-minute expansion and subsequent path, with nearby broker/reference differences (e.g. 1987.57 vs source 1987.56). This reinforces the feed separation rather than authorizing a numeric tolerance.

## Feed architecture remains non-negotiable
- Canonical TradingView visual/reference feed: `FOREXCOM:XAUUSD`.
- Exclusive Markets `XAUUSD!`: broker/execution research dataset.
- Feed disagreements are measured; never force equality and never silently substitute Exclusive geometry for Casino/Forex.com geometry.
- Primary source also indicates preference for IC Markets / Forex.com and warns about LTF broker-feed discrepancies.

## Data foundation already closed
Do not repeat:
- full MT5 M1 export;
- timezone support question;
- M1 ingestion/persist;
- MTF build;
- native H1/H4/H8/D1 validation;
- Agent-06 paid validation.

Immutable Exclusive dataset:
- 1,999,671 M1 bars;
- source SHA-256 `691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0`;
- normalized SHA-256 `ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`;
- snapshot id `sha256:ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`;
- timezone `EET`, broker-confirmed GMT+2 winter/GMT+3 summer;
- native representative validation: H1/H4/H8/D1 = 5,708/5,708 exact OHLC, zero missing, zero mismatches.

## Timeframe architecture
Do not collapse the system to only the initial derived TFs.
- Beta literal minute configuration is a helper/reference, not strategy truth.
- Source-led system uses a broader multi-timeframe universe.
- User observation preserved: 1h/2h/3h/5h/7h/11h are commonly used in the group.
- FU / ATT FU / Strong FU primitive mindset is timeframe-neutral; timeframe changes authority/context/use, not the primitive idea.
- 11h remains fail-closed under B-07 until its candle/session anchor is source-certified.

## Open blockers — never guess
- B-01: sufficient opposite-direction FU move/break mechanics.
- B-02: R-54 full-FU 70% fib anchor/orientation.
- B-03: universal numeric Strong-FU threshold only; timeframe scope itself is resolved.
- B-04: broker-specific Imbalanced-Candle calibration.
- B-05: x3-by-x3 raw OHLC grammar.
- B-06: Accepted RR numeric/dynamic definition.
- B-07: synthetic 11h candle/session anchor.
- B-08: production numeric risk policy.
Also preserve the separate Trail-level selection boundary unless later sourced.

## Agent-06 closure
Agent-06 is CLOSED. No more Anthropic/Claude calls are required for Agent-06 closure. Final focused results: 144 V1 exact + 6 locator-collision neutral + 19 focused supported + 4 focused insufficient = all 173 accounted for. No auto-promotion, no strategy truth change, live execution disabled.

## Current research objective
User premise: the Casino strategy has edge. The project's job is not to replace it with a different strategy or tune one winning example. The job is to reconstruct it faithfully and demonstrate/quantify that edge through:
source fidelity -> deterministic raw observables -> semantic gates -> lookahead-safe replay -> frozen rules -> all-event historical backtest -> locked OOS/walk-forward -> costs/feed robustness -> paper/shadow.

## What is NOT yet done
- Full certified raw FU detector under B-01.
- Universal Strong-FU numeric threshold under B-03.
- Full automatic raw extraction of all six R-143 stages.
- Exact Forex.com geometry for feed-sensitive March examples.
- All custom TF anchors, especially 11h.
- Population-level unbiased backtest, OOS, walk-forward, costs.
- Production risk values B-08.
- Paper/shadow and live authorization.

## NEXT ACTION FROM THIS CHECKPOINT
Continue engineering without asking the user to repeat setup.

1. Consolidate the March workflow into a single deterministic local replay bundle so the user eventually runs one command instead of several blind copy/pastes.
2. The bundle must consume the already-verified MT5 ingestion manifest plus March source-fidelity fixtures, run source-fidelity replay, primitive scan, exact-time source/primitive bridge, and governed R-143 evidence-map checks; freeze hashes/results under a content-addressed local report directory.
3. It must never infer missing semantic stages or certify FU/HCS from primitive candidates.
4. Add tests for identity/hash mismatch, data-gap safety, ordered-anchor safety, no lookahead, and no performance/promotion flags.
5. Once this bundle is CI-green, the next user-local step should be ONE command against the already-persisted snapshot to generate the March 30/31 bundle reports.
6. Then inspect those results and only after that decide whether the small `FOREXCOM:XAUUSD` historical sample is genuinely required immediately.
7. After March component fidelity is stable, expand to additional primary source episodes before rule freeze and population backtest.

## User communication rule
Use simple Greek. Before any terminal command explain: `τι κάνουμε -> γιατί -> τι περιμένουμε -> τι σημαίνει`. Avoid making the user a blind terminal operator.
