# MR CASINO — XAUUSD Trading System

Mechanical reconstruction of the MR CASINO XAUUSD strategy: a TradingView Pine indicator plus a source-locked rulebook.

## Structure
- `build/` — the live TradingView Pine indicator (current working build).
- `docs/SOURCE_TRUTH.md` — genuine, source-locked strategy definitions (the real rulebook).
- `docs/AUDIT_READ.md` — reference to the full read/audit: what was kept vs discarded.
- `casino-source/` — the genuine primary MR CASINO material kept verbatim (narratives, feed guidance, replay episodes/anchors, user clarifications).

## Status
- Indicator: LIVE, multi-timeframe (3/5/10/15/30m), intrabar signals, per-trade audit log, structural SL, TF-adaptive partials.
- Source of truth = the uploaded MR CASINO material (PDFs, handwritten notebook photos, chart screenshots) held in the Claude project.
- The prior ChatGPT `xauusd-system-v2` scaffolding was audited and removed: it produced 0 verified rules and 0 backtests. Its genuine source extractions are folded into `docs/SOURCE_TRUTH.md`; the raw primary material is preserved under `casino-source/`.

Research/backtesting only. No live execution. Not financial advice.
