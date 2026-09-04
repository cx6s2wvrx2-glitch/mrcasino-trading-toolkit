from __future__ import annotations

from collections import Counter
from typing import Any


_KIND_LABELS = {
    "strong_fu": "Strong FU",
    "attempted_fu": "Attempted FU",
    "beta_hcs": "BETA HCS",
    "source_hcs_proxy": "HCS",
    "hcs_retest": "HCS retest",
    "beta_negation": "BETA negation",
    "fu_negation_proxy": "FU Negation",
    "hcs_plus_negation_proxy": "HCS + Negation",
}

_DIRECTION_LABELS = {
    "bullish": "bullish",
    "bearish": "bearish",
}


def build_greek_human_review(report: dict[str, Any], *, compound_limit: int = 12) -> str:
    """Build a compact Greek review from a verified indicator-history report.

    This formatter deliberately keeps implementation evidence and source-marker
    research proxies separate. It is intended as the textual backbone for the final
    user-facing validation artifact, not as a strategy-certification surface.
    """

    if compound_limit < 0:
        raise ValueError("compound_limit must be non-negative")

    events = tuple(report.get("events", ()))
    source_hcs = tuple(report.get("source_hcs_marker_proxy_candidates", ()))
    negations = tuple(report.get("source_marker_fu_negation_proxy_candidates", ()))
    hcs_negations = tuple(report.get("source_hcs_plus_negation_proxy_candidates", ()))
    analysis_frames = tuple(report.get("analysis_event_stream_frames", ()))
    comparison = report.get("hcs_implementation_vs_source_marker_proxy", {}) or {}

    strong = Counter(
        item.get("direction")
        for item in events
        if item.get("kind") == "strong_fu"
    )
    attempted = Counter(
        item.get("direction")
        for item in events
        if item.get("kind") == "attempted_fu"
    )
    hcs_forms = Counter(item.get("form") for item in source_hcs)
    hcs_relation = Counter(
        "ίδια κατεύθυνση" if item.get("same_direction") else "αντίθετη κατεύθυνση"
        for item in source_hcs
    )

    lines: list[str] = [
        "# XAUUSD V2 — Ανθρώπινη ανάγνωση replay",
        "",
        "## 1. Τι δεδομένα κοιτάμε",
        f"- Broker / feed έρευνας: {report.get('broker_name')} — {report.get('broker_symbol')}",
        f"- Timeframe: {report.get('timeframe')}",
        f"- Παράθυρο: {report.get('window_start_utc')} → {report.get('window_end_utc')}",
        f"- Canonical FOREXCOM alignment ολοκληρωμένο: {bool(report.get('reference_feed_alignment_complete'))}",
        "",
        "## 2. Τι αναγνώρισε ο supplied Casino helper",
        f"- Strong FU bullish: {strong.get('bullish', 0)}",
        f"- Strong FU bearish: {strong.get('bearish', 0)}",
        f"- Attempted FU bullish: {attempted.get('bullish', 0)}",
        f"- Attempted FU bearish: {attempted.get('bearish', 0)}",
        "",
        "Ορατό legend που έχει κλειδωθεί:",
        "- έντονο πράσινο = Strong FU bullish",
        "- θολό πράσινο = Attempted FU bullish",
        "- έντονο κόκκινο = Strong FU bearish",
        "- θολό κόκκινο = Attempted FU bearish",
        "",
        "## 3. HCS",
        f"- BETA HCS bars: {comparison.get('beta_hcs_event_bar_count', 0)}",
        f"- Source-style HCS candidate bars: {comparison.get('source_marker_proxy_bar_count', len(source_hcs))}",
        f"- Κοινά bars: {comparison.get('overlap_bar_count', 0)}",
        f"- BETA-only bars: {comparison.get('beta_only_bar_count', 0)}",
        f"- Source-style-only bars: {comparison.get('source_proxy_only_bar_count', 0)}",
        "",
    ]

    if source_hcs:
        lines.append("Source-style HCS ανά μορφή:")
        for form, count in sorted(hcs_forms.items()):
            lines.append(f"- {form}: {count}")
        lines.append("")
        for relation, count in sorted(hcs_relation.items()):
            lines.append(f"- HCS με {relation}: {count}")
        lines.extend(
            (
                "",
                "Σημείωση: BETA HCS και source-style HCS παραμένουν δύο διαφορετικοί μηχανισμοί. ",
                "Η μικρή ή μεγάλη συμφωνία τους είναι diagnostic και όχι απόδειξη ότι ο ένας είναι η στρατηγική.",
                "",
            )
        )

    lines.extend(
        (
            "## 4. Negations",
            f"- FU Negation candidates: {len(negations)}",
            f"- HCS + Negation candidates: {len(hcs_negations)}",
            "",
            "Κανόνας που χρησιμοποιεί το research layer σήμερα:",
            "- η προηγούμενη manipulation μπορεί να είναι Strong ή ATT,",
            "- το ordinary negating candle πρέπει να εμφανίζεται ως αντίθετο Strong/F,",
            "- επιτρέπεται στο +1 ή +2 candle,",
            "- ATT → αντίθετο ATT δεν βαφτίζεται FU Negation.",
            "",
            "## 5. Candles με σύνθετη πληροφορία",
        )
    )

    compounds = [frame for frame in analysis_frames if len(frame.get("events", ())) > 1]
    if not compounds:
        lines.append("- Δεν υπάρχουν σύνθετα unified frames στο συγκεκριμένο παράθυρο.")
    else:
        for frame in compounds[:compound_limit]:
            labels: list[str] = []
            for event in frame.get("events", ()):
                kind = str(event.get("kind"))
                direction = str(event.get("direction"))
                label = _KIND_LABELS.get(kind, kind)
                direction_label = _DIRECTION_LABELS.get(direction, direction)
                candidate = " [candidate]" if event.get("candidate_only") else ""
                labels.append(f"{label} {direction_label}{candidate}")
            lines.append(f"- {frame.get('bar_time_utc')}: " + " + ".join(labels))

    lines.extend(
        (
            "",
            "## 6. Τι σημαίνει αυτό για το project",
            "- Ο analyzer δεν χρειάζεται να ξανα-ανακαλύπτει τα A/F markers από το μηδέν.",
            "- Τα Strong/ATT outputs του supplied helper μπαίνουν ως πρώτης τάξης chart events.",
            "- HCS, FU Negation και HCS + Negation χτίζονται πάνω σε αυτά, με provenance.",
            "- Candidate/source-proxy γεγονός δεν παρουσιάζεται σαν πιστοποιημένη στρατηγική αλήθεια.",
            "",
            "## 7. Τι ΔΕΝ έχει κλείσει",
            "- ακριβής FOREXCOM:XAUUSD reference alignment,",
            "- raw x3 / negation-of-negation grammar,",
            "- True Stop / TFS / πλήρης R-143 ακολουθία,",
            "- performance, risk και live readiness.",
            "",
            "## 8. Κατάσταση",
            "Αυτό το report είναι review/observability artifact. Δεν αποτελεί backtest απόδοσης ή trading certification.",
        )
    )
    return "\n".join(lines)
