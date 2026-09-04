from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from xauusd_v2.beta_intra_negation_shadow import (
    BetaIntraDirection,
    BetaIntraNegatingManipulation,
)
from xauusd_v2.casino_directional_marker_semantics import CasinoMarkerDirection
from xauusd_v2.casino_indicator_event_stream import (
    HCSCounterEventInput,
    build_supplied_indicator_event_frame,
)
from xauusd_v2.casino_indicator_events import CasinoIndicatorEventKind
from xauusd_v2.helper_fu_shadow import HelperFUClass


class CasinoIndicatorEventStreamTests(unittest.TestCase):
    def test_empty_frame_has_no_events(self) -> None:
        frame = build_supplied_indicator_event_frame(
            symbol="XAUUSD",
            timeframe="15m",
            bar_time_utc=datetime(2026, 9, 4, 4, 0, tzinfo=UTC),
        )
        self.assertEqual(frame.events, ())
        self.assertEqual(frame.supplied_indicator_event_count, 0)
        self.assertFalse(frame.strategy_semantics_certified)

    def test_four_way_fu_marker_output_enters_one_event_stream(self) -> None:
        frame = build_supplied_indicator_event_frame(
            symbol="XAUUSD",
            timeframe="15m",
            bar_time_utc=datetime(2026, 9, 4, 4, 0, tzinfo=UTC),
            bullish_fu_class=HelperFUClass.FU,
            bearish_fu_class=HelperFUClass.ATT,
        )
        self.assertEqual(
            [event.kind for event in frame.events],
            [CasinoIndicatorEventKind.STRONG_FU, CasinoIndicatorEventKind.ATTEMPTED_FU],
        )
        self.assertEqual(
            [event.direction for event in frame.events],
            [CasinoMarkerDirection.BULLISH, CasinoMarkerDirection.BEARISH],
        )

    def test_hcs_counter_and_hcs_retest_are_normalized_together(self) -> None:
        frame = build_supplied_indicator_event_frame(
            symbol="XAUUSD",
            timeframe="15m",
            bar_time_utc=datetime(2026, 9, 4, 4, 0, tzinfo=UTC),
            hcs_events=(
                HCSCounterEventInput(direction=CasinoMarkerDirection.BULLISH, count=2),
            ),
            hcs_retest_directions=(CasinoMarkerDirection.BULLISH,),
        )
        self.assertEqual(
            [event.kind for event in frame.events],
            [CasinoIndicatorEventKind.HCS, CasinoIndicatorEventKind.HCS_RETEST],
        )
        self.assertEqual(frame.events[0].marker_text, "HCS X2")
        self.assertEqual(frame.events[1].marker_text, "HCS RETESTING")

    def test_negation_and_hcs_context_are_visible_without_semantic_overpromotion(self) -> None:
        negation = BetaIntraNegatingManipulation(
            detected=True,
            direction=BetaIntraDirection.BEAR,
            forming=False,
            confirmed=True,
            contains_hcs_component=True,
            reason="test",
        )
        frame = build_supplied_indicator_event_frame(
            symbol="XAUUSD",
            timeframe="1m",
            bar_time_utc=datetime(2026, 9, 4, 4, 0, tzinfo=UTC),
            negating_manipulation=negation,
            negation_has_hcs_context=True,
        )
        self.assertEqual(
            [event.kind for event in frame.events],
            [CasinoIndicatorEventKind.NEGATION, CasinoIndicatorEventKind.HCS_CONTEXT_NEGATION],
        )
        self.assertNotIn(CasinoIndicatorEventKind.FU_NEGATION, [event.kind for event in frame.events])
        self.assertNotIn(CasinoIndicatorEventKind.HCS_NEGATION, [event.kind for event in frame.events])
        self.assertTrue(all(not event.strategy_semantics_certified for event in frame.events))

    def test_full_mixed_frame_is_deterministic(self) -> None:
        negation = BetaIntraNegatingManipulation(
            detected=True,
            direction=BetaIntraDirection.BEAR,
            forming=True,
            confirmed=False,
            contains_hcs_component=False,
            reason="test",
        )
        frame = build_supplied_indicator_event_frame(
            symbol="MNQ1!",
            timeframe="15m",
            bar_time_utc=datetime(2026, 9, 4, 7, 0, tzinfo=timezone_plus_three()),
            bullish_fu_class=HelperFUClass.FU,
            hcs_events=(HCSCounterEventInput(direction=CasinoMarkerDirection.BULLISH, count=1),),
            hcs_retest_directions=(CasinoMarkerDirection.BULLISH,),
            negating_manipulation=negation,
            negation_has_hcs_context=False,
        )
        self.assertEqual(frame.bar_time_utc, datetime(2026, 9, 4, 4, 0, tzinfo=UTC))
        self.assertEqual(
            [event.kind for event in frame.events],
            [
                CasinoIndicatorEventKind.STRONG_FU,
                CasinoIndicatorEventKind.HCS,
                CasinoIndicatorEventKind.HCS_RETEST,
                CasinoIndicatorEventKind.NEGATION,
            ],
        )
        self.assertEqual(frame.supplied_indicator_event_count, 4)

    def test_naive_datetime_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_supplied_indicator_event_frame(
                symbol="XAUUSD",
                timeframe="15m",
                bar_time_utc=datetime(2026, 9, 4, 4, 0),
            )

    def test_blank_symbol_and_timeframe_are_rejected(self) -> None:
        aware = datetime(2026, 9, 4, 4, 0, tzinfo=UTC)
        with self.assertRaises(ValueError):
            build_supplied_indicator_event_frame(symbol="", timeframe="15m", bar_time_utc=aware)
        with self.assertRaises(ValueError):
            build_supplied_indicator_event_frame(symbol="XAUUSD", timeframe="", bar_time_utc=aware)


def timezone_plus_three():
    return timezone(timedelta(hours=3))


from datetime import timezone


if __name__ == "__main__":
    unittest.main()
