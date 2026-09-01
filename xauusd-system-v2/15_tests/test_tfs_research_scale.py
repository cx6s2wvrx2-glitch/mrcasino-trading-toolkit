from __future__ import annotations

import unittest

from xauusd_v2.tfs_research_scale import TFSCategory, candidate_tfs_bands


class TFSResearchScaleTests(unittest.TestCase):
    def test_1m_is_ltf(self) -> None:
        bands = candidate_tfs_bands(1)
        self.assertEqual([b.category for b in bands], [TFSCategory.LTF])

    def test_6m_gap_is_preserved_not_guessed(self) -> None:
        self.assertEqual(candidate_tfs_bands(6), ())

    def test_30m_boundary_returns_scalp_and_intraday(self) -> None:
        bands = candidate_tfs_bands(30)
        self.assertEqual({b.category for b in bands}, {TFSCategory.SCALP, TFSCategory.INTRADAY})

    def test_60m_is_intraday_with_100_pip_source_hypothesis(self) -> None:
        bands = candidate_tfs_bands(60)
        self.assertEqual(len(bands), 1)
        self.assertEqual(bands[0].category, TFSCategory.INTRADAY)
        self.assertEqual(bands[0].source_min_pips, 100)

    def test_3h_boundary_returns_intraday_and_swing(self) -> None:
        bands = candidate_tfs_bands(180)
        self.assertEqual({b.category for b in bands}, {TFSCategory.INTRADAY, TFSCategory.SWING})

    def test_7h_boundary_returns_swing_and_longterm(self) -> None:
        bands = candidate_tfs_bands(420)
        self.assertEqual({b.category for b in bands}, {TFSCategory.SWING, TFSCategory.LONGTERM_SWING})

    def test_above_4d_remains_longterm_candidate(self) -> None:
        bands = candidate_tfs_bands(6000)
        self.assertEqual([b.category for b in bands], [TFSCategory.LONGTERM_SWING])
        self.assertEqual(bands[0].source_min_pips, 350)

    def test_non_positive_timeframe_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            candidate_tfs_bands(0)


if __name__ == "__main__":
    unittest.main()
