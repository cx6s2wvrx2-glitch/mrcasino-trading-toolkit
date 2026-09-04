from __future__ import annotations

import unittest

from xauusd_v2.beta_intra_negation_shadow import (
    BetaIntraDirection,
    BetaIntraNegatingManipulation,
)
from xauusd_v2.casino_directional_marker_semantics import (
    CasinoMarkerDirection,
    CasinoMarkerVisualCue,
)
from xauusd_v2.casino_indicator_events import (
    CasinoIndicatorEventKind,
    CasinoIndicatorEventSource,
    beta_hcs_context_negation_event,
    beta_hcs_event,
    beta_hcs_retest_event,
    beta_negation_event,
    fu_event_from_legacy_helper_output,
)
from xauusd_v2.helper_fu_shadow import HelperFUClass


class CasinoIndicatorEventsTests(unittest.TestCase):
    def test_bullish_strong_helper_event_is_bright_green_strong_fu(self) -> None:
        event = fu_event_from_legacy_helper_output(
            direction=CasinoMarkerDirection.BULLISH,
            helper_class=HelperFUClass.FU,
        )
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.kind, CasinoIndicatorEventKind.STRONG_FU)
        self.assertEqual(event.visual_cue, CasinoMarkerVisualCue.BRIGHT_GREEN)
        self.assertEqual(event.marker_text, "F")
        self.assertFalse(event.strategy_semantics_certified)

    def test_bearish_attempted_helper_event_is_faded_red_attempted_fu(self) -> None:
        event = fu_event_from_legacy_helper_output(
            direction=CasinoMarkerDirection.BEARISH,
            helper_class=HelperFUClass.ATT,
        )
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.kind, CasinoIndicatorEventKind.ATTEMPTED_FU)
        self.assertEqual(event.visual_cue, CasinoMarkerVisualCue.FADED_RED)
        self.assertEqual(event.marker_text, "A")

    def test_none_helper_output_creates_no_event(self) -> None:
        self.assertIsNone(
            fu_event_from_legacy_helper_output(
                direction=CasinoMarkerDirection.BULLISH,
                helper_class=HelperFUClass.NONE,
            )
        )

    def test_beta_hcs_count_is_preserved_as_event(self) -> None:
        event = beta_hcs_event(
            direction=CasinoMarkerDirection.BULLISH,
            hcs_count=2,
        )
        self.assertEqual(event.kind, CasinoIndicatorEventKind.HCS)
        self.assertEqual(event.source, CasinoIndicatorEventSource.SUPPLIED_BETA_STATE_MACHINE)
        self.assertEqual(event.hcs_count, 2)
        self.assertEqual(event.marker_text, "HCS X2")
        self.assertEqual(event.relation_to_prior_event, "retest_of_tracked_fu_or_sn_zone")
        self.assertTrue(event.confirmed)
        self.assertFalse(event.strategy_semantics_certified)

    def test_beta_hcs_retesting_is_explicit_event(self) -> None:
        event = beta_hcs_retest_event(direction=CasinoMarkerDirection.BEARISH)
        self.assertEqual(event.kind, CasinoIndicatorEventKind.HCS_RETEST)
        self.assertEqual(event.marker_text, "HCS RETESTING")
        self.assertEqual(event.relation_to_prior_event, "retest_of_tracked_hcs_zone")

    def test_beta_opposite_em_is_neutral_negation_event_not_fu_negation(self) -> None:
        state = BetaIntraNegatingManipulation(
            detected=True,
            direction=BetaIntraDirection.BEAR,
            forming=False,
            confirmed=True,
            contains_hcs_component=False,
            reason="test",
        )
        event = beta_negation_event(state)
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.kind, CasinoIndicatorEventKind.NEGATION)
        self.assertEqual(event.direction, CasinoMarkerDirection.BEARISH)
        self.assertEqual(event.marker_text, "NEG")
        self.assertTrue(event.confirmed)
        self.assertFalse(event.strategy_semantics_certified)

    def test_beta_forming_negation_preserves_forming_state(self) -> None:
        state = BetaIntraNegatingManipulation(
            detected=True,
            direction=BetaIntraDirection.BULL,
            forming=True,
            confirmed=False,
            contains_hcs_component=True,
            reason="test",
        )
        event = beta_negation_event(state)
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.marker_text, "NEG FORMING")
        self.assertTrue(event.forming)
        self.assertTrue(event.contains_hcs_context)

    def test_beta_hcs_context_negation_is_separate_from_source_hcs_negation(self) -> None:
        state = BetaIntraNegatingManipulation(
            detected=True,
            direction=BetaIntraDirection.BEAR,
            forming=False,
            confirmed=True,
            contains_hcs_component=False,
            reason="test",
        )
        event = beta_hcs_context_negation_event(state, hcs_context=True)
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.kind, CasinoIndicatorEventKind.HCS_CONTEXT_NEGATION)
        self.assertEqual(event.marker_text, "NEG + HCS CONTEXT")
        self.assertTrue(event.contains_hcs_context)
        self.assertNotEqual(event.kind, CasinoIndicatorEventKind.HCS_NEGATION)
        self.assertFalse(event.strategy_semantics_certified)

    def test_missing_hcs_context_does_not_create_hcs_context_negation(self) -> None:
        state = BetaIntraNegatingManipulation(
            detected=True,
            direction=BetaIntraDirection.BEAR,
            forming=False,
            confirmed=True,
            contains_hcs_component=False,
            reason="test",
        )
        self.assertIsNone(beta_hcs_context_negation_event(state, hcs_context=False))

    def test_undetected_negation_creates_no_event(self) -> None:
        state = BetaIntraNegatingManipulation(
            detected=False,
            direction=None,
            forming=False,
            confirmed=False,
            contains_hcs_component=False,
            reason="test",
        )
        self.assertIsNone(beta_negation_event(state))

    def test_hcs_count_zero_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            beta_hcs_event(
                direction=CasinoMarkerDirection.BULLISH,
                hcs_count=0,
            )


if __name__ == "__main__":
    unittest.main()
