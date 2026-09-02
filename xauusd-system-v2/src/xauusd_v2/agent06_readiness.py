from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .blind_validation_packet import BlindValidationPacket
from .primary_context_bundle import FileSystemPrimaryContextBundleResolver


_IMAGE_LOCATOR_MARKERS = ("#image:", "#visual:", "#embedded:")


def locator_requires_primary_image(source_locator: str) -> bool:
    value = source_locator.strip().lower()
    return any(marker in value for marker in _IMAGE_LOCATOR_MARKERS)


@dataclass(frozen=True, slots=True)
class Agent06ReadinessReport:
    total_cases: int
    unique_locators: int
    resolved_cases: int
    missing_locators: tuple[str, ...]
    invalid_context_locators: tuple[str, ...]
    image_required_cases: int
    image_missing_locators: tuple[str, ...]
    provider_configured: bool
    model_configured: bool
    multimodal_supported: bool
    ready_to_run: bool

    @property
    def blockers(self) -> tuple[str, ...]:
        items: list[str] = []
        if self.missing_locators:
            items.append(f"missing primary bundle locators: {len(self.missing_locators)}")
        if self.invalid_context_locators:
            items.append(f"invalid/unreadable primary contexts: {len(self.invalid_context_locators)}")
        if self.image_missing_locators:
            items.append(f"chart locators without primary images: {len(self.image_missing_locators)}")
        if not self.provider_configured:
            items.append("model provider metadata is missing")
        if not self.model_configured:
            items.append("model name metadata is missing")
        if not self.multimodal_supported and self.image_required_cases:
            items.append("configured model client is not multimodal-capable")
        return tuple(items)


def assess_agent06_readiness(
    *,
    packet: BlindValidationPacket,
    resolver: FileSystemPrimaryContextBundleResolver,
    model_client: Any,
    model_provider: str,
    model_name: str,
) -> Agent06ReadinessReport:
    if not packet.cases:
        raise ValueError("blind packet must contain cases")

    provider_configured = bool(model_provider.strip())
    model_configured = bool(model_name.strip())
    multimodal_supported = callable(getattr(model_client, "generate_json_multimodal", None))

    missing: list[str] = []
    invalid: list[str] = []
    image_missing: list[str] = []
    resolved_cases = 0
    image_required_cases = 0

    entries = resolver.entries
    for case in packet.cases:
        locator = case.source_locator
        if locator not in entries:
            missing.append(locator)
            continue
        try:
            payload = resolver.resolve_payload(locator)
        except (FileNotFoundError, LookupError, UnicodeDecodeError, ValueError, OSError):
            invalid.append(locator)
            continue

        requires_image = locator_requires_primary_image(locator)
        if requires_image:
            image_required_cases += 1
            if not payload.images:
                image_missing.append(locator)
                continue
        resolved_cases += 1

    missing_tuple = tuple(sorted(set(missing)))
    invalid_tuple = tuple(sorted(set(invalid)))
    image_missing_tuple = tuple(sorted(set(image_missing)))
    ready = (
        resolved_cases == len(packet.cases)
        and not missing_tuple
        and not invalid_tuple
        and not image_missing_tuple
        and provider_configured
        and model_configured
        and (multimodal_supported or image_required_cases == 0)
    )
    return Agent06ReadinessReport(
        total_cases=len(packet.cases),
        unique_locators=len({case.source_locator for case in packet.cases}),
        resolved_cases=resolved_cases,
        missing_locators=missing_tuple,
        invalid_context_locators=invalid_tuple,
        image_required_cases=image_required_cases,
        image_missing_locators=image_missing_tuple,
        provider_configured=provider_configured,
        model_configured=model_configured,
        multimodal_supported=multimodal_supported,
        ready_to_run=ready,
    )
