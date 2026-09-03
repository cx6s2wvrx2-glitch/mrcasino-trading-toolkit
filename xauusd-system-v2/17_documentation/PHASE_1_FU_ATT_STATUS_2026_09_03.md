# XAUUSD V2 — Phase 1 FU / ATT FU Status

Date: 2026-09-03
Status: RESEARCH FOUNDATION COMPLETE / SEMANTIC CERTIFICATION OPEN
Next phase: HCS / FU Negation

## Τι κλείδωσε

Η Φάση 1 δεν ισχυρίζεται ότι υπάρχει πλέον universal certified FU detector.
Κλειδώνει ότι το project έχει αρκετά καθαρή και δομημένη βάση ώστε τα επόμενα components να μη βασίζονται στον παλιό στενό `basic_fu_candidate` ως μοναδική αλήθεια.

Source-backed δομή που θεωρείται επαρκώς σταθερή για research composition:

- FU = liquidity + αντίθετη κίνηση/break στο ίδιο candle.
- Strong FU / ATT FU primitive logic είναι timeframe-neutral/fractal.
- Complete FU, ATT Form 1 και ATT Form 2 είναι διαφορετικές Reflection κλάσεις.
- ATT Form 1 μπορεί να υπάρχει χωρίς νέο high/low.
- Final close position και structural-break evidence είναι ξεχωριστές διαστάσεις.
- Strongness/quality είναι ξεχωριστή από FU validity.
- FU δεν αποτελεί μόνο του trade signal· liquidity, manipulation, market structure και targets/context προηγούνται.
- HCS downstream μπορεί να χρησιμοποιεί Strong FU, ATT FU και FU negation nodes.

## Τι αξιοποιήθηκε από τους κώδικες του χρήστη

Οι supplied `Casino_v7` και `BETA 1 + LAOL` κώδικες χρησιμοποιήθηκαν ενεργά ως high-value mechanics/implementation evidence.

Casino_v7 evidence:
- continuation / pullback / reversal branches,
- close/open σχέσεις με previous OHLC,
- FU vs ATT branch distinctions,
- doji filter που καθαρίζει ordinary FU αλλά όχι ATT flags,
- configurable doji `BodyRatio=0.30` preserved strictly as helper parameter, NOT strategy threshold.

BETA evidence:
- broad bullish/bearish FU candidates,
- x3 exclusion,
- self-negation-together exclusion,
- return-inside-previous-range mechanics,
- interaction/state-machine evidence.

Δεν επιλέχθηκε κανένας supplied codebase ως μοναδική canonical strategy truth.

## Νέα research components

- `fu_family_observability.py`
  - κοινή γλώσσα raw facts + Reflection + Casino_v7 + BETA.
- expanded `fu_observables.py`
  - previous OHLC relationships χωρίς FU classification.
- `fu_break_evidence.py`
  - wick break vs close-through previous opposite extreme.
- `fu_intrabar_break_sequence.py`
  - ordered marked-liquidity take -> later opposite previous-extreme break evidence.
- `helper_fu_doji_shadow.py`
  - faithful Casino_v7 doji/FU/ATT implementation evidence without promoting the helper threshold.

Όλα παραμένουν non-certifying by construction.

## Ground truth inventory

Live FU-related corpus inventory:
- 69 FU-related examples,
- 53 ground-truth labelled,
- 55 visual/image anchored,
- 40 sequence anchored.

Το corpus είναι πλούσιο σε semantic/visual truth αλλά δεν έχει 69 έτοιμα raw OHLC/timestamp fixtures.
Raw alignment γίνεται μόνο όπου μπορεί να αποδειχθεί χωρίς inference.

## Τι παραμένει ανοιχτό

### B-01

Exact sufficient opposite-direction move/break mechanics.

Έχει πλέον στενέψει σε:
- ποιο structural-break family είναι αρκετό ανά context,
- αν/πώς πρέπει να συμβεί μετά το marked-liquidity take,
- πώς χαρτογραφούνται older/code branches σε later Reflection classes.

Δεν είναι πλέον γενική άγνοια του FU.

### B-03

Universal numeric Strong-FU threshold.

Δεν υπάρχει source-backed καθολικό body/wick percentage.
Τα objective quality metrics είναι διαθέσιμα, αλλά κανένα αυθαίρετο cutoff δεν προωθείται.

## Τι ΔΕΝ έχει κλειδώσει

- universal certified FU detector,
- universal Strong-FU numeric classifier,
- profitability,
- strategy promotion,
- live execution.

## Γιατί μπορούμε να περάσουμε Phase 2

Το HCS/Negation research μπορεί πλέον να χρησιμοποιεί ένα richer FU-family node representation με explicit evidence state αντί να απαιτεί `basic_fu_candidate=true`.

Κάθε node θα πρέπει να δηλώνει ξεχωριστά:
- node family/type,
- evidence basis,
- wick/range provenance όπου είναι γνωστό,
- semantic certification state,
- unresolved blockers.

Ένα unresolved FU node μπορεί να χρησιμοποιηθεί μόνο για observational/research diagnostics, ποτέ για certified HCS/strategy promotion.

## Next action

Phase 2 — HCS / FU Negation:
1. audit primary HCS + negation grammar,
2. audit current `hcs_semantic.py` / `negation_semantic.py`,
3. create a versioned non-certifying FU-family research-node representation,
4. enforce latest-FU-wick/retest rules without arbitrary +1-candle stitching,
5. revisit March 1975/1986 as diagnostics only,
6. expand to broader labelled HCS/negation corpus.

User manual action: NONE.
