from __future__ import annotations

import unittest

from xauusd_v2.eleven_hour_timeframe import ElevenHourState, evaluate_eleven_hour_series


class ElevenHourTimeframeTests(unittest.TestCase):
    def test_native_11h_series_with_provenance_is_usable_for_context(self) -> None:
        result = evaluate_eleven_hour_series(
            timeframe_minutes=660,
            already_formed_series=True,
            source_name="TradingView approved source chart",
        )
        self.assertEqual(result.state, ElevenHourState.NATIVE_SERIES_USABLE)
        self.assertTrue(result.usable_for_context)
        self.assertFalse(result.synthetic_construction_allowed)

    def test_lower_tf_synthesis_is_blocked_while_anchor_unresolved(self) -> None:
        result = evaluate_eleven_hour_series(
            timeframe_minutes=660,
            already_formed_series=False,
            source_name="IC Markets",
            synthesis_requested=True,
            anchor_definition_certified=False,
        )
        self.assertEqual(result.state, ElevenHourState.SYNTHESIS_BLOCKED)
        self.assertFalse(result.synthetic_construction_allowed)

    def test_future_certified_anchor_only_creates_synthesis_candidate(self) -> None:
        result = evaluate_eleven_hour_series(
            timeframe_minutes=660,
            already_formed_series=False,
            source_name="IC Markets",
            synthesis_requested=True,
            anchor_definition_certified=True,
        )
        self.assertEqual(result.state, ElevenHourState.SYNTHESIS_CANDIDATE)
        self.assertTrue(result.synthetic_construction_allowed)

    def test_native_series_without_provenance_is_not_certified(self) -> None:
        result = evaluate_eleven_hour_series(
            timeframe_minutes=660,
            already_formed_series=True,
            source_name="",
        )
        self.assertEqual(result.state, ElevenHourState.NOT_CERTIFIED)

    def test_unknown_native_status_fails_closed(self) -> None:
        result = evaluate_eleven_hour_series(
            timeframe_minutes=660,
            already_formed_series=None,
            source_name="IC Markets",
        )
        self.assertEqual(result.state, ElevenHourState.NOT_CERTIFIED)

    def test_other_timeframe_is_outside_boundary(self) -> None:
        result = evaluate_eleven_hour_series(
            timeframe_minutes=420,
            already_formed_series=True,
            source_name="IC Markets",
        )
        self.assertEqual(result.state, ElevenHourState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
