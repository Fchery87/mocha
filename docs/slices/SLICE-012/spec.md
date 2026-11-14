# SLICE-012: complete Linux execution and descendant coverage

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M2. Requirements: FR-012, FR-004, FR-021, NFR-001, NFR-005, NFR-006, NFR-009. Prerequisites: [011](../SLICE-011/spec.md).

## User-visible result

The complete shell/local-server/background lifecycle enforces the declared filesystem, network and credential boundary, and doctor explains unsupported profiles without offering an unsandboxed retry.

## Interfaces and behavior

Extend the already-required M1 containment, never replace it with a late first sandbox. The [coverage matrix](../../contracts/tools-and-policy.md#execution-coverage) distinguishes built-in files, shell descendants, local MCP, host provider/auth HTTP and remote MCP. Inspect actual enforcement capabilities, not just kernel version or outer tool sandbox settings.

Close inherited non-stdio descriptors, reject external Unix services and unwanted UDP/Internet sockets in the network-off profile, sanitize child environment and deny private credential/state paths. Preserve only explicitly declared stdio/scratch/runtime resources. Authorize broader outbound capability only through a scoped user grant whose preview states arbitrary destinations may be reachable. Do not present a hostname string as enforced egress filtering.

Verify controlled descendants, process-group escape attempts, background jobs, cancellation, shutdown and local-server startup. The actual profile must prevent unsupported escape or preserve lifecycle control; process-group signalling alone is insufficient. Model tools cannot request a weaker fallback on an unsupported host. Doctor reports each probed capability and coverage category as supported, unsupported or unverified.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 012-A01 | Inside/outside write attempts | Allowed workspace/scratch behavior and denied escape are observed through real child execution. |
| 012-A02 | Inherited socket/Unix/UDP escape | No unintended network path survives the network-off profile. |
| 012-A03 | Explicit network grant | Only the named action/profile gets capability; unrelated commands remain off and preview is truthful. |
| 012-A04 | Credential environment and path probe | Known provider/login credentials cannot be inherited/read by default. |
| 012-A05 | Descendant/background escape or shutdown | No uncontrolled live mutator remains; unsupported containment refuses dispatch. |
| 012-A06 | Unavailable kernel/filesystem/backend | Doctor diagnoses and required execution fails closed; no unsandboxed retry. |
| 012-A07 | Host HTTP versus tools | Provider/login requests work through their own scoped resolver, not a blanket tool grant. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-012`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

011 completes checkpoint-required mutation behavior; 005 enforcement remains a prerequisite throughout. Local MCP lifecycle fixtures may use a harmless test child here, but complete protocol support belongs to 014. Confirm both release architectures' containment behavior before their release claims.

## Scope and decision status

No destination-only egress proxy, payload inspection guarantee, remote-service OS containment, macOS/Windows backend, or automatic privilege escalation to make probes pass.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
