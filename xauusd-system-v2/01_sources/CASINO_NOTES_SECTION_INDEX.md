# Casino Notes — Structured Extraction Index

Source: `casinonotes.excalidraw`
Supabase source id: `d16204ee-456e-4a18-9f37-83a72bdb0708`
Authority: notebook-authored annotations are PRIMARY Mr Casino; embedded images retain original provenance when identifiable.
Status: extraction / unverified / no auto-promotion.

## Extraction state

- Casino Notes text elements indexed: **85 / 85**
- Each text note stores exact Excalidraw note id, coordinates, extraction certainty class, concept tags, and the three nearest unique embedded image file ids.
- Nearby-image links are geometric associations only. They do **not** reclassify the embedded image as Casino-authored.
- `question_or_uncertain` and phrases such as `μάλλον`, `πιθανό`, or `?` remain uncertain primary notes.
- Numeric observations such as `0.1 pip apart` are not universal thresholds unless independently certified.

## Extraction-class counts
- `explicit_annotation`: 29
- `sequence_marker`: 24
- `section_heading`: 17
- `interpretive_annotation`: 7
- `question_or_uncertain`: 4
- `numeric_observation`: 2
- `casual_note`: 2

## Priority notes for certification cross-check

- `YZEldwDvpx8Qy3-XDcGiy` — **x3, hcs, negation** — Αυτο το κερι ειναι x3 negation by 3rd αρα το πιανει σαν x3 by x3 hcs ολο αυτο. — nearby: `1bfe38147fef…`, `5f9592a3f5ff…`, `196363d22385…`
- `O7iJi_0Z_9YmONOb-tIkv` — **x3, true_stop, hcs, negation, entry** — Απο τα task εχουμε το hcs/negation true stop POI και στο 1m βλεπουμε το χτισιμο του true stop με καποια ακολουθεια x3. — nearby: `907e1816bce4…`, `60904c92ce38…`, `7db77b4d1409…`
- `ScMC67lCEeUa1G1G_NMgN` — **true_stop** — Δηλαδη σου λεει οτι στο 1m πρεπει να δεις τουλαχιστον μία ακολουθια χτισιματος true stop, δηλ. οτι οι τράπεζες εχουν μπει. — nearby: `7db77b4d1409…`, `f62714cc997c…`, `60904c92ce38…`
- `RYgB4M1DqzjrwWMiOv7nn` — **liquidity, low_liquidity_move, entry, target** — 0.1 pip apart. This is a sign of a low liquidity move/ potential aggressive entry/ no reason to target — nearby: `2c21227c9e77…`, `cda63ee1668c…`, `80e5b09a1203…`
- `d6_mVoihg6A2H-TOh2XGo` — **true_stop, negation, target** — Να το. Αδυναμη μορφη negation, αδυναμο χτισιμο true stop, ειναι μελλοντικος στοχος. — nearby: `449b0f1663db…`, `ecde65a130d2…`, `ef13546b390a…`
- `ZgNVY6Xq86arZ3M7gOYds` — **liquidity, low_liquidity_move, retest, target** — Τι σημαινει αυτο? Οτι περιμεναμε να γινει ενα retest στην περιοχη και προεκυψε ενα με 1 pip apart απο το να γινει στοχος. αρα low liq move — nearby image associations stored in the JSON index.
- `OMwY9lMSC1oWmpOAW7S7p` — **true_stop, laol, entry** — το laol πρεπει να ειναι μεσα σε POI δηλαδη κοντα σε καποιο true stop — nearby: `7f407ec94a41…`, `8a834788ba82…`, `4f7b9247f868…`
- `oNO70d7Uw52j8YQbeD-XH` — **negation, 11h, 10h** — Δηλαδη στο 11ωρο σημειωσε το low του κεριου και κατεβηκε στο 10ωρο και ειναι negation. — nearby: `dfa3fcc13882…`, `e5de3334d80d…`, `01aad1e3275d…`
- `RxJ3-9U4w6wefZKKCCMhM` — **broker** — Δεν ειναι εδω. ειναι στον broker — nearby: `21fb92d6e167…`, `337e8ec785a2…`, `34ad1699e69b…`
- `3Ob0-Afeox8hy6st1JYGK` — **core_liquidity, liquidity, target** — core liq: Πρεπει να παρθει αμεσα. Πρεπει να ερθει buy τωρα να παρει τα πανω σαν στοχο — nearby: `1c60b3368360…`, `809c17de20c9…`, `116ae41945a1…`
- `mA_dhCs6AxSy7WxBTK5eV` — **true_stop** — Ωωωωπ. Να το. TS το 0.1 — nearby: `dea5fc09b712…`, `48fb5d2c109a…`, `4f8e61f2addd…`

## Current implications — not yet VERIFIED

- **x3-by-x3 HCS:** the notebook explicitly links an `x3 negation by 3rd` candle to an `x3 by x3 HCS` structure. This materially narrows R-149, but the full raw-candle grammar still requires cluster-level certification.
- **True Stop build-up:** multiple notes say the 1m should show at least one sequence of True-Stop construction and name HCS / negation / x3 as examples of such build-up. This strengthens the existing True-Stop semantic layer, but does not by itself define exact raw geometry for every case.
- **0.1 pip / low-liquidity move:** the idea appears repeatedly and is linked to low-liquidity move / possible aggressive entry / lack of reason to target. Treat `0.1` as observed source context, not yet a universal production threshold.
- **LAOL:** notebook note says LAOL should be inside a POI / near a True Stop. This is strong primary interpretation evidence to cross-check against the existing LAOL model before formalization.
- **11h → 10h refinement:** notebook note says the low is marked on 11h and then checked on 10h where negation is seen. This supports refinement behavior but does **not** define the 11h candle construction/anchor.
- **Broker-only evidence:** a note explicitly says a feature is not visible there but is in the broker feed, reinforcing the existing broker-provenance requirement.

## Next extraction order

1. Fully inspect local image clusters around the priority notes above.
2. Separate exact source labels from interpretive notes and uncertain questions.
3. Cross-reference each surviving claim with Reflection / Q&A / approved PDFs to avoid double-counting.
4. Add only non-duplicate unverified knowledge candidates; no direct VERIFIED promotion.
5. Continue remaining Casino Notes clusters until all 220 unique images are inspected.
