from __future__ import annotations

import unittest

from xauusd_v2.casino_marker_semantics import CasinoVisibleMarker
from xauusd_v2.hcs_node_evidence import (
    HCSNodeEvidence,
    HCSNodeEvidenceSource,
    evaluate_hcs_research_evidence,
    hcs_node_from_casino_marker,
)
from xauusd_v2.hcs_semantic import HCSNodeType, HCSRetestState, HCSState, HCSStrength


class HCSNodeEvidenceTests(unittest.TestCase):
    def test_f_marker_maps_to_strong_fu_hcs_node(self) -> None:
        node = hcs_node_from_casino_marker(CasinoVisibleMarker.STRONG_FU)
        self.assertEqual(node.node_type, HCSNodeType.STRONG_FU)
        self.assertTrue(node.node_label_resolved)
        self.assertFalse(node.raw_node_semantics_certified)

    def test_a_marker_maps_to_attempted_fu_hcs_node(self) -> None:
        node = hcs_node_from_casino_marker(CasinoVisibleMarker.ATTEMPTED_FU)
        self.assertEqual(node.node_type, HCSNodeType.ATTEMPTED_FU)
        self.assertFalse(node.raw_node_semantics_certified)

    def test_two_f_markers_with_exact_retest_satisfy_strongest_grammar_but_not_certification(self) -> None:
        first = hcs_node_from_casino_marker(CasinoVisibleMarker.STRONG_FU)
        second = hcs_node_from_casino_marker(CasinoVisibleMarker.STRONG_FU)

        result = evaluate_hcs_research_evidence(
            first_node=first,
            second_node=second,
            retest_state=HCSRetestState.EXACT_WICK,
            retest_semantics_certified=True,
        )

        self.assertEqual(result.grammar_result.state, HCSState.CONFIRMED)
        self.assertEqual(result.grammar_result.strength, HCSStrength.EXPLICIT_STRONGEST)
        self.assertFalse(result.hcs_strategy_certified)

    def test_a_plus_f_exact_retest_is_valid_unranked_grammar_but_not_certified(self) -> None:
        first = hcs_node_from_casino_marker(CasinoVisibleMarker.ATTEMPTED_FU)
        second = hcs_node_from_casino_marker(CasinoVisibleMarker.STRONG_FU)

        result = evaluate_hcs_research_evidence(
            first_node=first,
            second_node=second,
            retest_state=HCSRetestState.EXACT_WICK,
            retest_semantics_certified=True,
        )

        self.assertEqual(result.grammar_result.state, HCSState.CONFIRMED)
        self.assertEqual(result.grammar_result.strength, HCSStrength.UNRANKED)
        self.assertFalse(result.hcs_strategy_certified)

    def test_no_retest_remains_not_hcs_even_with_two_f_markers(self) -> None:
        first = hcs_node_from_casino_marker(CasinoVisibleMarker.STRONG_FU)
        second = hcs_node_from_casino_marker(CasinoVisibleMarker.STRONG_FU)

        result = evaluate_hcs_research_evidence(
            first_node=first,
            second_node=second,
            retest_state=HCSRetestState.NO_RETEST,
            retest_semantics_certified=False,
        )

        self.assertEqual(result.grammar_result.state, HCSState.NOT_HCS)
        self.assertFalse(result.hcs_strategy_certified)

    def test_fully_certified_source_nodes_can_certify_hcs_when_retest_is_certified(self) -> None:
        first = HCSNodeEvidence(
            node_type=HCSNodeType.STRONG_FU,
            source=HCSNodeEvidenceSource.SOURCE_LABELLED,
            source_label="fixture:first",
            visible_marker=None,
            node_label_resolved=True,
            raw_node_semantics_certified=True,
        )
        second = HCSNodeEvidence(
            node_type=HCSNodeType.STRONG_FU,
            source=HCSNodeEvidenceSource.SOURCE_LABELLED,
            source_label="fixture:second",
            visible_marker=None,
            node_label_resolved=True,
            raw_node_semantics_certified=True,
        )

        result = evaluate_hcs_research_evidence(
            first_node=first,
            second_node=second,
            retest_state=HCSRetestState.EXACT_WICK,
            retest_semantics_certified=True,
        )

        self.assertTrue(result.hcs_strategy_certified)


if __name__ == "__main__":
    unittest.main()
