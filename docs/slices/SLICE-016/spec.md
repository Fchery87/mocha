# SLICE-016: native ChatGPT connection and account lifecycle

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M2. Requirements: FR-008, FR-006, FR-007, FR-020, NFR-002, NFR-003, NFR-007, NFR-009. Prerequisites: [004](../SLICE-004/spec.md), [015](../SLICE-015/spec.md).

## User-visible result

An eligible user explicitly signs Mocha into ChatGPT and completes a supported coding-tool turn using that connection. API-key connections remain independently usable and logout/expiry/revocation do not corrupt history or leak tokens.

## Interfaces and behavior

Complete the distinct [official SIWC profile](../../contracts/providers-and-mcp.md#native-chatgpt-sign-in), following feasibility evidence from 004. `mocha login chatgpt`, `mocha logout chatgpt` and the provider picker use the same one-account-per-auth-method lifecycle. OpenAI BYOK and ChatGPT are separate connections, with explicit selection and no silent fallback between allowances.

Use Mocha's issued registration/client ID, stable opaque host identity, PKCE/state/nonce, granted inference checks and temporary 127.0.0.1 callback. Login expires after five minutes or explicit cancellation and closes the listener. A browserless/noninteractive invocation returns an actionable input-required outcome rather than borrowing another client's token/device flow. Token-bearing callback URLs never enter logs or transcripts.

Use the public Responses endpoint, account-specific model list, store:false, stream:true and complete local input history. Do not send unsupported ordinary BYOK fields or hosted tools. Only response.completed is successful inference, even if text already streamed. Cross-process credential generations serialize refresh/logout. Distinguish local credential deletion from confirmed remote revocation. Eligibility/quota/permission/refresh failures keep history intact and require explicit user recovery.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 016-A01 | Real registered eligible inference | Record Mocha registration, selected account/model/profile and successful tool-capable completed response without retaining credentials. |
| 016-A02 | PKCE/state/nonce or callback failure | Reject wrong/missing identity evidence, close listener and retain no plaintext token. |
| 016-A03 | Timeout/cancel/browserless login | Clear actionable outcome, no stale listener or invented fallback auth flow. |
| 016-A04 | Forbidden BYOK request fields | Profile fixtures prove excluded fields are not serialized and required storage/stream settings are set. |
| 016-A05 | Concurrent refresh/logout | Serialized protected generations; logout cannot be undone by an old refresher. |
| 016-A06 | Rotated-token save failure | Uncertain refresh stops reuse of obsolete tokens and asks for reconciliation/sign-in. |
| 016-A07 | Quota/eligibility/error after partial text | Failure remains failure; no false Done or silent BYOK charge. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-016`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

Actual registration/eligibility is a required external gate, not a product choice to defer the feature. If the 004 spike failed, stop this dependent support/release claim until fixed or explicitly rescoped. Real login/inference is a deliberate maintainer action and is not run by CI or by a documentation audit.

## Scope and decision status

No multi-account switching/pools, Claude-plan access, proprietary backend routes, another client's registration reuse, plaintext tokens or undisclosed fallback billing.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
