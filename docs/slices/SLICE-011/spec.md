# SLICE-011: covered checkpoints, rewind and explicit cleanup

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M2. Requirements: FR-014, FR-010, FR-011, NFR-001, NFR-002, NFR-007, NFR-009. Prerequisites: [010](../SLICE-010/spec.md).

## User-visible result

Authorized covered workspace changes have real recovery points. Users preview and restore code, conversation or both, and preview deletions of retained sessions/evidence without silently losing recovery material.

## Interfaces and behavior

Follow [checkpoint coverage](../../contracts/storage-and-context.md#checkpoints) exactly. Use a private shadow Git repository with explicit path enumeration, disabled hooks/filters/global config, and no modification of the user's refs/index/stash. Include covered tracked/untracked regular files and binaries; exclude ignored/configured-sensitive paths, links, devices and Mocha private state. Scan before staging; exclude the whole file if it contains a known harness credential. Record absent coverage and require uncovered-file approval. Never stage a redacted imitation.

Create the required checkpoint before a protected mutation and record its manifest/path hashes and conversation position. Publish checkpoint references durably before dispatch. `/rewind` and Ctrl+Z show preview and require confirmation. Compare actual current state to the expected post-checkpoint state; external changes require explicit conflict review. Stage all restore targets, publish atomically per file, and record partial restore paths rather than claiming transactionality.

Cleanup interfaces are `mocha sessions delete <id> --preview`, `mocha sessions delete <id> --confirm <preview-id>`, and analogous `mocha checkpoints delete <id>`. A preview binds target identities, references and revisions, expires after ten minutes, and is invalidated by changed references. A shared checkpoint/spill object cannot be deleted while a retained recovery point references it. No automatic pruning or separate plaintext .env backup. Invalidate affected read observations and reload guidance after restore. Taint stays sticky across all rewind scopes. Rerun 009 mode integration tests with real checkpoints before enabling protected automatic mutations. Basic content scanners may reject known credential material but cannot promise detection of every secret.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 011-A01 | Covered mutation | Checkpoint manifest is durable before effect; Auto uses actual coverage, not an optimistic claim. |
| 011-A02 | Ignored/sensitive/link targets | Excluded from snapshots; uncovered edit asks explicitly; absolute credential blocks still win. |
| 011-A03 | Code/conversation/both rewind | Correct preview, original conversation retained, no provider inference or command replay. |
| 011-A04 | External edits or second-file restore failure | Conflict/partial state reported, changed/pending paths recorded, no blind rollback. |
| 011-A05 | Git absent, ENOSPC/EIO or kill during restore | Protected dispatch fails closed or recovery resumes as incomplete, never false complete. |
| 011-A06 | User source Git | Refs/index/stash and normal Git history unchanged by checkpoint machinery. |
| 011-A07 | Explicit cleanup | Revision-bound preview, live reference checks, no automatic deletion or dangling retained evidence. |
| 011-A08 | Mutation performance | Checkpoint/persistence/containment costs included in the actual one-operation overhead measurement. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-011`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

010 trust/policy/storage is required. Git executable and actual filesystem sync behavior must pass the shadow-repo spike. A valid budget miss stops for optimization or explicit review; do not omit checkpoint work from accounting. Full automatic protected execution is accepted only after these cases pass.

## Scope and decision status

No external-service undo, secret-free or encrypted history claim, universal power-loss guarantee, per-hunk undo, or automatic garbage collection deleting retained material.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
