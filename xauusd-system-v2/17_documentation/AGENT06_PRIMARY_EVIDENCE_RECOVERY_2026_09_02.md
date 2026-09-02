# Agent-06 Primary Evidence Recovery — 2026-09-02

Status: **source-side recovery complete enough for full blind-corpus resolution work; independent validation NOT executed**

This document records source recovery and staging only. It does not promote any strategy rule, does not change any expected blind label, and does not claim independent-provider agreement.

## Safety boundary

The Agent-06 evidence path remains label-blind:

`source_locator -> original approved source asset -> immutable/content-addressed context -> external validator`

The staging boundary does **not** accept or persist:
- `expected_label`
- `expected_class`
- `forbidden_inference`
- `ground_truth_answer`
- `promotion_allowed`

Ground-truth comparison remains downstream of the independent prediction step.

## Recovered original source material

Persistent private source recovery now includes the material needed by the canonical Rounds 02–13 source families:

1. `casinonotes.excalidraw`
   - original Excalidraw document recovered from the private Library;
   - all **18** R02 `#embedded:<fileId>` identifiers exist exactly in the document's `files` map and are referenced by live image elements;
   - the one R02 `#text:<elementId>` identifier exists as a live text element;
   - embedded image bytes are decoded from the original data URLs and validated against the declared image MIME/signature before staging.

2. `top down analysis (1).zip`
   - **188** original chart images;
   - **188** unique image basenames;
   - **29** date groups;
   - **28 XAUUSD** date groups / **186 XAUUSD images** staged as eligible evidence;
   - `2021-11-30` contains the two known GBPJPY images and remains explicitly excluded from XAUUSD evidence.

3. Approved primary PDF material used by R03–R05
   - `03_Analysis_Basics_.pdf`
   - `04_FU_Retests_.pdf`
   - `05_FU_Negations_.pdf`
   - `06_HCS_.pdf`
   - `08_Zones_.pdf`
   - `09_Imbalances_.pdf`
   - `GIANNO_CASINO_REFLECTION_MASTER.pdf`
   - `GIANNO_CASINO_BACKTEST_ASKISEIS_01.pdf`

The PDFs are staged as full physical PDF-page images. This preserves the original page visual without supplying analyst labels to Agent 06.

## Canonical provenance corrections

During source recovery, several old locators were found to use printed footer page numbers rather than physical 1-based PDF page numbers. Only provenance locators were corrected; expected labels/classes/evidence were not changed.

### Round 03 physical pages
- GT-R03-001 -> physical page 5
- GT-R03-002 -> physical page 3
- GT-R03-003 -> physical page 3
- GT-R03-004 -> physical page 3
- GT-R03-005 -> physical page 3
- GT-R03-006 -> physical page 3
- GT-R03-007 -> physical page 3

### Round 04 physical pages
- GT-R04-001 -> physical page 3
- GT-R04-002 -> physical page 3
- GT-R04-003 -> physical page 4
- GT-R04-004 -> physical page 5
- GT-R04-005 -> physical page 4
- GT-R04-006 -> physical page 6

### Round 05 correction
- GT-R05-002 -> physical `08_Zones_.pdf` page 3; the old locator pointed to nonexistent physical page 7.

Regression tests now pin these physical-page mappings.

## New deterministic staging code

Added/extended XAUUSD V2 source infrastructure:
- `src/xauusd_v2/topdown_primary_archive.py`
- `src/xauusd_v2/excalidraw_primary_context.py`
- `src/xauusd_v2/pdf_primary_pages.py`
- `src/xauusd_v2/primary_context_bundle.py` physical-page fallback for `v2_sources:<uuid>#page:N#...`
- `src/xauusd_v2/primary_context_bundle_merge.py`

The Excalidraw stager is fail-closed on deleted/missing elements, unsupported/mismatched MIME, invalid base64, invalid image signature, duplicate live element IDs, and content-addressed collisions.

## Private Agent-06 primary evidence bundle

A private evidence bundle was assembled from the recovered originals and stored outside the public repository:

- Library path: `/XAUUSD V2/Agent06/xauusd_agent06_primary_bundle_2026_09_02.zip`
- ZIP bytes: `17,623,961`
- ZIP SHA-256: `6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf`
- primary-context manifest SHA-256: `e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37`
- resolver entries: **477**
- unique staged image assets: **219**
- staged text assets: **1**

Why 477 entries rather than 173: the top-down section is deliberately a label-blind locator superset. For every eligible XAUUSD date/image it stages legacy and canonical sequence forms plus exact image forms. This lets canonical blind locators resolve without deriving the source selection from expected labels.

The uploaded Library ZIP was materialized back and verified **byte-identical** to the locally generated ZIP with the same SHA-256 above.

The bundle is intentionally **not committed to the public GitHub repository**.

## Supabase source persistence state

The original `casinonotes.excalidraw` record now has an exact private Library `storage_path` mapping. This was a provenance-only update; `approved_by_user`, source status, rule verification, knowledge verification, and disagreement resolution were not changed.

Live snapshot after the mapping:
- 29 approved-by-user sources remain in `review`
- 16 source records now have non-null `storage_path`
- 195 knowledge claims
- 23 rules
- 215 examples
- 32 agent runs
- 14 unresolved disagreement/certification rows
- 0 VERIFIED knowledge
- 0 VERIFIED rules

## What this does and does not unlock

This materially removes the previous missing-primary-source blocker for Agent 06.

It does **not** mean Agent 06 has independently validated the corpus. A real run still requires:
1. an actual independent external **multimodal** model provider/wrapper;
2. provider/model metadata;
3. a readiness pass against the private evidence bundle;
4. blind prediction before ground truth is revealed;
5. deterministic downstream comparison and disagreement logging.

No independent-provider run has been executed yet. No strategy or performance certification follows from source recovery alone.

## Latest verified code checkpoint at time of this document

Before this documentation commit:
- branch head: `79f99683cee122db5ecb1467f5f8341dadbe8a8a`
- GitHub Actions run: `33646095968`
- Python 3.12
- **595 / 595 tests PASS**

Any later documentation/code commit must be followed by a fresh CI check before becoming the new verified checkpoint.
