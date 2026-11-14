# Version-1 boundary definitions

Dated November 14, 2026. These are specified interfaces, not generated artifacts from an implemented application. The initial implementation must match them or make an explicit reviewed schema change before callers depend on the changed form.

## Schema ownership

| Schema | Boundary |
| --- | --- |
| [Protocol](protocol.schema.json) | Engine requests, acceptance/rejection responses and semantic events |
| [Shared payloads](payloads.schema.json) | Exact method/event/log payload definitions referenced by the other schemas |
| [Session records](session.schema.json) | Durable JSONL record envelope and typed payload |
| [User config](user-config.schema.json) | User presentation, new-session defaults and operational limits |
| [Project config](project-config.schema.json) | Trusted presentation and existing registered-model selection only |
| [Models](models.schema.json) | Built-in/custom provider model configuration and legacy import |
| [MCP server config](mcp-config.schema.json) | Trusted stdio/HTTP server definitions without credential values |
| [MCP auth references](mcp-auth.schema.json) | Non-secret resource/issuer-bound credential references and registration state |
| [Core tool arguments](tools.schema.json) | Complete built-in tool calls before registration/dispatch |

All IDs except filesystem paths and provider model IDs are opaque safe strings of at most 80 characters. Newly created session IDs use UUIDv7. An ID is not a path: never concatenate an unvalidated external ID into a store path. JSON Schema validates shape; semantic validation additionally enforces path/origin policy, sizes, exact grants, duplicate identities, record ordering/checksums, image byte/pixel limits and capability availability.

Reject duplicate JSON object keys at the input parser boundary instead of allowing last-key-wins changes to security fields. Saved schema versions and internal protocol versions are separate from MCP revisions. Unknown methods/events and newer saved schema versions fail visibly without guessed execution. Schema IDs under mocha.invalid are identifiers for local resolution, not runtime fetch destinations. Validation resolves all referenced schemas from the bundled registry with no network request.

## Request, response and event meaning

Initialize negotiates version before any other method. Create-session allocates an identity without persistence. Submit and queue/interject acceptance becomes durable before acknowledgement once the M1 store exists. Cancel-turn acceptance means the independently serviced dispatch gate is closed, not that child termination or fsync has completed. Approval responses bind both approval ID and the digest of the exact action; stale mismatched responses cannot authorize a changed action.

Request acceptance/rejection is correlated by request_id. Accepted responses also identify the method and require its session/turn/queue/preview/operation identities or version/list data. Empty submit/create/queue acceptance payloads are invalid. Turn-scoped log records require outer turn_id. Event sequence is session-local and increasing. Durable sequence identifies the highest successfully persisted boundary, or null for the M0 ephemeral path. It does not claim client delivery. Exactly one turn_finished follows an accepted turn unless the process is abruptly killed before delivery. Generated and persisted final outcomes are distinct from a successfully delivered event.

Queued/interjected text has a stable queued_message_id. Persist queue_added before accepting it, queue_cancelled before durable cancellation acknowledgement, and queue_activated plus its turn identity before activation. Recovery exposes pending items and requires deliberate continuation. It cannot activate the same queued message twice. Recheck mode, instructions, grants, limits and unresolved effects at activation. Changing a mode does not grant old queued actions new authority.

Provider/account setup, configuration previews, trust management and doctor are host-service operations with their validated configuration schemas. TUI and CLI call the same services; they do not call engine internals. A change to the active model/mode, a user tool decision, queued work or rewind crosses the engine protocol using its schema-defined method. Additions to a stable public method/event require updated schemas, fixtures and client compatibility tests before use.

## Record serialization and checksum

Each log line is a UTF-8 JSON object followed by LF, with checksum serialized last. The CRC32C input is the exact byte prefix before the final `,"checksum":` member separator. It excludes that separator, the checksum member, closing brace and line ending. Store the lowercase eight-hex-digit checksum. This detects accidental corruption, not malicious tampering or authenticity. Reordering or reformatting log bytes requires recomputing the checksum; do not normalize an existing log before validation.

The [JSONL header fixture](fixtures/session.valid.jsonl) has an actual checked CRC32C. The JSON arrays in the shape fixtures test decoded message schemas; they are not on-disk log byte streams. CRC32C uses the standard Castagnoli polynomial and the known 123456789 check value e3069283. Implemented writers must round-trip fixtures, detect torn lines, distinguish early corruption and never acknowledge a failed sync.

## Tool observations and results

The read result includes an opaque observation ID, resolved path, file identity/hash, observed spans, absence flag and redacted ranges. A redacted placeholder is not an observation of original bytes. Whole-file overwrite/delete/replace_all based on a redacted full-file view is refused; a targeted edit may preserve untouched redacted bytes only when exact original spans and identity are still verifiable. Never substitute placeholder bytes into the file or treat a preview as a complete read.

Tool results use the shared tool_result payload, with actual status, evidence identity, changed/pending paths where relevant and recovery_coverage. In M1 recovery_coverage is none until real checkpoints exist. Explicitly approved M1 changes may proceed without rewind, but cannot claim Tier-1 checkpoint protection. Actions requiring protected recovery refuse until that subsystem passes. Empty output is distinct from missing evidence or truncated capture.

Core tool argument schemas define the wire shape; the parser validates each path and current observation in addition. Apply-patch accepts a textual patch plus a path-to-observation-ID map. Every existing affected path requires appropriate coverage; each create target requires an observed-absent target. The patch grammar is unified hunks with explicit create/update/delete paths; unsupported rename/mode/binary forms fail without mutation. Rename may be expressed as independently validated delete/create in a staged patch. Patch previews never authorize an action.

Run `python3 scripts/check_boundary_schemas.py --self-test` in an environment with jsonschema installed to validate local schemas, positive fixtures, invalid inputs and the actual log checksum. These checks prove schema/fixture consistency only, not an implementation.


## Durable taint observations

Record taint_changed when untrusted project guidance, file content, tool/MCP output or imported history enters the model view. Include provenance kind/ref and a content hash where available. A true taint transition is persisted before the content can influence another authorized request/action. Before the first accepted prompt, startup may hold a pending observation in memory without writing; persist it with first-prompt initialization before provider use. Replayed taint is monotonic for that session and cannot be cleared by model text, mode changes, compaction or any rewind scope.

Older/imported history without complete provenance is conservatively tainted. Absence of an explicit old taint record cannot prove history clean. Tool-result-derived provenance remains useful but cannot substitute for recording instruction/file observations that occur before any tool result.
