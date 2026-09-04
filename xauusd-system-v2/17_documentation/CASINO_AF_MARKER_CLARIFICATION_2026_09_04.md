# XAUUSD V2 — Supplied Casino Indicator A/F Marker Clarification

Date: 2026-09-04
Status: EXPLICIT USER CLARIFICATION / IMPLEMENTATION LEGEND EVIDENCE
Scope: Supplied Casino indicator marker semantics only

## User clarification

The user explicitly clarified the visible marker legend used by the supplied Casino indicator:

- `A` = **Attempted FU**
- `F` = **Strong FU**

This clarification was supplied together with a TradingView screenshot showing the Casino indicator running on `MNQ1!` on the `15m` timeframe, with multiple visible `A` and `F` markers.

## What this resolves

Historically, the V2 shadow of the supplied helper code preserved the original implementation enum names:

- `HelperFUClass.FU`
- `HelperFUClass.ATT`

Those names were intentionally treated as implementation labels rather than final strategy semantics.

The explicit user clarification now resolves the **visible indicator legend mapping**:

- legacy helper `FU` output -> visible `F` -> **Strong FU marker**
- legacy helper `ATT` output -> visible `A` -> **Attempted FU marker**
- legacy helper `NONE` -> no FU-family marker

This mapping is implemented in `src/xauusd_v2/casino_marker_semantics.py` rather than by renaming the legacy helper enum, so historical code-shadow fidelity is preserved.

## Important boundary

This clarification establishes what the supplied indicator's visible labels mean. It does **not** by itself establish:

- a universal numeric Strong-FU threshold;
- that every `F` produced by the helper is source-certified Strong FU strategy truth;
- that every `A` produced by the helper maps exactly to Reflection ATT Form 1 versus Form 2;
- a universal raw FU detector;
- XAUUSD performance or trading validity.

Therefore `B-03` remains open for any universal numeric Strong-FU threshold.

## Screenshot use boundary

The screenshot is from `MNQ1!` / `15m`, not XAUUSD.

It is used only as:
- visual confirmation of the supplied indicator marker legend;
- implementation-behavior evidence;
- support for the user's explicit clarification.

It must **not** be inserted into the XAUUSD replay corpus as raw market ground truth and no XAUUSD candle timestamp/OHLC may be inferred from it.

## HCS implication

Primary HCS grammar allows node types:
- Strong FU,
- Attempted FU,
- FU Negation.

The clarified marker legend therefore gives a clean research-node adapter:

- `F` marker -> `HCSNodeType.STRONG_FU`
- `A` marker -> `HCSNodeType.ATTEMPTED_FU`

However the adapter must preserve provenance. A user-clarified indicator marker is not equivalent to a source-certified raw FU node.

For example, two `F` markers can satisfy the **Strong-FU + Strong-FU HCS grammar** if a valid retest is supplied, but the resulting HCS must remain non-certified unless the underlying node semantics and retest evidence are independently certified.

## Governance

Do not:
- reinterpret `F` as generic Complete FU;
- reinterpret `A` as one specific Reflection ATT subtype without more evidence;
- infer a Strong-FU percentage threshold from the marker output;
- use the MNQ screenshot as XAUUSD replay data;
- promote HCS/live readiness from marker agreement alone.
