from __future__ import annotations

from collections.abc import Iterable

from .phase3_stage_comparison import StageComparisonResult


_STATE_GR = {
    "observed": "ΠΑΡΑΤΗΡΗΘΗΚΕ",
    "missing": "ΛΕΙΠΕΙ",
    "blocked": "ΜΠΛΟΚΑΡΙΣΜΕΝΟ",
}

_STAGE_GR = {
    "hcs_zone_reaction": "HCS zone reaction",
    "tfs_confirmed": "TFS",
    "laol_met": "LAOL met",
    "true_stop_respected": "True Stop respected",
    "ten_min_true_stop_established": "10m True Stop established",
    "targets_and_timing": "Core + Major + LAOL targets / timing",
}


def _state_label(state: object | None) -> str:
    if state is None:
        return "ΔΕΝ ΥΠΑΡΧΕΙ RECORD"
    value = getattr(state, "value", str(state))
    return _STATE_GR.get(value, value)


def render_source_broker_comparison(results: Iterable[StageComparisonResult]) -> str:
    """Render a Greek stage-by-stage source vs broker review.

    A broker price-path observation is shown independently from semantic-stage
    evidence so a matching price can never masquerade as strategy certification.
    """
    lines = [
        "XAUUSD V2 — SOURCE vs BROKER PHASE-3 REVIEW",
        "Broker path ≠ semantic stage ≠ canonical source-feed equivalence",
        "",
    ]

    for result in results:
        stage_label = _STAGE_GR.get(result.stage.value, result.stage.value)
        path = "ΝΑΙ" if result.broker_path_observed is True else "ΟΧΙ" if result.broker_path_observed is False else "ΑΓΝΩΣΤΟ"
        aligned = "ΝΑΙ" if result.reference_feed_aligned else "ΟΧΙ"
        equivalence = "ΝΑΙ" if result.canonical_equivalence_allowed else "ΟΧΙ"

        lines.extend(
            [
                stage_label,
                f"  Πηγή: {_state_label(result.source_state)}",
                f"  Broker semantic: {_state_label(result.broker_semantic_state)}",
                f"  Broker price/path observation: {path}",
                f"  FOREXCOM reference aligned: {aligned}",
                f"  Canonical equivalence allowed: {equivalence}",
                f"  Κατάταξη: {result.comparison_state.value}",
                f"  Γιατί: {result.reason}",
                "",
            ]
        )

    lines.extend(
        [
            "ΣΥΜΠΕΡΑΣΜΑ",
            "Ίδια ή κοντινή τιμή στον broker δεν πιστοποιεί FU/HCS/TFS/True Stop/LAOL.",
            "Canonical equivalence επιτρέπεται μόνο όταν source stage + broker semantic stage είναι observed και το reference feed είναι ρητά aligned.",
            "Performance / promotion / live authority: false.",
        ]
    )
    return "\n".join(lines)
