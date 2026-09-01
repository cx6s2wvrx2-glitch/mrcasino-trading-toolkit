from __future__ import annotations

import unittest

from xauusd_v2.agents.market_state_agent import (
    ContextState,
    Direction,
    MarketContextInput,
    MarketStateAgent,
)


class MarketStateAgentTests(unittest.TestCase):
    def test_all_known_bullish_inputs_align(self) -> None:
        report, run = MarketStateAgent().evaluate(
            MarketContextInput(
                prevalent_htf_direction=Direction.BULLISH,
                established_tfs_direction=Direction.BULLISH,
                major_liquidity_target_direction=Direction.BULLISH,
                active_zone_direction=Direction.BULLISH,
                source_refs=("HTF-1", "TFS-1", "LIQ-1", "ZONE-1"),
            )
        )
        self.assertEqual(report.state, ContextState.ALIGNED_BULLISH)
        self.assertEqual(report.aligned_direction, Direction.BULLISH)
        self.assertFalse(run.needs_review)

    def test_all_known_bearish_inputs_align(self) -> None:
        report, _ = MarketStateAgent().evaluate(
            MarketContextInput(
                prevalent_htf_direction=Direction.BEARISH,
                established_tfs_direction=Direction.BEARISH,
                major_liquidity_target_direction=Direction.BEARISH,
                source_refs=("HTF-2", "TFS-2", "LIQ-2"),
            )
        )
        self.assertEqual(report.state, ContextState.ALIGNED_BEARISH)

    def test_conflicting_confirmed_inputs_fail_closed(self) -> None:
        report, run = MarketStateAgent().evaluate(
            MarketContextInput(
                prevalent_htf_direction=Direction.BULLISH,
                established_tfs_direction=Direction.BEARISH,
                source_refs=("HTF-3", "TFS-3"),
            )
        )
        self.assertEqual(report.state, ContextState.CONFLICTING)
        self.assertEqual(report.aligned_direction, Direction.UNKNOWN)
        self.assertTrue(run.needs_review)

    def test_provisional_required_input_forces_ambiguity(self) -> None:
        report, _ = MarketStateAgent().evaluate(
            MarketContextInput(
                prevalent_htf_direction=Direction.BULLISH,
                established_tfs_direction=Direction.BULLISH,
                has_provisional_required_input=True,
                source_refs=("HTF-4", "TFS-4"),
            )
        )
        self.assertEqual(report.state, ContextState.AMBIGUOUS)

    def test_unresolved_required_input_forces_ambiguity(self) -> None:
        report, _ = MarketStateAgent().evaluate(
            MarketContextInput(
                prevalent_htf_direction=Direction.BULLISH,
                has_unresolved_required_input=True,
                source_refs=("HTF-5",),
            )
        )
        self.assertEqual(report.state, ContextState.AMBIGUOUS)

    def test_no_known_direction_returns_no_context(self) -> None:
        report, run = MarketStateAgent().evaluate(MarketContextInput(source_refs=("CTX-6",)))
        self.assertEqual(report.state, ContextState.NO_CONTEXT)
        self.assertTrue(run.needs_review)


if __name__ == "__main__":
    unittest.main()
