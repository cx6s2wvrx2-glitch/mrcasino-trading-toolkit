# XAUUSD V2 — Primary Evidence Audit for B-05 to B-08

Date: 2026-09-02
Scope: XAUUSD V2 only
Status: PRIMARY-EVIDENCE RECONCILIATION / NO VERIFIED PROMOTION / NO DATABASE RESOLUTION

## Purpose

This audit narrows B-05 through B-08 using the already recovered approved corpus and the current V2 fail-closed boundaries. It records what is source-backed, what is only an applied example, and what remains genuinely unresolved.

Nothing in this document:
- changes `resolved_by_user`;
- changes source approval/status;
- promotes knowledge or rules to VERIFIED;
- authorizes live execution;
- treats helper code as strategy authority;
- converts a historical source percentage into production risk policy.

## B-05 — x3-by-x3 raw grammar

Primary evidence reviewed:
- `GIANNO_CASINO_REFLECTION_MASTER.pdf`, applied LTF establishment sequence around Reflection R-146/R-149;
- Reflection x3/negation sections distinguishing pure x3 negation from self-negating x3.

What the primary source establishes:
- an applied sequence exists in which retail liquidity is manipulated, LTF LAOL is taken, a 1m HCS x3 is followed by a 1m x3 negation labelled `x3 by x3`, and that sequence contributes to 10m HCS establishment;
- the source says the same process repeats across legs, supporting fractal reuse of the sequence logic;
- x3 has a special negation rule: its negation is the exception that does not require an ordinary full-FU close;
- `pure x3 negation` and `self-negating x3` are different concepts; the latter is weaker;
- x3 confirmation may take precedence in the cited context.

What the source does **not** establish:
- a standalone candle-by-candle grammar that lets V2 infer `x3 by x3` from raw OHLC alone;
- exact raw geometry of the first x3 component and the second/nested x3 component sufficient for a universal detector;
- a deterministic rule saying every visually similar nested manipulation is x3-by-x3.

Reconciled boundary:
- B-05 is no longer an empty label: its **relational role in an applied establishment sequence** is source-backed.
- B-05 remains open only at the **raw autonomous detector grammar** layer.
- `xauusd_v2.x3_by_x3_boundary` is therefore correct to allow an explicit primary-source label as context while keeping `raw_detector_allowed=False` and `strategy_condition_allowed=False`.

Do not infer:
- `x3 by x3 = any two x3 candles`;
- `x3 by x3 = HCS x3 + any following negation`;
- a raw OHLC formula from the name alone.

Evidence capable of resolving B-05:
- an explicit primary definition of x3-by-x3 raw geometry, or labelled positive/negative raw-candle fixtures sufficient to derive a reproducible rule without reverse-engineering from helper code.

## B-06 — Accepted RR numeric/dynamic definition

Primary evidence reviewed:
- `GIANNO_CASINO_REFLECTION_MASTER.pdf`, advanced x3 entry model / Reflection R-116.

What the primary source establishes:
- `Accepted RR` is a real source concept used together with complete liquidity calculation and multi-timeframe alignment in the advanced x3 entry model;
- the source describes the possibility of an exact-high entry in that advanced context;
- the source explicitly presents this as an advanced condition that does not occur on every setup;
- a more ordinary execution path remains entry after 1m negation closure and retest.

What the primary source does **not** establish:
- a numeric minimum RR;
- a fixed formula such as 1:N;
- whether acceptance changes by timeframe, target class, setup quality, spread/costs or liquidity structure;
- whether `Accepted RR` means a hard threshold or a context-dependent relationship between structural target and invalidation.

Reconciled boundary:
- B-06 is a confirmed concept with an unconfirmed decision function.
- No historical example of 1:10, 1:15, 1:100+ or any other RR may be inserted as the definition of `Accepted RR`.
- `xauusd_v2.accepted_rr_boundary` correctly rejects caller-supplied numbers unless a separate certified source definition exists.

Evidence capable of resolving B-06:
- an explicit primary statement defining the acceptance threshold/formula; or
- a user-approved production/research policy intentionally defined as an empirical policy rather than falsely attributed to the source.

## B-07 — 11h candle construction anchor

Primary evidence reviewed:
- `GIANNO_CASINO_REFLECTION_MASTER.pdf`, Reflection R-118 and multiple 11h applied examples.

What the primary source establishes:
- 11h is a genuine strategy/context timeframe in the approved corpus, not a transcription accident;
- 1h/3h/11h forming is used in longer-term swing context;
- an 11h HCS+negation forming state can be confirmed by the first aligned established 3h closure in its area;
- when the lower-timeframe confirmation stack and 11h/TFS align, the source discusses multi-day swing potential;
- the logic is applied fractally while refining lower.

What remains explicitly unresolved:
- why the custom bar is exactly 11 hours;
- its session origin/anchor;
- the timestamp at which the first 11h candle begins;
- how DST or broker/server time should affect synthetic aggregation, if at all.

Reconciled boundary:
- B-07 is **not** a question about whether 11h is strategically meaningful. Its role is source-backed.
- B-07 is only the reproducible bar-construction problem required to synthesize 11h from lower-timeframe broker data.
- `xauusd_v2.eleven_hour_timeframe` correctly permits already-formed provenance-bearing 11h context while blocking lower-TF synthesis without a certified anchor.

Evidence capable of resolving B-07:
- primary platform/chart settings or explicit source statement identifying the 11h anchor/session origin;
- alternatively, a provenance-preserving native 11h series can be consumed without pretending V2 knows how to synthesize it.

## B-08 — Production risk policy

Primary/historical evidence reviewed:
- `03_Analysis_Basics_.pdf` historical risk statements;
- older instructional material containing fixed-per-trade risk examples and conditional 3%/5% language;
- current `TARGETS_MANAGEMENT_RISK_CERTIFICATION_DRAFT.md` separation of strategy targets, trade management and production risk.

What the corpus establishes:
- risk management must be explicit and mechanical;
- historical material contains 3% guidance and a separate conditional up-to-5% statement in another context;
- RR, confluence/account context and risk are discussed together in older teaching material;
- these statements are **source claims**, not automatically a production policy for V2.

Critical governance distinction:

`strategy_source_truth != production_account_risk_policy`

A production risk limit is a deterministic safety policy chosen for the system/account. It should not be manufactured by resolving a historical teaching-source disagreement as though one percentage were universal strategy truth.

Reconciled boundary:
- B-08 cannot be resolved by selecting 3% or 5% from the corpus.
- The deterministic Risk Engine already supports an explicit policy and must remain a veto layer above strategy output.
- No production risk policy exists until the user explicitly approves one.

### Minimal production decision packet for B-08

When production policy is intentionally selected, record at minimum:
1. maximum risk per trade;
2. maximum aggregate open risk;
3. maximum daily realized+open loss before hard stop;
4. maximum concurrent positions and/or correlated XAUUSD exposure;
5. spread/slippage/data-quality veto behavior;
6. whether event/session restrictions are hard vetoes or strategy-context filters.

These values must be stored as **user-approved production policy**, not promoted as Mr Casino strategy facts.

Until then:
- live execution remains disabled;
- an incomplete risk policy must fail closed;
- 3% and 5% remain historical evidence only.

## Net result

No blocker is promoted or database-resolved by this audit.

The remaining unknowns are now precise:
- **B-05:** raw autonomous x3-by-x3 detector grammar only; applied relational semantics are known.
- **B-06:** Accepted-RR acceptance function/threshold only; concept and advanced-entry context are known.
- **B-07:** synthetic 11h anchor/session construction only; strategic use of 11h is known.
- **B-08:** explicit user-approved production safety policy; this is a governance/account-risk decision, not missing strategy-source truth.

## Implementation check

Current V2 boundaries already match this evidence:
- `src/xauusd_v2/x3_by_x3_boundary.py` — context-label only; no raw detector/strategy gate;
- `src/xauusd_v2/accepted_rr_boundary.py` — no arbitrary numeric threshold;
- `src/xauusd_v2/eleven_hour_timeframe.py` — native/provenance context allowed, synthetic aggregation blocked without anchor;
- deterministic Risk Engine — supplied complete policy required; strategy output cannot override risk vetoes.

No code relaxation is justified by this audit.

## Next actions

1. Keep Agent-06 independent validation separate from blocker resolution and let the real blind run complete.
2. Do not spend further extraction time trying to derive B-05/B-06/B-07 from names or helper behavior.
3. If additional primary material explicitly defines x3-by-x3, Accepted RR or the 11h anchor, ingest it as new evidence and re-open only the relevant boundary.
4. Prepare B-08 for an explicit user policy decision after strategy validation/backtest infrastructure is stable; do not silently choose a percentage now.
5. Keep VERIFIED counts unchanged and live execution disabled.