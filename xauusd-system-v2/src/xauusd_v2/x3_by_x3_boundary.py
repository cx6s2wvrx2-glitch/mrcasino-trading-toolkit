from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class X3ByX3State(StrEnum):
    SOURCE_LABEL_ONLY = "source_label_only"
    NOT_LABELLED = "not_labelled"
    NOT_CERTIFIED = "not_certified"


@dataclass(frozen=True, slots=True)
class X3ByX3Result:
    state: X3ByX3State
    usable_as_context_label: bool
    raw_detector_allowed: bool
    strategy_condition_allowed: bool
    reason: str


def register_x3_by_x3_source_label(
    *,
    explicitly_labelled_by_approved_primary_source: bool | None,
) -> X3ByX3Result:
    """Preserve Reflection R-149 without inventing a raw-candle definition.

    The fully extracted Reflection Master uses the phrase `x3 by x3` in an applied
    1min sequence but explicitly leaves the construct without a standalone definition.
    Therefore it may be preserved only when the approved primary source itself labels
    the occurrence. It cannot be inferred from candles and cannot be used as an
    autonomous strategy condition.
    """
    if explicitly_labelled_by_approved_primary_source is None:
        return X3ByX3Result(
            state=X3ByX3State.NOT_CERTIFIED,
            usable_as_context_label=False,
            raw_detector_allowed=False,
            strategy_condition_allowed=False,
            reason="whether the approved primary source explicitly labels x3-by-x3 is unknown",
        )

    if not explicitly_labelled_by_approved_primary_source:
        return X3ByX3Result(
            state=X3ByX3State.NOT_LABELLED,
            usable_as_context_label=False,
            raw_detector_allowed=False,
            strategy_condition_allowed=False,
            reason="R-149 has no certified detector grammar; absence of an explicit source label cannot be filled by inference",
        )

    return X3ByX3Result(
        state=X3ByX3State.SOURCE_LABEL_ONLY,
        usable_as_context_label=True,
        raw_detector_allowed=False,
        strategy_condition_allowed=False,
        reason="R-149 may be retained as an explicit primary-source context label only; raw detection remains unresolved",
    )
