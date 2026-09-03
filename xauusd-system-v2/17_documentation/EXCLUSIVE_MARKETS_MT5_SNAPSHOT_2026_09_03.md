# Exclusive Markets MT5 Snapshot — 2026-09-03

## Status
The first real broker-side XAUUSD M1 dataset for V2 was successfully validated and persisted as an immutable local snapshot.

This record is data provenance only. It does **not** change strategy truth, promote any rule, or authorize live execution.

## Broker / source provenance
- Broker: `Exclusive Markets Ltd.`
- MT5 server: `ExclusiveMarkets-Demo`
- Broker symbol: `XAUUSD!`
- Canonical symbol: `XAUUSD`
- Timeframe: `M1` (`60` seconds)
- Account context: demo, Standard Plus
- Server timezone: winter `GMT+2`, summer `GMT+3` due to DST, confirmed by Exclusive Markets support on 2026-09-03
- Ingestion timezone identifier used: `EET`

## Dry-run validation
- Status: `VALIDATED_NOT_PERSISTED`
- Bar count: `1,999,671`
- First timestamp UTC: `2021-01-03T23:00:00+00:00`
- Last timestamp UTC: `2026-09-03T09:51:00+00:00`
- Closed only: `true`
- Gap count: `1604`
- Detected delimiter: `TAB`
- Optional columns: `tick_volume`, `real_volume`, `spread`

## Immutable persisted snapshot
- Status: `PERSISTED`
- Persisted: `true`
- Source SHA-256: `691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0`
- Normalized SHA-256: `ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`
- Snapshot ID: `sha256:ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24`

Local immutable paths reported by the ingestion CLI:
- Raw source: `~/.xauusd-v2/mt5/raw/691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0/source.mt5.txt`
- Canonical snapshot: `~/.xauusd-v2/mt5/snapshots/ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24/xauusd_ohlc.csv`
- Ingestion manifest: `~/.xauusd-v2/mt5/ingestions/691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0--ff8b8996bc70dff90e96d2c8f233f3c3a7841ece4bc620287947dd4a7558cf24.json`

## Governance
- This Exclusive Markets dataset is an execution/broker feed dataset, not the canonical TradingView strategy reference feed.
- TradingView strategy/reference alignment remains `FOREXCOM:XAUUSD` per the user-provided Mr Casino clarification.
- Feed differences must remain explicit and measurable; they must never be silently merged or forced identical.
- Missing intervals are diagnostic evidence and must not be synthetically filled without an explicit governed research rule.
- No strategy certification, paper-trading approval, production-risk approval, or live-execution authorization is implied by successful data ingestion.

## Next research stage
Use this immutable M1 snapshot to align approved source examples and build lookahead-safe historical replay evidence, starting with the six-stage R-143 sequence:
1. HCS zone reaction
2. TFS
3. LAOL met
4. True Stop respected
5. 10m True Stop established
6. targets / timing

Open strategy blockers remain fail-closed until resolved from approved primary evidence or explicit user clarification.
