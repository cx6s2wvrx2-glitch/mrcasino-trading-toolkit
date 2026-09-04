# XAUUSD V2 — Strategy Truth Map

Date: 2026-09-04
Scope: `xauusd-system-v2/` only
Status: CURRENT UNDERSTANDING / RESEARCH FOUNDATION / NOT STRATEGY-CERTIFIED

## Η στρατηγική όπως έχει πλέον χαρτογραφηθεί

Η στρατηγική **δεν** είναι `βλέπω HCS/FU -> μπαίνω trade`.

Η πλήρης λογική που υποστηρίζεται από το εγκεκριμένο source corpus είναι:

`Liquidity / directional context`
→ `Strong/ATT manipulation language`
→ `HCS / Negation relationships`
→ `active Zone / POI reaction`
→ `TFS / prevalent direction`
→ `active LAOL`
→ `True Stop / Main POI respect`
→ `10m True Stop establishment`
→ `LTF execution/refinement`
→ `Core -> Major Liquidity -> opposite LAOL targets`
→ `separate deterministic risk gate`

Το επίσημο R-143 subset είναι:

`HCS zone reaction -> TFS -> LAOL met -> TS respected -> 10m TS EST -> core + major + LAOL target/timing`.

## 1. Liquidity / Directional Context

Κλειδωμένη αρχή:
- liquidity calculation προηγείται της τελικής entry logic;
- major liquidity != LAOL;
- ένα ορατό LTF liquidity point δεν γίνεται αυτόματα ενεργός στόχος;
- η σύγκριση κοιτά prevalent move, ποια πλευρά έχει ήδη χειραγωγηθεί περισσότερο και ποια πλευρά κρατά σημαντικότερη εναπομένουσα liquidity.

Ανοιχτά:
- πλήρης deterministic priority function όταν υπάρχουν πολλαπλά liquidity candidates;
- broker-specific IMB calibration;
- exact active-LAOL selection/refinement.

## 2. Strong FU / Attempted FU

Το downstream σύστημα διαβάζει τα markers από το supplied implementation layer:
- bright green = bullish Strong FU;
- faded green = bullish Attempted FU;
- bright red = bearish Strong FU;
- faded red = bearish Attempted FU.

Ο χρήστης έχει διευκρινίσει ότι η primitive λογική είναι fractal και ίδια σε όλα τα timeframes. Το timeframe αλλάζει authority/context/application, όχι την primitive έννοια.

Το supplied Casino code/helper είναι σημαντική implementation evidence. Δεν μετατρέπεται αυτόματα σε source-certified strategy truth.

## 3. HCS / FU Negation / HCS + Negation

Υλοποιημένο research event layer:
- source-style HCS proxy από retest του latest visible prior FU-family wick από νέο FU-family node;
- FU Negation proxy από latest Strong/ATT manipulation σε opposite Strong/F μέσα σε +1/+2 candles;
- ATT -> opposite ATT δεν προάγεται σε ordinary FU Negation;
- physical Strong/F node μπορεί να έχει semantic role FU Negation μέσα σε HCS χωρίς να διπλομετράται;
- HCS + Negation είναι ξεχωριστό composite;
- BETA HCS κρατιέται χωριστά από source-style HCS.

Ανοιχτά:
- universal raw HCS certification;
- x3 / x3-by-x3 / negation-of-negation raw grammar;
- canonical source-feed occurrence alignment.

## 4. Zone / POI

Κλειδωμένη αρχή:
- HCS-zone reaction είναι **secondary confluence** που συνθέτει το POI;
- zone touch από μόνο του δεν είναι entry;
- HCS-zone reaction είναι το πρώτο στάδιο του επίσημου R-143.

Machine frontier στα March episodes:
- source labels υπάρχουν;
- Exclusive broker path υπάρχει;
- canonical HCS-zone semantic occurrence δεν έχει πιστοποιηθεί.

## 5. TFS

Κλειδωμένη έννοια:
- TFS = **confirmed prevalent direction**;
- confirmation αναλύεται μετά το candle close;
- refined entry στηρίζεται σε 10/15m+ confirmation ανά setup;
- sub-10m μπορεί να κάνει refinement, όχι να δημιουργήσει μόνο του established TFS;
- AS FORMING πατά μόνο πάνω σε ήδη established prevalent TFS;
- macro/scalp/intraday/swing/extreme-swing settings δεν συγχωνεύονται σε ένα global bias.

March SELL boundary:
- το source λέει ότι το setup κάνει sense με timeframe strength και ότι ήταν στο σωστό σημείο να **form** daily FU downside;
- αυτό δεν ισοδυναμεί αυτόματα με explicit confirmed TFS occurrence πριν το 1986 entry;
- μεταγενέστερο 4h close δεν χρησιμοποιείται αναδρομικά.

## 6. LAOL

Κλειδωμένη έννοια:
- true reversal = LAOL-to-LAOL ανά TFS setting;
- LAOL είναι το active last-area / final liquidity-trail reference της reversal structure;
- TFS μπορεί να επιβεβαιώνει LAOL/refined POI μέσω multi-TF confluence;
- `LAOL respected`, `LAOL taken`, `R-143 LAOL met` **δεν εξισώνονται σιωπηλά**;
- LTF LAOL taken ξεκινά το 10m TS build στο execution sequence.

March BUY boundary:
- `1972.19 liquidity is being left behind` δεν πιστοποιεί από μόνο του `LAOL met`;
- μέχρι να υπάρχει explicit mapping, το R-143 LAOL stage μένει blocked.

## 7. True Stop / Main POI

Κλειδωμένη έννοια:
- True Stop δεν είναι οποιοδήποτε high/low ή FU wick;
- κάθε true PA wave βασίζεται σε 10m+ HCS/negation manipulation;
- Main HTF TS είναι το low/high όπου ευθυγραμμίζονται οι απαιτούμενοι 10m+ TFS factors;
- το Main POI πρέπει να γίνει respected πριν από LTF HCS/negation entry πάνω στον τελικό liquidity calculation.

March BUY:
- source: `1972.70 True Stop respected`;
- Exclusive: M1 low `1972.70` υπάρχει, αλλά το προηγούμενο M1 έχει `1972.69`;
- άρα broker path observation ΝΑΙ, canonical semantic equivalence ΟΧΙ.

## 8. 10m True Stop Establishment

Κλειδωμένη source relationship:

`TS respected -> LAOL taken -> new 10m HCS TS for established direction`.

Επίσης το source δείχνει LTF build-up:

`retail liquidity manipulated -> LTF LAOL taken -> 1m HCS x3 -> x3 negation -> 10m HCS EST`.

Όμως το raw x3-by-x3 grammar παραμένει ανοιχτό, επομένως το συγκεκριμένο building process δεν προάγεται ακόμη σε complete automation.

## 9. LTF Execution / Entry Candidate

Confirmed source sequence:

`retail liquidity manipulated -> LTF LAOL taken -> 1m negation OR 3m HCS+negation`.

Confirmed execution περιμένει 10m TS established. Aggressive exception απαιτεί full TFS factors + 10m TS forming.

March source δείχνει επίσης:
- αφού τα buys ήταν established, 5m ATT-FU retest + strongest 1m FU close γύρω από 1973 ως advanced optimal entry;
- 1975 ως easier 1m HCS re-entry όταν η buy direction ήταν περισσότερο established.

Pattern alone != entry allowed.

## 10. Targets / Management

Source-backed:
- Core Breakout Liquidity = minimum target μετά από opposite LAOL/POI respect;
- R-143 target/timing package = core + major + opposite LAOL;
- προηγούμενα liquidity-trail steps μπορούν να γίνουν targets μετά reversal.

Ανοιχτά:
- exact trail-level selection;
- Accepted RR numeric/dynamic definition;
- broker-quality cost model πριν performance research.

## 11. Risk / Live Authority

Ανεξάρτητη deterministic gate.

Δεν είναι αποτέλεσμα των FU/HCS detectors.

Current state:
- numeric production risk policy: unapproved;
- strategy certified: NO;
- performance claim allowed: NO;
- promotion allowed: NO;
- live execution: DISABLED.

## March validation frontiers τώρα

### 30 March BUY
- source semantic frontier: **LAOL_MET**;
- broker semantic frontier: **HCS_ZONE_REACTION**;
- FOREXCOM alignment: **not complete**.

### 31 March SELL
- source semantic frontier: **TFS_CONFIRMED**;
- broker semantic frontier: **HCS_ZONE_REACTION**;
- FOREXCOM alignment: **not complete**.

Αυτό δεν ακυρώνει το replay. Το Exclusive path αναπαράγει πολύ χρήσιμα τα source-labelled price paths. Απλώς το project δεν επιτρέπεται να μετατρέψει price similarity σε semantic truth.

## Τι πρέπει να δει ο χρήστης πριν performance backtest

Το τελικό validation pack θα πρέπει να παρουσιάσει οπτικά:

1. `F / A` marker language;
2. HCS / FU Negation / HCS+Negation relationships;
3. το πλήρες strategy flow του παρόντος αρχείου;
4. March BUY και SELL timelines δίπλα σε source/broker semantic status;
5. τα unresolved σημεία με ξεκάθαρο χρώμα/σήμανση;
6. ποιο layer προέρχεται από supplied code, ποιο από primary source, ποιο είναι research proxy;
7. agent/component status;
8. explicit statement ότι profitability/live readiness δεν έχει ακόμη αποδειχθεί.
