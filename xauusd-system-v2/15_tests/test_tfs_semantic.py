from __future__ import annotations

import unittest

from xauusd_v2.tfs_semantic import (
    Direction,
    TFSEntryState,
    TFSState,
    evaluate_established_tfs,
    evaluate_hcs_establishment,
    evaluate_tfs_as_forming,
    evaluate_tfs_entry,
)


class TFSSemanticTests(unittest.TestCase):
    def test_closed_10m_plus_prevalent_direction_establishes_tfs(self) -> None:
        result = evaluate_established_tfs(
            prevalent_direction=Direction.BULLISH,
            candle_closed=True,
            confirmation_timeframe_minutes=15,
        )
        self.assertEqual(result.state, TFSState.ESTABLISHED)

    def test_open_candle_cannot_establish_tfs(self) -> None:
        result = evaluate_established_tfs(
            prevalent_direction=Direction.BULLISH,
            candle_closed=False,
            confirmation_timeframe_minutes=15,
        )
        self.assertEqual(result.state, TFSState.NOT_ESTABLISHED)

    def test_sub_10m_cannot_establish_tfs_alone(self) -> None:
        result = evaluate_established_tfs(
            prevalent_direction=Direction.BEARISH,
            candle_closed=True,
            confirmation_timeframe_minutes=5,
        )
        self.assertEqual(result.state, TFSState.NOT_ESTABLISHED)

    def test_missing_tfs_evidence_fails_closed(self) -> None:
        result = evaluate_established_tfs(
            prevalent_direction=None,
            candle_closed=True,
            confirmation_timeframe_minutes=15,
        )
        self.assertEqual(result.state, TFSState.NOT_CERTIFIED)

    def test_hcs_requires_left_fu_retest_to_be_established(self) -> None:
        result = evaluate_hcs_establishment(left_fu_retested_first=False, hcs_present=True)
        self.assertEqual(result.state, TFSState.NOT_ESTABLISHED)

    def test_hcs_after_left_fu_retest_is_established(self) -> None:
        result = evaluate_hcs_establishment(left_fu_retested_first=True, hcs_present=True)
        self.assertEqual(result.state, TFSState.ESTABLISHED)

    def test_forming_requires_existing_prevalent_tfs(self) -> None:
        result = evaluate_tfs_as_forming(
            established_prevalent_tfs_exists=False,
            power_poi_present=True,
            aligned_lower_tf_closure=True,
        )
        self.assertEqual(result.state, TFSState.NOT_ESTABLISHED)

    def test_forming_power_poi_inside_established_tfs_is_allowed(self) -> None:
        result = evaluate_tfs_as_forming(
            established_prevalent_tfs_exists=True,
            power_poi_present=True,
            aligned_lower_tf_closure=True,
        )
        self.assertEqual(result.state, TFSState.AS_FORMING_POWER_POI)

    def test_entry_waits_until_established_tfs_is_retested(self) -> None:
        result = evaluate_tfs_entry(
            established_tfs=True,
            established_tfs_retested=False,
            prevalent_direction_confirmed=True,
            direction=Direction.BULLISH,
        )
        self.assertEqual(result.state, TFSEntryState.WAIT)

    def test_entry_candidate_requires_all_r182_inputs(self) -> None:
        result = evaluate_tfs_entry(
            established_tfs=True,
            established_tfs_retested=True,
            prevalent_direction_confirmed=True,
            direction=Direction.BEARISH,
        )
        self.assertEqual(result.state, TFSEntryState.ENTRY_CANDIDATE)

    def test_missing_entry_direction_fails_closed(self) -> None:
        result = evaluate_tfs_entry(
            established_tfs=True,
            established_tfs_retested=True,
            prevalent_direction_confirmed=True,
            direction=None,
        )
        self.assertEqual(result.state, TFSEntryState.NOT_CERTIFIED)


if __name__ == "__main__":
    unittest.main()
