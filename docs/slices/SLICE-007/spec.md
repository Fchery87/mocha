# SLICE-007: scoped instructions, compaction and bounded context

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M1. Requirements: FR-009, FR-017, FR-007, NFR-002, NFR-005, NFR-007, NFR-009. Prerequisites: [006](../SLICE-006/spec.md).

## User-visible result

Mocha applies the correct instruction scope to touched files, compacts long conversations without losing authority/evidence state, and exposes oversized output through bounded redacted references.

## Interfaces and behavior

Use [storage/context rules](../../contracts/storage-and-context.md#context) and [instruction precedence](../../contracts/tools-and-policy.md#trust-and-instructions). Global guidance precedes project guidance; nearest applicable repository scope refines local instructions; explicit user instructions retain priority. AGENTS.md wins over CLAUDE.md at a directory. Limits are 64 KiB per instruction file and 256 KiB combined; report overflow. No imports or executable instruction directives are implied.

Discover nested guidance before each affected operation, reload changed applicable files, and preserve each path's scope in a multi-file batch. Conflicting batch-local guidance remains attached to its path; a single instruction cannot grant broader authority. Required user clarification uses ask_user or input_required headless rather than inventing intent.

Compaction starts at 80% of effective input capacity after output/reasoning reserves. Preserve goals, decisions, touched-file state, active guidance, unresolved calls, grants/taint and evidence references. Keep original history and adapter-owned opaque blocks. Failed compaction leaves history usable. One context-limit compaction retry is allowed within the same turn limits. A smaller-model switch must prepare a compatible view and explain required compaction before its authorized request. Referenced spill data persists under the explicit retention policy.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 007-A01 | Nested changed guidance | Correct AGENTS/CLAUDE fallback and scope are selected for each touched path without executing configuration. |
| 007-A02 | Batch/symlink/oversized guidance | No scope escape; overflow/conflict gives an actionable outcome rather than silent omission. |
| 007-A03 | Compaction handoff | Goals, grants, taint, pending calls and evidence references survive; full history remains available. |
| 007-A04 | Compaction failure or insufficient capacity | Original history retained, typed failure, no endless retry or silent paid-model switch. |
| 007-A05 | Model switch | Foreign signatures never sent; compatible complete tool exchanges retained. |
| 007-A06 | Missing capacity limits | Interactive request or headless exit 2; estimates are labeled and not reported as provider usage. |
| 007-A07 | Oversized or secret-bearing output | Bounded view and redacted spill reference; no known credential persists across chunk boundaries. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-007`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

006 supplies stable turn/budget semantics and 005 already supplies bounded spill for real tools. Provider-specific accounting/serialization must be fixture-tested; 80% is a selected default, not a guarantee that every vendor counts identically. A failed storage/compaction operation blocks dependent dispatch.

## Scope and decision status

No instruction imports, hooks/skills, automatic memory, staged result pruning, hidden fast-model summaries, or arbitrary cross-provider lossless reasoning conversion.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
