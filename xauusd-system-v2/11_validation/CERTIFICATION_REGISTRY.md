# XAUUSD V2 — Certification Registry

Date: 2026-09-01
Status: ACTIVE

Purpose: make correctness auditable. A module is not considered VERIFIED because it has a plausible explanation or because an AI wrote a rule. It must pass explicit gates.

## Certification gates

Each module must pass all applicable gates:

1. **Primary-source support** — direct Mr Casino / top-priority Reflection evidence exists.
2. **Cross-source consistency** — later/high-authority sources do not materially contradict the candidate rule, or conflicts are explicitly resolved.
3. **Primary visual evidence** — labelled Mr Casino charts/examples support the interpretation where visual interpretation is required.
4. **Positive examples** — examples where the rule applies.
5. **Negative examples** — visually similar cases where the rule must not apply.
6. **Edge cases** — ambiguous/borderline cases are labelled and handled deterministically.
7. **Mechanical definition** — conditions, state transitions, invalidation and timestamps are unambiguous enough to implement.
8. **Independent validation** — a separate validation pass reproduces the labels without relying on the formalization pass.
9. **Historical reproducibility** — detector output can be recreated using only information available at that historical timestamp.
10. **Promotion decision** — user/certified process approves promotion from DRAFT/UNVERIFIED.

A module that fails any required gate remains `DRAFT / UNVERIFIED`.

## Current registry

| Module | Primary source | Cross-source | Primary visuals | Pos/Neg/Edge | Mechanical | Independent validation | Historical reproducibility | Current status |
|---|---|---|---|---|---|---|---|---|
| Liquidity / Major Liquidity / LAOL | strong | partial; source-evolution issue open | partial; PA Reflection labels started | incomplete | candidate v0.1 | not run | not run | DRAFT / UNVERIFIED |
| TFS / True Stop | strong Reflection + primary text | partial | partial | incomplete | candidate v0.1 | not run | not run | DRAFT / UNVERIFIED |
| FU Family | strong mixed primary/approved | blockers open: FU break + SFU threshold | partial | incomplete | candidate v0.1 | not run | not run | DRAFT / UNVERIFIED |
| FU Retest / HCS | strong | HCS grammar conflict open | partial | incomplete | candidate v0.1 | not run | not run | DRAFT / UNVERIFIED |
| Zones | source support exists | not consolidated yet | not certified | not built | not built | not run | not run | NOT STARTED |
| Imbalances | source support exists | geometry conflict open | not certified | not built | not built | not run | not run | NOT STARTED |
| Top-down Bias Engine | strong visual corpus exists | depends on previous modules | 188 Casino charts + Reflection visuals available | not built | not built | not run | not run | NOT STARTED |
| Entry / Re-entry Models | primary support exists | depends on TFS/TS/HCS/LAOL | partial | not built | not built | not run | not run | NOT STARTED |
| Targets / Management / Risk | mixed | risk conflict open | not applicable/partial | not built | not built | not run | not run | NOT STARTED |

## Current blockers that prevent VERIFIED status

Open conflicts/ambiguities are tracked in Supabase with `resolved_by_user=false` until genuinely resolved. Important current blockers include:

- major-liquidity source evolution / big-wick role;
- HCS strict definition versus broader component grammar;
- FU exact break criterion: wick breach versus close;
- FU retest validity versus quality;
- Strong FU quantitative threshold;
- imbalance geometry;
- order-block body/wick boundary exceptions;
- risk 3% versus 5%;
- Reflection source-number collisions.

## Promotion rule

No strategy rule is promoted because it is repeated often. Promotion requires evidence quality, not vote count.

Authority precedence for conflict review:

1. direct/top-priority Mr Casino primary material and explicitly current Reflection;
2. primary Mr Casino Q&A / Price Action Reflection / original top-down sequences;
3. earlier approved instructional PDFs/books;
4. high-value serious-student material as corroboration;
5. ordinary student material as examples/hypotheses only;
6. implementation helpers only after strategy certification.

Later sources are not automatically correct merely because they are later; explicit source evolution, direct clarification and visual certification are required.

## Failure-safe behavior

If a candidate cannot be classified reproducibly:

`AMBIGUOUS -> NOT CERTIFIED -> NO TRADE`

The objective is not to force every chart into a label. The objective is to make every production label defensible, reproducible and traceable.