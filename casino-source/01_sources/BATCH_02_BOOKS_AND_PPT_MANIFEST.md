# XAUUSD V2 — Batch 02 Source Manifest

Approval date: 2026-09-01
Status: REVIEW

## Approved sources

| Source | Type | SHA-256 | Provenance handling |
|---|---|---|---|
| `How to rinse the banks - A forex guide.pdf` | Book | `1a16347bdbf0245a4caabb02375bfbb492f747d81bea40155bf438cb0a00b57e` | Primary instructional text; content identifies Mr. Casino framework. |
| `The Manipulation Mastery.pdf` | Book | `a3718f6d3eaed8caaf949a04308153407d87e84a04cd383eb24b83de31b87293` | Primary-style instructional book; page imagery is evidence. |
| `MrDomino_breakdown.pdf` | Visual case study | `c4fadce1b9197effb20a4efb16853b1489b951908fdaa4ec3cf8154931aac08e` | Author not established by metadata. Use primarily as annotated examples, not universal theory. |
| `BASICSTOINSTITUTIONALTRADING.pptx` | Presentation | `2e6a39f6871c0d57e7f62df3416cca57a1af3c2bd947a6736cd9b340a6568edd` | PPTX core author metadata: Irving Santiago. Secondary instructional evidence unless later promoted by user/cross-source certification. |

## Ingestion result

- 40 new `v2_knowledge` claims — all `UNVERIFIED`
- 8 `v2_examples` from the MrDomino visual breakdown — all `NEUTRAL / UNVERIFIED`
- 6 new glossary terms — all `UNVERIFIED`
- 4 sources moved to `REVIEW`
- Knowledge Agent run logged in `v2_agent_runs`

## New unresolved issues

1. **Risk conflict:** Analysis Basics caps risk at 3%; How to Rinse the Banks allows up to 5% for small accounts.
2. **FU definition partially clarified:** How to Rinse the Banks says liquidity taken + break of previous candle high/low, but exact wick-vs-close test remains unresolved.
3. **Imbalance geometry conflict:** earlier close-to-open definition vs later wick-before-to-wick-after definition.
4. **Orderblock boundary conflict:** body-only baseline vs explicit optional inclusion of wicks / limited exceptions.
5. **PowerPoint authority:** four-phase Manipulation Cycle and Fractals mapping are secondary-source candidates, not silently canonical.

## Governance

No item in this batch is `VERIFIED`. No conflict is auto-resolved. The visual MrDomino file is not used to generate universal rules without separate evidence. Secondary-source PowerPoint concepts must retain their source-authority label.
