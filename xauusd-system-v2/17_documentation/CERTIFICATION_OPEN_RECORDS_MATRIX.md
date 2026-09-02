# XAUUSD V2 — Open Certification Records Matrix

Updated: 2026-09-02

Purpose: distinguish database records that are genuinely blocking strategy certification from records that are already operationally contained by fail-closed code or source-governance rules.

Important: this document does **not** mark any `v2_disagreements.resolved_by_user` flag true. It is a current engineering classification only.

## A. Real strategy calibration blockers

### FU opposite-direction sufficiency
Database records: `66a9f8fb-2579-44cd-9a17-6fffc0ba2ffd`, `928a1381-b0d2-4905-a971-0fc311d6b105`

Current state:
- source-backed semantic criterion = liquidity take + opposite-direction move in the same candle;
- marked-liquidity interaction is implemented;
- lower-TF intrabar path reconstruction is implemented;
- parent/child broker-bar reconstruction is implemented;
- **remaining unknown** = what source-backed evidence is sufficient to declare the opposite-direction move complete without inventing a pip/body threshold.

Impact: blocks universal raw FU detector certification, but does not block semantic/candidate analysis.

### Imbalanced Candle broker geometry
Database record: `b332f762-21e8-4e60-bbe8-3a6243157c73`

Current state:
- Classic Imbalance and Imbalanced Candle are separated;
- broker precision/tick distance observables exist;
- helper `open==low/open==high` remains implementation hypothesis only;
- **remaining unknown** = canonical broker-feed geometry/tolerance for Imbalanced Candle.

Impact: blocks canonical raw Imbalanced-Candle detector.

### Universal Strong FU calibration
Database record: `39a7c1ef-06de-465e-abeb-94638c8b53ef`

Current state:
- source says strong close + little/no rejection and warns against excessive rigidity;
- threshold-free candle-quality metrics exist;
- one 1m-scoped structural Strong-FU feature exists in Reflection;
- **remaining unknown** = universal classification boundary, if one exists.

Impact: blocks universal numeric SFU detector; qualitative/scoped source labels remain usable.

### R-54 70% full-FU Fibonacci anchor
Database record: `712b253e-c9ba-48f3-a6b8-55d9b54e1498`

Current state:
- validity vs quality separated;
- wick touch = stronger;
- 50% of FU wick = strongest;
- >70% full-FU without wick = weak only when anchor is certified;
- **remaining unknown** = exact 0/100 orientation for full-FU fib.

Impact: blocks only the numeric 70% branch, not wick-based grading.

### x3 by x3 standalone grammar
Database record: `167aa018-4d6d-45e4-aa07-ca935c0855b3`

Current state:
- preserved as explicit primary source label only;
- no raw detector allowed;
- **remaining unknown** = standalone source definition/grammar.

Impact: blocks raw x3-by-x3 detector only.

### 11h construction anchor
Database record: `9f1b1bc0-5767-473a-a194-737b70d4b240`

Current state:
- native/provenance-backed 11h may be consumed;
- synthetic lower-TF construction is blocked;
- **remaining unknown** = session/candle anchor needed to reconstruct 11h bars.

Impact: blocks synthetic 11h historical reconstruction, not use of trusted native 11h series.

### Accepted RR numeric definition
Database record: `5c71cac8-ce92-4ecb-8cd1-e585fa66987a`

Current state:
- concept is preserved;
- arbitrary fixed RR thresholds are rejected;
- **remaining unknown** = numeric or dynamic source definition.

Impact: blocks using Accepted RR as a quantitative strategy gate.

## B. Production policy decision — intentionally not source-resolved

### 3% vs 5% risk
Database record: `7f77aa6b-ef30-470b-817a-d7cef9f016de`

Current state:
- deterministic risk engine is implemented;
- no 3% or 5% production value is hardcoded;
- production policy must be selected only after research/stress testing and explicit user approval.

Impact: does **not** block strategy understanding or historical signal research; it blocks final production risk configuration.

## C. Operationally handled — formal VERIFIED promotion still pending

### Liquidity-list source evolution
Database record: `e0dfa8f4-5949-4c8b-9867-3a2a16e3669f`

Handled by scoped `liquidity_taxonomy.py`: Reflection R-207 governs 30m+ core marking while older broader lists remain historical context.

### HCS definition evolution
Database record: `543b8f52-46ed-407e-81bb-7cd9fdd69507`

Handled by `hcs_semantic.py`: eligible new manipulation on retest of prior FU wick; source-confirmed near-enough allowed; unknown distance fails closed.

### Zone / orderblock body-vs-wick conflict
Database record: `db53242b-c544-4d64-a0a0-acc06db734e7`

Handled as distinct geometries in `zone_geometry.py`, not one optional wick switch.

These records remain database-open because operational containment is not the same as formal strategy verification.

## D. Governance / source-control records

### Secondary PPT authority
Database record: `6d143f13-6abc-4422-acb6-6b961c920653`

Already classified as secondary instructional evidence. It cannot override primary Casino material.

### Reflection numbering collision
Database record: `715fd692-7f17-47ee-9212-bc55a45d8e9b`

Already contained by page/occurrence/internal-ID provenance. Never use source R-number alone as unique identity.

## E. Separate known boundary not represented as one of the 14 current DB rows

### Trail-level selection
Reflection R-150 provides trail ordering/context but not a certified selector for which exact trail levels to mark/use. `target_semantic.py` therefore returns NOT_CERTIFIED for trail-level targeting unless an upstream certified selector is supplied.

## Practical interpretation

The database currently having 14 unresolved records does **not** mean 14 strategy components are broken.

The important remaining technical/source unknowns are concentrated in:
- FU opposite-move calibration;
- Imbalanced-Candle broker geometry;
- universal Strong-FU calibration;
- R-54 fib anchor;
- x3-by-x3 grammar;
- 11h construction anchor;
- Accepted RR definition;
- trail-level selection;
- final production risk policy.

Everything else above is either already fail-closed/operationally contained or is a governance record awaiting formal certification rather than invention.
