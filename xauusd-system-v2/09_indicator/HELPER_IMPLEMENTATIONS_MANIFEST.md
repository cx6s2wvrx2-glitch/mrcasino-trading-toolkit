# XAUUSD V2 — Helper Implementations Manifest

These supplied artifacts are **high-value operational detector / implementation references**. They contain substantial Casino mechanics and should be used actively to reproduce the chart event stream (Strong FU, Attempted FU and downstream manipulation states) before inventing replacement detectors.

They are still not allowed to override an explicit Mr Casino / Reflection source statement or an explicit user clarification when a real conflict exists.

## 1) Casino_v7.txt

- Type: Pine Script v5 helper indicator
- SHA-256: `0428b835b2072fba3c414e368d1c13223bf9634cc77af53685b0dd9e7f112faf`
- Header author: `sincereStork12718`
- License header: Mozilla Public License 2.0
- Main implemented concepts: FU, Attempted FU, Doji, FVG/Imbalance, alerts
- Explicit non-strategy options in source: SMA confluence and inside bars are labelled `Not part of Casino strategy`
- User-clarified visible legend:
  - `F` = Strong FU
  - `A` = Attempted FU
  - bright green = bullish Strong FU
  - faded green = bullish Attempted FU
  - bright red = bearish Strong FU
  - faded red = bearish Attempted FU
- Status: OPERATIONAL DETECTOR REFERENCE / REVIEW

### Known implementation hazards

1. Duplicate/unreachable bullish `else if` branches exist. An identical condition first sets `isAttFUBullv6=true`, while a later identical branch attempts `isFUBullv6=true`; the later branch can never execute.
2. Multiple reversal branches are duplicates/subsets of earlier branches, making some intended FU states unreachable.
3. Equivalent unreachable/subset logic is present in the bearish reversal section.
4. The two-candle-combination block is explicitly marked `Experimental!!!!` and computes OHLC variables without promoting them into the FU detector.
5. These hazards must be preserved and tested when reproducing indicator behavior; they must not be silently "fixed" and then presented as faithful equivalence.

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

## 4) BETA 1 + LAOL.txt

- Type: Pine Script v6 multi-timeframe state machine supplied by the user
- Important operational concepts include FU, self-negation, x3-family states, LAOL, HCS formation/counting, HCS boxes/retests and broader establishment logic.
- The code explicitly tracks `bear_hcs` / `bull_hcs`, increments `hcs_count`, renders `HCS Xn`, and tracks `Bear/Bull HCS RETESTING` states.
- Status: HIGH-VALUE OPERATIONAL STATE-MACHINE REFERENCE / REPAINTING REPORTED BY USER

The repainting warning means historical outputs must be tested for timing/finality. It does not make the code irrelevant to strategy understanding.

## V2 policy for supplied code

Preferred reconstruction path:

`explicit source/user semantics -> faithfully reproduce supplied indicator event stream -> compare labelled examples -> compose strategy -> historical replay/backtest`

Raw OHLC reconstruction remains a diagnostic tool when the supplied indicator and source examples disagree. It is not the default reason to rediscover every Strong FU / ATT FU / HCS primitive from zero.

Never:

- silently change supplied-code behavior while claiming exact reproduction;
- let helper behavior override an explicit source/user rule conflict;
- treat indicator agreement alone as profitability/live certification.
