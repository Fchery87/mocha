# SLICE-014: tools-only MCP across explicit protocol profiles

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M2. Requirements: FR-016, FR-011, FR-012, FR-013, FR-015, NFR-002, NFR-005, NFR-006, NFR-009. Prerequisites: [013](../SLICE-013/spec.md).

## User-visible result

Users invoke trusted, explicitly configured MCP tools over stdio or Streamable HTTP with honest capability/version support and the same authorization/evidence semantics as built-ins.

## Interfaces and behavior

Implement exactly the [MCP profile](../../contracts/providers-and-mcp.md#mcp-profile): revisions 2026-07-28 and 2025-11-25, tools only, stdio and Streamable HTTP. Keep current stateless discovery separate from older initialize negotiation. Select a profile from explicit configuration/negotiation; unsupported negotiation is an actionable failure, never guessed compatibility. Preserve server/resource identity in tool names and approvals.

Discovery limits are 100 pages, 10,000 tools and 1 MiB per schema. Defer prompt schema insertion until needed. Cache at most five minutes or the shorter server TTL; profile/endpoint/account/schema changes invalidate affected definitions/grants. Validate every complete invocation against the current schema before durable intent/dispatch. Changed schema after an approval requires reevaluation.

Project servers require trust and separate execution grants. Local server children use complete containment. Remote HTTP credentials bind to the intended resource/origin and never automatically forward across origins. Remote authentication includes both static server-scoped bearer/env references and the [confirmed browser OAuth profile](../../contracts/providers-and-mcp.md#remote-mcp-authentication). Implement resource/issuer discovery, PKCE/state validation, protected refresh/logout and pre-registration/CIMD with DCR compatibility fallback. Use the checked public metadata document and fixed loopback redirect. Headless/Unattended never opens a browser or waits for consent. Successful OAuth never overrides tool authorization. Never advertise unsupported sampling, resources, prompts or elicitation. Transport reconnection cannot repeat an uncertain mutation.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 014-A01 | Two revisions × two transports | Independent fixtures prove lifecycle, discovery, call and result behavior for all advertised combinations. |
| 014-A02 | Pagination/cache/schema changes | Bounded discovery, correct invalidation and no stale-approved-schema invocation. |
| 014-A03 | Unknown effect or changed server identity | Approval required; Unattended/headless stops distinctly without execution. |
| 014-A04 | Local server/resource escape | Actual containment/credential policy applies, not only model tool naming. |
| 014-A05 | Remote credential/auth challenge | Static and OAuth profiles preserve resource/issuer binding. Missing state/PKCE, unsafe redirects, refresh/save/logout races and browserless consent fail actionably without key leakage. |
| 014-A06 | Disconnect after remote effect | Outcome unknown, durable identity retained and no auto replay on reconnection. |
| 014-A07 | Unsupported capabilities/input required | Truthful capability advertisement and typed unsupported response, no hang. |
| 014-A08 | Hostile server content | 013 adversarial cases pass through actual MCP dispatch/effect checks. |
| 014-A09 | CIMD, preregistration and DCR | Published client metadata/registered callbacks match; supported registration paths work without another client identity. |
| 014-A10 | Successful OAuth then forbidden tool | Authentication does not override independent tool approval or absolute deny. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-014`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

Trust and complete containment must exist. Verify selected rmcp APIs against all four version/transport combinations before marking support. An SDK ProtocolVersion constant alone is not conformance evidence. Unsupported or rejected server auth must remain visible rather than silently downgraded to anonymous access. CIMD publication via the selected GitHub Pages project endpoint and actual SDK OAuth support are acceptance gates. Configure Pages only with the required publication authority; verify HTTP 200, application/json, exact client_id/body and no redirects. Preparing the source file is not that proof.

## Scope and decision status

No MCP resources/prompts/sampling/elicitation, legacy HTTP+SSE support, hosted provider MCP tools, arbitrary OAuth token passthrough or background unsolicited browser login. Remote MCP OAuth is confirmed MVP scope, independently of ChatGPT sign-in.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
