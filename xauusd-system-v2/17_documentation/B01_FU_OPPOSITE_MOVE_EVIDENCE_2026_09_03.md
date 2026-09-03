# XAUUSD V2 — B-01 FU Opposite-Move / Break Evidence

Date: 2026-09-03
Status: OPEN BLOCKER NARROWING / NOT CERTIFIED

## Question

What exact raw mechanic is sufficient for the FU requirement that, after taking liquidity, price moves/breaks in the opposite direction within the same candle?

This document narrows B-01 using primary source evidence plus the user-supplied Casino_v7/BETA code. It does not invent a universal rule.

## Primary-source boundary

Approved source evidence establishes the semantic requirement:
- liquidity is taken;
- an opposite-direction move/break occurs;
- the relationship belongs to the same FU candle.

Older/parallel source descriptions refer to a break of structure / previous-candle high-low, while later Reflection separates completion classes by new-extreme state and closure relative to the previous candle body.

The live draft FU rule already preserves the unresolved point as `Exact break-of-structure/close threshold`.

## Casino_v7 mechanical evidence

The original user-supplied code is explicit but context-dependent.

### Bullish continuation FU

Requires:
- bullish current candle,
- current low below previous low,
- current close above previous close,
- current high above previous high,
- current close above previous high.

This is strong evidence for one implementation interpretation in which the opposite move trades through and closes beyond the opposite previous extreme.

### Bullish continuation ATT

Same broad two-side excursion, but current close remains below previous high.
The code labels this ATT rather than FU.

### Bearish continuation FU — close-through branch

Requires:
- bearish current candle,
- high above previous high,
- close below previous close,
- low below previous low,
- close below previous low.

This mirrors the bullish close-through interpretation.

### Bearish continuation FU — inside-range branch

The same code also has a FU branch where:
- high exceeds previous high,
- low breaks previous low,
- close is below previous close,
- BUT close remains above previous low.

Therefore Casino_v7 itself does not support a universal statement that every FU must close beyond the opposite previous extreme.

### Pullback / reversal blocks

Casino_v7 uses additional relationships involving:
- current candle colour,
- previous open,
- previous close,
- whether the second extreme is broken by wick,
- whether close is above/below previous open/body.

Many of these branches are ATT rather than FU, and some duplicate/subset branches are unreachable because an earlier condition captures the same geometry.

Conclusion: Casino_v7 provides high-value branch mechanics but not one internally consistent universal B-01 threshold.

## BETA 1 + LAOL mechanical evidence

The BETA core FU predicates are broader and structurally different:

Bullish candidate:
- low below previous low,
- close back above previous low,
- close below previous high,
- not x3,
- not self-negation-together.

Bearish candidate:
- high above previous high,
- close back below previous high,
- close above previous low,
- not x3,
- not self-negation-together.

Thus the BETA candidate explicitly permits/targets a close back inside the previous range rather than requiring a close through the opposite extreme.

The BETA also routes both-side outside-bar structures into x3 or self-negation states before ordinary FU candidates.

Conclusion: BETA contributes state/exclusion mechanics and a broad return-inside-range FU candidate interpretation. It cannot be substituted directly for Reflection Complete/ATT truth.

## Reflection completion evidence

Reflection gives a different layer of the problem:
- ATT Form 1: no new high/low;
- Complete FU: FU criteria met + close inside previous candle body;
- ATT Form 2: FU criteria met/new extreme + required body closure not achieved.

This means the final Complete-vs-ATT2 class is not identical to the Casino_v7 continuation FU/ATT distinction.

## What is now objectively measurable

`fu_observables.py` now records, without classification:
- whether previous high/low were swept;
- whether both sides were swept;
- whether close is inside previous total range;
- whether close is above previous high / below previous low;
- whether close is inside/above/below previous body;
- close relative to previous open and previous close;
- open relative to previous open and previous close;
- candle direction.

This covers the key raw relationships used by Casino_v7/BETA while leaving strategy truth unresolved.

## B-01 narrowed conclusion

B-01 is no longer an undefined generic question.
It is specifically the unresolved **selection/composition rule** over observable opposite-move evidence.

Candidate evidence families now separated are:

1. `CLOSE_THROUGH_OPPOSITE_EXTREME`
   - represented by Casino_v7 continuation FU branches.

2. `WICK_THROUGH_OPPOSITE_EXTREME_CLOSE_INSIDE_RANGE`
   - represented in Casino_v7/BETA branches and potentially interacts with Reflection closure classes.

3. `RETURN_RELATIVE_TO_PREVIOUS_BODY`
   - previous open/close relationships used in pullback/reversal and Reflection Complete/ATT2 classification.

4. `NO_NEW_EXTREME_ATT_FORM_1`
   - Reflection ATT Form 1; cannot be detected by sweep-only logic.

5. `BOTH_SIDE_X3_OR_SELF_NEGATION_EXCLUSION`
   - BETA routes some both-side geometry away from ordinary FU.

The unresolved strategy question is which of these observable families satisfy the source phrase `FU criteria met` in each context, and under what preceding liquidity/manipulation conditions.

## What must NOT happen

- Do not set `close beyond previous high/low` as a universal FU rule from Casino_v7 alone.
- Do not set `close back inside previous range` as a universal FU rule from BETA alone.
- Do not use candle colour alone as the opposite-direction move.
- Do not collapse ATT Form 1 into no-FU.
- Do not tune a threshold from historical profitability.

## Next action

Use source-labelled cases and existing source text to search specifically for statements/examples that distinguish:
- close-through extreme,
- wick-through + body return,
- body-close requirement,
- pullback/reversal FU versus ATT.

Where raw source examples lack exact market timestamps, they remain semantic evidence rather than inferred raw fixtures.

Only after this comparison should B-01 be converted into a versioned candidate semantic rule for broader replay testing.
