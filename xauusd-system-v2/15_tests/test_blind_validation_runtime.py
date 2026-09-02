from __future__ import annotations

import dataclasses
import hashlib
import unittest

from xauusd_v2.agents.validation_agent import IndependentValidationAgent
from xauusd_v2.blind_validation_packet import BlindValidationCase, BlindValidationPacket
from xauusd_v2.blind_validation_runtime import blind_packet_sha256, execute_blind_validation_runtime


class RuntimeClient:
    def __init__(self, labels: list[str | None]) -> None:
        self.labels = list(labels)
        self.calls: list[str] = []

    def generate_json(self, *, system: str, user: str) -> dict[str, object]:
        self.calls.append(user)
        label = self.labels.pop(0)
        return {
            "predicted_label": label,
            "confidence": 0.8 if label else 0.0,
            "evidence": ["primary source observation"] if label else [],
            "ambiguities": [] if label else ["insufficient evidence"],
        }


class BlindValidationRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = BlindValidationPacket(
            dataset_name="multi-round",
            taxonomy=("label_a", "label_b", "label_c"),
            cases=(
                BlindValidationCase("V1", "primary#one"),
                BlindValidationCase("V2", "primary#two"),
            ),
        )

    def test_runtime_manifest_is_complete_and_never_promotes(self) -> None:
        client = RuntimeClient(["label_a", None])
        batch, manifest = execute_blind_validation_runtime(
            run_id="run-001",
            model_provider="provider-x",
            model_name="model-y",
            packet=self.packet,
            agent=IndependentValidationAgent(client),
            source_context_resolver=lambda locator: f"PRIMARY CONTEXT {locator}",
        )
        self.assertEqual(batch.predictions, {"V1": "label_a", "V2": None})
        self.assertEqual(manifest.case_count, 2)
        self.assertEqual(manifest.completed_count, 2)
        self.assertEqual(manifest.abstained_count, 1)
        self.assertFalse(manifest.promotion_allowed)
        self.assertEqual(manifest.model_provider, "provider-x")
        self.assertEqual(manifest.model_name, "model-y")

    def test_manifest_contains_context_hash_not_raw_primary_context(self) -> None:
        context = "VERY SENSITIVE PRIMARY SOURCE CONTEXT"
        _, manifest = execute_blind_validation_runtime(
            run_id="run-002",
            model_provider="provider-x",
            model_name="model-y",
            packet=self.packet,
            agent=IndependentValidationAgent(RuntimeClient(["label_a", "label_b"])),
            source_context_resolver=lambda locator: context,
        )
        expected = hashlib.sha256(context.encode("utf-8")).hexdigest()
        self.assertTrue(all(case.source_context_sha256 == expected for case in manifest.cases))
        self.assertNotIn(context, repr(manifest))

    def test_manifest_schema_cannot_store_ground_truth_answer_fields(self) -> None:
        _, manifest = execute_blind_validation_runtime(
            run_id="run-003",
            model_provider="provider-x",
            model_name="model-y",
            packet=self.packet,
            agent=IndependentValidationAgent(RuntimeClient([None, None])),
            source_context_resolver=lambda locator: f"context {locator}",
        )
        manifest_fields = {field.name for field in dataclasses.fields(manifest)}
        case_fields = {field.name for field in dataclasses.fields(manifest.cases[0])}
        for forbidden in ("expected_label", "expected_class", "analyst_evidence", "forbidden_inference"):
            self.assertNotIn(forbidden, manifest_fields)
            self.assertNotIn(forbidden, case_fields)

    def test_packet_fingerprint_is_stable_and_content_sensitive(self) -> None:
        first = blind_packet_sha256(self.packet)
        second = blind_packet_sha256(self.packet)
        changed = BlindValidationPacket(
            dataset_name=self.packet.dataset_name,
            taxonomy=self.packet.taxonomy,
            cases=(BlindValidationCase("V1", "primary#changed"), self.packet.cases[1]),
        )
        self.assertEqual(first, second)
        self.assertNotEqual(first, blind_packet_sha256(changed))

    def test_missing_run_or_model_metadata_fails_closed(self) -> None:
        agent = IndependentValidationAgent(RuntimeClient([None, None]))
        kwargs = dict(
            packet=self.packet,
            agent=agent,
            source_context_resolver=lambda locator: "context",
        )
        with self.assertRaises(ValueError):
            execute_blind_validation_runtime(run_id="", model_provider="p", model_name="m", **kwargs)
        with self.assertRaises(ValueError):
            execute_blind_validation_runtime(run_id="r", model_provider="", model_name="m", **kwargs)
        with self.assertRaises(ValueError):
            execute_blind_validation_runtime(run_id="r", model_provider="p", model_name="", **kwargs)

    def test_context_change_within_same_run_is_rejected(self) -> None:
        packet = BlindValidationPacket(
            dataset_name="duplicate-locator",
            taxonomy=("label_a", "label_b"),
            cases=(BlindValidationCase("V1", "same#locator"), BlindValidationCase("V2", "same#locator")),
        )
        calls = 0

        def changing_resolver(locator: str) -> str:
            nonlocal calls
            calls += 1
            return "first version" if calls == 1 else "changed version"

        with self.assertRaises(ValueError):
            execute_blind_validation_runtime(
                run_id="run-004",
                model_provider="provider-x",
                model_name="model-y",
                packet=packet,
                agent=IndependentValidationAgent(RuntimeClient(["label_a", "label_b"])),
                source_context_resolver=changing_resolver,
            )


if __name__ == "__main__":
    unittest.main()
