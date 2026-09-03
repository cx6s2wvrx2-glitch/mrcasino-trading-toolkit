from __future__ import annotations

from dataclasses import dataclass

from .fu_basic_candidate import BasicFUCandidateState, classify_basic_fu_candidate
from .fu_break_evidence import (
    FUCandidateDirection,
    FUPreviousCandleBreakEvidence,
    assess_previous_candle_break,
)
from .fu_completion import FUCompletionClass, classify_fu_completion
from .fu_observables import CandleDirection, extract_fu_observables
from .helper_fu_shadow import HelperFUClass, beta_fu_core_shadow, casino_v7_core_shadow


@dataclass(frozen=True, slots=True)
class FUFamilyObservability:
    """Union of objective/source-relevant FU-family observations.

    This object is deliberately NOT a FU classifier. It keeps raw previous-OHLC
    relationships, direction-specific structural-break facts, the current narrow
    V2 proxy, Reflection completion evidence and the user-supplied Casino_v7/BETA
    implementation evidence side by side so divergences remain visible.

    No field in this object certifies FU semantics, Strong FU, HCS, strategy
    readiness, performance, promotion or live execution.
    """

    direction: CandleDirection

    swept_previous_high: bool
    swept_previous_low: bool
    swept_both_sides: bool

    close_within_previous_range: bool
    close_above_previous_high: bool
    close_below_previous_low: bool

    close_within_previous_body: bool
    close_above_previous_body: bool
    close_below_previous_body: bool

    close_above_previous_open: bool
    close_below_previous_open: bool
    close_above_previous_close: bool
    close_below_previous_close: bool
    open_above_previous_open: bool
    open_below_previous_open: bool

    bullish_previous_candle_break: FUPreviousCandleBreakEvidence
    bearish_previous_candle_break: FUPreviousCandleBreakEvidence

    basic_fu_proxy: BasicFUCandidateState

    reflection_observed_class: FUCompletionClass
    reflection_conditional_if_fu_criteria_met: FUCompletionClass | None
    reflection_conditional_is_counterfactual: bool

    casino_v7_bullish: HelperFUClass
    casino_v7_bearish: HelperFUClass
    casino_v7_bullish_branch: str
    casino_v7_bearish_branch: str

    beta_bullish_fu_candidate: bool
    beta_bearish_fu_candidate: bool
    beta_is_x3: bool
    beta_self_negation_together: bool

    fu_semantics_certified: bool
    strong_fu_certified: bool
    strategy_truth_changed: bool


def observe_fu_family(
    *,
    open: float,
    high: float,
    low: float,
    close: float,
    previous_open: float,
    previous_high: float,
    previous_low: float,
    previous_close: float,
) -> FUFamilyObservability:
    """Collect FU-family evidence without collapsing competing definitions.

    Reflection ATT Form 1 is observable when there is no new high/low. When a new
    high/low exists, Reflection Complete-vs-ATT2 still depends on upstream FU
    criteria. In that case we record a clearly counterfactual class under the
    explicit assumption ``fu_criteria_met=True``; the actual observed class stays
    NOT_CERTIFIED until the semantic prerequisite is supplied elsewhere.

    Direction-specific previous-candle break evidence is also recorded for both
    bullish and bearish FU hypotheses. Those facts do not assert that valid
    liquidity was taken or that the opposite break happened after the take.
    """

    raw = extract_fu_observables(
        open=open,
        high=high,
        low=low,
        close=close,
        previous_open=previous_open,
        previous_high=previous_high,
        previous_low=previous_low,
        previous_close=previous_close,
    )
    bullish_break = assess_previous_candle_break(
        direction=FUCandidateDirection.BULLISH,
        high=high,
        low=low,
        close=close,
        previous_high=previous_high,
        previous_low=previous_low,
    )
    bearish_break = assess_previous_candle_break(
        direction=FUCandidateDirection.BEARISH,
        high=high,
        low=low,
        close=close,
        previous_high=previous_high,
        previous_low=previous_low,
    )
    basic = classify_basic_fu_candidate(
        open=open,
        high=high,
        low=low,
        close=close,
        previous_high=previous_high,
        previous_low=previous_low,
    )
    v7 = casino_v7_core_shadow(
        open=open,
        high=high,
        low=low,
        close=close,
        previous_open=previous_open,
        previous_high=previous_high,
        previous_low=previous_low,
        previous_close=previous_close,
    )
    beta = beta_fu_core_shadow(
        open=open,
        high=high,
        low=low,
        close=close,
        previous_high=previous_high,
        previous_low=previous_low,
    )

    new_high_or_low = raw.swept_previous_high or raw.swept_previous_low
    observed_completion = classify_fu_completion(
        new_high_or_low=new_high_or_low,
        fu_criteria_met=None,
        close=close,
        previous_open=previous_open,
        previous_close=previous_close,
    )

    conditional_class: FUCompletionClass | None = None
    conditional_is_counterfactual = False
    if new_high_or_low:
        conditional = classify_fu_completion(
            new_high_or_low=True,
            fu_criteria_met=True,
            close=close,
            previous_open=previous_open,
            previous_close=previous_close,
        )
        conditional_class = conditional.classification
        conditional_is_counterfactual = True

    return FUFamilyObservability(
        direction=raw.direction,
        swept_previous_high=raw.swept_previous_high,
        swept_previous_low=raw.swept_previous_low,
        swept_both_sides=raw.swept_both_sides,
        close_within_previous_range=raw.close_within_previous_range,
        close_above_previous_high=raw.close_above_previous_high,
        close_below_previous_low=raw.close_below_previous_low,
        close_within_previous_body=raw.close_within_previous_body,
        close_above_previous_body=raw.close_above_previous_body,
        close_below_previous_body=raw.close_below_previous_body,
        close_above_previous_open=raw.close_above_previous_open,
        close_below_previous_open=raw.close_below_previous_open,
        close_above_previous_close=raw.close_above_previous_close,
        close_below_previous_close=raw.close_below_previous_close,
        open_above_previous_open=raw.open_above_previous_open,
        open_below_previous_open=raw.open_below_previous_open,
        bullish_previous_candle_break=bullish_break,
        bearish_previous_candle_break=bearish_break,
        basic_fu_proxy=basic.state,
        reflection_observed_class=observed_completion.classification,
        reflection_conditional_if_fu_criteria_met=conditional_class,
        reflection_conditional_is_counterfactual=conditional_is_counterfactual,
        casino_v7_bullish=v7.bullish,
        casino_v7_bearish=v7.bearish,
        casino_v7_bullish_branch=v7.bullish_branch,
        casino_v7_bearish_branch=v7.bearish_branch,
        beta_bullish_fu_candidate=beta.bullish_fu_candidate,
        beta_bearish_fu_candidate=beta.bearish_fu_candidate,
        beta_is_x3=beta.is_x3,
        beta_self_negation_together=beta.self_negation_together,
        fu_semantics_certified=False,
        strong_fu_certified=False,
        strategy_truth_changed=False,
    )
