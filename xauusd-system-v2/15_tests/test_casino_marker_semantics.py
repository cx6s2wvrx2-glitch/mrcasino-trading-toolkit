from __future__ import annotations

import unittest

from xauusd_v2.casino_marker_semantics import (
    CasinoMarkerMeaning,
    CasinoVisibleMarker,
    semantic_for_visible_marker,
    visible_marker_from_legacy_helper_class,
)
from xauusd_v2.helper_fu_shadow import HelperFUClass


class CasinoMarkerSemanticsTests(unittest.TestCase):
    def test_a_marker_means_attempted_fu(self) -> None:
        evidence = semantic_for_visible_marker(CasinoVisibleMarker.ATTEMPTED_FU)
        self.assertEqual(evidence.marker.value, "A")
        self.assertEqual(evidence.meaning, CasinoMarkerMeaning.ATTEMPTED_FU)
        self.assertTrue(evidence.marker_meaning_user_clarified)
        self.assertFalse(evidence.raw_strategy_semantics_certified)

    def test_f_marker_means_strong_fu(self) -> None:
        evidence = semantic_for_visible_marker(CasinoVisibleMarker.STRONG_FU)
        self.assertEqual(evidence.marker.value, "F")
        self.assertEqual(evidence.meaning, CasinoMarkerMeaning.STRONG_FU)
        self.assertTrue(evidence.marker_meaning_user_clarified)
        self.assertFalse(evidence.universal_strong_fu_threshold_certified)

    def test_legacy_fu_helper_output_maps_to_visible_f_strong_fu_marker(self) -> None:
        marker = visible_marker_from_legacy_helper_class(HelperFUClass.FU)
        self.assertEqual(marker, CasinoVisibleMarker.STRONG_FU)

    def test_legacy_att_helper_output_maps_to_visible_a_attempted_fu_marker(self) -> None:
        marker = visible_marker_from_legacy_helper_class(HelperFUClass.ATT)
        self.assertEqual(marker, CasinoVisibleMarker.ATTEMPTED_FU)

    def test_none_helper_output_has_no_visible_marker(self) -> None:
        self.assertIsNone(visible_marker_from_legacy_helper_class(HelperFUClass.NONE))


if __name__ == "__main__":
    unittest.main()
