# Independent Validation Protocol — XAUUSD V2

Status: ACTIVE PROTOCOL / NO STRATEGY PROMOTION IMPLIED
Date: 2026-09-01

Purpose: verify that candidate strategy labels/rules can be reproduced independently from primary evidence, rather than merely appearing plausible to the same formalization pass that created them.

## 1. Independence rule

The validation pass must not rely on the wording of the candidate rule as its evidence source.

For each test item, validator input should contain only:
- source chart / source text excerpt;
- timestamp / timeframe where known;
- permitted prior market context available at that historical moment;
- source provenance.

The validator should output its own classification before seeing the expected formalized label.

## 2. Required outputs per test item

- `concept`
- `observed_label`
- `confidence`
- `evidence_refs`
- `reason_summary`
- `ambiguity_flags`
- `historical_information_available`
- `no_trade_if_ambiguous`

Then compare against the expected candidate label.

## 3. Comparison outcomes

`AGREE_EXACT`
- validator independently returns the same concept/state.

`AGREE_FUNCTIONAL`
- wording differs but deterministic downstream meaning is the same.

`DISAGREE`
- validator selects a materially different state/rule outcome.

`AMBIGUOUS`
- source evidence does not support one deterministic label.

`INVALID_TEST`
- missing context / future information leakage / source provenance problem.

Only `AGREE_EXACT` and pre-approved `AGREE_FUNCTIONAL` count as agreement.

## 4. No future leakage

Historical validation must use only information available at the decision timestamp.

Forbidden:
- using later candles to decide whether a forming state was 'really' valid;
- reclassifying a failed provisional pattern as if the failure had been knowable earlier;
- using later annotations that reveal future outcome unless the task is explicitly post-session classification.

Every test must declare:
- `decision_timestamp`
- `confirmation_timestamp`
- `post_session_only = true/false`

## 5. Minimum test composition per concept

Before promotion, each mechanical concept should include at least:
- positive / valid examples;
- negative lookalikes / invalid examples;
- edge cases;
- multi-timeframe conflict examples when relevant;
- broker-data discrepancy examples when the concept depends on precise LTF geometry.

No concept passes with only positive examples.

## 6. Core modules to validate

Order:
1. Liquidity / Major Liquidity / LAOL
2. TFS / True Stop
3. FU Family
4. FU Retest / HCS
5. Zones
6. Imbalances
7. Top-down Bias Engine
8. Entry / Re-entry Models
9. Targets
10. Trade Management
11. Risk policy (policy validation, not source-truth validation)

## 7. Promotion metrics

Two metrics are kept separate:

### A. Label agreement
How often independent validation matches expected labels.

### B. Coverage / abstention
How often the source is sufficiently clear to label at all.

High agreement achieved by forcing ambiguous cases into labels is NOT acceptable.

Preferred behavior:
`AMBIGUOUS -> NO_TRADE / NOT_CERTIFIED`

## 8. Initial promotion target

For strict ground-truth examples intended to become deterministic implementation tests, target approximately 98–100% functional agreement on the approved labelled set before promotion.

This is an implementation-consistency target, NOT a profitability guarantee and NOT an expected win rate.

## 9. Disagreement handling

If validator and formalizer disagree:
1. return to primary evidence;
2. inspect source wording + chart context;
3. determine whether the issue is:
   - bad candidate rule;
   - missing context;
   - ambiguous source;
   - multiple valid states;
   - source evolution;
   - data-feed discrepancy;
4. do not silently choose the formalizer's answer;
5. create/update a disagreement record where material;
6. ask user only if approved sources cannot resolve it.

## 10. First validation set

Use existing labelled evidence already stored in `v2_examples`, beginning with:
- Casino notebook True Stop valid/invalid/edge cases;
- Reflection HCS tolerance and establishment cases;
- Price Action Reflection liquidity/LAOL cases;
- zone activation/lifecycle cases;
- 2023-11-01 primary top-down sequence as an end-to-end contextual test.

## 11. Reproducibility gate

A label that is semantically correct but cannot be recreated programmatically without future information is not implementation-certified.

Final promotion requires BOTH:
- source/visual agreement;
- historical reproducibility.

## 12. Risk-policy exception

Production risk percentages are not validated as 'Casino strategy truth'. They require an explicit production policy decision plus empirical stress testing.

The deterministic risk engine always retains veto authority over strategy output.