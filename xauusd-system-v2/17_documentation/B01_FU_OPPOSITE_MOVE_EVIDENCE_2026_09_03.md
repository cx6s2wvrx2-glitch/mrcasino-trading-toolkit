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

### Free Lessons

Lesson 4 explicitly describes a valid FU with two confirmations:
1. liquidity is taken;
2. the SAME candle breaks structure after taking the liquidity.

The lesson image/text does not provide a universal numeric distance or body-close threshold for that structure break.

### How to rinse the banks

The book states:
1. FU takes liquidity;
2. it must break the high/low of the previous candle.

The available parsed text contains a damaged/truncated parenthetical after that sentence. Searches do not recover a separate trustworthy `close above` / `close below` statement. Therefore no universal close-through rule is inferred from the damaged text.

The book also reinforces:
- the FU concept applies across all timeframes;
- liquidity/context comes before FU setups;
- not every forming FU should be traded.

### Reflection completion

Reflection later separates completion from the underlying FU criteria:
- ATT Form 1: no new high/low;
- Complete FU: FU criteria are met AND close is inside the previous open/close body;
- ATT Form 2: FU setup/new extreme exists but the required closure within the previous body is not achieved.

This is strong evidence that **structural break evidence and final closure location are separate dimensions**. It does not, by itself, fully define the upstream `FU criteria met` mechanic.

### Primary-source candidate interpretation — NOT PROMOTED

A source-consistent working interpretation is now plausible for Complete-FU research:
- the FU candle takes the relevant liquidity;
- the candle makes the required opposite-side structural excursion/break;
- final close location is then used by Reflection to distinguish Complete from ATT Form 2.

Because the exact intrabar order and exact universal structural-break mechanic are not fully stated for every FU context, this remains a candidate interpretation rather than a certified rule.

The live draft FU rule therefore continues to preserve `Exact break-of-structure/close threshold` as unresolved.

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

## What is now objectively measurable

`fu_observables.py` records, without classification:
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
It is specifically the unresolved **selection/composition rule** over observable opposite-move evidence plus intrabar ordering after liquidity is taken.

Candidate evidence families now separated are:

1. `CLOSE_THROUGH_OPPOSITE_EXTREME`
   - represented by Casino_v7 continuation FU branches.

2. `WICK_THROUGH_OPPOSITE_EXTREME_CLOSE_INSIDE_RANGE`
   - represented in Casino_v7/BETA branches and compatible with the idea that break evidence and closure class are separate dimensions.

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
- Do not treat the damaged book parenthetical as evidence of a close requirement.
- Do not use candle colour alone as the opposite-direction move.
- Do not collapse ATT Form 1 into no-FU.
- Do not tune a threshold from historical profitability.

## Next action

Represent previous-candle structural break evidence independently from final close position, then compare source-labelled examples/implementation branches against those facts.

Where raw source examples lack exact market timestamps, they remain semantic evidence rather than inferred raw fixtures.

Only after this comparison should B-01 be converted into a versioned candidate semantic rule for broader replay testing.
