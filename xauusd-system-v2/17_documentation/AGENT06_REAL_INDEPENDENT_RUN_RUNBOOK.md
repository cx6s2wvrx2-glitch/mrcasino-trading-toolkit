# XAUUSD V2 — Agent-06 Real Independent Run Runbook

Updated: 2026-09-02
Scope: XAUUSD V2 only
Branch: `xauusd-v2-foundation`

## Purpose

This runbook is the controlled path for the first real external multimodal Agent-06 blind validation run.

It does **not** certify strategy profitability, does **not** promote any rule to VERIFIED, and does **not** authorize live execution.

The critical separation is:

`ground truth -> answer-free packet build` **before provider process**

then

`answer-free packet + original primary source evidence -> independent model predictions`

then, only after that process completes:

`frozen blind predictions -> deterministic ground-truth comparison`

The blind-run process itself never loads ground-truth dataset files and never performs comparison.

## Recommended one-command local path

The preferred first-run path is now the tested local orchestrator:

```bash
xauusd-v2-agent06-local \
  --bundle "/absolute/path/xauusd_agent06_primary_bundle_2026_09_02.zip" \
  --model claude-sonnet-5
```

Run it from the repository root after:

```bash
git checkout xauusd-v2-foundation
git pull
python3 -m pip install -e ./xauusd-system-v2
```

The local orchestrator performs the complete controlled sequence automatically:
1. verifies the canonical private ZIP SHA-256;
2. refuses to run if the private ZIP is inside the public Git repository;
3. refuses a private work directory inside the public repository;
4. safely extracts the ZIP and rejects traversal/symlink entries;
5. verifies the primary-context manifest SHA-256;
6. builds the frozen answer-free packet with Anthropic secrets stripped from that subprocess environment;
7. obtains the API key from an existing `ANTHROPIC_API_KEY` environment variable or, if absent, prompts for it with hidden terminal input;
8. exposes the key/model only to the blind-provider subprocess;
9. executes the 173-case isolated blind run;
10. freezes and hashes predictions/runtime manifest before comparison;
11. removes Anthropic secret/model environment variables before the comparison subprocess;
12. performs deterministic post-run comparison separately;
13. writes audit outputs under a private work root, default `~/.xauusd-agent06`;
14. deletes temporary extracted source staging when the command exits.

The API key is never written to disk by the orchestrator. The command still makes real paid Anthropic API calls and therefore requires an active Anthropic API account/credits.

The manual staged procedure below remains the audit/reference path and can be used to diagnose any fail-closed stop.

## Required private inputs

1. XAUUSD V2 repository at the exact tested branch/commit.
2. Private Agent-06 evidence bundle, kept outside the public repository:
   - Library canonical copy: `/XAUUSD V2/Agent06/xauusd_agent06_primary_bundle_2026_09_02.zip`
   - expected ZIP SHA-256: `6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf`
   - expected `primary_context_bundle.json` SHA-256: `e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37`
3. A real Anthropic API credential supplied only through a secure environment/secret mechanism.
4. Explicit model metadata. Selected model for the first run as of 2026-09-02: `claude-sonnet-5`.

Re-check official Anthropic model status immediately before the real paid run. Do not silently substitute another model.

## Secret handling

Never:
- commit the API key;
- paste the API key into GitHub files, command arguments, blind packets, manifests, Supabase rows, logs, or documentation;
- upload the private source bundle into the public GitHub repository;
- expose the key in Agent-06 output artifacts.

Required environment variables for the Anthropic wrapper when using the manual staged path:

```bash
export ANTHROPIC_API_KEY='set-securely-outside-repo'
export XAUUSD_AGENT06_ANTHROPIC_MODEL='claude-sonnet-5'
```

Prefer a local secret manager or the one-command runner's hidden prompt rather than persisting the secret in shell history.

## 0. Pin and verify the repository checkpoint

Before the real run, verify the checked-out branch and commit against the latest green XAUUSD V2 CI checkpoint documented in `CURRENT_PROJECT_HANDOFF.md`.

Install the package from the checked-out XAUUSD V2 project:

```bash
python3 -m pip install -e ./xauusd-system-v2
```

## 1. Verify the private evidence bundle

Example:

```bash
shasum -a 256 xauusd_agent06_primary_bundle_2026_09_02.zip
```

Expected:

```text
6d3dea44ab528c240b05458628c93e38e8582a53d356bb5414aad4730aab9daf
```

Extract it into a private directory that is **not** inside the public Git repository.

Example layout:

```text
/private/xauusd-agent06/evidence/
  primary_context_bundle.json
  ...source assets...
```

Verify the manifest hash too:

```bash
shasum -a 256 /private/xauusd-agent06/evidence/primary_context_bundle.json
```

Expected:

```text
e73568e4af896c4e4ffcb9bee7cbd694902d706003e2e594babeaa5faa422a37
```

Any hash mismatch = STOP. Do not run the model.

## 2. Build the frozen answer-free blind packet

This is the only pre-provider step that reads the canonical ground-truth datasets. Its output schema can contain only:
- dataset name;
- batch-wide taxonomy;
- vector ID;
- source locator.

It recursively rejects expected labels/classes/evidence/forbidden-inference/promotion fields.

```bash
mkdir -p /private/xauusd-agent06/run-input

xauusd-v2-agent06-packet \
  --datasets-dir ./xauusd-system-v2/15_tests \
  --output /private/xauusd-agent06/run-input/blind_packet.json
```

Record the printed `packet_sha256` before any provider call.

After this point, the external-model process must use the frozen packet file. Do not rebuild or mutate it mid-run.

## 3. Optional preflight readiness

A readiness preflight can be run before spending provider tokens:

```bash
xauusd-v2-agent06-readiness \
  --bundle-root /private/xauusd-agent06/evidence \
  --manifest /private/xauusd-agent06/evidence/primary_context_bundle.json \
  --datasets-dir ./xauusd-system-v2/15_tests \
  --provider anthropic \
  --model claude-sonnet-5 \
  --command xauusd-v2-anthropic-runner
```

Expected status before proceeding:

```text
READY_TO_RUN
```

Any missing/invalid locator, missing required primary image, missing provider/model metadata, or lack of multimodal capability = STOP.

This preflight does not call the provider.

## 4. Execute the isolated blind run

Create a unique run ID. Do not reuse an output directory from any previous attempt.

Example:

```bash
RUN_ID="agent06-anthropic-sonnet5-$(date -u +%Y%m%dT%H%M%SZ)"

xauusd-v2-agent06-run \
  --packet /private/xauusd-agent06/run-input/blind_packet.json \
  --bundle-root /private/xauusd-agent06/evidence \
  --manifest /private/xauusd-agent06/evidence/primary_context_bundle.json \
  --provider anthropic \
  --model claude-sonnet-5 \
  --run-id "$RUN_ID" \
  --output-dir "/private/xauusd-agent06/runs/$RUN_ID" \
  --command xauusd-v2-anthropic-runner
```

The command performs readiness again before the first provider call.

The blind-run process reads:
- frozen answer-free packet;
- original primary source text/images through the private bundle;
- provider/model metadata;
- provider secret from environment only.

It does **not** load `ground_truth_round_*.json` and does **not** compare predictions.

Successful blind output contains:
- `agent06_blind_predictions.json`
- `agent06_runtime_manifest.json`
- `agent06_readiness.json`

The runtime manifest records source text/image hashes and predictions/abstentions, not local image paths or ground-truth answers.

If the provider call fails, output is incomplete, image bytes mutate, context changes inside the run, structured output is invalid, or the output directory already exists: fail closed. Do not fill missing predictions manually.

## 5. Freeze the blind outputs before comparison

Immediately hash the completed blind outputs.

Example:

```bash
shasum -a 256 "/private/xauusd-agent06/runs/$RUN_ID/agent06_blind_predictions.json"
shasum -a 256 "/private/xauusd-agent06/runs/$RUN_ID/agent06_runtime_manifest.json"
```

Do not edit model predictions after this point.

## 6. Only now perform deterministic ground-truth comparison

This is a separate process that is allowed to load canonical ground truth **after** blind predictions are frozen.

```bash
xauusd-v2-agent06-compare \
  --packet /private/xauusd-agent06/run-input/blind_packet.json \
  --predictions "/private/xauusd-agent06/runs/$RUN_ID/agent06_blind_predictions.json" \
  --datasets-dir ./xauusd-system-v2/15_tests \
  --output "/private/xauusd-agent06/runs/$RUN_ID/agent06_comparison.json"
```

The comparator verifies:
- blind-packet fingerprint;
- exact vector-ID set;
- exact source locator per vector;
- prediction labels stay inside the frozen packet taxonomy;
- no silent dropping of missing predictions.

Outcomes:
- AGREE
- DISAGREE
- AMBIGUOUS

Abstention/missing prediction becomes AMBIGUOUS. It must never be silently rewritten as the formalizer answer.

## 7. Persist only truthful run metadata

Only after an actual provider run has completed may the system log an independent Agent-06 run in project metadata/database.

Persist:
- real run ID;
- provider and exact model;
- repository commit;
- blind packet SHA-256;
- private bundle ZIP/manifest SHA-256 identifiers;
- prediction file SHA-256;
- runtime manifest SHA-256;
- comparison counts;
- abstention/disagreement counts;
- timestamps;
- `promotion_allowed=false`.

Never persist the API secret.

Do not mark knowledge/rules VERIFIED merely because the model agrees.

## 8. Interpretation boundary

Even a hypothetical 173/173 blind agreement means only that the independent model functionally reproduced the canonical labelled corpus under the supplied evidence and taxonomy.

It does **not** establish:
- profitability;
- robustness;
- broker invariance;
- historical reproducibility;
- live readiness;
- production risk policy.

Those require the separate historical/research certification pipeline.

## Current first-run model

Selected for first independent run:

```text
provider: anthropic
model: claude-sonnet-5
```

This is explicit runtime metadata, not strategy truth. If the model is unavailable or retired, STOP and record a deliberate new model-selection decision before running anything else.
