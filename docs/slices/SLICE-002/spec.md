# SLICE-002: headless turns and durable recovery

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M1. Requirements: FR-003, FR-010, FR-022, NFR-001, NFR-002, NFR-003, NFR-005, NFR-007. Prerequisites: [001](../SLICE-001/spec.md).

## User-visible result

`mocha run --mock "prompt"` emits a deterministic final response or protocol JSON. Persisted mock sessions can be listed and reopened without provider calls, tool effects, or automatic continuation. A killed turn is reconstructed with honest interrupted/unknown state.

## Interfaces and behavior

Use protocol v1 and the [runtime contract](../../contracts/runtime.md). `--json` writes exactly one event per stdout line; diagnostics go to stderr. `mocha sessions`, `mocha -c`, and `mocha --resume <id-or-name>` use the canonical workspace session index. Ambiguous names produce `input_required` and list matching opaque IDs, without guessing. Continue-last selects the most recently updated session for that workspace, with ID as stable tie-breaker.

Implement [versioned durable storage and writer ownership](../../contracts/storage-and-context.md#durability). Session IDs are opaque UUIDv7 values, request/turn/call IDs are unique opaque strings, and log sequences increase per session. Persist and sync accepted prompts, dispatch intent, results and final outcomes before durable acknowledgement. Correlate received, delivered and persisted sequences separately. Startup/list/read-only resume do not create a store or rewrite an index. A writer lock is acquired only for a write-capable opened session.

Freeze version-1 record serialization and checksum coverage in checked fixtures before using them for persistence. CRC32C covers the exact serialized byte prefix defined by the boundary contract; checksum is the final member. Unsupported schema versions fail read-only. Preserve originals on migration. Fault injection runs in a disposable store, never the real home directory. All runtime exit codes are tested using mock outcomes; actual tool effects arrive in 005.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 002-A01 | Text and JSON runs | Final text/protocol outcomes and diagnostics are separated; no styling or credentials enter JSON. |
| 002-A02 | Read-only reopen | History reconstructs and no inference, command, cache rewrite or automatic retry occurs. |
| 002-A03 | Crash at durable boundaries | Earlier acknowledged records survive; torn final record is reported; incomplete effects are unknown. |
| 002-A04 | Corruption before final record | Recovery stops with a repair path and original bytes retained. |
| 002-A05 | Concurrent writer | Second writer is rejected; process death releases ownership without repeating unfinished work. |
| 002-A06 | Storage full, EIO, failed migration | No false durable acknowledgement or destructive original rewrite. |
| 002-A07 | 10k-record resume | Usable view meets the declared fixture/hash and calibrated resume budget. |
| 002-A08 | Missing/ambiguous session | Actionable typed rejection and correct nonzero exit; no new paid turn. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-002`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

001 must establish protocol ordering and cancellation. Real tool dispatch remains unavailable. The published v1 record fixture and fault injector are acceptance outputs, not optional future design work. Filesystem sync semantics and stable benchmark metadata must be demonstrated before claiming durable recovery or resume performance.

## Scope and decision status

No real credentials, providers, shell execution, checkpoint restore, cross-session search, or automatic transcript execution. The in-process mock remains visibly identified.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
