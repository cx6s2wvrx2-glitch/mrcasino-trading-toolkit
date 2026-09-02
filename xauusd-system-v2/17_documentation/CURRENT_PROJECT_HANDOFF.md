# XAUUSD V2 — Current Project Handoff

Updated: 2026-09-02
Branch: `xauusd-v2-foundation`
Repository: `cx6s2wvrx2-glitch/mrcasino-trading-toolkit`
Project root: `xauusd-system-v2/`
Supabase project: `mr-casino` (`wuhrhlzabiuudswktcvk`)

## Non-negotiable scope

- Work ONLY inside `xauusd-system-v2/` and, when strictly necessary, XAUUSD-specific GitHub workflow files.
- Do not touch gym / Flowstate / LUMOS / THRV / unrelated repos, tables, files or data.
- Clean-room V2: legacy strategy content is invalid unless the user explicitly re-approves a specific item.
- Source authority: approved primary Mr Casino > approved secondary/corroborative material > implementation helpers.
- Helper code never becomes strategy truth by itself.
- Ambiguity = fail closed / NO TRADE / NOT CERTIFIED.
- No LLM has live execution authority.
- Never bypass connector safety blocks.
- Never call source recovery, implementation coverage, blind-model agreement, or test success a VERIFIED strategy promotion.
- Never describe independent validation as completed unless an actual external provider/model ran blind and the run was logged.

## Current verified technical checkpoint

Latest verified branch state before this handoff-only commit:
- branch head: `a8d56f9774a5743ced31de058b3928992e5f124b`
- GitHub Actions run: `33647241660`
- job: `100304975505`
- Python: 3.12
- result: **603 / 603 tests PASS**

This handoff update itself creates a newer documentation commit and therefore another CI run. In every fresh continuation, verify the live branch head and latest XAUUSD V2 CI before modifying anything.

## Live Supabase snapshot checked 2026-09-02

- **29** approved-by-user source records remain in `status='review'`
- **16** source records have non-null `storage_path`
- **195** knowledge claims
- **23** V2 rules
- **215** examples
- **32** agent runs
- **14** unresolved disagreement/certification rows (`resolved_by_user=false`)
- **0 VERIFIED knowledge**
- **0 VERIFIED rules**

Do not rewrite the 29 approved source rows as `ACTIVE`; the factual database state is approved-by-user + `review`.

The 14 unresolved rows were reconciled into **8 canonical blocker families** in:
`17_documentation/OPEN_BOUNDARY_RECONCILIATION_2026_09_02.md`.

The reconciliation is deduplication/governance documentation only. It did not set `resolved_by_user=true` and did not promote any rule.

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

All eight have foundation code. Critical strategy/research/execution gates consume evidence-bearing reports rather than free booleans.

## Agent 06 — current state

Agent 06 has a provider-neutral multimodal blind-validation path.

Implemented:
- blind packet excludes expected label/class/evidence per case;
- external command JSON stdin/stdout boundary;
- timeout, command failure, empty output and invalid JSON fail closed;
- multimodal command contract;
- primary images carry local path + MIME + SHA-256 + byte size to the provider wrapper;
- image mutation is detected before model call;
- text-only client cannot silently validate image evidence;
- multimodal runtime audit manifest stores source hashes/metadata and predictions/abstentions but not ground-truth answers or local image paths;
- primary-context filesystem resolver;
- full physical-PDF-page fallback for `v2_sources:<uuid>#page:N#...`, with exact fragment entries taking precedence;
- duplicate locator, answer-leakage and path-traversal rejection;
- original top-down ZIP label-blind stager;
- original Excalidraw label-blind stager;
- PDF-page label-blind stager;
- primary-context manifest merger;
- Agent-06 readiness gate and CLI;
- **direct Anthropic Messages API multimodal runner** behind the provider-neutral command boundary.

Relevant code:
- `src/xauusd_v2/primary_context_payload.py`
- `src/xauusd_v2/primary_context_bundle.py`
- `src/xauusd_v2/topdown_primary_archive.py`
- `src/xauusd_v2/excalidraw_primary_context.py`
- `src/xauusd_v2/pdf_primary_pages.py`
- `src/xauusd_v2/primary_context_bundle_merge.py`
- `src/xauusd_v2/structured_model_clients.py`
- `src/xauusd_v2/anthropic_model_runner.py`
- `src/xauusd_v2/agents/validation_agent.py`
- `src/xauusd_v2/blind_validation_multimodal_runtime.py`
- `src/xauusd_v2/agent06_readiness.py`
- `src/xauusd_v2/agent06_readiness_cli.py`

CLI exposed by the package:
- `xauusd-v2-anthropic-runner`

### Anthropic runner contract

The runner is intentionally credential- and model-neutral in repository state:
- API key must come from environment variable `ANTHROPIC_API_KEY`;
- the model must be explicitly selected through `XAUUSD_AGENT06_ANTHROPIC_MODEL`;
- there is **no hardcoded default model**;
- optional `XAUUSD_AGENT06_ANTHROPIC_MAX_TOKENS` defaults to 2048;
- optional `XAUUSD_AGENT06_ANTHROPIC_TIMEOUT_SECONDS` defaults to 120;
- optional `ANTHROPIC_WORKSPACE_ID` is supported;
- endpoint is the Anthropic Messages API;
- primary images are rechecked for path, MIME, byte size and SHA-256 immediately before the provider request;
- image payload safety limits are enforced;
- provider output is requested as native JSON-schema structured output with exactly: `predicted_label`, `confidence`, `evidence`, `ambiguities`;
- non-`end_turn`, malformed JSON, unexpected fields, network/API failure and mutated image evidence fail closed;
- API error handling does not expose response bodies or credentials.

This wrapper was tested without making a real provider call. Infrastructure tests do **not** count as independent validation.

A **real independent-provider Agent-06 validation run has NOT been executed**.

## Agent-06 primary evidence recovery

The previous missing-primary-source blocker has been materially removed.

Canonical recovery audit:
`17_documentation/AGENT06_PRIMARY_EVIDENCE_RECOVERY_2026_09_02.md`.

Recovered original private source material includes:
- `casinonotes.excalidraw`
- `top down analysis (1).zip`
- `PRICE ACTION REFLECTION.zip`
- approved primary PDFs required by R03–R05, including Analysis Basics, FU Retests, FU Negations, HCS, Zones, Imbalances, Reflection Master and the approved backtest-exercises document.

### Original Excalidraw

The original `casinonotes.excalidraw` exists in the private Library and its exact Supabase source record now has a private Library `storage_path` mapping.

For canonical R02:
- all **18** `#embedded:<fileId>` identifiers exist exactly;
- each referenced file is attached to at least one live image element;
- all 18 decode as real images and pass declared MIME/signature checks;
- the one `#text:<elementId>` identifier exists as a live text element.

No analyst label or summary is required to retrieve these original source assets.

### Original top-down ZIP

`top down analysis (1).zip`:
- **188 / 188** original chart images present
- **188 / 188** unique image basenames
- **29** filename date groups
- **28 XAUUSD sequences / 186 XAUUSD images** eligible for XAUUSD evidence
- the `2021-11-30` sequence contains the two known GBPJPY images and remains explicitly excluded from XAUUSD ground truth/evidence.

The private bundle stages canonical and legacy sequence/image locator forms as a label-blind superset, so source resolution does not depend on expected answers.

### Corrected PDF physical-page provenance

Several old R03–R05 locators used printed footer page numbers rather than physical 1-based PDF pages. Only provenance locators were corrected; expected labels/classes/evidence were not changed.

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
- GT-R05-002 -> physical `08_Zones_.pdf` page 3; its old locator pointed to nonexistent physical page 7.

Regression tests pin these mappings.

## Private Agent-06 source bundle

The recovered evidence is persisted privately, outside the public repository:

- Library path: `/XAUUSD V2/Agent06/xauusd_agent06_primary_bundle_2026_09_02.zip`
- ZIP size: `17,623,961` bytes
- ZIP SHA-256: `6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf`
- `primary_context_bundle.json` SHA-256: `e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37`
- **477** resolver entries
- **219** unique image assets
- **1** text asset

477 entries are deliberate: the top-down section is a label-blind locator superset rather than a 173-answer-selected bundle.

The private Library ZIP was materialized back and verified byte-for-byte identical to the generated ZIP with the same SHA-256.

Do **not** commit this binary evidence bundle to the public GitHub repository.

## Current real Agent-06 blocker

The source persistence and provider-wrapper engineering blockers are now removed.

The remaining hard blocker is external configuration that cannot be invented or stored in repository code:
1. a real Anthropic API credential must be available securely to the runtime as `ANTHROPIC_API_KEY`;
2. an explicit Anthropic multimodal model must be selected as `XAUUSD_AGENT06_ANTHROPIC_MODEL`.

No Anthropic/Claude, Gemini or OpenRouter connector/plugin was available in the current ChatGPT environment, and the GitHub connector does not expose secrets APIs. Do not paste or commit credentials into source files, manifests, command arguments or documentation.

When the secure credential and explicit model are available:
1. materialize/unpack the private Agent-06 evidence bundle;
2. configure `CommandStructuredModelClient` to execute `xauusd-v2-anthropic-runner`;
3. run `agent06_readiness` using honest provider/model metadata and the real multimodal client capability;
4. only if it returns `READY_TO_RUN`, execute the 173 cases blind;
5. persist the auditable runtime manifest/predictions;
6. reveal expected answers only to the deterministic downstream comparator;
7. log disagreements/abstentions as unresolved review material;
8. do not auto-promote rules even if agreement is 173/173.

Do not simulate independence with the same formalizer/model labels.

## Broker historical-data path

Implemented:
- strict MT5 export parsing;
- explicit broker/symbol/source-timezone/timeframe/evaluation timestamp;
- UTC OHLC normalization;
- provisional-final-bar preservation;
- gap reporting rather than silent filling;
- raw-source + canonical-snapshot SHA-256;
- immutable content-addressed persistence for exact raw export, canonical CSV and audit manifest;
- tamper/collision fail-closed behavior;
- CLI `xauusd-v2-ingest-mt5`.

A real broker-quality MT5 XAUUSD history export has **not** been ingested. Therefore no replay or performance claim is unlocked by the ingestion code alone.

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

## Canonical unresolved source/calibration blocker families — DO NOT GUESS

1. FU: exact source-backed sufficiency for the opposite-direction move after liquidity take
2. R-54 exact Fibonacci 0/100 orientation for numeric 70% grading
3. universal numeric Strong-FU threshold, if one exists
4. exact broker-specific Imbalanced-Candle geometry/tolerance
5. x3-by-x3 standalone raw grammar
6. Accepted RR numeric/dynamic definition
7. 11h candle construction/session anchor
8. final production risk policy, including historical 3% vs 5% conflict

Other operational/governance issues remain source-scoped rather than silently flattened: liquidity-list evolution, HCS evolution, zone/orderblock geometry split, secondary PPT authority and Reflection numbering collisions.

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

Direction remains:
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

Agent 06 receives case identity/locator plus the batch-wide taxonomy; primary context is resolved separately without expected answers. Ground truth is exposed only to the downstream deterministic comparator.

Even 173/173 functional agreement cannot auto-promote strategy rules and is not a profitability metric.

## Primary top-down archive — exhausted

`top down analysis (1).zip`:
- **188 / 188** real chart images inspected
- **29 / 29** dated sequences inspected
- **28 XAUUSD** sequences
- **1 GBPJPY (`2021-11-30`)** inspected and explicitly excluded from XAUUSD ground truth

Canonical reference:
`01_sources/TOPDOWN_PRIMARY_SEQUENCE_INDEX.md`.

The final 47 XAUUSD charts from 2023-07-10, 2023-08-21 and July-2024 sequences were visually exhausted, but their detailed candidate labels were connector-blocked from canonical persistence. Do not treat them as persisted blind cases or VERIFIED evidence.

Other exhausted/indexed corpora:
- Price Action Reflection visuals through 2023-05-31
- student Swing-low archive — secondary only
- student handwritten notes — secondary only
- Casino Notes material

Inspected/exhausted != VERIFIED.

## Reflection policy

Reflection Master is TOP PRIORITY. Final Master state supersedes stale page-1 progress text. R-label collisions exist; identify by source label + page/section/occurrence + unique V2 ID.

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
- the persistent private Agent-06 source bundle exists;
- 173 canonical blind cases exist;
- direct Anthropic multimodal provider wrapper exists and is fail-closed;
- latest verified pre-handoff regression suite is **603 / 603 PASS**;
- VERIFIED knowledge = 0;
- VERIFIED rules = 0;
- no real independent external blind-model run has occurred;
- no real broker-history research run has occurred;
- no performance claim is certified;
- live execution remains disabled.

## Immediate next work

The next legitimate step is blocked only by real external provider configuration.

Priority:
1. Verify this handoff commit with CI and always resume from the live branch head.
2. Obtain/configure `ANTHROPIC_API_KEY` securely outside the repo and explicitly select `XAUUSD_AGENT06_ANTHROPIC_MODEL`.
3. Materialize the private source bundle and run Agent-06 readiness with the real client.
4. If READY, execute the 173-case blind external-model run and persist an auditable runtime manifest.
5. Compare predictions deterministically against ground truth only afterward; disagreement/abstention stays unverified.
6. After/alongside independent validation, ingest real broker-quality XAUUSD MT5 history into the immutable snapshot store.
7. Turn replay candidates READY only with proven broker/time/timestamp alignment; never invent timestamps.
8. Keep helpers in shadow mode only.
9. Keep connector-blocked candidate material noncanonical unless a compliant persistence path exists.
10. Ingest future Discord material gradually with chronology/source authority preserved.
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