# XAUUSD V2 — Batch 05: Repainting Beta + Top-Down Archive

Date: 2026-09-01
Status: REVIEW

## 1) BETA 1 + LAOL.txt

- SHA-256: `cd89f37f160ec3f54c53b52b38272999189eaaa8a40e93bfa3cf1ad430b3c9e4`
- Size: 136,482 bytes
- Pine Script: v6
- User-confirmed status: **beta implementation reference that repaints**
- Authority: implementation helper only; **NOT strategy ground truth**

### Valuable architecture to preserve for later redesign

- 25 configured timeframes.
- Implementation categories: ENTRY 1–5m, SCALP 6–20m, INTRA 30–100m.
- Explicit lifecycle/state-machine concepts: FORMING, ESTABLISHED, EST_RETEST, FORMING_FRESH, RESPECTED, broken/invalidated.
- Separate state for FU, self-negation, x3/sequence logic, HCS/HCS-forming, LAOL, cross-timeframe retests.
- LAOL aggregation/merging across timeframes and categories.
- Cross-layer structure connecting ENTRY → SCALP → INTRA.
- Forming vs confirmed vs final-entry concepts.
- Alert/event ideas that can later become deterministic event logs.

### Repaint / validation warning

The script uses `request.security(..., lookahead=barmerge.lookahead_off)` and carries `barstate.isconfirmed`; it does **not** use `lookahead_on`. However, it explicitly consumes current unconfirmed multi-timeframe OHLC/state and produces FORMING states/alerts before the relevant timeframe candle is confirmed. Therefore realtime forming output can change before close and may differ from the historical/reloaded chart.

Rules for V2:
1. FORMING state may be displayed/logged as provisional realtime context only.
2. FORMING output is never historical ground truth.
3. Strategy certification/backtests must distinguish information available at event time from information known after close.
4. All final deterministic decisions must be reproducible from timestamped closed-bar/tick inputs.
5. If run on a chart timeframe above any requested lower timeframe, lower-TF `request.security` behavior must be separately validated; do not assume historical equivalence.
6. Hardcoded beta parameters (`TP_MULTIPLIER=8`, `PIP_TARGET=40`, etc.) are implementation experiments, not canonical strategy rules unless supported by approved strategy sources.

## 2) top down analysis (1).zip

- SHA-256: `774c5beee897ff2782878439a1a625dd78801f46494e5835a300021c2c048cf4`
- Size: 8,091,069 bytes
- Real image files: **188 JPG screenshots**
- Dated sequences: **29**
- Date span visible from filenames: 2021–2024
- macOS metadata entries excluded from inventory.
- Current authority: **PENDING USER CONFIRMATION**

### Visual inspection

The archive is not a random screenshot dump. Dated groups form sequential top-down analysis sets: higher-timeframe context and directional narrative, zones/HCS/refinement, then progressively lower-timeframe chart context/execution areas. This makes the archive potentially very valuable for sequence-level training and certification.

### Current handling

- Approved for preservation and review.
- May be segmented by date into top-down episodes.
- Until author/provenance is confirmed, annotations are **not canonical strategy rules** and examples are **not ground truth**.
- Once authority is known, each dated episode can be converted into a structured training object:
  `HTF context → active zones → liquidity/TFS/HCS state → refinement → LTF decision → outcome/next state`.

## Separation policy

`Reflection / approved primary knowledge` remains above implementation helpers. Code can suggest detectors, data structures and state machines; it may never silently redefine a strategy concept. Visual top-down material can teach sequencing only according to its confirmed authority level.
