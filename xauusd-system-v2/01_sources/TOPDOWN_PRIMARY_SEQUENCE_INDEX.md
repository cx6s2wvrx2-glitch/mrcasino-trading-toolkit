# Primary Mr Casino Top-Down Visual Archive — Sequence Index

Source: `top down analysis (1).zip`
Source ID: `b271d0b8-a86b-4d65-a4ae-b7e49d5803a6`
Authority: `primary_mr_casino_top_down_visual_ground_truth`
User approved: yes
Total real chart images: **188**
Total dated sequences: **29**

Important: macOS `__MACOSX/._*` metadata files are excluded and are not chart evidence.

## Processing policy

Each dated sequence is processed in this order:
1. inspect every real chart in the sequence,
2. preserve exact chart date/file provenance,
3. extract only explicit or tightly supported Casino-labelled claims,
4. create valid / invalid / edge-case ground-truth candidates where justified,
5. attach honest implementation coverage/blockers,
6. keep all candidates `unverified` and `promotion_allowed=false`,
7. insert cases into persistent stores only when the connector permits the write,
8. extend blind validation only from persisted canonical datasets,
9. require green CI before any promotion claim.

A screenshot is not converted into a rule merely because it exists.
A non-XAUUSD sequence can be inspected for source inventory, but is excluded from XAUUSD strategy ground truth unless the user explicitly approves cross-instrument evidence.

## Sequence inventory

| Date | Images | Status | Ground-truth round |
|---|---:|---|---|
| 2021-11-21 | 5 | processed | Round 10 |
| 2021-11-28 | 4 | processed | Round 10 |
| 2021-11-30 | 2 | inspected_non_xauusd_excluded | — |
| 2021-12-06 | 4 | processed | Round 10 |
| 2021-12-12 | 7 | processed | Round 10 |
| 2022-01-10 | 4 | processed | Round 11 |
| 2022-03-14 | 4 | processed | Round 11 |
| 2022-04-03 | 5 | processed | Round 11 |
| 2022-07-30 | 5 | processed | Round 11 |
| 2022-10-10 | 7 | processed | Round 11 |
| 2022-11-20 | 5 | processed | Round 11 |
| 2023-05-18 | 6 | processed | Round 12 |
| 2023-05-19 | 8 | processed | Round 12 |
| 2023-05-22 | 5 | processed | Round 12 |
| 2023-05-30 | 5 | processed | Round 12 |
| 2023-06-06 | 7 | processed | Round 13 |
| 2023-06-20 | 6 | processed | Round 13 |
| 2023-06-21 | 10 | processed | Round 13 |
| 2023-06-26 | 6 | processed | Round 13 |
| 2023-07-10 | 6 | inspected_exhausted_gt_write_blocked | Round 14 prepared |
| 2023-08-21 | 9 | inspected_exhausted_gt_write_blocked | Round 14 prepared |
| 2023-11-01 | 12 | processed | Round 06 |
| 2023-11-06 | 10 | processed | Round 07 |
| 2023-11-08 | 2 | processed | Round 09 |
| 2023-11-20 | 12 | processed | Round 08 |
| 2024-07-16 | 11 | inspected_exhausted_gt_write_blocked | Round 15 prepared |
| 2024-07-24 | 7 | inspected_exhausted_gt_write_blocked | Round 15 prepared |
| 2024-07-29 | 8 | inspected_exhausted_gt_write_blocked | Round 15 prepared |
| 2024-07-30 | 6 | inspected_exhausted_gt_write_blocked | Round 15 prepared |

Current inspected/exhausted: **188 / 188 images across 29 / 29 sequences**.
Of those sequences, **28 are XAUUSD sequences** and **1 is a non-XAUUSD sequence inspected and excluded**.

### Persistence boundary

The final 47 XAUUSD charts (2023-07-10, 2023-08-21 and the four July-2024 sequences) have been visually inspected and their dominant ground-truth candidates/blockers prepared. A connector safety block prevented persisting the detailed trading-rule labels to GitHub during this pass. The block was not bypassed. These sequences are therefore source-exhausted but are **not** claimed as persisted canonical ground truth, blind-validation inputs, verified knowledge, verified rules, or certified detectors.

This index tracks source exhaustion only. `processed` or `inspected_exhausted_gt_write_blocked` does **not** mean strategy-verified or detector-certified.
