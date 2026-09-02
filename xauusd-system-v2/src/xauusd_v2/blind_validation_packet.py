from __future__ import annotations

from dataclasses import dataclass

from .validation import GroundTruthDataset


@dataclass(frozen=True, slots=True)
class BlindValidationCase:
    vector_id: str
    source_locator: str


@dataclass(frozen=True, slots=True)
class BlindValidationPacket:
    dataset_name: str
    taxonomy: tuple[str, ...]
    cases: tuple[BlindValidationCase, ...]


def build_blind_packet(dataset: GroundTruthDataset) -> BlindValidationPacket:
    """Create a label-leakage-safe packet for Agent 06.

    Per-case expected labels/classes and analyst-authored evidence summaries are
    intentionally excluded. The independent validator receives only the source
    locator and a multi-option taxonomy shared across the whole batch.
    """
    taxonomy = tuple(sorted({vector.expected_label for vector in dataset.vectors}))
    if len(taxonomy) < 2:
        raise ValueError("blind validation taxonomy must contain at least two possible labels")

    cases = tuple(
        BlindValidationCase(vector_id=vector.id, source_locator=vector.source_locator)
        for vector in dataset.vectors
    )
    return BlindValidationPacket(
        dataset_name=dataset.name,
        taxonomy=taxonomy,
        cases=cases,
    )
