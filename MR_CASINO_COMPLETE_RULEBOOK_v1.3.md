# MR CASINO — COMPLETE RULEBOOK v1.3
### PHASE 1 — Πλήρης εξαγωγή στρατηγικής (single source of truth)

> **v1.3 changelog:** Ενσωματώθηκαν τα **13 αυθεντικά Telegram docs** (channel_data). Νέο/διορθωμένο: ακριβής ορισμός FU/ATT FU/negation/HCS από πηγή, **4 τύποι major liquidity**, **strength hierarchy**, **timeframe-strength negation**, **TSL**, zones, imbalances (excluded), liquidity-based bias. Σημειώνονται 3 συγκρούσεις πηγής↔χρήστη.

**Tags:** `[CONF]`=επιβεβαιωμένο από υλικό · `[EX]`=συμπέρασμα από παραδείγματα · `[?]`=ασαφές/θέλει επιβεβαίωση · `[EXP]`=πειραματικό (δικό μου, ΟΧΙ MR CASINO)

**Πηγές:** How to rinse the banks (βιβλίο), The Manipulation Masterkey (βιβλίο), MrDomino breakdown, 13 Telegram docs (basics/liquidity/FU/FU-retests/FU-negations/HCS/LAOL/imbalances/zones/TSL/timeframe-strength/reflection/studying), beta indicator (2293 γρ.), teaching screenshots, χειρόγραφες σημειώσεις, ~3.646 example charts.

---

## 0. ΘΕΜΕΛΙΩΔΗΣ ΦΙΛΟΣΟΦΙΑ `[CONF]`
Trade **ΜΑΖΙ με τη manipulation** των τραπεζών. Το retail trading είναι facade για να παράγει liquidity· εμείς κάνουμε το αντίθετο από τη liquidity που παράγεται. **Ιεραρχία σκέψης:** Liquidity **πρώτα** → FU/manipulation → timeframe strength → zones (δευτερεύον). «Follow the manipulation» = η βάση κάθε trade. Στόχος: υψηλό RR (1:10–1:100), tight SL, κυρίως XAU.

---

## 1. MARKET STRUCTURE RULES

| # | Κανόνας | Tag |
|---|---|---|
| MS-1 | Πριν κάθε μέρα: flick weekly→1h, μάρκαρε major liquidity **και στις δύο** κατευθύνσεις, **χωρίς bias attachment**. | `[CONF]` |
| MS-2 | HTF υπερισχύει LTF (περισσότερα orders = μεγαλύτερες κινήσεις). Focus σε HTF, LTF ως confirmation. | `[CONF]` |
| MS-3 | Refine ανάλυση μέχρι **1min** — αλλά LTF liquidity δεν εξετάζεται χωρίς HTF target. | `[CONF]` |
| MS-4 | Zone-to-zone: από μια concentrated area στην άλλη, rapid move (δεν σταματά η τιμή μέχρι το επόμενο area). | `[CONF]` |

---

## 2. LIQUIDITY RULES (ο πυρήνας — «liquidity is everything»)

| # | Κανόνας | Tag |
|---|---|---|
| LQ-1 | Liquidity = προφανείς περιοχές όπου βρίσκονται τα retail stop losses. | `[CONF]` |
| LQ-2 | **4 τύποι MAJOR liquidity:** (1) **doji** (μέσα στο prev high/low, δεν το σπάει), (2) **perfect double top/bottom** (όχι equal — τέλειο double rejection), (3) **perfect trendline** (≥3 σημεία τέλειας απόρριψης), (4) **imbalanced candle** (άμεση κίνηση μιας κατεύθυνσης, το high/low δεν manipulated). | `[CONF]` |
| LQ-3 | **Κάθε major έχει opposite = MINOR liquidity:** doji↔**ATT FU**· perfect double/trendline↔ατελής απόρριψη· imbalanced↔**balanced** candle. Η διάκριση major/minor = το βασικό skill («calculating liquidity»). | `[CONF]` |
| LQ-4 | Bias/direction: όποια πλευρά έχει **περισσότερη liquidity** στα LTF (30m→1m) = η κατεύθυνση. Price hunts την πλευρά με τη μεγαλύτερη liquidity. | `[CONF]` |
| LQ-5 | Big wick rejection → αφήνει liquidity· ψάξε να «γεμίσει» ή να παρθεί. | `[CONF]` |
| LQ-6 | **LAOL (Last Area Of Liquidity):** η πιο συμπυκνωμένη/refined τελευταία περιοχή liquidity. Εκεί περιμένουμε reaction/reversal (αν υπάρχει major target αντίθετα). Το εύρος **εξαρτάται από τον στόχο:** scalp=1m–30m, intraday=1h–D, swing=D. | `[CONF]` |
| LQ-7 | Trendline: valid μόνο με **≥3 τέλεια σημεία**· 2 σημεία = low liquidity, no target. Perfect double = 0 απόσταση (zoom in, broker όχι TV). | `[CONF]` |

---

## 3. STRENGTH HIERARCHY (η «ιστορία της manipulation») `[CONF]`
Από ασθενέστερο σε ισχυρότερο:
> **ATT FU  <  FU  <  FU retest  <  HCS  <  multiple HCS**

Αυτό ορίζει το «πόσο σοβαρό είναι το σήμα». Ο indicator πρέπει να **κατατάσσει** τα σήματα σε αυτή την κλίμακα.

---

## 4. FU — CONFIRMATION TRIGGER (το «όπλο των τραπεζών»)

| # | Κανόνας | Tag |
|---|---|---|
| FU-1 | **FU** = candle που παίρνει liquidity **ΚΑΙ** αντιστρέφει στην αντίθετη κατεύθυνση, όλα στο **ίδιο κερί**. Το wick που πήρε τη liquidity = το FU. | `[CONF]` |
| FU-2 | Ιδανικό FU = **strong close** (λίγο/καθόλου rejection) → καλύτερο retest entry. «Don't be too strict in the definition.» | `[CONF]` |
| FU-3 | Code-verified ορισμός (beta γρ.537): bear `high>prevHigh & close<prevHigh & close>prevLow`· bull αντίστροφα. | `[CONF]` |
| FU-4 | **ΔΕΝ** τρακάρουμε κάθε FU — μόνο όσα ευθυγραμμίζονται με τη συνολική manipulation (bias + major liquidity target + LTF trail). | `[CONF]` |
| FU-5 | **ATT FU (attempted FU)** = manipulates high/low με wick αλλά **αποτυγχάνει** (doji-τύπου) = **minor/weak** liquidity. Opposite του doji. Μπορεί κι αυτό να γίνει retest (με LTF confirmation). | `[CONF]` |

---

## 5. FU NEGATION — REVERSAL SIGNAL

| # | Κανόνας | Tag |
|---|---|---|
| NG-1 | **Negation** = το candle **αμέσως μετά** ένα FU σχηματίζει FU **αντίθετης** φοράς → αλλαγή orderflow (τώρα στοχεύεται η αντίθετη liquidity). | `[CONF]` |
| NG-2 | Μετά από strong FU → περίμενε **2 σενάρια: retest Ή negation.** Δείχνουν ποια πλευρά στοχεύεται πρώτη. | `[CONF]` |
| NG-3 | Negation = 2η instance manipulation (η δύναμη των τραπεζών εξαντλείται). **Negation of negation = x3 manipulation** = ακόμα ισχυρότερη κίνηση. | `[CONF]` |
| NG-4 | 1min για entries / 4h για strong direction. Το FU wick του negation μπορεί να γίνει retest. | `[CONF]` |
| NG-5 | Code-verified (beta γρ.1627-1647): negation = αντίθετο EM (X3/LAOL/HCS/TBE) εμφανίζεται ενάντια στην intra-tier κατεύθυνση. | `[CONF]` |

---

## 6. HCS — HIGH CONFLUENCE SETUP (το ισχυρότερο σήμα)

| # | Κανόνας | Tag |
|---|---|---|
| HCS-1 | **Ορισμός (πηγή):** όταν ένα **FU γίνεται retest και το retest σχηματίζει κι αυτό FU.** = «any two [FU/ATT FU/negation] retesting each other.» | `[CONF]` |
| HCS-2 | Το **ισχυρότερο** candlestick formation· σήμα institutional orderflow. | `[CONF]` |
| HCS-3 | **Δύο μορφές ισχύος:** strong FU + strong FU = ισχυρότερο HCS· ATT FU + negation wick = ασθενέστερο HCS. | `[CONF]` |
| HCS-4 | Δύο χρήσεις: (1) bias/liquidity calc σε HTF, (2) **LTF entry model** — ανώτερο του FU retest (κανένα guesswork: περιμένεις το 2ο FU στο retest). | `[CONF]` |
| HCS-5 | **Weak HCS**: ξεκινά με 1min doji → αποφυγή. | `[CONF]` |
| HCS-6 | Code-verified (beta γρ.1147-1160): ζώνη FU/SN που ξανα-επιβεβαιώνεται από νέο FU/SN μέσα της → `hcs_count++` («HCS x2/x3»). Ταιριάζει 1:1 με τον ορισμό πηγής. | `[CONF]` |

---

## 7. TIMEFRAME STRENGTH (κρίσιμος μηχανικός κανόνας)

| # | Κανόνας | Tag |
|---|---|---|
| TF-1 | **4h manipulation χρειάζεται 4h+ manipulation για negate.** Γενικός κανόνας: αντίθετο σήμα ίσου ή ανώτερου TF για αναστροφή. | `[CONF]` |
| TF-2 | **HCS = διπλάσια ισχύς:** 30min HCS = 1h FU. | `[CONF]` |
| TF-3 | Παράδειγμα: reversal buy σε liquidity target, αλλά σχηματίστηκε 15min FU down → buy **μόνο** με 5min HCS up **ή** 15min+ negation. | `[CONF]` |
| TF-4 | LTF = πιο manipulated (tightest stops, highest RR, extreme manipulation). HTF = περισσότερη ισχύς/relevance. | `[CONF]` |
| TF-5 | Cross-TF equivalence: 30min FU down = 15min FU retest up (ίση ισχύς). | `[CONF]` |

---

## 8. ENTRY MODEL

| # | Κανόνας | Tag |
|---|---|---|
| EN-1 | **FU retest = ασφαλέστερη μέθοδος.** Κάθε retested FU = strong direction. Τα περισσότερα swing highs/lows ξεκινούν με FU retests. | `[CONF]` |
| EN-2 | **Πρωτεύον entry = LIMIT @ 50% του FU** (fib 0.5), **με προϋπόθεση: όχι full impulse** (Nikos + screenshot). | `[CONF]` |
| EN-3 | Entry geometry: `entry = FU_low + 0.5×(FU_high−FU_low)`. | `[CONF]` |
| EN-4 | **HCS entry** = ανώτερο: περίμενε το 2ο FU στο retest της ζώνης (no guesswork). | `[CONF]` |
| EN-5 | Aggressive «as-it-forms» entry = για πιο έμπειρους (catch reversal καθώς σχηματίζεται). | `[CONF]` |
| EN-6 | **Confluence stack (perfect setup):** Daily bias ✓ + institutional zone ✓ + liquidity taken ✓ + LAOL to target ✓ + FU/HCS at POI ✓ + TF-strength aligned ✓. Όσα περισσότερα, τόσο ισχυρότερο. | `[CONF]` |
| EN-7 | «Full impulse» ορισμός = **`[?]`** (proxy ATR στο v0.2). | `[?]` |

---

## 9. INVALIDATION RULES

| # | Κανόνας | Tag |
|---|---|---|
| IV-1 | Setup ακυρώνεται αν σπάσει το reference level ή >5 candles χωρίς εξέλιξη (beta seq). | `[CONF]` |
| IV-2 | LAOL/HCS «broken» όταν το περνά η τιμή → αλλάζει bias (broken TSL = BOS = νέα κατεύθυνση). | `[CONF]` |
| IV-3 | FU ενάντια σε ανώτερο TF manipulation → invalid (μην τρακάρεις 5min FU up vs 4h FU down). | `[CONF]` |
| IV-4 | Weak HCS (1min doji start) → invalid. | `[CONF]` |

---

## 10. STOP LOSS RULES

| # | Κανόνας | Tag |
|---|---|---|
| SL-1 | Μικρότερο δυνατό SL· πέρα από το **FU wick** που πήρε τη liquidity. | `[CONF]` |
| SL-2 | Με entry @ 50% FU → **1R ≈ 50% του FU range** (+ buffer). | `[CONF]` |
| SL-3 | **TSL (True Stop Loss)** = ισχυρότερη/πιο concentrated manipulation area = true BOS. Εργαλείο **bias/direction** (δευτερεύον στο bias). Όταν σπάσει → liquidity πέρα από εκεί = κατεύθυνση στόχου. HTF-oriented. Πρακτικά: trailing anchor πίσω από τη manipulation area. | `[CONF]` · μηχανικά `[?]` |

---

## 11. TAKE PROFIT / EXIT LADDER `[CONF]` (Nikos)

| Trigger | Ενέργεια | Υπόλοιπο |
|---|---|---|
| **+3R** | close 40% + SL→breakeven | 60% |
| **+8R** | close 30% | 30% |
| **+15R** | close 15% | 15% |
| **+20R** | full close | 0% |

Targets = επόμενα LAOL / zone-to-zone (το ladder τα προσεγγίζει σε R). Το edge κυριαρχείται από το **+3R (40%) leg**.

---

## 12. SESSION / TIME RULES `[CONF]`
London + NY μόνο → **ώρα Ελλάδας 10:00–24:00** (London 10:00–19:00, NY 15:00–24:00, overlap 15:00–19:00). **News −15′/+15′ = no trade.** Pine: tz `Europe/Athens`, session `1000-0000`. News source `[?]` (external feed / Supabase calendar).

---

## 13. RISK RULES — ⚠️ ΣΥΓΚΡΟΥΣΗ ΠΗΓΗΣ↔ΧΡΗΣΤΗ

| # | Κανόνας | Tag |
|---|---|---|
| RK-1 | **Πηγή (βιβλίο):** max 3% (1–3% ανά RR/confluence, ΠΟΤΕ πάνω). | `[CONF]` |
| RK-2 | **Nikos (operative):** FTMO **0.5%** · live **2%**. → Το backtest τρέχει με αυτά (2 runs). | `[CONF]` |
| RK-3 | Σκέψου σε **%**, όχι $. Fixed, ποτέ μην το αλλάζεις εν θερμώ. | `[CONF]` |
| RK-4 | **Max 5 trades/μέρα** (μόνο highest-probability). Αν οι **3 πρώτες = losses → στοπ για τη μέρα.** | `[CONF]` |
| RK-5 | Χαμένη μέρα < μισό της προηγούμενης κερδισμένης. | `[CONF]` |

---

## 14. PSYCHOLOGY / NO-BIAS `[CONF]` (context, όχι μηχανικό)
5 truths (Mark Douglas): anything can happen· δεν χρειάζεσαι πρόβλεψη· τυχαία κατανομή wins/losses· edge = πιθανότητα· κάθε στιγμή μοναδική. No bias attachment. Απόφυγε greed/anger/foolishness. Σταμάτα σε αρνητικά συναισθήματα.

---

## 15. NO-TRADE CONDITIONS

| # | Κανόνας | Tag |
|---|---|---|
| NT-1 | Εκτός London/NY session ή −15′/+15′ news. | `[CONF]` |
| NT-2 | FU ενάντια σε ανώτερο TF manipulation. | `[CONF]` |
| NT-3 | FU μόνο του, χωρίς liquidity context / εκτός POI. | `[CONF]` |
| NT-4 | ATT FU ως «ισχυρό» σήμα (είναι weak). | `[CONF]` |
| NT-5 | Reversal που **ξεκινά με imbalance** (only balanced moves). | `[CONF]` |
| NT-6 | Weak HCS (1min doji start). | `[CONF]` |
| NT-7 | Ενάντια στο bias / σε obvious manipulation. | `[CONF]` |
| NT-8 | Ατελές double top/trendline ως major liquidity. | `[CONF]` |
| NT-9 | >3 losses τη μέρα, ή >5 trades. | `[CONF]` |

---

## 16. ΠΑΡΑΔΕΙΓΜΑΤΑ ΤΕΛΕΙΩΝ SETUPS `[EX]` (από docs + example charts)
1. **HCS at LAOL, bias-aligned, HTF confluence:** major liquidity taken + HCS στο LAOL + timeframe strength ευθυγραμμισμένο → entry στο 2ο FU. Ο πιο ισχυρός.
2. **FU retest σε institutional zone** (weekly+daily+4h overlap) με major liquidity to target + LTF trail.
3. **FU negation στο 4h** για strong direction + 1min HCS για entry.
4. **Perfect double bottom (major liq) taken πρώτα** → μετά το grab κλείσει → buys confirmation.

## 17. ΠΑΡΑΔΕΙΓΜΑΤΑ SETUPS ΠΡΟΣ ΑΠΟΦΥΓΗ `[EX]`
1. 5min FU up ενώ 4h FU down (fighting superior TF).
2. ATT FU / imperfect double / 2-point trendline θεωρημένα major liquidity.
3. Reversal ξεκινά με imbalanced candle.
4. FU χωρίς major liquidity target ή χωρίς LTF trail.
5. Weak HCS (1min doji). Trade εκτός session/near news.

---

## 18. ΤΙ ΠΡΕΠΕΙ ΝΑ ΔΕΙΧΝΕΙ Ο INDICATOR
valid long/short setup (+ strength rank ATT-FU→multi-HCS) · entry (50% FU) · SL (wick) · TP1/TP2/final (R-ladder) · LAOL lines · HCS boxes (count) · FU/ATT-FU/negation labels · TSL level · invalidation · no-trade reason (out-of-session/news/against-bias/against-HTF/no-liquidity).

## 19. ΤΙ ΠΡΕΠΕΙ ΝΑ BACKTESTΑΡΕΙ ΤΟ STRATEGY
Entry 50% FU (limit) · SL wick · R-ladder exits · session Ελλάδας · risk 0.5%/2% · 5-trades/day + 3-loss stop · spread+commission+slippage · no repaint/lookahead. Metrics: instrument, TF, date range, #trades, win%, avg RR, PF, max DD, avg/best/worst weekly, losing streak, frequency, στόχος 3–10%.

---

## 20. ΤΙ ΛΕΙΠΕΙ ΓΙΑ ΠΛΗΡΗ ΜΗΧΑΝΟΠΟΙΗΣΗ (honest gaps)

| Gap | Πρόβλημα | Tag |
|---|---|---|
| G-1 | **Bias = liquidity-based** («ποια πλευρά έχει περισσότερη liquidity»), ΟΧΙ απλό HH/HL. Το HH/HL μου = **προσέγγιση**, όχι ο πραγματικός κανόνας. | `[?]`/`[EXP]` |
| G-2 | **«Calculating liquidity»** (major vs minor) = το κεντρικό discretionary skill· δύσκολο πλήρως μηχανικό. Proxy: swing sweeps + perfect double/trendline detection. | `[EXP]` |
| G-3 | **Imbalances**: (α) Nikos «όχι» στον code, (β) πηγή: «μόνο broker, όχι TradingView». → **EXCLUDED από code**, documented ως discretionary. | `[CONF]` (excluded) |
| G-4 | **«Perfect» double/trendline** = fuzzy («zoom in, broker not TV»). | `[?]` |
| G-5 | **«Full impulse»** ορισμός. | `[?]` |
| G-6 | **TSL** μηχανικά (ισχυρότερη manipulation area = discretionary). | `[?]` |
| G-7 | **BETA repaint-άρει 100%** (εμπειρικά) → δεν είναι backtestable ως έχει. | `[CONF]` |
| G-8 | News timestamps source. | `[?]` |

---

## 21. ΣΥΓΚΡΟΥΣΕΙΣ ΠΗΓΗΣ↔ΧΡΗΣΤΗ (καταγραφή για διαφάνεια)
1. **Risk:** βιβλίο 1–3% vs Nikos 0.5%/2% → ισχύει **Nikos**.
2. **Imbalance:** πηγή το θεωρεί vital vs Nikos «μην το κωδικοποιείς» + «broker-only» → **excluded από code**, μένει στη θεωρία.
3. **Bias:** πηγή = liquidity-based vs coded proxy = HH/HL → σημειωμένο ως προσέγγιση `[EXP]`.

---
*RULEBOOK v1.3 — PHASE 1 complete. Καμία στατιστική δήλωση δεν έχει γίνει· όλα τα performance claims εκκρεμούν backtest.*
