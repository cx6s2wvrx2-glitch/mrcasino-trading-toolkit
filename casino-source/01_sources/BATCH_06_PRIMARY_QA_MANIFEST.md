# XAUUSD V2 — Batch 06: Primary Mr Casino Q&A

Date: 2026-09-01
Status: REVIEW

## Source

- Title: `Mr Casino Q&A — March-April 2024`
- Original upload: `Pasted markdown(5).md`
- SHA-256: `ea42f7ea466c53ce8cfc204cfb87f2e53d1670a85c63dc6ba499409989997138`
- Size: 43,275 bytes
- Direct Mr Casino answer blocks found: **15**
- Authority: **PRIMARY SOURCE — Mr Casino direct answers**

## Ingestion policy

1. Student questions are context only.
2. A claim written by a student is NOT strategy truth unless Mr Casino explicitly confirms it in his answer.
3. Direct Mr Casino answers may become primary evidence, but remain `UNVERIFIED` at system level until certification.
4. Promotional/profitability rhetoric is preserved in the source archive but is not promoted into mechanical strategy rules or performance targets.
5. Where an answer appears to clarify an older rule, it is recorded as clarification/evolution rather than silently overwriting prior rules.

## First clean extraction

- 12 primary Q&A knowledge claims inserted into `v2_knowledge`.
- 1 knowledge-agent run logged as `needs_review`.
- 1 new unresolved ambiguity opened: **FU retest validity vs FU retest quality**.

## High-value primary clarifications

### x3 FU
Mr Casino defines x3 FU as the strongest manipulation type with three components:
1. FU wick in one direction.
2. Negation attempt by the opposite side.
3. The negation attempt is broken.

He also states that true moves are sought with some kind of x3 confirmation and that x3 can appear through different structures (x3 FU candle, x3 HCS retest, or three-candle manipulation sequence). Liquidity calculation remains more important than the isolated x3 concept.

### Top-down / no-trade under doubt
Every candle is to be interpreted inside the overall top-down analysis. Major liquidity in both directions, zones and timeframe strength must be accounted for. No entry when the trader is confused or doubtful.

### FU retest nuance
A 1m FU retest can be valid on the body; the wick does not always have to be met. This is kept separate from Reflection retest-quality grading, where wick touch / 50% wick describe stronger retests.

### Broker-data priority
Primary Q&A recommends IC Markets MT4 or Forex.com for analysis, with Pepperstone sometimes used around news when Forex.com does not align with broker data. Vantage is not preferred for precise LTF analysis.

### Liquidity set
Four main liquidity types are restated:
- perfect trendline,
- perfect double top/bottom,
- unmanipulated doji,
- imbalance (IMB).

Doji/IMB are described as the most prevalent. Liquidity calculation must still be combined with timeframe strength, zones and opposite-side liquidity.

### Entry-system coverage
The Q&A describes the system as covering zones, HCS, FU retest, x3, LAOL-met and negation POI. Entry models outside the trader's defined plan should not be taken. Full-confidence entries are tied to a true-stop retest inside liquidity calculation.

### Aggressive entry exception
A sole 1m FU forming may sometimes support an aggressive entry only with specific context, especially reaction from a prior FU retest/zone and extreme opposite-side liquidity. This is an exception context, not a universal entry rule.

### True-stop hierarchy
True-stop potential depends on liquidity context, formation strength and timeframe. HCS x3 is not equivalent to a sole OB+FU; HTF context prevails for larger true moves.

### Swing template
Daily/LTF extraction is prioritised before swing holding. A basic template in the Q&A uses 3h+ alignment for larger intraday moves and 7–11h+ backing for multi-day swing potential, with actual holding also dependent on targets, liquidity trail, TFS and formation strength.

## Open item: FU retest validity vs quality

Primary Q&A: a body retest may count even without wick touch.
Reflection R-54: retest quality is graded stronger on wick touch and strongest at 50% of FU wick.

V2 interpretation for now:
- `retest_validity` and `retest_quality` must be separate fields.
- Do not require 50% wick merely to label every FU retest.
- Do not assume every body retest is entry-quality.
- Certify this distinction against Mr Casino primary visual examples before promotion.
