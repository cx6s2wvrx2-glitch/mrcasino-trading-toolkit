# Imbalances — Certification Draft

Status: DRAFT / NOT VERIFIED / NOT PRODUCTION
Date: 2026-09-01

## 1. Current role

Approved sources consistently treat imbalance/IMB as liquidity-relevant structure used for target selection, refinement and directional context. Later material also includes imbalanced candle among the four main major-liquidity categories.

An imbalance is therefore not just a visual gap object; it participates in liquidity calculation.

## 2. What is currently supported

- IMB is a form of liquidity/context.
- Higher-TF major IMBs may act as targets.
- A sole 1m imbalance is not automatically sufficient as a target.
- Price Action Reflection shows IMB targets being ranked relative to stronger/weaker liquidity and interpreted together with HCS, zones and timeframe strength.
- Broker data is preferred for imbalance reading in the approved Imbalances source.

## 3. Geometry conflict — unresolved

There is a genuine source conflict:

- earlier lesson: imbalance zone described from previous candle close to next candle open;
- later book: imbalance marking described wick-before to wick-after.

The current corpus does not yet provide a certified mechanical rule that reconciles these two geometries.

Therefore implementation must preserve candidate geometries separately:

`imbalance_geometry = close_to_open | wick_to_wick | other_primary_certified | ambiguous`

No indicator may silently choose one because it is easier to code.

## 4. Fill / manipulation interpretation

Approved material supports the idea that imbalanced areas can be revisited/filled and that degree of fill can change interpretation, but does not yet supply one universal numeric fill rule for every timeframe and context.

Price Action Reflection provides concrete contextual examples where a mostly filled 1m IMB contributes to downside manipulation interpretation while larger liquidity/zone/TFS context governs the decision.

Thus:

`IMB_FILL alone != reversal`

and

`IMB_TARGET alone != trade entry`.

## 5. Priority / target ranking

Candidate hierarchy principles supported by current sources:

- timeframe matters;
- major/liquidity stacking matters;
- a nearby LTF IMB may remain liquidity yet be lower priority than a stronger target;
- IMB should be evaluated with current liquidity calculation, TFS and active zones.

No universal numeric priority score is certified.

## 6. Broker-data requirement

Approved Imbalances material explicitly says imbalance reading should come from broker data rather than TradingView.

Future implementation therefore needs to store:

- broker/source feed;
- symbol specification;
- timeframe;
- candle timestamps;
- exact OHLC values used for geometry.

Visual TradingView confirmation cannot become execution truth when broker candles differ.

## 7. Certification blockers

The module remains NOT VERIFIED until labelled primary examples resolve:

1. canonical geometry: close/open vs wick/wick or context-dependent rule;
2. exact definition of "filled" and whether thresholds vary by use;
3. target qualification by timeframe;
4. distinction between major IMB liquidity and lower-priority IMB;
5. invalidation conditions;
6. positive, negative and edge examples;
7. broker discrepancy handling;
8. relationship between IMB geometry and the later major-liquidity definition.

## 8. Future implementation fields

- imbalance_id
- timeframe
- direction
- geometry_type
- lower_bound
- upper_bound
- origin_candle_ids
- feed_id
- created_timestamp
- first_touch_timestamp
- fill_fraction
- filled_status
- liquidity_priority
- target_status
- parent_context_refs
- provisional_or_confirmed
- provenance_refs