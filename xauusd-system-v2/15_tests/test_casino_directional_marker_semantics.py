from __future__ import annotations

import unittest

from xauusd_v2.casino_directional_marker_semantics import (
    CasinoMarkerDirection,
    CasinoMarkerVisualCue,
    directional_marker_from_legacy_helper_class,
)
from xauusd_v2.casino_marker_semantics import CasinoMarkerMeaning, CasinoVisibleMarker
from xauusd_v2.helper_fu_shadow import HelperFUClass


class CasinoDirectionalMarkerSemanticsTests(unittest.TestCase):
    def test_bullish_strong_fu_is_bright_green(self) -> None:
        result = directional_marker_from_legacy_helper_class(
            direction=CasinoMarkerDirection.BULLISH,
            helper_class=HelperFUClass.FU,
        )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.marker, CasinoVisibleMarker.STRONG_FU)
        self.assertEqual(result.meaning, CasinoMarkerMeaning.STRONG_FU)
        self.assertEqual(result.visual_cue, CasinoMarkerVisualCue.BRIGHT_GREEN)
        self.assertFalse(result.raw_strategy_semantics_certified)

    def test_bullish_attempted_fu_is_faded_green(self) -> None:
        result = directional_marker_from_legacy_helper_class(
            direction=CasinoMarkerDirection.BULLISH,
            helper_class=HelperFUClass.ATT,
        )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.visual_cue, CasinoMarkerVisualCue.FADED_GREEN)
        self.assertEqual(result.meaning, CasinoMarkerMeaning.ATTEMPTED_FU)

    def test_bearish_strong_fu_is_bright_red(self) -> None:
        result = directional_marker_from_legacy_helper_class(
            direction=CasinoMarkerDirection.BEARISH,
            helper_class=HelperFUClass.FU,
        )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.visual_cue, CasinoMarkerVisualCue.BRIGHT_RED)
        self.assertEqual(result.meaning, CasinoMarkerMeaning.STRONG_FU)

    def test_bearish_attempted_fu_is_faded_red(self) -> None:
        result = directional_marker_from_legacy_helper_class(
            direction=CasinoMarkerDirection.BEARISH,
            helper_class=HelperFUClass.ATT,
        )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.visual_cue, CasinoMarkerVisualCue.FADED_RED)
        self.assertEqual(result.meaning, CasinoMarkerMeaning.ATTEMPTED_FU)

    def test_no_helper_marker_has_no_directional_marker(self) -> None:
        result = directional_marker_from_legacy_helper_class(
            direction=CasinoMarkerDirection.BULLISH,
            helper_class=HelperFUClass.NONE,
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
