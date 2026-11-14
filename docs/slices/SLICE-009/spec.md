# SLICE-009: permission modes and action review

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M2. Requirements: FR-011, FR-002, FR-003, NFR-005, NFR-006, NFR-009. Prerequisites: [008](../SLICE-008/spec.md).

## User-visible result

Users choose Auto, Approve, Plan or explicitly selected Unattended and receive consistent action decisions in both interfaces. No mode can grant itself authority, bypass hard denies or disguise missing recovery coverage.

## Interfaces and behavior

Implement the exact [mode matrix](../../contracts/tools-and-policy.md#mode-decision-matrix), five tiers, grant scopes, precedence and [44 acceptance examples](../../contracts/fixtures/permission-decisions.json). The fixture is a specification; execute real dispatch tests as well. Auto is the M2 default, Approve confirms mutations, Plan blocks them, and Unattended executes within existing grants without reflection or approval waits.

`--mode` and `/mode` share engine semantics. Shift+Tab cycles Auto → Approve → Plan. Unattended is explicit per run/session and cannot become a saved default. A mode change reevaluates queued actions; switching to Plan closes mutation dispatch and cancels incompatible active work before confirming the completed switch.

Auto reflection is limited to one retry for an unchanged normalized action. Reevaluate scope/path/containment/checkpoint requirements; justification never supplies authority. Unattended stops with approval_required/input_required rather than hanging. Project policy cannot override user/absolute denies. Until 011 provides real checkpoint coverage, checkpoint-dependent automatic mutations return recovery_unavailable before dispatch; mode UI explains this prerequisite. This is a deliberate dependency gate, not a weaker temporary execution path.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 009-A01 | All-mode decision table | Representative grants/denies/read/mutation/unknown-MCP cases match expectations at actual dispatch. |
| 009-A02 | Reflection scope escape or rewording | No new authority, retry reset, unresolved-operation bypass or execution outside coverage. |
| 009-A03 | Unattended missing approval/input | Failed reason, retained prior work, exit 3/2 headless and TUI returns idle without approval wait. |
| 009-A04 | Plan switch during mutation | Dispatch closes, running incompatible work is stopped/reconciled; no false undo claim. |
| 009-A05 | Missing required checkpoint | Automatic protected action refused with recovery_unavailable, even in Unattended. |
| 009-A06 | Hard-deny targets and credential stores | Every mode blocks independently of explicit model justification or broader allow rules. |
| 009-A07 | Mode persistence | Only explicit allowed default changes persist; Unattended never silently becomes the next-session default. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-009`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

008/M1 is required. This slice can qualify policy decisions with checkpoint ports but cannot claim real checkpoint-protected automatic execution until 011 passes. Requested platform containment remains mandatory from 005. No additional provider call is used as a safety-classifier requirement.

## Scope and decision status

No approval-reviewer subagent, model classifier safety guarantee, broader network grant, new subscription scope, or weakening of M1 hard denies. The selected names describe Mocha behavior, not exact aliases for competitors.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
