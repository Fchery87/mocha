# Storage and context contract

Specification dated November 14, 2026. [Recovery decision](../adr/0001-bounded-local-recovery-storage.md) and [replay decision](../adr/0002-separate-replay-from-execution.md) record accepted tradeoffs. No crash test has run against application code.

## Durability

Use versioned JSONL records and a rebuildable project index. Each record has schema version, session ID, increasing sequence, type, payload, and integrity checksum. One process holds an exclusive OS-released writer lock per session. A second writer fails visibly. Startup and unused sessions write nothing. First accepted prompt creates the private session directory and durable header.

Accepted prompts, dispatch intents, tool results, and final outcomes require append and fsync before durable acknowledgement. Sync containing directories when creating or replacing files. Text deltas trigger persistence every 250 ms or 4 KiB, whichever comes first under healthy IO. This bounds batching, not completion time on slow storage. The last successful durable sequence is authoritative. Unflushed streamed text can be lost.

ENOSPC/EIO before intent persistence prevents dispatch. Failure after an effect leaves the operation uncertain if its result cannot be persisted. Show the storage failure and stop protected mutation. A torn final record can be discarded with a recovery notice; corruption in an earlier record stops recovery for explicit repair rather than silently deleting history.

Resume is read-only reconstruction. It performs no provider request, command, or remote mutation until authorized continuation. Intent without durable result is `outcome unknown`. A new call ID does not bypass unresolved-operation review. Read-only reconciliation can establish current state. Retrying an arbitrary uncertain operation requires explicit authorization. Replay never executes tools.

Migrations retain the original, write and validate a new representation, sync it, then publish. Failed or unsupported migrations leave the original intact. No automatic downgrade is promised. Maintain sessions, checkpoints, and referenced spill/evidence until explicit deletion. Cleanup previews affected recovery points and references. Storage pressure warns or stops work rather than silently pruning.

## Shared state across processes

Session writer ownership does not authorize writes to shared configuration or authentication state. Stable lock files live outside replaceable data files. Lock waits are cancellable and default to a two-second acquisition timeout, returning `state_busy` without changing state. Never treat a stale-looking timestamp as proof that a live OS lock may be bypassed.

| Shared object | Required coordination |
| --- | --- |
| Models, defaults, last-good snapshots | Acquire the configuration transaction lock, reread current revision, validate expected revision, stage, sync and publish. A same-field concurrent change returns `state_conflict` with a reload path. |
| Trust and permission rules | Lock and compare expected revision. Never silently merge or broaden authorization changes. |
| Discovery caches | Lock per endpoint/account/auth profile. Publish immutable generations; an older refresh cannot overwrite newer data. |
| Project indexes | Serialize updates or publish generation snapshots. Rebuild from source session records if stale/missing. A stale index cannot hide an otherwise valid session. |
| Login registration, refresh and logout | Cross-process lock per provider/auth profile. Reread current protected credential generation under lock and serialize refresh/logout. Publish tokens and their generation as one protected bundle. |

Independent configuration changes may be reapplied only after rereading and validation. Never resolve authorization or same-field conflicts using last-writer-wins. A multi-file configuration transaction needs a versioned manifest that identifies the complete committed generation; readers reject incomplete generations. Validate and sync staged state before publication. Failures retain the previous usable generation.

Avoid nested shared-object locks. Where a transaction requires more than one, acquire canonical lock identities in lexical order. Do not hold short-lived shared-object locks while acquiring session ownership or waiting for a user/browser. Session ownership is independent of these short-lived transaction locks.

Before refreshing, acquire the auth-profile lock and reread the latest generation. Bound network refresh by its explicit request timeout while holding that lock. A successful remote refresh whose replacement token cannot be saved is uncertain: stop using the obsolete token and require reconciliation or sign-in. Logout publishes an invalidated generation so an old refresh cannot recreate the connection. Non-secret metadata must identify the matching protected generation; a mismatch disables credential use rather than attaching a guessed token.

Backend tests must establish the protected-bundle publication and failure behavior. No plaintext credential journal is permitted. Verify concurrent setup/default edits, authorization conflicts, discovery publication, refresh races, logout races, lock timeout/cancellation, and crashes around publication.

## Checkpoints

A separate private shadow Git repository stores only explicitly covered workspace paths. Never change the user's refs, index, or stash. Disable hooks, global/system Git config, filters, and external helpers. Missing Git or checkpoint failure blocks an operation that requires recovery coverage.

Coverage includes regular tracked and untracked non-ignored workspace files, binary contents, executable bits, creation, deletion, and rename as delete plus create. Ignore ignored files, configured sensitive paths, known Mocha credentials/state, symlinks, hard links, special files, and paths outside the workspace. An edit outside coverage needs approval naming that absence of rewind. Absolute access denies still win.

Recovery storage is private plaintext, with directories 0700 and files 0600. Covered content and history can contain unrecognized secrets. Checkpoint exclusions do not prevent an authorized read from entering model context or history. Never separately back up `.env` plaintext. Do not put known harness credentials into even temporary checkpoint objects.

Before rewind, preview paths and compare current state with the expected post-checkpoint state. External changes require conflict approval. Code-only rewind leaves conversation intact with a rewind event. Conversation-only rewind changes the active conversation view and retains originals. Combined rewind applies both with an explicit result. Validate and stage all restores before per-file publication. Interrupted/partial restore records changed and pending paths and blocks a false complete result. External services cannot be rewound.

## Context

Preserve the original history. Build a provider-specific model view in stable logical order: system constraints, active instructions, structured handoff, then chronological messages and complete tool exchanges. Keep evidence references and permission/taint state outside lossy summaries too.

Default compaction starts at 80% of effective input capacity. Effective capacity is contextWindow minus requested output and adapter-required reasoning reserves. Count tool schemas, images, pending exchanges, and system instructions. Distinguish estimates from reported usage. If no tokenizer exists, use a conservative UTF-8-byte-based estimate and label it. Missing required context/output limits require user input or configuration; headless fails with exit 2.

A compaction handoff preserves goals, decisions, touched files, current guidance, unresolved calls/effects, open tasks, grants, and evidence references. Failure leaves history intact. One safe compaction retry is allowed for a context-limit failure within the same budgets. No permission or taint state resets.

A model switch constructs a compatible view before its first request. Never forward another provider's opaque signatures or reasoning state. Keep those original blocks in history. Explain compaction needed for a smaller model before the authorized continuation incurs inference. Refreshing metadata cannot switch the session or saved default.

Image inputs use `--image <path>` in headless mode and `/attach <path>` in the TUI. Validate file type, size, path policy, and selected model capability. Unsupported image input gives an actionable failure and never silently switches paid models. Terminal image rendering is optional; textual attachment identity remains available.


## Snapshot and rewind integrity

Scan candidate file bytes before Git staging. If a covered file contains a known harness credential, exclude the whole file, record absent coverage and require explicit uncovered-file approval for its mutation. Never store a redacted imitation of the file as a faithful checkpoint, including temporary objects. Unrecognized secrets remain within the accepted private-plaintext boundary. A later discovery does not justify silently deleting retained history; stop new exposure and require explicit cleanup with its reference preview.

After any restore, invalidate affected read observations and reload applicable instruction files. Taint remains sticky across code-only, conversation-only and combined rewind in the same session. Reevaluate pending actions/approvals against restored state and current grants. Conversation rewind cannot erase authority checks or make an uncertain side effect safe to repeat.

Image attachment limits and persistence are specified in [SLICE-015](../slices/SLICE-015/spec.md#interfaces-and-behavior). Those same validation limits apply from the first M1 adapter path that accepts images, rather than deferring basic capability validation to M2 qualification.
