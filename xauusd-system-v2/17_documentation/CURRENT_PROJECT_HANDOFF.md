# XAUUSD V2 — Current Project Handoff

Updated: 2026-09-02
Branch: `xauusd-v2-foundation`
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
Project root: `xauusd-system-v2/`
Supabase project: `mr-casino` (`wuhrhlzabiuudswktcvk`)

## Non-negotiable scope

- ONLY the XAUUSD V2 project.
- Do not touch gym / Flowstate / LUMOS / THRV / unrelated repos or data.
- Clean-room V2: legacy strategy content is invalid unless the user explicitly re-approves a specific item.
- Source authority: approved primary Mr Casino > approved secondary/corroborative > implementation helpers.
- Helper code never becomes strategy truth by itself.
- Ambiguity = fail closed / NO TRADE / NOT CERTIFIED.
- No LLM has live execution authority.
- Never bypass connector safety blocks.
- Never call source recovery, implementation coverage, or blind-model agreement a VERIFIED strategy promotion.

## Current verified technical checkpoint

Latest fully verified code checkpoint before the documentation-only recovery commits:
- branch head: `79f99683cee122db5ecb1467f5f8341dadbe8a8a`
- GitHub Actions run: `33646095968`
- job: `100301105070`
- Python: 3.12
- result: **595 / 595 tests PASS**

The branch may be ahead of this SHA because the Agent-06 recovery documentation itself is committed afterward. Always verify the live head and latest CI before modifying anything.

## Live Supabase snapshot checked 2026-09-02

- **29** approved-by-user source records remain in `status='review'`
- **16** source records now have non-null `storage_path`
- **195** knowledge claims
- **23** V2 rules
- **215** examples
- **32** agent runs
- **14** unresolved disagreement/certification rows (`resolved_by_user=false`)
- **0 VERIFIED knowledge**
- **0 VERIFIED rules**

Do not rewrite the 29 approved source rows as `ACTIVE`; the live database state is approved-by-user + `review`.

The 14 unresolved rows were previously reconciled into **8 canonical blocker families** in:
`17_documentation/OPEN_BOUNDARY_RECONCILIATION_2026_09_02.md`.

This reconciliation did not set `resolved_by_user=true` and did not promote rules.

## Architecture

Canonical roles:
1. Knowledge Agent
2. Strategy Formalization Agent
3. XAUUSD Data Agent
4. Market State / Context Agent
5. Quant Research / Backtesting Agent
6. Independent Validation Agent
7. Deterministic Risk Engine
8. Continuous Improvement Agent

All eight have foundation code. Critical strategy/research/execution gates consume evidence-bearing reports, not free booleans.

## Agent 06 — current state

Agent 06 has a provider-neutral multimodal blind-validation path.

Implemented:
- blind packet excludes expected label/class/evidence per case;
- external command JSON stdin/stdout model boundary;
- timeout + nonzero-exit + invalid-JSON fail-closed behavior;
- multimodal external model command contract;
- original primary images travel as file evidence with MIME + SHA-256 + byte size;
- image mutation is detected before model call;
- text-only client cannot silently validate an image case;
- multimodal runtime audit manifest stores source hashes/metadata and prediction/abstention, but no ground-truth answer and no local image path;
- primary-context filesystem bundle resolver;
- full-physical-PDF-page fallback for `v2_sources:<uuid>#page:N#...` when no exact fragment entry exists;
- bundle rejects duplicate locators, answer-leakage fields and path traversal;
- top-down original-ZIP label-blind stager;
- original-Excalidraw label-blind stager;
- PDF-page label-blind stager;
- primary-context manifest merger;
- Agent-06 readiness gate and CLI.

Relevant code:
- `src/xauusd_v2/primary_context_payload.py`
- `src/xauusd_v2/primary_context_bundle.py`
- `src/xauusd_v2/topdown_primary_archive.py`
- `src/xauusd_v2/excalidraw_primary_context.py`
- `src/xauusd_v2/pdf_primary_pages.py`
- `src/xauusd_v2/primary_context_bundle_merge.py`
- `src/xauusd_v2/structured_model_clients.py`
- `src/xauusd_v2/agents/validation_agent.py`
- `src/xauusd_v2/blind_validation_multimodal_runtime.py`
- `src/xauusd_v2/agent06_readiness.py`
- `src/xauusd_v2/agent06_readiness_cli.py`

A **real independent-provider validation run has NOT been executed**. Never describe it as completed until an actual external provider/model runs blind and is logged.

## Agent-06 primary evidence recovery — major update

The previous missing-primary-source blocker has been materially removed.

Original private source material recovered:
- `casinonotes.excalidraw`
- `top down analysis (1).zip`
- `PRICE ACTION REFLECTION.zip`
- approved primary PDFs needed by R03–R05, including Analysis Basics, FU Retests, FU Negations, HCS, Zones, Imbalances, Reflection Master, and the approved backtest exercises document.

### Original Excalidraw

The private original `casinonotes.excalidraw` is available and has an exact Supabase `storage_path` mapping.

For canonical R02:
- all **18** `#embedded:<fileId>` identifiers exist exactly;
- each referenced file is attached to at least one live image element;
- all 18 recovered embedded assets decode as real images and pass signature checks;
- the one `#text:<elementId>` identifier exists as a live text element.

No analyst label is required to retrieve those source assets.

### Original top-down ZIP

`top down analysis (1).zip` recovery state:
- **188 / 188** original chart images present
- **188 / 188** unique image basenames
- **29** filename date groups
- **28 XAUUSD sequences / 186 XAUUSD images** eligible for XAUUSD evidence
- `2021-11-30` has exactly the two known GBPJPY images and remains excluded from XAUUSD ground truth/evidence.

The private bundle stages both legacy and canonical sequence/image locator forms as a label-blind superset, so source retrieval does not depend on expected labels.

### Corrected PDF physical-page provenance

Several old R03–R05 locators used the PDF's printed footer page number instead of the real physical 1-based PDF page number. Only `source_locator` provenance was corrected; labels/classes/evidence were not changed.

Round 03 physical pages:
- GT-R03-001 -> 5
- GT-R03-002 -> 3
- GT-R03-003 -> 3
- GT-R03-004 -> 3
- GT-R03-005 -> 3
- GT-R03-006 -> 3
- GT-R03-007 -> 3

Round 04 physical pages:
- GT-R04-001 -> 3
- GT-R04-002 -> 3
- GT-R04-003 -> 4
- GT-R04-004 -> 5
- GT-R04-005 -> 4
- GT-R04-006 -> 6

Round 05:
- GT-R05-002 -> physical `08_Zones_.pdf` page 3; the old locator pointed to nonexistent physical page 7.

Regression tests pin these mappings.

Canonical recovery audit:
`17_documentation/AGENT06_PRIMARY_EVIDENCE_RECOVERY_2026_09_02.md`.

## Private Agent-06 source bundle

The recovered evidence is persisted privately, outside the public GitHub repository:

- Library path: `/XAUUSD V2/Agent06/xauusd_agent06_primary_bundle_2026_09_02.zip`
- ZIP size: `17,623,961` bytes
- ZIP SHA-256: `6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf`
- `primary_context_bundle.json` SHA-256: `e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37`
- **477** resolver entries
- **219** unique image assets
- **1** text asset

The 477 entries are deliberately more than the 173 blind cases because top-down evidence is staged as a label-blind locator superset.

The Library copy was materialized back and verified byte-for-byte identical to the locally generated ZIP with the same SHA-256.

Do **not** commit this binary evidence bundle to the public repository.

## Current real Agent-06 blocker

The primary-source persistence problem is no longer the main blocker.

The remaining hard blocker for a real independent run is:
- no genuinely independent external **multimodal** provider/credential runner is currently connected to the command boundary.

Before a real blind run:
1. connect an actual external multimodal provider/wrapper;
2. supply honest provider/model metadata;
3. run Agent-06 readiness against the private evidence bundle and the real client capability;
4. only if readiness passes, run blind prediction with no expected answers exposed;
5. compare predictions to ground truth afterward;
6. disagreement/abstention remains unverified and cannot silently select the formalizer answer.

Do not simulate this with the same model/formalized labels and do not claim independent validation based on infrastructure tests.

## Broker historical-data path

The MT5 historical-data ingestion path has also advanced.

Implemented:
- strict MT5 export parsing;
- explicit broker/symbol/source-timezone/timeframe/evaluation timestamp;
- canonical UTC OHLC normalization;
- provisional-final-bar preservation;
- gap reporting rather than silent filling;
- raw-source SHA-256 + canonical snapshot SHA-256;
- immutable content-addressed persistence for exact raw export, canonical CSV, and ingestion/audit manifest;
- tamper/collision fail-closed behavior;
- CLI: `xauusd-v2-ingest-mt5`.

A real broker-quality MT5 XAUUSD history export has **not** yet been ingested. Therefore no historical replay/performance claim is unlocked by the ingestion code alone.

## Strategy / research modules already implemented at semantic or candidate level

- FU semantic criteria + marked-liquidity bridge
- FU raw observables
- Complete FU / ATT FU Form 1 / Form 2
- FU intrabar evidence reconstruction
- FU quality metrics without invented Strong-FU threshold
- FU retest quality with R-54 fail-closed fib-anchor boundary
- `Casino_v7` / `BETA 1 + LAOL` shadow comparison
- liquidity interaction + R-207 scoped taxonomy
- doji-liquidity semantics
- zone lifecycle + separate zone geometries
- True Orderblock body-in-wick geometry
- HCS semantics / establishment
- negation semantics
- final x3 semantic definition
- x3-by-x3 explicit-source-only boundary
- TFS forming / established / retest states
- 10m+ establishment floor
- True Stop semantic gate
- LAOL / target hierarchy candidate semantics
- R-143 official backtest-sequence state machine
- R-145 LTF execution candidate logic
- Accepted-RR safeguard
- 11h safeguard
- deterministic Risk Engine with no hardcoded production 3%/5%
- broker precision / tick-size / digits
- immutable historical-data snapshots
- MT5 source ingestion + content-addressed store
- parent-child candle alignment
- source-chart ↔ immutable broker-bar alignment
- component replay / lookahead protection
- blind-validation packet / runner / comparator / text runtime / multimodal runtime

## Real source/calibration unknowns — DO NOT GUESS

Canonical unresolved blocker families remain:
1. FU: exact source-backed sufficiency for the opposite-direction move after liquidity take
2. R-54 exact Fibonacci 0/100 orientation for numeric 70% grading
3. universal numeric Strong-FU threshold, if one exists
4. exact broker-specific Imbalanced-Candle geometry/tolerance
5. x3-by-x3 standalone raw grammar
6. Accepted RR numeric/dynamic definition
7. 11h candle construction/session anchor
8. final production risk policy, including historical 3% vs 5% conflict

Other operational/governance issues remain source-scoped rather than silently flattened: liquidity-list evolution, HCS evolution, zone/orderblock geometry split, secondary PPT authority, Reflection numbering collisions.

## Source restrictions still active

The original first-10 approval did NOT include:
- `True Stop Loss`
- `Entries`
- `Attempted FU`

Do not use them as formal authority unless explicitly approved later.

Helper policy:
- `Casino_v7.txt`: implementation evidence only; known duplicate/unreachable FU/ATT branches.
- `BETA 1 + LAOL.txt`: implementation prototype; user reports repaint; provisional states are never historical truth.
- `MMB_AFU_v1.ex5`: AFU = Attempted FU; compiled black box.
- `MMB_SFU_v1.ex5`: SFU = Strong FU; compiled black box.

Direction is always:
`approved source -> canonical rule -> labelled example -> helper behavior comparison`.

## Blind-validation corpus

Persisted canonical blind corpus: **Rounds 02–13 = 173 cases**.

- R02 20
- R03 7
- R04 6
- R05 5
- R06 8
- R07 10
- R08 10
- R09 4
- R10 20
- R11 30
- R12 24
- R13 29

Agent 06 receives case identity/locator and batch-wide taxonomy, then source context is resolved without expected answers. Expected labels are revealed only to the downstream comparator.

Even 173/173 functional agreement cannot auto-promote strategy rules and says nothing by itself about profitability.

## Primary top-down archive — exhausted

`top down analysis (1).zip`:
- **188 / 188** real chart images inspected
- **29 / 29** dated sequences inspected
- **28 XAUUSD** sequences
- **1 GBPJPY (`2021-11-30`)** inspected and explicitly excluded from XAUUSD ground truth

Canonical reference:
`01_sources/TOPDOWN_PRIMARY_SEQUENCE_INDEX.md`.

The final 47 XAUUSD charts from 2023-07-10, 2023-08-21 and July-2024 sequences were visually exhausted but their detailed candidate labels were connector-blocked from canonical persistence. Do not treat them as persisted blind cases or VERIFIED evidence.

Other already-exhausted/indexed corpora:
- Price Action Reflection visuals through 2023-05-31
- student Swing-low archive — secondary only
- student handwritten notes — secondary only
- Casino Notes material

Inspected/exhausted != VERIFIED.

## Reflection policy

Reflection Master is TOP PRIORITY. Final Master state supersedes stale page-1 progress text. R-label collisions exist; use source label + page/section/occurrence + unique V2 ID.

Evidence classes:
- `[C]` source-confirmed / system-unverified
- `[I]` inference / unverified
- `[U]` ambiguous
- `[E]` experimental / unverified

Never auto-promote `[C]` to VERIFIED.

## Current strategic status

**NOT strategy-verified. NOT performance-certified. NOT live-ready.**

Facts:
- substantial semantic/candidate engine exists;
- approved primary source recovery is now sufficient to build a persistent private Agent-06 evidence bundle;
- 173 persisted blind cases exist;
- latest verified pre-documentation regression suite is **595 / 595 PASS**;
- VERIFIED knowledge = 0;
- VERIFIED rules = 0;
- no independent external blind-model run has occurred;
- no real broker-history research run has occurred;
- no performance claim is certified;
- live execution remains disabled.

## Immediate next work

Continue without waiting for the large Discord channel; user will provide that gradually.

Priority:
1. Verify the latest documentation commits with CI and always resume from the live branch head.
2. Find/connect a genuinely independent external multimodal provider/wrapper compatible with the command client; do not fake independence.
3. Run `agent06_readiness` against the private evidence bundle and the real external client/model metadata.
4. If READY, execute the 173-case blind external-model run and persist an auditable runtime manifest.
5. Compare blind predictions deterministically against ground truth only afterward; disagreements/abstentions remain unverified.
6. In parallel/after the independent-validation gate, ingest real broker-quality XAUUSD MT5 history into the immutable snapshot store.
7. Turn replay candidates READY only with proven broker/time/timestamp alignment; never invent timestamps.
8. Keep helpers in shadow mode only.
9. Keep connector-blocked candidate material noncanonical unless a compliant persistence path appears.
10. Ingest future Discord photos gradually with chronology/source authority preserved.
11. Only after sufficient certification: OOS -> walk-forward -> costs/slippage -> sensitivity -> Monte Carlo -> paper/demo -> shadow -> tiny live -> production.

## Workflow discipline

For every new source/candidate:
1. verify authority + approval,
2. preserve provenance,
3. separate source statement from inference,
4. create valid/invalid/edge cases only when justified,
5. name blockers honestly,
6. keep unverified/draft by default,
7. never auto-promote,
8. run CI after code/data-contract changes,
9. do not claim persistence if a connector blocks it,
10. never touch unrelated projects.

## Fresh-chat resume prompt

`Συνέχισε το XAUUSD V2 από xauusd-system-v2/17_documentation/CURRENT_PROJECT_HANDOFF.md στο branch xauusd-v2-foundation. Διάβασε πρώτα το handoff, έλεγξε live GitHub/Supabase και το τελευταίο CI, και συνέχισε από το πραγματικό current state. Μην αγγίξεις τίποτα εκτός του XAUUSD project.`

In a fresh chat, fetch this file first, then verify live branch head, Supabase snapshot and latest CI before modifying anything.
