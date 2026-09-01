from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TFSCategory(StrEnum):
    LTF = "ltf"
    SCALP = "scalp"
    INTRADAY = "intraday"
    SWING = "swing"
    LONGTERM_SWING = "longterm_swing"


@dataclass(frozen=True, slots=True)
class TFSResearchBand:
    category: TFSCategory
    min_minutes: int
    max_minutes: int | None
    source_move_description: str
    source_min_pips: int | None

    def contains(self, timeframe_minutes: int) -> bool:
        if timeframe_minutes < self.min_minutes:
            return False
        return self.max_minutes is None or timeframe_minutes <= self.max_minutes


# R-215 is preserved literally enough to expose its overlapping boundary points
# instead of silently inventing precedence at 30m, 3h or 7h.
R215_BANDS: tuple[TFSResearchBand, ...] = (
    TFSResearchBand(TFSCategory.LTF, 1, 5, "minimum scalp move", None),
    TFSResearchBand(TFSCategory.SCALP, 7, 30, "intraday move", None),
    TFSResearchBand(TFSCategory.INTRADAY, 30, 180, "100+ pips", 100),
    TFSResearchBand(TFSCategory.SWING, 180, 420, "250+ pips", 250),
    TFSResearchBand(TFSCategory.LONGTERM_SWING, 420, None, "350+ pips", 350),
)


def candidate_tfs_bands(timeframe_minutes: int) -> tuple[TFSResearchBand, ...]:
    """Return every R-215 band compatible with the timeframe.

    Boundary overlaps are returned as multiple candidates. This is intentional:
    R-215 itself overlaps 30m, 3h and 7h, so V2 refuses to invent an undocumented
    tie-breaker. The scale is a source hypothesis for research/backtesting, not a
    production target guarantee.
    """
    if timeframe_minutes <= 0:
        raise ValueError("timeframe_minutes must be positive")
    return tuple(band for band in R215_BANDS if band.contains(timeframe_minutes))
