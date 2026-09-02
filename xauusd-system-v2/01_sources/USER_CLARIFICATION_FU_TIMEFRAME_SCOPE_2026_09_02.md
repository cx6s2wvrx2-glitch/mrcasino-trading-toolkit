# User Clarification — FU Family Timeframe Scope

Date: 2026-09-02
Scope: XAUUSD V2 only
Authority: explicit user clarification for strategy interpretation
Status: SCOPE CLARIFICATION / NOT A VERIFIED PROMOTION

## Clarification

The core logic and interpretation of the FU family is fractal across timeframes:

- Strong FU follows the same underlying logic on every timeframe.
- Attempted FU (ATT FU / AFU) follows the same underlying logic on every timeframe.
- A 1m example does **not** define a separate 1m-only Strong-FU or ATT-FU primitive.
- Timeframe changes contextual authority, hierarchy, expected move scale, and how the signal is used inside top-down analysis; it does not create a different primitive definition for FU / Strong FU / ATT FU.

## Important boundary

This clarification does **not** say that every downstream zone-construction rule is identical on every timeframe. A source may still prescribe a timeframe-specific application, such as a particular 1m zone construction. That application must remain scoped to the source that defines it.

Therefore:

`FU-family primitive logic = timeframe-invariant`

while

`downstream usage / authority / zone rules = may be timeframe-specific when explicitly source-backed`.

## What this resolves

The project must not infer from a 1m labelled Strong-FU example that Strong FU itself is a 1m-only concept or that its core logic changes on other timeframes.

## What this does not resolve

This clarification does not supply:

- a universal numeric Strong-FU body/wick/rejection threshold;
- the unresolved B-01 exact sufficient raw FU break mechanic;
- a universal rule that every Strong-FU candle on every timeframe becomes the same type of zone;
- any automatic VERIFIED promotion;
- live execution authority.

Ambiguous raw detection boundaries remain fail-closed until separately certified.