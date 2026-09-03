# XAUUSD V2 — FU Ground-Truth Coverage

Date: 2026-09-03
Status: ACTIVE PHASE-1 INVENTORY / NOT CERTIFIED
Scope: FU / Strong FU / ATT FU and directly related FU retest, negation, HCS/context examples.

## Why this exists

The project must not infer the complete FU architecture from the March 1975/1986 episode alone.
This inventory measures the breadth of the existing user-approved FU evidence corpus and separates:

1. semantic/visual ground truth,
2. mechanically executable raw-OHLC evidence,
3. cases blocked by unresolved FU semantics,
4. cases that actually belong to downstream HCS/negation/zone phases.

No profitability, promotion, strategy certification or live authority is implied.

## Live Supabase snapshot

Project: `mr-casino`
Table basis: `v2_examples` joined to `v2_sources`
Snapshot date: 2026-09-03

FU-related example selection includes titles/annotations/rule codes referring to FU, Strong FU or Attempted FU.

### Aggregate coverage

- FU-related examples: **69**
- Ground-truth-labelled: **53**
- Have a source locator field in annotation: **43**
- Visual/image anchored: **55**
- Sequence anchored: **40**
- Explicit raw OHLC fields inside example annotation: **0**
- Explicit candle timestamp/bar-open fields inside example annotation: **0**

Interpretation:

The corpus is rich in labelled semantic/visual evidence but is not itself a ready-made raw-OHLC regression dataset. A separate source-to-market alignment step is required before a visual case can be used as a deterministic candle-level test.

## Source-family distribution

- `top down analysis (1).zip`: 42 cases, all 42 GT-labelled, all 42 visual/image anchored.
- `casinonotes.excalidraw`: 7 cases, primary/notebook visual evidence.
- `PRICE ACTION REFLECTION — visuals through 2023-05-31`: 6 cases, visual historical evidence.
- `08_Zones_.pdf`: 4 labelled cases.
- `MrDomino_breakdown.pdf`: 3 contextual cases.
- `05_FU_Negations_.pdf`: 2 labelled cases.
- `GIANNO_CASINO_REFLECTION_MASTER.pdf`: 2 FU-related cases in this example filter.
- `03_Analysis_Basics_.pdf`: 1 ideal Strong-FU qualitative case.
- `04_FU_Retests_.pdf`: 1 labelled FU-retest case.
- `GIANNO_CASINO_BACKTEST_ASKISEIS_01.pdf`: 1 ATT-FU/doji edge case.

## Topic overlap inside the 69 examples

These categories overlap; they are not mutually exclusive.

- Attempted-FU related: **14**
- Strong-FU related: **5**
- FU-negation related: **5**
- FU-retest related: **18**
- HCS related: **13**
- forming-FU related: **3**
- zone/POI related: **30**

This confirms that FU is represented in the corpus as a family embedded in context, not just one isolated two-candle pattern.

## Mechanical readiness classes

### Class A — RAW / DIRECTLY EXECUTABLE NOW

Definition: exact raw OHLC/timestamps or an already-governed market fixture exists so the V2 code can be run without guessing source timing.

Current broad GT corpus count from Supabase annotations: **0**.

Separate existing replay diagnostics such as March 2023 are not counted here because they are repo-level market/source alignment fixtures, not raw OHLC stored in `v2_examples`.

### Class B — SOURCE-LABELLED VISUAL, ALIGNMENT REQUIRED

This is the dominant class.

Examples include:
- ideal qualitative Strong FU,
- weekly/H1 FU negation visuals,
- H4 FU retest,
- ATT-FU zone examples,
- 1m Strong-FU zone example,
- forming multi-timeframe FU examples,
- daily/monthly ATT-FU context,
- strong 3h/weekly FU-retest examples,
- FU contextual veto/continuation examples.

These are excellent semantic ground truth, but they need a governed mapping to raw broker/reference candles before being used as candle-level detector tests.

### Class C — QUALITY / STRENGTH EVIDENCE

Examples explicitly labelled Strong FU or qualitative strength relationships.

Useful now for:
- shape/quality observables,
- ordering/comparisons,
- checking that a candidate does not contradict source examples.

Blocked from a universal binary `Strong FU = true/false` detector by B-03 unless a source-backed numeric boundary is found.

### Class D — DOWNSTREAM FU USE

Examples whose main label concerns:
- FU retest,
- HCS,
- negation,
- zone/POI,
- TFS/context,
- forming/established state.

They are preserved now but should not drive the core FU-validity detector prematurely.
They become primary test material in Phase 2/3 after the FU-family primitive is consolidated.

## Representative high-value cases for Phase 1

### Core/quality

- `GT-R03-001` — Ideal Strong FU qualitative.
  Use: source-backed quality shape; forbidden: deriving one universal numeric threshold from the image.

### ATT FU edge behavior

- `GT-R05-004` — Doji outside last wick is Attempted FU, not core major doji.
  Use: proves ATT semantics interact with geometry/context and cannot be reduced to candle colour.

### Multi-timeframe/fractal behavior

- `GT-R08-001` — established 2M/1M Strong FU while 3M FU still forming.
  Use: supports separation of forming/established state and reinforces timeframe-neutral FU primitive with timeframe-specific state/authority.

### Context dependence

- `GT-R10-013` — nearby liquidity can veto an Attempted-FU limit setup.
- `GT-R10-005` — FU retest does not override an equal-lows liquidity target.
- `GT-R12-008` — FU POI interest is conditioned by opposite-side liquidity and timeframe strength.

Use: prevents the implementation from turning every FU-family observation into a trade signal.

### Negation / comparable strength

- `GT-R03-002` and `GT-R03-003` — Weekly/H1 FU-negation visuals.
- `GT-R11-014` — strong weekly FU can negate prior weekly FU while other areas remain context.

Use: later Phase 2 validation after core FU-family node representation exists.

## March 2023 role after this inventory

March remains useful because it has broker replay data and source-labelled price levels.
It is now explicitly treated as a **mechanical diagnostic episode**, not as the sole definition source for FU/HCS.

The 1975/1986 work should be revisited only after the Phase-1 FU-family representation is mature enough to test richer node classes.
The terminal tick fallback is therefore secondary and non-blocking.

## What Phase 1 must deliver before Phase 2

1. One union FU-family observability representation — DONE (`fu_family_observability.py`).
2. Cross-map primary source ↔ user clarifications ↔ Casino_v7 ↔ BETA — DONE (`FU_ATT_EVIDENCE_CROSSMAP_2026_09_03.md`).
3. Broad GT coverage inventory — DONE (this document).
4. A source-alignment registry that marks each FU case as:
   - raw replay-ready,
   - visual/source-only,
   - needs timestamp/price alignment,
   - quality-only,
   - downstream-only.
5. A small set of source-labelled FU cases promoted to deterministic **test fixtures** only when raw mapping is exact and non-inferred.
6. Run `fu_family_observability` on those fixtures and report divergences among:
   - primary semantic expectations,
   - V2 basic proxy,
   - Reflection completion class,
   - Casino_v7 implementation evidence,
   - BETA implementation evidence.
7. Identify which remaining mismatches are truly B-01/B-03 source gaps versus ordinary code gaps.
8. Only then design a richer FU-family detector; do not rewrite `basic_fu_candidate` by convenience.

## User action

None required at this stage.
If exact raw alignment of a high-value visual case cannot be recovered from existing source metadata/reference feeds, the project will surface that as a specific source-alignment blocker rather than asking for broad manual rework.
