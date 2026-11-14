# SLICE-010: project trust and layered configuration

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M2. Requirements: FR-013, FR-020, FR-011, NFR-003, NFR-007, NFR-009. Prerequisites: [009](../SLICE-009/spec.md).

## User-visible result

A user can inspect and trust a workspace's supported project settings. Declining trust keeps user configuration active, and changed executable/resource settings cannot run under stale trust.

## Interfaces and behavior

Use the canonical workspace identity and hashes of `.mocha/config.toml` and `.mcp.json` defined in [trust rules](../../contracts/tools-and-policy.md#trust-and-instructions). `/trust` and `mocha trust <workspace>` show effective paths, changed files and resources, then record the explicit decision. `mocha trust revoke <workspace>` removes future project-resource authority without deleting sessions.

Version-1 project configuration supports UI/model selection from existing registered providers and named MCP server definitions. It cannot supply credentials, rebind endpoints, elevate grants, disable policy, or change the global default. Precedence follows [provider configuration](../../contracts/providers-and-mcp.md#connections-and-model-selection). Unknown project fields, including unsupported presentation extensions, are rejected consistently with the strict project schema. Model metadata extensions retain their separately documented warning behavior. Freeze the supported config/MCP schemas and sanitized fixtures before loading them as active configuration.

Canonicalize identity and bind trust to the exact validated bytes/hashes before use. Reject symlink substitutions and recheck path identity/hash at the active-use boundary so approval cannot authorize different bytes. A changed relevant hash invalidates affected startup/grants and requires renewal. Stop accepting new calls for revoked resources, cancel controlled local processes and record in-flight results/unknown effects. Revocation cannot undo a previously completed remote mutation. No project MCP server starts before both trust and its explicit execution/resource grants exist; real MCP invocation is completed in 014.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 010-A01 | Untrusted or declined project | Instructions remain untrusted guidance; repo config cannot run commands, attach credentials or start MCP. |
| 010-A02 | Changed hash or renamed workspace | No stale trust reuse by path guessing; user sees exact new identity/resource changes. |
| 010-A03 | Credential/endpoint/grant override attempt | Rejected, no key sent and no permission broadened. |
| 010-A04 | Concurrent trust/rule update | Revision conflict, no last-writer-wins authorization merge. |
| 010-A05 | Revocation during work | No new resource dispatch; observed and uncertain in-flight effects reported honestly. |
| 010-A06 | Headless missing trust | Distinct approval-required outcome; no implicit trust or waiting prompt. |
| 010-A07 | Valid presentation/model selection | Layering is deterministic and cannot rewrite explicit user overrides/defaults. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-010`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

009 policy and shared-state storage are required. 014 depends on this trust contract. Project schemas are shipped and tested as part of this slice; informal TOML/JSON parsing alone cannot establish supported security behavior.

## Scope and decision status

No executable hooks, arbitrary project code loading, repository-defined credential bindings, enterprise management, or trust auto-granted because a repository contains instructions.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
