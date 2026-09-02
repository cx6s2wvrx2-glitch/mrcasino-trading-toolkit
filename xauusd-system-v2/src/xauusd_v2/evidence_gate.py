from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EvidenceGateReport:
    """Small provenance-bearing gate for upstream states without a richer report type.

    A positive gate cannot exist as a bare boolean: it must carry at least one
    non-empty evidence reference. This is a transport/provenance contract only;
    it does not create strategy truth or verify the referenced evidence by itself.
    """

    gate_name: str
    passed: bool
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.gate_name.strip():
            raise ValueError("evidence gate name cannot be empty")
        if any(not ref.strip() for ref in self.evidence_refs):
            raise ValueError("evidence gate refs cannot contain empty values")
        if self.passed and not self.evidence_refs:
            raise ValueError("a passed evidence gate requires at least one provenance reference")
