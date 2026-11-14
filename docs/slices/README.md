# MVP slice specifications

All 19 planned MVP slices now have a local specification. The [manifest](manifest.json) is the machine-readable identity, dependency and requirement map. The PRD and normative contracts remain authoritative for required behavior. These files are implementation inputs, not claims of completed code, passed CI, working accounts or published artifacts.

## Specification index

| Slice | Milestone | Specification | Blocked by |
| --- | --- | --- | --- |
| SLICE-001 | M0 | [mock walking skeleton and calibration](SLICE-001/spec.md) | None |
| SLICE-002 | M1 | [headless turns and durable recovery](SLICE-002/spec.md) | SLICE-001 |
| SLICE-003 | M1 | [provider setup, credentials and Anthropic connection](SLICE-003/spec.md) | SLICE-002 |
| SLICE-004 | M1 | [complete provider catalog and four API families](SLICE-004/spec.md) | SLICE-003 |
| SLICE-005 | M1 | [contained tools with evidence and minimum loop guards](SLICE-005/spec.md) | SLICE-002, SLICE-003, SLICE-004 |
| SLICE-006 | M1 | [interjection, queued work and loop control](SLICE-006/spec.md) | SLICE-005 |
| SLICE-007 | M1 | [scoped instructions, compaction and bounded context](SLICE-007/spec.md) | SLICE-006 |
| SLICE-008 | M1 | [plain terminal daily workflow and M1 qualification](SLICE-008/spec.md) | SLICE-007 |
| SLICE-009 | M2 | [permission modes and action review](SLICE-009/spec.md) | SLICE-008 |
| SLICE-010 | M2 | [project trust and layered configuration](SLICE-010/spec.md) | SLICE-009 |
| SLICE-011 | M2 | [covered checkpoints, rewind and explicit cleanup](SLICE-011/spec.md) | SLICE-010 |
| SLICE-012 | M2 | [complete Linux execution and descendant coverage](SLICE-012/spec.md) | SLICE-011 |
| SLICE-013 | M2 | [injection and authority regression qualification](SLICE-013/spec.md) | SLICE-012 |
| SLICE-014 | M2 | [tools-only MCP across explicit protocol profiles](SLICE-014/spec.md) | SLICE-013 |
| SLICE-015 | M2 | [cross-adapter continuation and attachment qualification](SLICE-015/spec.md) | SLICE-014 |
| SLICE-016 | M2 | [native ChatGPT connection and account lifecycle](SLICE-016/spec.md) | SLICE-004, SLICE-015 |
| SLICE-017 | M2 | [full transcript navigation, search and source copy](SLICE-017/spec.md) | SLICE-008, SLICE-009, SLICE-011 |
| SLICE-018 | M2 | [welcome, rail, themes and accessibility qualification](SLICE-018/spec.md) | SLICE-017 |
| SLICE-019 | M2 | [verified Linux release and daily-driver acceptance](SLICE-019/spec.md) | SLICE-008, SLICE-012, SLICE-013, SLICE-014, SLICE-015, SLICE-016, SLICE-018 |

## Completion contract

Each slice is an end-to-end specification. Ticketing may split it into smaller independently verifiable vertical deliveries, but cannot remove its acceptance/failure cases or rewrite blocking relationships without review. The owner is the maintainer. The coding agent supplies implementation assistance and evidence; the maintainer owns acceptance and scope changes.

Before implementing a public boundary, use the [checked payload schemas](../contracts/boundary-payloads.md), compatible adapters and failure semantics. Add schema/fixture updates before relying on changed fields. Module-internal Rust types may be designed within these boundaries; that is engineering work, not authorization to change product scope. Existing callers and future clients cannot guess incompatible enum/payload formats independently.

A slice cannot be accepted until its declared prerequisites have passed their relevant checks. Planned verifier entry points are `cargo xtask verify slice-NNN`; none exists yet. An implementation must make that entry point run the declared acceptance/failure cases and emit a result manifest. At minimum it records case ID, pass/fail/blocked/not-applicable with reason, command/fixture hashes, build revision/features, environment, evidence references and observed effects. Missing evidence is blocked, never passed. Required full checks and applicable performance gates also pass before acceptance.

The evidence directory is `docs/slices/SLICE-NNN/evidence/` unless large machine-readable artifacts live in an immutable CI run linked from that directory. Keep credentials and raw authentication URLs out of committed evidence. Mark failures and unavailable target/account/hosting prerequisites explicitly. Retain readable links to immutable outputs so later sessions can verify claims without trusting a prose summary.

Before handoff, recheck PRD requirement coverage, protocol/event compatibility, dependency direction, known-secret sinks, migration/original retention, real enforcement and applicable PTY behavior. Reopen affected downstream checks after a contract change. A later slice extends an earlier proof; it does not retroactively certify missing prerequisites.

## External and feasibility gates

Dependency resolution/static linking, reference-machine repeatability, kernel/filesystem/lifetime enforcement, provider/account access, SIWC eligibility, MCP OAuth registration/metadata publication, package ownership, signing authority and native arm64 execution require actual evidence. They remain gates even though the product choices are settled. A failure stops the affected implementation/support/release claim for repair or an explicit scope revision.

The current version-1 schemas, configuration/import fixtures, permission examples and small [coding task corpus](../fixtures/coding-acceptance.json) provide bounded verification inputs. They cannot establish that the future engine is correct, that every hosted service works, or that no implementation surprise will occur.

Run `python3 scripts/check_slices.py --self-test` from the repository root for spec existence, graph, requirement coverage and acceptance-case checks. Run the boundary-schema, permission and corpus checks described in the verification plan as well. These checks validate the written handoff and fixtures, not runtime release readiness.
