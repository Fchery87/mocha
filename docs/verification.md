# Verification plan

Dated November 14, 2026. All application checks below are PLANNED. Documentation checks establish internal consistency only. The maintainer owns acceptance. Keep commands, raw outputs, build revision, environment, timestamps, and failures under each slice's evidence directory when implemented. Never replace actual output with an agent-written success narrative.

## Requirement coverage

Each row identifies required evidence. The first applicable slice establishes the check, and later slices rerun it where behavior changes. P0 release gates remain those in the PRD.

| Requirement | Slice | Required evidence |
| --- | --- | --- |
| FR-001 | 001 | Real PTY mock stream, failure/retry, quit, fallback and terminal restoration |
| FR-002 | 005, 006 | State-machine cancellation races under full buffers, 30-second blocked-delivery interruption, step/tool/time limits, informational token usage without a cumulative cap, model request limits, loops, queues and actual child escalation |
| FR-003 | 002, 005, 006 | Real headless stdout/stderr/JSON and every exit code, unavailable approval/input |
| FR-004 | 005 | Stale/partial reads, path/link races, ambiguous edits, atomic file publication, second-file patch failure |
| FR-005 | 005, 008 | Durable intent/result evidence and independent real verification command |
| FR-006 | 003, 004 | Catalog onboarding, model/default selection, schema/import, last-good/discovery and missing limits |
| FR-007 | 003, 004, 015 | Four adapter families and per-preset text/tool/reasoning/image/error fixtures |
| FR-008 | 004, 016 | Actual Mocha registration, eligible account inference, refresh, logout/revocation and failure cases |
| FR-009 | 007, 015 | Effective capacity, compaction failure, complete exchanges, switch views and opaque-state isolation |
| FR-010 | 002 | Lock contention, read-only resume, crash boundaries and unknown effects without repeat execution |
| FR-011 | 005, 009 | Scoped grants, auto reflection without authority escalation, the four-mode matrix and unattended refusal, explicit-deny priority, headless refusal and hard blocks |
| FR-012 | 005, 012 | Real filesystem/network/descriptor/environment escape attempts and unavailable-profile refusal |
| FR-013 | 005, 010 | Untrusted repo cannot execute config; changed trust hashes require renewed approval |
| FR-014 | 011 | Exact coverage/exclusion matrix, external edits, ENOSPC, partial restore and no source-Git changes |
| FR-015 | 013 | Hostile content exercises actual authorization, secret and outbound boundaries |
| FR-016 | 014 | Both revisions × both transports, static/OAuth discovery/registration/refresh/logout, pagination, cache/schema changes and uncertain remote effects |
| FR-017 | 007 | Global/nested precedence, changes, batch scopes, size and symlink boundaries |
| FR-018 | 008 | Plain TUI PTY, resize, honest progress, color degradation and keyboard cancellation |
| FR-019 | 017, 018 | Scroll anchor, source copy, clipboard fallback, search, rail and keyboard/inline parity |
| FR-020 | 003, 010 | Credential entry/env/keychain, no plaintext fallback, read-only startup and explicit setup writes |
| FR-021 | 008, 019 | Doctor reports actual evidence/capabilities and unavailable checks honestly |
| FR-022 | 001, 002 | Negotiation, correlated event ordering, bounded-channel stress and dependency checks |
| FR-023 | 019 | Both static targets, clean install, checksums/signatures/provenance and protected publication |
| FR-024 | 004 | Dated standard-endpoint notices, no Coding Plan preset or unsupported access claim |
| NFR-001 | 001 onward | Raw reproducible performance results with all safety/storage costs included |
| NFR-002 | 002, 005, 011 | SIGKILL, torn record, ENOSPC/EIO, effect-before-result, migration/restore failure injection |
| NFR-003 | Every slice | Observed outbound destinations match explicit actions; no telemetry |
| NFR-004 | 001, 019 | Actual resolved feature graph, license/advisory/source checks and clean-room review |
| NFR-005 | 008 onward | Deterministic mechanics plus separately graded real edit-test-repair workflows |
| NFR-006 | 013, 014 | Real enforcement adversarial suite including inherited resources and hostile MCP |
| NFR-007 | 002, 003 | Versioned fixtures, retained originals, failed/newer schema migration outcomes |
| NFR-008 | 008, 018 | Keyboard, NO_COLOR, reduced motion, 80×24, missing OSC and terminal restoration |
| NFR-009 | 003 onward | Known secrets absent from config/logs/JSON/spill/checkpoints/child environments, including chunk boundaries |

## Performance protocol

The PRD's numeric budgets remain unchanged. Interpret MB as 1,000,000 bytes. Candidate reference host is the observed Linux Mint 22.2 x86_64 machine, Intel i5-2415M at 2.30 GHz, four logical CPUs, about 15.5 GiB RAM, ext4, kernel 7.0.0-42-generic. Its capability observations are not containment proof. M0 records the actual terminal emulator/version, PTY size, kernel, filesystem/mount options, CPU governor, thermal state, toolchain and selected features in a committed calibration manifest before accepting results. Missing metadata invalidates a run.

Use the release build with declared optimization/LTO settings and the same actual features for comparisons. No provider credentials or paid requests. Warm startup uses 10 warmups and 100 measured launches per batch, three independent batches. Cold launch is reported separately with its method and is never silently substituted for warm results. Measure process launch to the PTY's observable input-ready acknowledgement, not --version.

Use a fixed 100×30 PTY. Measure keypress-to-painted-response p99 over 1,000 injected keystrokes after warmup. Idle RSS includes the in-process engine and provider/config state after 30 seconds idle, sampled for 60 seconds. Report process-tree/child memory separately whenever children exist, without hiding engine allocations. Streaming uses 200 text chunks per second, eight UTF-8 bytes per chunk, for 60 seconds, with a fixed ten-tool-event script. Report CPU time divided by elapsed time as percent of one core. Fix chunk/event payloads in the future benchmark fixture and record their hash.

The resume fixture contains 10,000 versioned records, with 1 KiB text payloads on text records and a declared 10% tool/evidence record mix. Record exact byte size and fixture hash. Resume ends at a usable reconstructed view, without model or tool execution. Startup/resume/tool-overhead budgets use p95 across 100 samples per batch. Binary size is the actual stripped release artifact.

Per-tool overhead is the ready-call-to-durable-result interval minus only intrinsic tool execution and human approval think time. Include policy/path checks, sandbox setup, required checkpoint creation, ledger/evidence work, queue/IPC/serialization, and required file/directory synchronization. Measure separate read and one-operation mutation cases. Do not subtract storage waits or amortize required per-call checkpoints. M0 calibrates instrumentation; these cases become gating when their real subsystems land. The 1 ms target is an unresolved performance risk, not a demonstrated result.

A batch is invalid if setup fails, work is skipped, fixture hashes differ, or competing load/thermal throttling invalidates the declared conditions. Report invalid batches and causes. If valid batch medians differ by more than 10%, investigate and rerun all three batches once under corrected conditions. Continued instability blocks performance acceptance. Do not discard slow samples after observing results. A valid budget miss stops for optimization or explicit budget revision, without weakening safety or durability. Shared-runner CI is functional-only until a stable benchmark runner is calibrated. Never execute untrusted PR code on a privileged maintainer runner.

## Execution evidence

CI uses deterministic mock providers and isolated loopback fixtures with no external route or credentials. Start with focused parser, state, tool and storage cases. Add bounded fuzzing when untrusted parsers land, initially 60 seconds per target in scheduled CI with corpus/seeds and crashing inputs retained. PTY checks drive the actual binary.

Real coding acceptance uses a disposable copy of a fixed task repository. Record task/version, selected model/account profile without credentials, context/tool/time budgets, resulting diff, independent test output, interventions, and outcome. Grade outside the agent-writable environment. A mock stream or model claim cannot certify coding quality. Paid calls require deliberate maintainer execution, never CI credentials.

## Documentation checks

Run `python3 scripts/check_docs.py` from any directory. It checks repository Markdown links and anchors outside historical research, all 33 PRD requirement headings and verification rows, contract presence, and stale decision markers in current specifications. Run its `--self-test` option to prove broken links and missing coverage are detected. These checks cannot certify semantic completeness, external URLs, schema compliance, or runtime behavior.

For full configuration-schema validation, run `uv run --no-project --with jsonschema python scripts/check_model_schema.py` in an isolated environment. The script validates Draft 2020-12, the 61-entry fixture, and rejected invalid API/credential/endpoint/limit/flag cases. A standard Python environment with `jsonschema` installed can also run the script directly. Schema shape checks do not replace loader security/endpoint semantics. The expected missing-limit case loads but cannot start inference until limits are resolved.

[Permission decision fixtures](contracts/fixtures/permission-decisions.json) capture expected mode outcomes. Future SLICE-009 policy tests must consume equivalent independent acceptance cases and exercise real dispatch. Structurally validating these fixture files does not test an implemented engine.

Run `python3 scripts/check_permission_contract.py --self-test` to check canonical mode columns, all-mode acceptance coverage, and selected policy invariants. The self-test deliberately introduces Plan mutation, unattended-wait and missing-scope errors. This validates the written examples, not an executing policy engine.


## Complete slice and interface checks

All 19 local slice specifications are indexed in [the manifest and completion contract](slices/README.md). Run `python3 scripts/check_slices.py --self-test` to verify existence, acyclic dependencies, acceptance-case structure and complete PRD ID coverage. Run `uv run --no-project --with jsonschema python scripts/check_boundary_schemas.py --self-test` for local schemas, positive/invalid messages, CRC32C and prepared OAuth metadata. Both are document/interface consistency checks, not runtime proofs.

Run `python3 scripts/check_acceptance_corpus.py` with an installed rustc to prove the fixed coding graders fail broken/stub candidates and pass reference candidates. This makes the [small coding corpus](fixtures/coding-acceptance.json) a checked acceptance input, not a real-model quality result. The independent runner must keep grading inputs outside the agent-writable workspace and record task/model/budget/intervention/effect evidence.

SLICE-014 additionally requires the published Client ID Metadata Document to match the checked source and exact callback, both MCP auth/version profiles, invalid-discovery/PKCE/resource/issuer cases, protected refresh/logout races, and headless consent refusal. OAuth success cannot mark a forbidden tool authorized. Documentation review performs no login, metadata deployment, signing or publication.
