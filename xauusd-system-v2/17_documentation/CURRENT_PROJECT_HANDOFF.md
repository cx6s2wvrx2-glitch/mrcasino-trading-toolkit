# XAUUSD V2 — Current Project Handoff

Updated: 2026-09-04  
Branch: `xauusd-v2-foundation`  
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`  
Project root: `xauusd-system-v2/`  
Supabase: `mr-casino` (`wuhrhlzabiuudswktcvk`)

## Read this first

The current human source of truth is now:

1. `17_documentation/MASTER_VALIDATION_PACK_2026_09_04.md`
2. `06_examples/MASTER_VALIDATION_PACK_2026_09_04.json`
3. `17_documentation/STRATEGY_TRUTH_MAP_2026_09_04.md`
4. `06_examples/STRATEGY_TRUTH_MAP_2026_09_04.json`
5. `17_documentation/AGENT_REALITY_AUDIT_2026_09_04.md`
6. `06_examples/AGENT_REALITY_AUDIT_2026_09_04.json`
7. `17_documentation/PHASE3_MARCH_TIMED_RECONSTRUCTION_2026_09_04.md`
8. `17_documentation/PHASE3_SOURCE_FRONTIER_AUDIT_2026_09_04.md`

Older checkpoint/state documents remain historical evidence and must not override these newer current-state documents.

Before new substantive code changes, fetch the live branch head and latest `XAUUSD V2 Tests` run.

## Non-negotiable scope/governance

- Work only inside `xauusd-system-v2/` plus strictly necessary XAUUSD-specific workflow files.
- Never touch Flowstate, LUMOS, THRV, gym or unrelated projects.
- V2 remains clean-room and fail-closed.
- Approved primary Mr Casino source > approved corroborative evidence > implementation helpers.
- Helper/beta code never defines strategy truth by itself.
- Ambiguity => `BLOCKED / NOT CERTIFIED / NO TRADE`, never guess.
- No automatic promotion.
- No LLM has live execution authority.
- Live execution remains disabled.
- Broker path similarity is not source-semantic equivalence.
- Later evidence cannot retroactively certify an earlier decision point.

## Current strategy understanding

The strategy is not `FU/HCS -> trade`.

Current mapped flow:

`Liquidity/context`
-> `Strong/ATT manipulation language`
-> `HCS/FU-Negation relationships`
-> `Zone/POI reaction`
-> `TFS/prevalent direction`
-> `active LAOL`
-> `True Stop/Main POI respect`
-> `10m True Stop establishment`
-> `LTF execution/refinement`
-> `Core/Major/opposite-LAOL targets`
-> `separate deterministic risk gate`.

Official R-143 subset:

`Zone/POI reaction -> TFS -> LAOL met -> True Stop respected -> 10m True Stop established -> targets/management`.

FU, HCS, TFS, LAOL, True Stop, targets and risk remain separate evidence layers.

## Critical semantic boundaries already protected by tests

- FU semantic criteria require liquidity taken + opposite-direction move + same-candle relationship.
- Previous-candle sweep is not a universal substitute for source-backed liquidity-taken evidence.
- `liquidity left behind != LAOL met`.
- `LAOL respected != LAOL met`.
- `LAOL taken != LAOL met` unless governing evidence explicitly maps it.
- forming FU / generic timeframe-strength context != established TFS.
- a later 4h close cannot retroactively certify the earlier 1986 entry decision.
- March BUY `12:31 retest + 12:32 ATT1` must not be merged into staged HCS without source authority.
- Exclusive Markets path similarity cannot become `FOREXCOM:XAUUSD` equivalence by inference.

## March Phase-3 truth

### 2023-03-30 BUY

- role: validation specimen;
- source semantic frontier: **LAOL_MET**;
- broker semantic frontier: **HCS_ZONE_REACTION / Zone-POI stage**;
- source labels TFS context and `1972.70` True Stop respect;
- Exclusive broker preserves a useful ordered path through the 1972/1973/1975 regions toward `1984.19`;
- `1975` remains unresolved and must not be force-fit;
- canonical reference alignment remains false.

### 2023-03-31 SELL

- role: validation specimen;
- source semantic frontier: **TFS_CONFIRMED**;
- broker semantic frontier: **HCS_ZONE_REACTION / Zone-POI stage**;
- source labels the 1986 region as clear 1m HCS sell context/entry in the narrative;
- Exclusive broker reproduces the distinctive 1987.56/1986 region and later path toward 1973;
- path fidelity does not certify universal HCS/TFS semantics;
- canonical reference alignment remains false.

## Reference/broker data truth

Canonical visual/reference feed:

`FOREXCOM:XAUUSD = REQUIRED / DEFERRED / NOT ALIGNED`

Broker/execution research feed:

`Exclusive Markets XAUUSD!`

Broader V2 infrastructure now contains real Exclusive Markets March MT5/broker evidence, immutable snapshot/replay tooling, source/broker comparison, timed reconstruction and March semantic probes.

Do **not** revert to the old statement `real MT5 dataset = 0`.

The remaining reference problem is canonical FOREXCOM alignment, not absence of all real broker data.

## Agent reality

Eight canonical foundations are implemented:

1. `KnowledgeAgent` v0.1.0 — provider-dependent, UNVERIFIED claims only.
2. `RulesAgent` v0.1.0 — provider-dependent, DRAFT rules only.
3. `XAUUSDDataAgent` v0.1.0 — deterministic data/provenance validator.
4. `MarketStateAgent` v0.1.0 — deterministic context-consistency gate.
5. `QuantitativeResearchAgent` v0.2.0 — deterministic research-design/reproducibility gate.
6. `IndependentValidationAgent` v0.3.0 — provider-dependent blind/focused independent validation.
7. `DeterministicRiskEngine` v0.2.0 — deterministic hard-veto risk gate.
8. `ContinuousImprovementAgent` v0.1.0 — proposal-only improvement governance.

Orchestrator: `AgentPipelineCoordinator` v0.6.0.

Critical interpretation:
- 8/8 foundations exist;
- they are not eight autonomous background workers;
- no continuous eight-agent swarm is observed;
- runs happen when explicitly invoked;
- stored run records are history, not active processes;
- orchestrator always keeps `live_execution_authorized=false`.

Agent 06:
- blind corpus R02-R13 = **173 cases**;
- answer-free packets, multimodal primary evidence, checkpoint/resume, immutable hashes, separate comparison and post-run audit are implemented;
- current connected-state canonical DB row remains `needs_review` with provider `none` / model `not_connected`;
- do not claim a currently observed completed+audited full external 173-case provider result;
- do not auto-promote even if a future full run has perfect agreement.

## Live Supabase truth — checked 2026-09-04

Read-only snapshot:
- 29 user-approved sources;
- 215 examples;
- 195 knowledge claims;
- 23 rules;
- 14 unresolved disagreement/certification rows;
- 32 stored agent/support runs;
- VERIFIED knowledge = 0;
- VERIFIED rules = 0.

No Supabase writes or schema changes were made during the 2026-09-04 Phase-3/audit work described here.

## Current engineering checkpoint at handoff refresh

Immediately before this handoff refresh, the latest green checkpoint observed was:
- branch head `290c6c122fb3f48cc35e08de0929cb9a56da00ba`;
- `XAUUSD V2 Tests` run id `33870462762`;
- run number `677`;
- conclusion `success`.

This included the new master validation-pack invariants. After this documentation update, re-check the latest run/head before quoting a newer green checkpoint.

## Canonical blocker families

- B-01 — exact sufficient opposite-direction FU move/break mechanics.
- B-02 — exact R-54 full-FU 70% Fibonacci anchor/orientation.
- B-03 — universal numeric Strong-FU threshold, if one exists.
- B-04 — broker-specific Imbalanced-Candle calibration.
- B-05 — raw OHLC grammar for x3-by-x3.
- B-06 — exact numeric/dynamic Accepted RR definition.
- B-07 — synthetic 11h candle/session anchor.
- B-08 — explicit user-approved production risk policy.

Additional boundaries:
- HCS temporal/co-location grammar;
- exact trail-level selection;
- canonical FOREXCOM alignment.

## Current user-only questions — isolated but NOT YET ASKED

Only two current source-semantic frontiers have been isolated as likely requiring user clarification if no further governing evidence appears:

### UQ-01 — LAOL_MET

What exact event/criterion counts as `R-143 LAOL met`, especially in the March 30 BUY sequence?

Do not infer the answer from `liquidity left behind`, `LAOL respected` or `LAOL taken` without explicit authority.

### UQ-02 — TFS_CONFIRMED

What exact pre-entry evidence establishes TFS in the March 31 SELL before/around the 1986 decision?

Do not use forming daily FU, generic timeframe-strength wording or later 4h evidence as a substitute.

Ask the user **one question at a time** only when the remaining assistant-side engineering/source work is exhausted.

## Performance/backtest gate

Do not present the current project as performance validated.

Correct future order:

1. resolve source semantic frontiers without invention;
2. complete canonical reference alignment when suitable data becomes available;
3. freeze a specific strategy definition/version;
4. complete independent validation on the frozen definition;
5. establish immutable parameter and broker-quality cost artifacts;
6. run lookahead-safe replay/OOS/walk-forward research;
7. approve production risk policy separately;
8. perform separate certification/promotion review;
9. only then discuss production/live readiness.

Current truth:
- strategy certified: NO;
- FU certified: NO;
- HCS certified: NO;
- TFS certified: NO;
- True Stop certified: NO;
- R-143 certified: NO;
- credible profitability evidence established: NO;
- production risk ready: NO;
- promotion allowed: NO;
- live execution: DISABLED.

## Immediate continuation direction

Do not add more agent names or tune the detector to known March answers.

Continue by:
- preserving the master validation pack and agent reality audit as current truth;
- exhausting remaining assistant-side evidence/reconciliation work before asking UQ-01/UQ-02;
- keeping source/broker/reference layers separate;
- keeping all certification/performance/live flags fail-closed.
