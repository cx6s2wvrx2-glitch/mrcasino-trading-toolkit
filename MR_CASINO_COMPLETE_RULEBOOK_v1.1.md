# MR CASINO — COMPLETE RULEBOOK v1.1
### PHASE 1 deliverable — Knowledge extraction & mechanical rule mapping
> **v1.1 changelog:** Ενσωματώθηκαν οι επιβεβαιωμένες απαντήσεις του Nikos (exit ladder, session, risk, imbalance) + color-coded TF legend από το video frame-OCR. Video audio narration παραμένει μη-transcribed (network-blocked στο sandbox — βλ. §19).
Project: **MR CASINO STRATEGY** · Instrument focus: **XAU/USD (Gold)** · Author of source material: **Mr. Casino / Mr_Tzini**

> Σκοπός αυτού του εγγράφου: να μετατρέψει τη στρατηγική MR CASINO σε αυστηρούς, μηχανικούς, κωδικοποιήσιμους κανόνες — **χωρίς εφεύρεση κανόνων που δεν υπάρχουν στα αρχεία**.

**Tagging legend για κάθε κανόνα:**
- `[CONF]` = Επιβεβαιωμένος από το ανεβασμένο υλικό (βιβλίο/code/σημειώσεις δηλώνουν ρητά τον κανόνα)
- `[EX]`   = Συμπέρασμα από παραδείγματα (προκύπτει από screenshots/examples, όχι ρητή διατύπωση)
- `[?]`    = Ασαφές / θέλει επιβεβαίωση
- `[EXP]`  = Πειραματικό (δική μου προτεινόμενη βελτίωση — ΔΕΝ είναι MR CASINO)

---

## 0. ΠΗΓΕΣ ΠΟΥ ΑΝΑΛΥΘΗΚΑΝ

| Αρχείο | Τι είναι | Κατάσταση |
|---|---|---|
| `How_to_rinse_the_banks__A_forex_guide.pdf` (34σ) | Θεμελιώδες βιβλίο #1 (Mr. Casino). Psychology, RR, market structure, liquidity, FU candles, imbalances, XAU case study | ✅ Διαβάστηκε πλήρως (OCR) |
| `The_Manipulation_Mastery.pdf` (27σ) | Βιβλίο #2 «The Manipulation Masterkey». Βαθύτερα: LAOL, orderblocks, types of FU, aggressive entry, perfect setup, trade management, swing | ✅ Διαβάστηκε πλήρως (OCR) |
| `MrDomino_breakdown.pdf` (16σ) | Live XAUUSD walkthrough με HCS / FU / OB / NY session | ✅ Διαβάστηκε πλήρως (OCR) |
| `BETA_INDICATOR_1_LAOL_` (Pine v6, 2293 γρ.) | Ο beta indicator — η πιο μηχανική πηγή αλήθειας | ✅ Διαβάστηκε αρχιτεκτονικά + key logic |
| `XAUUSD_20251211_*.png` (32 screenshots) | Annotated teaching top-down ανάλυση (Mr_Tzini, 1h gold) | ✅ Δείγμα αναλύθηκε |
| `IMG_9321.jpg` (αγγλικά) | **Χειρόγραφη μηχανική σημείωση multi-TF entry model** — γέφυρα θεωρίας↔code | ✅ Κρίσιμο, αναλύθηκε |
| `IMG_93xx / 94xx.jpg` (~60 αρχεία) | Ελληνικές περιλήψεις θεωρίας + επιπλέον σημειώσεις/examples | ⚠️ Δείγμα αναλύθηκε — χρειάζεται πλήρης σάρωση |
| `Student_story_1.pdf` | Testimonial | ⚠️ Χαμηλή προτεραιότητα — δεν επηρεάζει κανόνες |
| `TRADING_IN_THE_ZONE.pdf` | Βιβλίο ψυχολογίας Mark Douglas (γενικό, ΟΧΙ MR CASINO-specific) | ✅ Αναγνωρίστηκε — ψυχολογία, όχι μηχανικοί κανόνες |
| `How_to_enter_FU_retest_.mp4` (22′) | **Video: μέθοδος εισόδου FU retest** | ❌ **ΔΕΝ έχει διαβαστεί — δεν μπορώ να δω/ακούσω video απευθείας** |
| `video1065867161.mp4` (33′) | **Video: άγνωστο περιεχόμενο** | ❌ **ΔΕΝ έχει διαβαστεί** |

---

## 1. ΣΥΝΟΛΙΚΗ ΦΙΛΟΣΟΦΙΑ (η «καρδιά» της MR CASINO)

`[CONF]` Η στρατηγική είναι **liquidity-based manipulation following**: τραντάρουμε ΜΑΖΙ με τις τράπεζες, ποτέ απέναντι. Κάθε κίνηση = παίρνει buy-side ή sell-side liquidity ή κάνει consolidation πριν την «αληθινή» κίνηση.

`[CONF]` Πέντε θεμελιώδεις πυλώνες (από το confirmation list, σ.33 βιβλίο #1):
1. Market structure (Daily + 4h) = κατεύθυνση/bias πρώτα
2. Institutional zones / orderblocks = πού αντιδρά η τιμή
3. Liquidity (πού είναι τα stop losses: dojis, double tops/bottoms, big wicks)
4. FU candles = το «physical sign» ότι οι τράπεζες κινούνται
5. Imbalances = γεμίζουν πάντα, δίνουν κατεύθυνση & target

`[CONF]` Το edge δηλώνεται ως **πολύ υψηλό Risk:Reward** (το βιβλίο μιλά για 1:10 minimum, με παραδείγματα 1:50–1:103), με μικρό SL σε χαμηλά timeframes (1m/5m), σε **gold** κυρίως («κινείται 10× πιο γρήγορα → 10× manipulation → daily setups»).

> ⚠️ **Σημείωση ειλικρίνειας:** Τα νούμερα 1:50–1:103 RR στα βιβλία είναι cherry-picked best trades, όχι στατιστικό μέσο. Δεν αποτελούν edge claim που μπορεί να ληφθεί τοις μετρητοίς. Θα τα ελέγξουμε στο PHASE 4.

---

## 2. ΑΠΟΚΩΔΙΚΟΠΟΙΗΣΗ ΟΡΟΛΟΓΙΑΣ — CODE ↔ ΘΕΩΡΙΑ (το πιο σημαντικό κομμάτι)

Αυτός ο πίνακας συνδέει τα primitives του beta indicator με τις έννοιες των βιβλίων/σημειώσεων. **Είναι η βάση για κάθε μελλοντικό code.**

| Code term | Ορισμός στον κώδικα | MR CASINO έννοια | Tag |
|---|---|---|---|
| **FU** | `high>prev_high AND close<prev_high AND close>prev_low` (bear· σπάει prev high, κλείνει πίσω μέσα). Όχι X3, όχι SN | **FU candle**: παίρνει liquidity πάνω από prev candle + κάνει rejection. Ταιριάζει 1:1 με τον ορισμό βιβλίου: «(1) takes liquidity (2) breaks high/low of previous candle» | `[CONF]` |
| **SN** | `high>prev_high AND low<prev_low` αλλά **σώμα μέσα** στο prev range | **Liquidity grab / sweep** και των δύο πλευρών με ουδέτερο κλείσιμο (sweep candle, «doji-like» grab) | `[EX]` |
| **X3** | `high>prev_high AND low<prev_low`, και οι δύο wicks, bear αν close<open | Δυνατό **manipulation engulfing** που σαρώνει και τις δύο πλευρές (ισχυρότερο SN με κατεύθυνση) | `[EX]` |
| **LAOL** | Lines («laol_line_data»), merge ανά level/TF, σπάνε όταν τις περνά η τιμή | **Last Area Of Liquidity** = «the final area of liquidity» (βιβλίο #2: «Identifying the final area of liquidity») | `[CONF]` |
| **HCS** | Boxes ανά TF («hcs_box_data»), confluence πολλών TF, «HCS x3», forming/confirmed/retesting | **High Confluence Setup** = manipulation micro-zone / orderblock όπου ευθυγραμμίζονται TFs (MrDomino: «we made our 1st HCS», «HCS x3») | `[CONF]` |
| **EM** | «Established Move» — χτίζεται από X3 First/Third / LAOL / TBE / HCS | Επιβεβαιωμένη κατευθυντική κίνηση (στις σημειώσεις: **«established TS»**) | `[EX]` |
| **TS** (σημειώσεις) | — | «established TS» = EM/sequence (established directional sequence). 15min TS, 1h HCS κ.λπ. | `[CONF]` |
| **EST + RETEST** | Box state: established → retest → respected | **Break & retest του zone** (βιβλίο #1: «price MUST break and retest every zone») | `[CONF]` |
| **ATT FU** (screenshots) | — | **Attempted FU** = «Doji FU attempt» (βιβλίο #2): προσπάθεια FU που κλείνει doji | `[CONF]` |
| **S1–S4** | 4 valid base setups (βλ. §4) | Οι 4 έγκυροι συνδυασμοί confluence ENTRY+SCALP tier | `[EX]` |
| **TBE** | Modifier στο FU: «FU [TBE✓]» | **Άγνωστο** (πιθανόν «Took Both Ends» ή time-based). Δεν τεκμηριώνεται στα PDFs. Nikos: «δεν ξέρω» → παραμένει ανοιχτό | `[?]` |
| **Tiers** | ENTRY 1–5m, SCALP 6–20m, INTRA 30–120m | INTRA = zones (κανόνας «μην κάτω από 30min για zones»). ENTRY/SCALP = execution/refinement | `[CONF]` |

### 2β. Color-coded timeframe legend (από video `How_to_enter_FU_retest`, frame-OCR)
`[CONF]` Ο trader χρωματίζει τα zones ανά TF group στο TradingView:

| Χρώμα | Timeframes | Tier αντιστοίχιση |
|---|---|---|
| PINK | Monthly | HTF bias |
| ORANGE | Weekly | HTF bias |
| BLUE | Daily | HTF bias / direction (MS-2) |
| PURPLE | 4H / 3H | INTRA (zones) |
| BLACK | 2H / 1H / 30M | INTRA (zones) |
| RED | 15M / 5M / 3M / 1M | SCALP + ENTRY (execution) |

Πλατφόρμα video: **TradingView + PEPPERSTONE**, instrument **XAUUSD**. Επιβεβαιώνει: HTF (M/W/D) = bias· 4H–30M = zones· 15M–1M = execution.

---

## 3. MARKET STRUCTURE RULES

| # | Κανόνας | Tag |
|---|---|---|
| MS-1 | Market structure είναι ΠΑΝΤΑ πρώτο, ακόμα κι αν η τιμή είναι manipulated. | `[CONF]` |
| MS-2 | Direction/bias ορίζεται από **Daily**, refined στο **4h**. Retail S/R zones μόνο για bias, ΟΧΙ entries. | `[CONF]` |
| MS-3 | «Price MUST break and retest every zone before continuing.» Αν σπάσει 2 zones χωρίς retest → θα επιστρέψει για retest (bias signal). | `[CONF]` |
| MS-4 | Higher timeframe = περισσότερη ισχύς. Daily confirmation υποχρεωτικό· entries σε 1m/5m πρέπει να «βγάζουν νόημα» στο Daily. | `[CONF]` |
| MS-5 | Top-down ανάλυση σε ΟΛΑ τα timeframes για να βρεθεί η **last area of liquidity (LAOL)**. | `[CONF]` |

---

## 4. LIQUIDITY RULES

| # | Κανόνας | Tag |
|---|---|---|
| LQ-1 | Liquidity = εκεί που είναι τα stop losses: **dojis, double tops/bottoms, big wick rejections**. | `[CONF]` |
| LQ-2 | Στόχευσε πάντα τη **Last Area Of Liquidity (LAOL)** — όχι την πρώτη τυχαία area, αλλά την τελευταία major area όπου οι retailers «κέρδιζαν». | `[CONF]` |
| LQ-3 | «Calculate liquidity»: ανάλογα με το πόση liquidity μένει πίσω (σε όλα τα TF), κρίνεις αν οι τράπεζες θα την κυνηγήσουν τώρα ή θα την αφήσουν για μέλλον. | `[CONF]` (αλλά **discretionary** → δύσκολα μηχανικό) |
| LQ-4 | Big wick → είτε hunt του bottom του wick (πολλή liquidity) είτε fill. | `[CONF]` |
| LQ-5 | True direction = το μονοπάτι με τη **χαμηλότερη liquidity**. Liquidity taken σε μία πλευρά → trade προς εκείνη την κατεύθυνση. | `[CONF]` |
| **CODE map** | Στον indicator: LAOL lines (last area), SN/X3 (liquidity sweep candles), HCS boxes (confluence zones). | `[CONF]` |

---

## 5. INSTITUTIONAL ZONES / ORDERBLOCKS

| # | Κανόνας | Tag |
|---|---|---|
| OB-1 | Orderblock = το odd bearish candle πριν/κατά move-up (ή bullish πριν move-down). «Sold to buy» / «bought to sell». | `[CONF]` |
| OB-2 | Μάρκαρε **μόνο το body** του orderblock (όχι όλο το candle) — εκεί συγκεντρώνονται τα orders. | `[CONF]` |
| OB-3 | **Συμπεριέλαβε τη manipulation** (το FU candle πριν τη κίνηση) στο zone. | `[CONF]` |
| OB-4 | **Μην πας κάτω από 30min** για zones (εκτός αν scalping). 4h = ισχυρότερο, 1h = αγαπημένο intraday. | `[CONF]` |
| OB-5 | **Strong zones** = orderblocks ακολουθούμενα από major κίνηση (διαφορετικό χρώμα, «base» της ανάλυσης). | `[CONF]` |
| **CODE map** | INTRA tier (30–120m) = zone tier. HCS = το coded ισοδύναμο του strong confluence zone. | `[CONF]` |

---

## 6. ENTRY MODEL (το core)

### 6α. Confluence stack (master checklist — βιβλίο #1, σ.33)
`[CONF]` Όσο περισσότερα ✓, τόσο ισχυρότερο το setup:
1. Price makes sense στο Daily
2. Price σε institutional zone
3. Liquidity has been taken
4. Liquidity to target (LAOL)
5. FU scenario formed
6. Awaiting **FU retest**
7. Imbalance fill έγινε
8. Imbalance to target

### 6β. FU candle (το βασικό trigger)
`[CONF]` **Valid FU** = (1) παίρνει liquidity **ΚΑΙ** (2) σπάει high/low προηγούμενου candle και κλείνει πίσω (rejection). Μόνο του δεν αρκεί — χρειάζεται confluence (LQ + zone + direction).

`[CONF]` **Τρεις μέθοδοι εισόδου με FU:**
- **(A) After-close entry:** μπες μετά το κλείσιμο του FU, SL πάνω/κάτω από το wick. (Μικρό SL → μόνο σε χαμηλά TF.)
- **(B) Aggressive / as-it-forms:** μπες καθώς σχηματίζεται το wick rejection (market execute). Μέγιστο RR. Χρειάζεται όλα τα άλλα confirmations.
- **(C) FU retest / limit order:** περίμενε την τιμή να επιστρέψει στο FU level (retest) και μπες με limit. **«True FU retests = strongest setups»** (→ αυτό αναλύει το video `How_to_enter_FU_retest`).

### 6γ. Multi-TF entry hierarchy (από χειρόγραφη σημείωση IMG_9321 — η πιο μηχανική περιγραφή)
`[CONF]` (Bullish παράδειγμα· αντίστροφα για bear):
```
15min: HCS με TS potential
1h   : 15min established TS που "corresponds" στο 1h HCS / negation
       → ENTER στο 1h HCS με established 15min TS
3h   : 15min TS + 1h HCS + 3h FU
       → SWING potential
TFS (swing targets): 3h – 5h – 7h – 11h
```

### 6δ. Code-level setups S1–S4 (από beta indicator — η μηχανική υλοποίηση του 6γ)
`[EX]` Προϋπόθεση: ENTRY-tier last-valid-direction == SCALP-tier last-valid-direction (alignment) & κανένα δεν «broken».
- **S1:** SCALP έχει EM(est/forming)>0 **&** ENTRY EM total>0 **&** ENTRY EM retest>0
- **S2:** S1 + SCALP EM retest>0 (πιο αυστηρό — retest και στα δύο tiers)
- **S3:** SCALP EM forming≥1 **&** ENTRY EM total>0 **&** ENTRY EM retest>0
- **S4:** ENTRY HCS στο m1 ≥1 (HCS-driven setup)
- INTRA-enhanced variants: INTRA+EST+RETEST / INTRA+EM / INTRA+ZONE / INTRA+NEG (προσθέτουν zone confluence)

---

## 7. CONFIRMATION RULES

| # | Κανόνας | Tag |
|---|---|---|
| CF-1 | **Confirmation = κλείσιμο του 1-minute candle** (`m1_conf`). «Forming» πριν το close, «Confirmed» στο close. | `[CONF]` (από code) |
| CF-2 | Entries σε 1m/5m **μόνο** όταν η τιμή είναι σε «area of interest» (zone + liquidity taken). | `[CONF]` |
| CF-3 | FU χρειάζεται «other reasons to react» — όχι FU μεμονωμένο. | `[CONF]` |
| CF-4 | Lower-TF established sequence πρέπει να «corresponds» με higher-TF HCS/negation. | `[CONF]` |

---

## 8. INVALIDATION RULES

| # | Κανόνας | Tag |
|---|---|---|
| IV-1 | Sequence ακυρώνεται αν η τιμή σπάσει το reference level (bear: high>level / bull: low<level) ή αν περάσουν >5 candles χωρίς εξέλιξη (code: `f_update_seq`). | `[CONF]` (code) |
| IV-2 | LAOL line «broken» όταν την περνά η τιμή → παύει να είναι valid liquidity reference. | `[CONF]` (code) |
| IV-3 | HCS broken/respected αλλάζει το bias (MrDomino: «broken HCS → θέλουμε πάνω»). | `[CONF]` |
| IV-4 | Last-valid pattern «BROKEN» όταν παραβιαστεί το level του → το setup του tier ακυρώνεται. | `[CONF]` (code) |
| IV-5 | «Weak HCS»: ξεκινά με 1m doji → αδύναμο, αποφυγή. | `[CONF]` (MrDomino) |

---

## 9. STOP LOSS RULES

| # | Κανόνας | Tag |
|---|---|---|
| SL-1 | **Στόχος: μικρότερο δυνατό SL.** | `[CONF]` |
| SL-2 | SL πάνω/κάτω από το **wick του FU** (bear: πάνω από high· bull: κάτω από low). | `[CONF]` |
| SL-3 | (Code) Entry = body edge του signal candle [bear: `max(open,close)`· bull: `min(open,close)`]. SL = wick extreme, **extended** στο επόμενο πιο ακραίο candle αν υπάρχει (`f_find_next_extreme_candle`). | `[CONF]` (code) |

---

## 10. TAKE PROFIT RULES

**ΕΠΙΒΕΒΑΙΩΜΕΝΟ EXIT LADDER (Nikos):** Το take-profit είναι κλιμακωτό partials — αυτό είναι το επίσημο exit model για backtest.

| Trigger | Ενέργεια | Υπόλοιπο θέσης | Tag |
|---|---|---|---|
| **+3R** | Κλείσε **40%** partial **ΚΑΙ** μετακίνησε SL → **breakeven** | 60% | `[CONF]` (Nikos) |
| **+8R** | Κλείσε **30%** partial | 30% | `[CONF]` (Nikos) |
| **+15R** | Κλείσε **15%** partial | 15% | `[CONF]` (Nikos) |
| **+20R** | **Full close** του υπόλοιπου 15% | 0% | `[CONF]` (Nikos) |

Σημειώσεις:
- **1R = risk = |entry − SL|** (SL στο wick extreme, §9). Μετά το +3R η θέση είναι risk-free (SL@BE).
- Το «primary TP ανάλογα το setup» (ερ.4) = **αυτό ακριβώς το ladder**· δεν υπάρχει ξεχωριστός fixed TP.
- Ο παλιός beta code (8R fixed / 40-pip line) **αντικαθίσταται** από αυτό το ladder ως το κανονικό exit.
- ⚠️ Το +20R full-close σημαίνει ότι απαιτείται **πολύ μεγάλο move** για πλήρη ρευστοποίηση· στην πράξη οι περισσότερες θέσεις θα κλείνουν με το trailing/BE ή σε ενδιάμεσο partial. Το expectancy κυριαρχείται από το **+3R (40%) leg** — αυτό θα φανεί στο backtest.

| TP-legacy | (Βιβλία) Targets = επόμενα LAOL / zone-to-zone / imbalance fills (discretionary) — τώρα **προσεγγίζονται** από το R-ladder. | superseded |

---

## 11. SESSION / TIME RULES

| # | Κανόνας | Tag |
|---|---|---|
| TM-1 | **Trade ΜΟΝΟ σε London session + New York session** (Nikos). | `[CONF]` (Nikos) |
| TM-2 | **News filter: NO trades από −15′ έως +15′** γύρω από news release (Nikos). | `[CONF]` (Nikos) |
| TM-3 | NY open/close = σημαντικό manipulation shift (MrDomino). News events (NFP) = γρήγορες κινήσεις. | `[CONF]` |
| ⚠️-impl | Πρέπει να οριστούν ακριβή UTC windows για London/NY (π.χ. London 07:00–16:00, NY 12:00–21:00 UTC — **[?] ακριβή όρια θέλουν επιβεβαίωση**) + πηγή news calendar (economic calendar feed) για το ±15′ filter. Στο Pine, το news-filter χρειάζεται είτε manual input array είτε external data. | `[?]` (υλοποίηση) |

---

## 12. RISK RULES

| # | Κανόνας | Tag |
|---|---|---|
| RK-1 | **Fixed % risk ανά trade, ΠΟΤΕ μην το αλλάζεις.** | `[CONF]` |
| RK-2 | **FTMO / funded account: 0.5% risk ανά trade** (Nikos). | `[CONF]` (Nikos) |
| RK-3 | **Live account: 2% risk ανά trade** (Nikos). | `[CONF]` (Nikos) |
| RK-4 | Σκέψου σε **%**, όχι σε $. Preserve capital πρώτα. | `[CONF]` |
| ℹ️ | Το backtest θα τρέξει με **δύο ρυθμίσεις: 0.5% (FTMO) και 2% (live)**. Το target 3–10%/εβδ αξιολογείται κυρίως στο 2% (το 0.5% προφανώς δίνει ~¼ των returns αλλά πολύ μικρότερο DD). | note |

---

## 13. TRADE MANAGEMENT RULES

| # | Κανόνας | Tag |
|---|---|---|
| MG-1 | **Break-even ASAP** (ειδικά για funded). | `[CONF]` |
| MG-2 | **Πάντα partials** («always pay yourself»). | `[CONF]` |
| MG-3 | Κάθε position έχει **swing potential** — άσε runner στο BE για «home run». | `[CONF]` |
| MG-4 | Swing = ισχυρότερο entry: αφού παρθεί όλη η major liquidity (high & low TF), από start of move. Hold ημέρες/εβδομάδες. | `[CONF]` |
| ✅ | MG-1..3 πλέον **ΜΗΧΑΝΙΚΟΠΟΙΗΘΗΚΑΝ** μέσω του exit ladder (§10): BE στο +3R, partials 40/30/15%, full close +20R. | `[CONF]` (Nikos) |

---

## 14. NO-TRADE CONDITIONS

| # | Κανόνας | Tag |
|---|---|---|
| NT-1 | **«No HCS TS → No entry»** (από teaching screenshot). | `[EX]` |
| NT-2 | FU μόνο του, χωρίς liquidity context / εκτός area of interest. | `[CONF]` |
| NT-3 | Trade **απέναντι στο Daily** direction. | `[CONF]` |
| NT-4 | **Imbalanced candle** στην αρχή κίνησης → δεν κρατά· μην τρακάρεις μέχρι να γεμίσει («only take balanced moves»). | `[CONF]` |
| NT-5 | **Weak HCS** (ξεκινά με 1m doji). | `[CONF]` |
| NT-6 | Tier alignment broken (ENTRY≠SCALP direction, ή last-valid broken). | `[CONF]` (code) |
| NT-7 | **Εκτός London/NY session** → no trade. | `[CONF]` (Nikos) |
| NT-8 | **−15′ έως +15′ γύρω από news** → no trade. | `[CONF]` (Nikos) |

---

## 15. ΤΙ ΠΡΕΠΕΙ ΝΑ ΔΕΙΧΝΕΙ Ο INDICATOR

`[CONF]` Με βάση τον beta + τη θεωρία, ο μηχανικός indicator πρέπει να δείχνει καθαρά:
- Valid LONG setup / valid SHORT setup (με τύπο: S1/S2/S3/S4 + INTRA variant)
- Entry level (body edge)
- Stop loss level (wick extreme, extended)
- TP1 (π.χ. 40-pip / 1ο LAOL) · TP2 · Final target (8R / επόμενο major LAOL)
- LAOL lines (last areas of liquidity) ανά tier
- HCS boxes (forming / confirmed / retested) ανά tier
- FU labels (FU / ATT FU / SN / X3)
- Invalidation level
- No-trade reason όπου είναι δυνατόν (π.χ. «no HCS», «against daily», «imbalance unfilled»)

---

## 16. ΤΙ ΠΡΕΠΕΙ ΝΑ BACKTESTΑΡΕΙ ΤΟ STRATEGY

`[CONF]` Μηχανικό backtest με:
- **Entry:** confirmed setup (m1 close) → entry στο body edge
- **SL:** wick extreme (extended, §9)
- **Exit ladder (ΕΠΙΒΕΒΑΙΩΜΕΝΟ, §10):** +3R → 40% + SL@BE · +8R → 30% · +15R → 15% · +20R → full close. Αν χτυπηθεί το SL (ή BE) πριν το +3R → loss (ή scratch).
- **Session filter:** μόνο London + NY· news −15′/+15′ excluded
- **Risk:** δύο runs → 0.5% (FTMO) και 2% (live)
- **Ρεαλισμός:** spread + commission + slippage (XAUUSD), realistic fill, **no lookahead, no repaint, no future candles**
- **Position sizing note:** επειδή το SL είναι πολύ μικρό (wick του 1m FU), το 1R σε τιμή είναι μικρό → το 2% risk μπορεί να δίνει μεγάλο lot· πρέπει να ελεγχθεί ρεαλισμός εκτέλεσης (slippage στο gold).

---

## 17. ΤΙ ΔΕΝ ΕΙΝΑΙ ΑΚΟΜΑ ΑΡΚΕΤΑ ΜΗΧΑΝΙΚΟ (gaps για κωδικοποίηση)

| Gap | Γιατί είναι πρόβλημα | Status |
|---|---|---|
| G-1 | **«Calculate liquidity»** (πότε hunt vs leave) είναι 100% discretionary | `[?]` Χρειάζεται quantification ή αποδοχή ότι ο indicator το προσεγγίζει μέσω LAOL/HCS |
| G-2 | **Daily/4h bias** δεν έχει αυστηρό κανόνα στον code (ο indicator δουλεύει intraday tiers) | `[?]` Πρέπει να οριστεί μηχανικός daily-direction filter |
| G-3 | **Exit/trade management** (BE, partials, swing) χωρίς αριθμούς | `[?]` Κρίσιμο για backtest — χρειάζεται απόφαση |
| G-4 | **Session window** δεν ορίζεται ρητά· code δεν έχει filter | `[?]` |
| G-5 | **TBE modifier** άγνωστο | `[?]` |
| G-6 | **Imbalance detection** δεν φαίνεται στον beta code (αναφέρεται στα βιβλία αλλά όχι κωδικοποιημένο) | `[?]` |
| G-7 | **8R fixed TP vs zone-to-zone** σύγκρουση | `[?]` |
| G-8 | **Repaint/lookahead audit** του beta (multi-TF `request.security`) δεν έχει γίνει ακόμα | pending PHASE 3 |
| G-9 | **2 videos (55′ συνολικά) δεν διαβάστηκαν** — πιθανόν περιέχουν ακριβείς κανόνες entry/management | ❌ blocking για πληρότητα |

---

## 18. ΡΕΑΛΙΣΜΟΣ ΣΤΟΧΟΥ 3–10%/ΕΒΔΟΜΑΔΑ (προκαταρκτική, ΟΧΙ απόδειξη)

Δεν έχει γίνει backtest ακόμα — οπότε **καμία στατιστική δήλωση**. Μόνο το math frame:

Εβδομαδιαία απόδοση ≈ `(#trades/εβδ) × risk% × [winrate×avgR − (1−winrate)]`.

- Με risk 3%/trade, 10 trades/εβδ, breakeven χρειάζεται winrate×avgR_win ισορροπία.
- Αν avg managed RR ≈ 2R καθαρό και winrate ≈ 45%: expectancy ≈ 3% × (0.45×2 − 0.55) = 3% × 0.35 = **~1.05%/trade** → 10 trades ≈ ~10%/εβδ (θεωρητικά, **πριν** drawdown/variance/costs).
- **ΑΛΛΑ:** αυτό προϋποθέτει σταθερό 2R καθαρό και 45% winrate που **δεν έχουν αποδειχθεί**. Με 8R-fixed TP το winrate πέφτει δραματικά· με partials/BE το avgR πέφτει. Το 3–10% είναι *μαθηματικά εφικτό* αλλά **εξαρτάται απόλυτα από winrate/frequency που μετράμε μόνο με backtest**.

> **Ειλικρινής θέση:** Το 3–10%/εβδ ΔΕΝ είναι ούτε επιβεβαιωμένο ούτε απορριπτέο σε αυτή τη φάση. Είναι «εφικτό σε χαρτί, αναπόδεικτο σε δεδομένα». Επιπλέον το 3% risk/trade καθιστά το variance/drawdown σοβαρό κίνδυνο ακόμα κι αν το μέσο return πιάνει στόχο.

---

## 19. ΚΑΤΑΣΤΑΣΗ ΑΝΟΙΧΤΩΝ ΘΕΜΑΤΩΝ (ενημερωμένο v1.1)

| # | Θέμα | Απάντηση Nikos | Status |
|---|---|---|---|
| 1 | Exit model | +3R:40%+BE / +8R:30% / +15R:15% / +20R:full | ✅ ΛΥΘΗΚΕ |
| 2 | TBE meaning | «δεν ξέρω» | ⚠️ ΑΝΟΙΧΤΟ — ίσως το λύσουν τα video transcripts· αλλιώς το αφήνουμε εκτός v0.1 |
| 3 | Session | London + NY· news −15′/+15′ | ✅ ΛΥΘΗΚΕ (ακριβή UTC όρια θέλουν επιβεβαίωση) |
| 4 | Primary TP | = το exit ladder ανά setup | ✅ ΛΥΘΗΚΕ |
| 5 | Risk | FTMO 0.5% · live 2% | ✅ ΛΥΘΗΚΕ |
| 6 | Imbalance | «όχι» → δεν κωδικοποιείται | ✅ ΛΥΘΗΚΕ (εκτός scope) |
| 7 | Videos | «ναι, σημαντικά» | ❌ **BLOCKED** — βλ. παρακάτω |

### ⚠️ Video transcription — τεχνικό εμπόδιο (πρέπει να αποφασίσεις τρόπο)
Και τα 2 videos είναι **«FU RETEST ENTRIES (HOW I TAKE THEM)»** (narrated screen recordings). Το frame-OCR έδωσε μόνο το color legend + τίτλους — η μεθοδολογία είναι στον **προφορικό λόγο**. Το αυτόματο audio transcription **δεν γίνεται σε αυτό το περιβάλλον**: όλοι οι hosts μοντέλων ASR (HuggingFace, OpenAI azureedge, Vosk/alphacephei) και τα github release-assets/LFS είναι network-blocked· κανένα cached μοντέλο. Επιλογές:
- **(Α) Εσύ τρέχεις whisper τοπικά** (γρηγορότερο, ακριβέστερο) και μου δίνεις το `.txt`. Εντολή: `pip install openai-whisper && whisper "How_to_enter_FU_retest_.mp4" --model small --language en --output_format txt` (ίδιο για το 2ο). Ή MacWhisper / online (turboscribe, otter, YouTube auto-captions).
- **(Β) Μου γράφεις εσύ 5–10 bullets** με το πώς ακριβώς παίρνεις το FU retest (ποιο candle, tolerance retest, TBE).
- **(Γ) Συνεχίζουμε PHASE 2 ΧΩΡΙΣ τα videos** (έχω ήδη το FU-retest entry από τα βιβλία: 3 μέθοδοι) και τα ενσωματώνουμε ως refinement όταν έρθει transcript.

---

## 20. ΕΠΟΜΕΝΑ ΒΗΜΑΤΑ (PHASE roadmap)

- **PHASE 2 (Strategy Logic):** Μετατροπή §3–§14 σε αυστηρό pseudocode / state machine (entry trigger, exit trigger, session filter, risk model) — μετά τις απαντήσεις στο §19.
- **PHASE 3 (v0.1 code):** Pine Script **strategy** (όχι μόνο indicator) **μόνο με `[CONF]` κανόνες**, με repaint/lookahead audit του multi-TF.
- **PHASE 4 (Backtest):** Δομημένο in-sample / out-of-sample / walk-forward σε XAUUSD, με πλήρη metrics (win rate, avg RR, PF, max DD, weekly return distribution, streaks) + έλεγχος στόχου 3–10%.
- **PHASE 5–7:** Optimization (μία μεταβλητή τη φορά) → forward test plan → automation readiness.

---
*MR CASINO COMPLETE RULEBOOK v1 — PHASE 1. Καμία στατιστική δήλωση δεν έχει γίνει· όλα τα performance claims εκκρεμούν backtest.*
