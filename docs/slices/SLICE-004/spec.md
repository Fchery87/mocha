# SLICE-004: complete provider catalog and four API families

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M1. Requirements: FR-006, FR-007, FR-008, FR-024, NFR-003, NFR-004, NFR-009. Prerequisites: [003](../SLICE-003/spec.md).

## User-visible result

All twelve confirmed providers plus Custom have a guided API-key setup and a supported coding-model path. Users can inspect and explicitly refresh metadata/discovery without a paid inference request or silent model/default change.

## Interfaces and behavior

Complete OpenAI Chat Completions, Responses, and native Gemini Interactions alongside Anthropic. Use the exact [provider matrix and adapter profile](../../contracts/providers-and-mcp.md). `mocha models refresh [provider]` performs explicit catalog/discovery refresh. `mocha providers test <provider>/<model>` is a separate inference action with a charge notice and explicit user invocation. `mocha providers import <path>` validates then previews configuration changes before publishing a user-approved transaction.

Bundle a reviewed models.dev snapshot and provenance/license manifest. Keep unknown account access distinct from listed/discovered/model-tested states. Store per-profile discovery generations, preserve user overrides and last-good snapshots, and do not poll in the background. Custom HTTPS uses one explicitly chosen supported family, named credential source and model metadata. HTTP is limited to explicitly authorized loopback development endpoints.

For each preset, capture exact endpoint/auth/model/capability/request-profile metadata and bounded fixture responses. Owner documentation and fixture compatibility are different from live account access. Enforce per-model API overrides and unsupported capability errors before inference. Separate OpenAI BYOK and SIWC profiles. Start a minimal SIWC registration/eligible-inference feasibility spike here, but never request credentials or run paid calls automatically. Its evidence is a prerequisite for 016, not a substitute for that slice.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 004-A01 | Twelve presets and Custom | Each supports key connection, explicit coding-model selection, text/tool stream fixtures and actionable unsupported states. |
| 004-A02 | Metadata refresh | No inference charge, background poll, override loss, default change or stale-generation overwrite. |
| 004-A03 | API-family fidelity | Fragmented UTF-8/events, interleaved calls, reasoning, images where supported and usage preserve required identities. |
| 004-A04 | Transient failures | At most three bounded pre-output attempts; no automatic retry after semantic output or uncertain effects. |
| 004-A05 | Missing limits/unsupported capability | Interactive input or headless exit 2; no guessed limits or paid-model fallback. |
| 004-A06 | Custom/import endpoint security | Unsafe URL/auth fields rejected, API overrides retained and credential rebinding requires explicit approval. |
| 004-A07 | Provider-specific access notices | Z.ai standard API is distinct from Coding Plan; unverified policy cannot be presented as Mocha approval. |
| 004-A08 | SIWC feasibility | Record registration/eligibility/inference findings or a visible blocked gate, without dropping required M2 scope. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-004`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

003 configuration/credential protection is required. Real tool-call behavior is qualified with 005 and at the M1 gate in 008. A provider is not marked supported on parser fixtures alone. Failure to establish a required preset/model path blocks M1 acceptance. SIWC uses official registration and the separate request profile.

## Scope and decision status

No credential pools, automatic provider/model fallback, Coding Plan preset, Claude-plan login or hosted provider tools. Native Gemini uses Interactions; a second generateContent adapter is not an MVP requirement.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
