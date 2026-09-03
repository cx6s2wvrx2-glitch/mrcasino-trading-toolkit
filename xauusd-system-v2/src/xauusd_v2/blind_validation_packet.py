from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

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
    """Backward-compatible single-dataset blind packet."""
    return build_blind_packet_multi((dataset,), dataset_name=dataset.name)


def build_blind_packet_multi(
    datasets: Iterable[GroundTruthDataset],
    *,
    dataset_name: str = "XAUUSD V2 Blind Validation Multi-Round",
) -> BlindValidationPacket:
    """Create one leakage-safe Agent-06 packet from multiple ground-truth rounds.

    Per-case expected labels/classes, evidence summaries and forbidden-inference notes
    never enter the packet. Expected labels are used only to build one batch-wide
    multi-option taxonomy; they are never associated with a case in Agent-06 input.
    """
    items = tuple(datasets)
    if not items:
        raise ValueError("at least one ground-truth dataset is required")

    vectors = tuple(vector for dataset in items for vector in dataset.vectors)
    if not vectors:
        raise ValueError("ground-truth datasets contain no vectors")

    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    for vector in vectors:
        if vector.id in seen_ids:
            duplicate_ids.add(vector.id)
        seen_ids.add(vector.id)
    if duplicate_ids:
        raise ValueError(f"duplicate vector ids across blind datasets: {sorted(duplicate_ids)!r}")

    taxonomy = tuple(sorted({vector.expected_label for vector in vectors}))
    if len(taxonomy) < 2:
        raise ValueError("blind validation taxonomy must contain at least two possible labels")

    cases = tuple(
        BlindValidationCase(vector_id=vector.id, source_locator=vector.source_locator)
        for vector in vectors
    )
    return BlindValidationPacket(
        dataset_name=dataset_name.strip() or "XAUUSD V2 Blind Validation Multi-Round",
        taxonomy=taxonomy,
        cases=cases,
    )
