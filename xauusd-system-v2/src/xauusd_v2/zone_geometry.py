from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class WickSide(StrEnum):
    UPPER = "upper"
    LOWER = "lower"


class NeighborSide(StrEnum):
    PREVIOUS = "previous"
    NEXT = "next"


@dataclass(frozen=True, slots=True)
class Candle:
    open: float
    high: float
    low: float
    close: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.open, self.high, self.low, self.close)):
            raise ValueError("OHLC values must be finite")
        if self.low > self.high:
            raise ValueError("low cannot exceed high")
        if self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            raise ValueError("invalid OHLC geometry")

    @property
    def body_low(self) -> float:
        return min(self.open, self.close)

    @property
    def body_high(self) -> float:
        return max(self.open, self.close)

    @property
    def upper_wick(self) -> tuple[float, float]:
        return self.body_high, self.high

    @property
    def lower_wick(self) -> tuple[float, float]:
        return self.low, self.body_low


@dataclass(frozen=True, slots=True)
class BodyInWickMatch:
    neighbor: NeighborSide
    wick_side: WickSide
    wick_low: float
    wick_high: float


@dataclass(frozen=True, slots=True)
class TrueOrderblockResult:
    is_true_orderblock: bool
    matches: tuple[BodyInWickMatch, ...]


@dataclass(frozen=True, slots=True)
class ZoneRange:
    low: float
    high: float
    source: str

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.low, self.high)):
            raise ValueError("zone prices must be finite")
        if self.low > self.high:
            raise ValueError("zone low cannot exceed zone high")


def _body_inside_interval(candle: Candle, interval: tuple[float, float]) -> bool:
    low, high = interval
    # A zero-size wick cannot contain a meaningful body-in-wick relationship.
    if high <= low:
        return False
    return candle.body_low >= low and candle.body_high <= high


def detect_true_orderblock(
    *,
    candle: Candle,
    previous_candle: Candle | None,
    next_candle: Candle | None,
) -> TrueOrderblockResult:
    """Detect Reflection's True Orderblock body-in-wick geometry.

    R-157: the current candle body is inside a wick of the previous OR next
    candle. This detector reports every qualifying neighboring wick rather than
    guessing one when multiple relationships exist.
    """
    matches: list[BodyInWickMatch] = []
    neighbors = (
        (NeighborSide.PREVIOUS, previous_candle),
        (NeighborSide.NEXT, next_candle),
    )
    for neighbor_side, neighbor in neighbors:
        if neighbor is None:
            continue
        for wick_side, interval in (
            (WickSide.UPPER, neighbor.upper_wick),
            (WickSide.LOWER, neighbor.lower_wick),
        ):
            if _body_inside_interval(candle, interval):
                matches.append(
                    BodyInWickMatch(
                        neighbor=neighbor_side,
                        wick_side=wick_side,
                        wick_low=interval[0],
                        wick_high=interval[1],
                    )
                )
    return TrueOrderblockResult(bool(matches), tuple(matches))


def build_1m_strong_fu_zone(*, candle: Candle, timeframe_minutes: int, strong_fu_confirmed: bool | None) -> ZoneRange | None:
    """Build the scoped R-162 full-candle 1m Strong-FU zone.

    This does not classify Strong FU. It only constructs the zone AFTER a
    separately certified Strong-FU label has been supplied.
    """
    if timeframe_minutes != 1:
        return None
    if strong_fu_confirmed is not True:
        return None
    return ZoneRange(candle.low, candle.high, "1m_strong_fu_full_candle")


def combine_full_zone_range(*, fu_wick: ZoneRange, body_in_wick_orderblock: ZoneRange) -> ZoneRange:
    """R-167 full range: union of FU wick and body-in-wick OB refinement."""
    return ZoneRange(
        low=min(fu_wick.low, body_in_wick_orderblock.low),
        high=max(fu_wick.high, body_in_wick_orderblock.high),
        source="fu_wick_plus_body_in_wick_orderblock",
    )
