# XAUUSD V2 — Batch 02 Draft Rule Candidates

Status: **DRAFT / NOT VERIFIED**

These candidates are extracted from the four approved Batch 02 sources. They are intentionally not promoted to production rules.

## Candidate set

### XAU-V2-TF-003 — Daily alignment candidate
A lower-timeframe trade candidate must first be checked against daily context.

**Unresolved:** exact mechanical definition of “aligned”.

### XAU-V2-FU-003 — Previous-candle break criterion candidate
A valid FU candidate takes liquidity and breaks the previous candle high/low.

**Unresolved:** whether a wick breach is enough or a close beyond the level is required; relationship to earlier “break of structure” wording.

### XAU-V2-FU-004 — Post-close FU entry candidate
One documented method enters after an FU closes and places the protective invalidation beyond the FU wick, primarily on smaller timeframes.

**Unresolved:** exact timeframe whitelist and execution buffer.

### XAU-V2-FU-005 — Aggressive FU context gate
Do not use every forming FU. Require prior manipulation/liquidity and alignment with broader structure/targeted liquidity.

**Unresolved:** minimum mandatory confluence set.

### XAU-V2-IMB-003 — Wick-to-wick imbalance geometry candidate
`How to Rinse the Banks` describes the untested imbalance region from the wick of the candle before displacement to the wick of the candle after it.

**Conflict:** Source 02 used a close-to-open geometry.

### XAU-V2-AN-002 — Eight-confirmation checklist candidate
Source checklist:
1. Daily context
2. Institutional zone
3. Liquidity taken
4. Liquidity to target
5. FU scenario
6. FU retest
7. Imbalance fill
8. Imbalance to target

**Unresolved:** mandatory gates vs optional confirmations and weighting.

### XAU-V2-LIQ-004 — Low-liquidity path direction candidate
After mapping relevant liquidity, the candidate directional framework prefers the path interpreted as lower liquidity.

**Unresolved:** mechanical low-liquidity score.

### XAU-V2-SEC-001 — [SECONDARY] Four-phase Manipulation Cycle
From Irving Santiago PowerPoint:
1. Stop-loss cluster
2. Manipulation against cluster
3. Return to original cluster level
4. Change in orderflow

Candidate entry timing is phase 3.

**Authority:** secondary instructional evidence only until explicitly promoted/certified.

### XAU-V2-SEC-002 — [SECONDARY] Fractal liquidity mapping workflow
PowerPoint mapping sequence: H4 → H2 → H1 → M30 → M15 → M5, using Fractals as a reference for possible liquidity levels before lower-TF execution.

**Authority:** secondary. **Unresolved:** whether Fractals becomes a canonical system input and which parameters are used.

### XAU-V2-MGMT-001 — Position-management candidate
`The Manipulation Masterkey` proposes reducing exposure toward break-even when feasible and securing partial profit while respecting the trade’s potential.

**Unresolved:** exact trigger, partial size and exceptions.

## Promotion rule

None of these candidates may become `VERIFIED` from source text alone. Conflicts must be resolved and mechanical definitions must be tested against approved examples before coding.
