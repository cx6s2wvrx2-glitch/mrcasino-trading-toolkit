from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from xauusd_v2.reproducibility import (
    HistoricalDecisionContext,
    HistoricalEvidence,
    ObservationState,
    assert_no_future_information,
    historical_label_is_reproducible,
)


UTC = timezone.utc


class HistoricalReproducibilityTests(unittest.TestCase):
    def test_future_confirmed_bar_is_rejected(self) -> None:
        decision_at = datetime(2026, 1, 1, 10, 5, tzinfo=UTC)
        evidence = HistoricalEvidence(
            evidence_id="10m_hcs_close",
            observed_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
            known_at=datetime(2026, 1, 1, 10, 10, tzinfo=UTC),
            state=ObservationState.CONFIRMED,
            source_timeframe="10m",
        )
        context = HistoricalDecisionContext(decision_at=decision_at, evidence=(evidence,))

        with self.assertRaises(ValueError):
            assert_no_future_information(context)
        self.assertFalse(
            historical_label_is_reproducible(
                context,
                required_confirmed_ids=("10m_hcs_close",),
            )
        )

    def test_closed_confirmed_bar_is_allowed(self) -> None:
        decision_at = datetime(2026, 1, 1, 10, 10, tzinfo=UTC)
        evidence = HistoricalEvidence(
            evidence_id="10m_hcs_close",
            observed_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
            known_at=decision_at,
            state=ObservationState.CONFIRMED,
            source_timeframe="10m",
        )
        context = HistoricalDecisionContext(decision_at=decision_at, evidence=(evidence,))

        assert_no_future_information(context)
        self.assertTrue(
            historical_label_is_reproducible(
                context,
                required_confirmed_ids=("10m_hcs_close",),
            )
        )

    def test_provisional_state_cannot_satisfy_confirmed_requirement(self) -> None:
        decision_at = datetime(2026, 1, 1, 10, 5, tzinfo=UTC)
        evidence = HistoricalEvidence(
            evidence_id="forming_10m_ts",
            observed_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
            known_at=datetime(2026, 1, 1, 10, 1, tzinfo=UTC),
            state=ObservationState.PROVISIONAL,
            source_timeframe="10m",
        )
        context = HistoricalDecisionContext(decision_at=decision_at, evidence=(evidence,))

        self.assertFalse(
            historical_label_is_reproducible(
                context,
                required_confirmed_ids=("forming_10m_ts",),
            )
        )

    def test_missing_required_evidence_fails_closed(self) -> None:
        decision_at = datetime.now(tz=UTC)
        context = HistoricalDecisionContext(decision_at=decision_at, evidence=())
        self.assertFalse(
            historical_label_is_reproducible(
                context,
                required_confirmed_ids=("required_ts",),
            )
        )


if __name__ == "__main__":
    unittest.main()
