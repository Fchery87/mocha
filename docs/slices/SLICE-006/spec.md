# SLICE-006: interjection, queued work and loop control

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M1. Requirements: FR-002, FR-003, FR-022, NFR-002, NFR-005. Prerequisites: [005](../SLICE-005/spec.md).

## User-visible result

Users interrupt, interject, or queue work without reviving cancelled turns or overlapping uncertain mutations. Runs stop with a named operational limit or repeated-work failure instead of looping indefinitely.

## Interfaces and behavior

Extend the already-tested control path from 005 using [runtime semantics](../../contracts/runtime.md). Enter during active work and Tab queue a follow-up at the next safe idle boundary. Ctrl+Enter cancels then submits at the safe boundary; Alt+Enter is its terminal fallback. Queue capacity is 16 messages; overflow preserves composer content. Persist accepted queue/interject text with a stable message ID before acknowledgement. Cancel/activate records are durable; each ID activates at most once, and crash recovery leaves it pending without automatic inference. Esc focus precedence and the two-second Ctrl+C quit hint remain unchanged.

Carry explicit turn state and call identities across cancellation, approvals, queues and final outcomes. A third unchanged identical tool call or second edit/revert cycle triggers one nudge; the next repetition stops with loop_detected. Reflection retry accounting is separate and cannot create authority. Usage totals are informational. Retries/compaction count against provider-step/time limits, and every dispatched tool counts against the call limit.

Interjection cannot bypass pending reconciliation of a possibly still-mutating process or unknown external effect. Safe read-only reconciliation is available without repeating the old command. Each accepted queued follow-up becomes its own turn only when admitted; IDs and prompt acceptance make queued versus started work visible.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 006-A01 | Cancel during provider/tool output | No new dispatch or late-event resurrection; partial observed outcomes retained. |
| 006-A02 | Interject during mutation | New mutation waits for termination/reconciliation; does not race the old process. |
| 006-A03 | Queue sixteen then overflow | Stable order, unique admitted turns and intact overflow composer text. |
| 006-A04 | Limit reached | BudgetExhausted names step/tool/time limit, preserves evidence and exits 4 headless. |
| 006-A05 | High cumulative tokens | No stop solely for aggregate token usage; per-request context/output limits still apply. |
| 006-A06 | Repeated action/edit-revert | One nudge then loop_detected at the documented thresholds. |
| 006-A07 | Key focus conflicts | Overlay/dock owns its keys; cancellation and quit remain available through their documented paths. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-006`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

005 cancellation/termination/limits are prerequisites rather than features introduced here. No operation with unresolved effects can be repeated because a new prompt, model or call ID exists. Missing interactive information cannot hang headless execution.

## Scope and decision status

No daemon, concurrent attached clients, subagents or automatic task resumption. Terminal keyboard delivery limits use documented fallbacks rather than fabricated shortcut support.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
