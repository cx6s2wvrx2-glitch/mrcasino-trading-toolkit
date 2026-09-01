# Liquidity / Major Liquidity / LAOL — Certification Draft

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01

This document consolidates currently approved source claims. It does not create new strategy truth and does not resolve conflicts automatically.

## 1. Core concept — strong cross-source support

Current approved sources repeatedly place liquidity first in analysis. The strategy does not treat a single pattern, zone, FU or HCS as sufficient context by itself. Liquidity calculation is the primary frame and other concepts refine or confirm it.

Primary-source formulation currently supported:

- Liquidity refers to obvious/concentrated retail stop-loss areas.
- Major liquidity is not identical to Last Area of Liquidity (LAOL).
- Liquidity left behind is not automatically taken immediately.
- A visible liquidity point can be downgraded when subsequent manipulation shows price is comfortable leaving it behind.
- Bias/continuation requires comparison of the prevalent move, which side has been manipulated more, and which side carries more important liquidity.

## 2. Major-liquidity types

Later direct/primary material strongly supports the following four-type list:

1. unmanipulated doji
2. perfect double top / double bottom
3. perfect trendline
4. imbalanced candle / IMB

Q&A 2024 independently repeats the same four categories and states doji/IMB liquidity is the most prevalent.

### Open evolution issue

Older Analysis Basics / How to Rinse material includes big-wick rejection as a liquidity example. Later Last Areas material explicitly presents the four-type list as an update, but no user certification has yet closed the evolution issue.

Therefore:

- do not delete the older big-wick evidence;
- do not treat big wick as a fifth canonical major-liquidity type yet;
- preserve it as historical/source-evolution evidence until certified against Reflection/top-down examples.

## 3. Major vs minor / lower-priority liquidity

Source-supported observations:

- A perfect trendline requires 3+ perfect rejection points for major-liquidity classification; two points are described as low liquidity.
- Opposite/weak forms are described in Last Areas material: doji ↔ Attempted FU, perfect double/trendline ↔ non-perfect rejection, imbalanced candle ↔ balanced candle.
- A lower-timeframe DB/doji is not automatically a major target merely because it exists.
- Primary Price Action Reflection examples explicitly downgrade nearby 1m liquidity after stronger HCS/manipulation evidence.
- Manipulation after a liquidity point can be evidence that opposite-side liquidity is more important.

Candidate future data field:

`liquidity_priority = major | lower_priority | minor | unresolved`

This field is NOT yet mechanically defined.

## 4. LAOL — current strongest source-supported interpretation

Direct approved sources support LAOL as more specific than generic liquidity.

Current best-supported formulation:

- LAOL is the final/refined liquidity area associated with the move/reversal, not every major-liquidity point.
- Reflection R-208: practical LAOL is the target of the liquidity grab that started the move; each reversal starts there and is refined lower.
- Reflection R-90: a doji taken instantly or inside a liquidity grab is the LAOL of its timeframe.
- Reflection R-60: true reversal is modeled LAOL→LAOL separately within each TFS setting.
- Last Areas material describes LAOL as the most concentrated/refined liquidity areas where reaction/reversal is expected when major targets exist opposite.

### Important distinction

`major_liquidity != LAOL`

A level can be major liquidity without being the final/active LAOL for the current move.

## 5. Timeframe dependence

Current source-supported points:

- HTF liquidity establishes broader target/context.
- Reflection R-111 says HTF major liquidity is finalized as a target only at 1m; 1m liquidity reasoning is core to final entry/refinement.
- Reflection R-207 narrows practical 30m+ marking to core items: unfilled big-wick-to-fill and unmanipulated dojis, with breakout liquidity optional/advanced.
- Earlier material gives broader scanning methods; these must be reconciled with the Reflection operational version rather than merged blindly.

No deterministic timeframe mapping is certified yet.

## 6. Liquidity calculation — candidate process map

The following sequence is supported strongly enough to use as a certification hypothesis, but not yet as a production rule:

1. identify major liquidity in both directions;
2. identify the prevalent/stronger move and HTF TFS context;
3. determine which side has already been manipulated more;
4. compare the importance/concentration of remaining liquidity on both sides;
5. account for zones and true-stop placement;
6. refine the active target/LAOL down to LTF, ultimately 1m where required;
7. only then evaluate entry-model evidence such as HCS, FU retest, negation or x3.

This ordering is reinforced by Reflection R-95/R-143/R-145 and Q&A statements that liquidity calculation outranks sole x3/pattern logic.

## 7. Liquidity and True Stop

Current evidence links liquidity and TS tightly:

- after liquidity is generated/manipulated, a true stop can form;
- Reflection R-108 defines TRUE STOP as the low/high where all 10min+ TFS factors align, followed by LTF HCS/negation entry after respect plus final liquidity calculation;
- primary Q&A states formation strength, timeframe, session timing, zones, major-liquidity reasoning and TFS placement determine the relevant true stop.

Therefore TS must not be coded as a static candle pattern independent of liquidity/TFS context.

## 8. Entry gate relationship

Current primary material supports:

- liquidity calculation first;
- entry only after the active liquidity/LAOL and true-stop context is established;
- aggressive/forming entries require stronger surrounding alignment, not merely a forming FU/HCS;
- visible liquidity alone does not imply reversal or entry.

## 9. Open items requiring visual certification

Before this concept can become VERIFIED, certify against primary Mr Casino Reflection/top-down visual episodes:

1. exact mechanical criteria for `major` vs `lower_priority` liquidity;
2. exact LAOL identification procedure when several candidates exist;
3. how 30m+ marking rules interact with 1m finalization;
4. whether/when big wick is a canonical liquidity type versus a fill/target structure;
5. how to quantify "which side has more important liquidity";
6. how manipulation/HCS downgrades a previously marked liquidity point;
7. positive, negative and edge-case examples for each of the four major-liquidity types;
8. positive, negative and edge-case examples for LAOL.

Until these are certified, ambiguous cases remain `NO TRADE / NOT CERTIFIED`.
