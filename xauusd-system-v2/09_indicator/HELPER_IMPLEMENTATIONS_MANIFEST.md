# XAUUSD V2 — Helper Implementations Manifest

These artifacts are implementation references only. They are NOT strategy-authority sources and must never override approved Reflection / Mr Casino knowledge.

## 1) Casino_v7.txt

- Type: Pine Script v5 helper indicator
- SHA-256: `0428b835b2072fba3c414e368d1c13223bf9634cc77af53685b0dd9e7f112faf`
- Header author: `sincereStork12718`
- License header: Mozilla Public License 2.0
- Main implemented concepts: FU, Attempted FU, Doji, FVG/Imbalance, alerts
- Explicit non-strategy options in source: SMA confluence and inside bars are labelled `Not part of Casino strategy`
- Status: REFERENCE / REVIEW

### Known implementation hazards

1. Duplicate/unreachable bullish `else if` branches exist. An identical condition first sets `isAttFUBullv6=true`, while a later identical branch attempts `isFUBullv6=true`; the later branch can never execute.
2. Multiple reversal branches are duplicates/subsets of earlier branches, making some intended FU states unreachable.
3. Equivalent unreachable/subset logic is present in the bearish reversal section.
4. The two-candle-combination block is explicitly marked `Experimental!!!!` and computes OHLC variables without promoting them into the FU detector.
5. Therefore this script is a prototype/reference and cannot be copied as the canonical V2 detector without source-rule comparison and test vectors.

## 2) MMB_AFU_v1.ex5

- Type: compiled MetaTrader 5 EX5 black-box helper
- Size: 7,768 bytes
- SHA-256: `863245931d62109cd66a4e7e3e5a9c99783e8f2b563c2facd4f07b7a04d2cbe1`
- EX5 binary header confirmed
- Recoverable metadata strings: `MMBInvest`, `https://mmbinvest.info`, version `1.00`
- Source code unavailable from supplied binary
- Status: BLACK-BOX REFERENCE / REVIEW
- Rule: do not infer the exact meaning of `AFU` from filename alone; validate in MT5 against labelled charts.

## 3) MMB_SFU_v1.ex5

- Type: compiled MetaTrader 5 EX5 black-box helper
- Size: 7,958 bytes
- SHA-256: `d48e93e1d7631d7ca7c1fd7379827d43c32fd4214064671abc640c8d6d74e862`
- EX5 binary header confirmed
- Recoverable metadata strings: `MMBInvest`, `https://mmbinvest.info`, version `1.00`
- Source code unavailable from supplied binary
- Status: BLACK-BOX REFERENCE / REVIEW
- Rule: do not infer the exact meaning of `SFU` from filename alone; validate in MT5 against labelled charts.

## V2 policy for helper code

`Strategy sources -> canonical rule model -> test vectors -> compare helper implementation -> accept/reject behavior`

Never:

`old helper code -> strategy definition`

The future TradingView and MQL5 V2 implementations will be generated from the canonical approved rule model and independently tested against labelled examples. Helper artifacts are useful for comparison, regression discovery and understanding prior implementation attempts only.
