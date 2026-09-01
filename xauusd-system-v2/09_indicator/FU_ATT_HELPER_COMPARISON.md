# FU / ATT FU Helper Implementation Comparison

Status: implementation-evidence only. This document does **not** define canonical strategy truth.

## Authority order

1. Approved Mr Casino primary sources
2. Canonical V2 definitions / certified labelled examples
3. Helper implementations (`Casino_v7.txt`, `BETA 1 + LAOL.txt`)

Helpers may reveal useful implementation structure, historical intent, edge cases and bugs. They may not override primary source evidence.

## Casino_v7.txt

The Pine v5 helper contains an explicit OHLC decision tree for bullish and bearish FU / Attempted FU with separate continuation, pullback and reversal branches.

### Bullish continuation branch

Observed helper logic includes:

- bullish candle
- current low below previous low
- current close above previous close
- current high above previous high
- close above previous high -> FU branch
- close below previous high -> ATT branch

Important implementation defect: a duplicated `close < high[1]` condition marks ATT first and then repeats the same condition for FU. Because this is an `else if` chain, the later FU branch is unreachable.

### Bearish continuation branch

Observed helper logic includes the mirror structure:

- bearish candle
- current high above previous high
- current close below previous close
- current low below previous low
- close below previous low -> FU branch
- variants closing back inside previous range -> ATT/FU branches

There are additional pullback and reversal branches. Some branches are duplicate/subset conditions and therefore unreachable. These must be treated as implementation bugs, not strategy definitions.

## BETA 1 + LAOL.txt

The later Pine v6 beta uses a much more compressed FU representation inside its multi-timeframe state machine.

Observed core candidate logic:

```text
bear_fu_candidate =
    current high > previous high
    AND current close < previous high
    AND current close > previous low
    AND NOT x3
    AND NOT self-negation

bull_fu_candidate =
    current low < previous low
    AND current close > previous low
    AND current close < previous high
    AND NOT x3
    AND NOT self-negation
```

This implementation therefore treats the current close as returning inside the **previous full high-low range**, not necessarily inside the previous candle body.

The beta also separately models x3, self-negation, HCS, retest states and LAOL, so FU is not intended to be interpreted in isolation.

## Comparison with current approved primary source layer

Reflection R-120..R-122 currently gives a newer source-backed classification layer:

- no new high/low -> Attempted FU form 1
- new extreme + upstream FU criteria + close inside previous candle body -> Complete FU
- new extreme + FU setup but no required closure inside previous body -> Attempted FU form 2

This creates a material implementation difference:

- `Casino_v7` often distinguishes FU/ATT using previous high/low and close-through conditions.
- `BETA` uses a one-side sweep followed by close inside previous **range**.
- Reflection R-120 uses close inside previous **body** once upstream `FU criteria met` is satisfied.

V2 must not silently collapse these three into one rule.

## Current V2 handling

V2 already extracts the raw facts needed to compare all three approaches without guessing:

- previous-high sweep
- previous-low sweep
- both-side sweep / outside-bar state
- current candle direction
- close location relative to previous high/low
- close inside previous body
- FU candle quality metrics

The next certification step is to build labelled test vectors and run the helper predicates side-by-side against the primary labels.

## Required next tests

For every approved explicit FU / ATT example, record:

1. Primary source label
2. OHLC observables
3. `Casino_v7` predicted class
4. `BETA` predicted class
5. Reflection R-120 completion class where applicable
6. Agreement / disagreement
7. Whether disagreement is caused by source evolution, helper bug, timeframe scope or unresolved upstream `FU criteria met`

No helper result may auto-promote a rule to VERIFIED.
