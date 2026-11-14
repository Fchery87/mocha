# SLICE-015: cross-adapter continuation and attachment qualification

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M2. Requirements: FR-007, FR-009, FR-010, FR-011, NFR-002, NFR-005, NFR-009. Prerequisites: [014](../SLICE-014/spec.md).

## User-visible result

Already-implemented M1 adapters remain correct when models switch, context compacts, a tool exchange is interrupted, or the user attaches a supported image. No foreign reasoning state or unreviewed paid-model fallback leaks through.

## Interfaces and behavior

Qualify all four existing families with the provider capability matrix. Preserve original history and use compatible per-adapter views. Same-adapter reasoning/signature continuation round-trips exactly where required; cross-adapter views omit foreign opaque state and keep valid call/result ordering. An incomplete/unknown operation cannot be converted to a fresh call merely to satisfy a different provider schema.

`--image <path>` and `/attach <path>` accept regular PNG, JPEG and WebP files up to 10 MiB each, at most four attachments per submitted message. Enforce stricter provider/model limits where documented; do not silently recompress, crop, send unsupported types or switch models. Validate file signatures and decode dimensions before use, with at most 40 million decoded pixels per image. Reject animated inputs in the MVP. Read path policy and known-credential denies apply. Store a private content-addressed copy only upon authorized submission so resume cannot attach different current bytes under the same identity. Previewing an attachment without submission writes nothing.

Attachment references record media type, byte size, decoded dimensions, content hash and authorization scope. Payload bytes are not dumped in diagnostics/JSON. Native terminal image protocols are optional; textual identity always remains. Missing/corrupt attachment evidence stops a request rather than silently substituting another file.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 015-A01 | Same-family continuation | Opaque signatures/call identities round-trip and complete tool exchanges remain valid. |
| 015-A02 | Cross-family switch | Foreign opaque blocks omitted from the new request but retained in original history. |
| 015-A03 | Smaller model/context error | Explain/perform authorized compatible compaction or fail; no implicit paid fallback. |
| 015-A04 | Unknown tool outcome on switch/resume | No redispatch or invented tool result under a new call ID. |
| 015-A05 | Attachment validation | Unsupported, oversized, animated, corrupt or decompression-heavy images fail before upload. |
| 015-A06 | Changed source after submission | Resumed view uses the recorded authorized content hash/copy, not newly changed bytes. |
| 015-A07 | Unsupported image model | Actionable input/capability failure and no model change or hidden upload. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-015`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

All adapters are already M1 requirements; this is qualification, not deferred implementation. Provider-specific image/context limits and actual account capability remain support gates. Attachment persistence uses existing private-store retention and credential-boundary rules.

## Scope and decision status

No audio/video/PDF, clipboard-binary import, image generation, hosted tools, universal lossless reasoning conversion or default Kitty/Sixel/iTerm2 rendering requirement.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
