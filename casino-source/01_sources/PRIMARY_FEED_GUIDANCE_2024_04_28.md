# Primary Feed Guidance — 2024-04-28

Status: PRIMARY SOURCE GUIDANCE / DATA PROVENANCE
Authority: Mr Casino Discord answer, 28 April 2024
Strategy promotion: disabled
Live execution: disabled

## Primary-source statement

In response to questions about broker candle discrepancies and Forex.com, Mr Casino states that he recommends IC Markets MT4 data or Forex.com, with Pepperstone sometimes used for news when Forex.com does not align with broker data. He also states that Vantage is not as reliable for correct lower-timeframe data and that in that case analysis should be done on Forex.com; IC/Forex.com are prioritised.

The same Q&A context explicitly asks how to distinguish broker candles from Forex.com candles when marking major liquidity, confirming that broker-feed differences in opens/closes and lower-timeframe geometry are an expected practical issue rather than something to erase by assumption.

## User clarification preserved separately

The user has additionally reported a specific Casino instruction for TradingView usage: when analysing TradingView, use the Forex.com XAUUSD feed because the other TradingView feeds are not considered good enough.

For V2 this remains the operational interpretation:

- TradingView canonical visual/reference feed: `FOREXCOM:XAUUSD`.
- Broker/execution research feeds are preserved separately with exact provenance.
- Exclusive Markets `XAUUSD!` is the first broker research dataset; it is not silently treated as the Casino visual reference geometry.
- Feed disagreements are measured, not rounded away or forced to match.

## Immediate relevance to replay work

The narrated 30–31 March 2023 episode gives a concrete example of why this separation matters:

- source narrative: `1972.70 true stop respected`;
- Exclusive Markets M1 reconnaissance: one bar prints `1972.69` immediately before a bar with exact low `1972.70`;
- source narrative: `1987.56` 1min imbalance context;
- Exclusive Markets prints a nearby high of `1987.57` in the distinctive high-impact burst.

No numeric cross-feed tolerance is inferred from these differences. Exact reference-feed stage geometry must be checked on `FOREXCOM:XAUUSD` before a feed-sensitive True Stop or imbalance condition is certified.
