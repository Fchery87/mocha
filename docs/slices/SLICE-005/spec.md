# SLICE-005: contained tools with evidence and minimum loop guards

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M1. Requirements: FR-002, FR-003, FR-004, FR-005, FR-011, FR-012, FR-013, FR-020, NFR-001, NFR-002, NFR-005, NFR-009. Prerequisites: [002](../SLICE-002/spec.md), [003](../SLICE-003/spec.md), [004](../SLICE-004/spec.md).

## User-visible result

A user authorizes a scoped workspace edit and verification command in either client. Mocha performs real effects only after policy, containment, cancellation, persistence and lifetime checks pass, and records independently observed results.

## Interfaces and behavior

The [tools/policy contract](../../contracts/tools-and-policy.md) governs built-ins, read ledger, path/link behavior, mutation coordination, output and grants. Before the first real command, establish independent cancellation/dispatch closure, the 30-minute turn deadline, 50 provider-step and 200 tool-call limits, 120-second command timeout, two-second SIGINT escalation, descendant control, credential isolation, bounded output/spill and durable intent/result recording. There is no cumulative token cap.

M1 requires interactive action approval or explicit user-scoped flags. `--allow-writes` covers built-in workspace edits only. `--allow-command <exact-command>` binds command/cwd and never adds network permission. Repository config cannot supply either grant. Keep project executable config/MCP disabled. File tools use current full/span observations and atomic per-file publication; patches validate/stage all targets first and report partial publication exactly.

The native tools are read, write, edit, apply_patch, grep, glob, ls, bash, todo and interactive ask_user. Publish their versioned argument/result schemas with positive/negative fixtures as part of this slice before registering them for model use. Background commands remain engine-owned and terminated on cancellation/shutdown. Output spill and minimal instruction/taint boundaries required for safe use land here; richer context handling arrives in 007/013. M1 mutations have explicit approval and no claim of M2 rewind; a policy action requiring a checkpoint is refused until coverage exists.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 005-A01 | No enforcement/no dispatch | Unavailable filesystem/network/lifetime containment fails closed before any child starts. |
| 005-A02 | Read-before-write | Partial/stale/ambiguous edits, unexpected creation, symlink and hard-link mutations do not overwrite data. |
| 005-A03 | Multi-file patch failure | Second-file failure reports exact changed/failed/pending paths; no false overall success or blind rollback. |
| 005-A04 | Crash before/after effect | Durable intent precedes effect; a missing durable result becomes unknown and never auto-repeats. |
| 005-A05 | Cancellation and process escape | Dispatch closes promptly, all controlled descendants stop, no overlapping mutation resumes early. |
| 005-A06 | Output/storage exhaustion | Bounded display and redacted spill; ENOSPC/EIO stops unsafe continuation without silently pruning evidence. |
| 005-A07 | Approval/headless denial | Exact grants work within scope; missing approval exits 3; repository text cannot authorize actions. |
| 005-A08 | Tool/overhead evidence | Real command exit/output/hash and mutation results are captured; read and mutation overhead include safety/persistence costs. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-005`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

002–004 must provide persistence, configuration, redaction and adapters. Do not defer minimum limits or output handling to 006/007. Checkpoint-dependent automatic recovery remains unavailable until 011. Shell parsing alone is not containment or proof of script effects. All real enforcement failure cases must pass before real-provider tool use.

## Scope and decision status

No full permission modes, repo MCP/trust execution, checkpoint restore, arbitrary shell grants, unrestricted networking, or background processes surviving engine shutdown. The basic read-only instruction boundary exists now even though contextual instruction discovery is expanded in 007.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
