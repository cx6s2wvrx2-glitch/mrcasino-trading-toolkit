# Exclusive Markets MT5 timezone confirmation — 2026-09-03

Purpose: preserve broker-feed provenance for the first real XAUUSD MT5 history dataset used by XAUUSD V2.

## Confirmed by Exclusive Markets support

The user asked Exclusive Markets support:

> What timezone does the ExclusiveMarkets-Demo MT5 server use for historical candle timestamps? Is it GMT+2 in winter and GMT+3 in summer due to DST?

Exclusive Markets support replied that the times stated in the question are correct.

## Canonical ingestion interpretation

For the exported MT5 candle timestamps:

- winter server offset: GMT+2;
- summer server offset: GMT+3;
- daylight-saving behavior is required across the multi-year history;
- do not ingest the complete 2021-2026 history under one fixed UTC offset.

The deterministic MT5 adapter accepts IANA/zoneinfo timezones. For this GMT+2/GMT+3 DST policy, use `EET` as the technical timezone identifier for ingestion. This encodes the required winter/summer offset behavior and does not imply that the broker server is geographically located in a particular city.

## Dataset identity already observed

- broker/feed: Exclusive Markets demo MT5;
- broker symbol: `XAUUSD!`;
- canonical symbol: `XAUUSD`;
- timeframe: M1 (60 seconds);
- native export filename: `XAUUSD!_M1_202101040100_202609031251.csv`;
- source SHA-256: `691c1c2e9793e5eaea3291bf215147c0e02113ec910a5fc96fa751e2f8c84bc0`;
- exported first server timestamp: `2021.01.04 01:00:00`;
- exported last server timestamp: `2026.09.03 12:51:00`;
- exported bar count observed before canonical ingestion: 1,999,671.

This record is data-provenance evidence only. It does not define strategy truth, certify strategy rules, make performance claims, or authorize live execution.
