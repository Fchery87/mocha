# SLICE-003: provider setup, credentials and Anthropic connection

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M1. Requirements: FR-006, FR-007, FR-020, FR-022, NFR-003, NFR-004, NFR-007, NFR-009. Prerequisites: [002](../SLICE-002/spec.md).

## User-visible result

A user connects Anthropic through protected key entry or an environment reference, chooses a model, and submits a real text turn. The same setup/configuration path supports the full provider catalog added in 004 without manual edits for presets.

## Interfaces and behavior

Use [provider configuration](../../contracts/providers-and-mcp.md#connections-and-model-selection), the checked JSON Schema and 61-entry sanitized import fixture. Commands are `mocha providers`, `mocha providers connect <provider>`, `mocha providers disconnect <provider>`, `mocha models`, `mocha models select <provider>/<model>`, and `mocha models default <provider>/<model>`. TUI first-run selection uses the same validated operations. These command interfaces are planned, not present.

Connections retain one profile per built-in provider/auth method. Entry is masked and never passed in argv, transcripts or logs. Environment references identify variable names, not copies of values. Resolve credentials at the host adapter boundary; redact before all output/persistence sinks. Secret Service failure leaves environment-based BYOK available without a plaintext fallback. Disconnection clears the saved binding/keychain item and invalidates discovery for that profile; it never unsets the user's shell variable. Environment-backed use may remain possible and must be stated honestly.

Implement cross-process configuration transactions and revision conflicts from [shared state](../../contracts/storage-and-context.md#shared-state-across-processes). Validate duplicates, effective per-model API override, endpoint policy and costs/limits in addition to JSON Schema. Never silently reuse credentials for a changed endpoint. Anthropic Messages preserves content/tool/signature identities, uses bounded streaming parsers, and exposes typed auth/transport/refusal outcomes. Before the first inference resolve model limits and validate a compatible fitting context view. Tool definitions may be serialized for fixture coverage but must not be advertised on the text-only live path before 005 can dispatch them. Unexpected tool requests fail with unsupported_tool_execution.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 003-A01 | Fresh setup | Provider picker, protected/environment key source, explicit model selection and optional saved default work without a hand-edited preset. |
| 003-A02 | Sanitized legacy import | All 61 entries load with per-model API overrides; missing limits require input rather than guessed capacity. |
| 003-A03 | Malformed update or newer schema | File/problem reported, last valid state preserved, unsupported migration retains original. |
| 003-A04 | Concurrent default/connection edits | Conflict is explicit; no silent lost update or broadened authorization. |
| 003-A05 | Credential exposure fixture | Known keys absent from TUI, stdout, JSON, logs, spill previews and diagnostics, including split output chunks. |
| 003-A06 | Secret Service unavailable | Environment connection works; protected-entry/login failure is actionable and stores no plaintext key. |
| 003-A07 | Anthropic stream/error cases | Fragmented text/tool payloads and opaque signatures round-trip; partial/invalid arguments never dispatch. |
| 003-A08 | Endpoint change/redirect | Reconnection is required for credential rebinding; a different origin never receives a forwarded key. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-003`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

002 storage/versioning is required. Pin the Secret Service backend and Messages request/event fixtures before adapter implementation. Explicit maintainer use may exercise a paid call; CI uses isolated fixtures only. End-to-end tool execution remains blocked on 005 even if an API stream requests one.

## Scope and decision status

No project config/trust elevation, multi-account pools, automatic key rotation, native subscription login, or other API-family implementation. Catalog identities and account access remain separate states.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
