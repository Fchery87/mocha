# Final MVP slice specification review

Reviewed November 14, 2026 against the confirmed PRD, architecture, four contracts, UI reference and all 19 planned slices. Only SLICE-001 had a local spec at the beginning of this round. SLICE-002 through SLICE-019 now have concrete local specifications, acceptance/failure cases, dependencies and planned verifier commands. This review does not claim implemented application behavior or a seamless build guarantee.

## Product decision resolved

The maintainer explicitly selected browser OAuth plus static keys for remote MCP. The [authentication contract](../contracts/providers-and-mcp.md#remote-mcp-authentication) now fixes discovery/registration, PKCE/resource/issuer binding, protected refresh/logout, headless behavior and the prepared public client metadata URL. This is separate from native ChatGPT sign-in and from permission to execute tools. Final artifact checks also tightened method acceptance/turn correlation, added explicit monotonic durable taint/provenance transitions and aligned strict project-field rejection with its schema. No other new product decision remained after the bounded reviews; engineering defaults and external proof gates are listed rather than silently delegated.

## Per-slice findings and closures

| Slice | Final review closure | Evidence still required |
| --- | --- | --- |
| 001 | Exact version-1 method/event payloads and failure fixtures now precede code; independent cancellation and reserved final-state capacity included. | Actual dependency resolution, PTY skeleton, static-build and benchmark calibration. |
| 002 | Typed session records, CRC32C byte format, read-only recovery, writer ownership, migration/original retention and exact headless outcomes specified. | Real fsync/kill/torn-log/full-disk/migration/concurrent-writer cases and resume measurements. |
| 003 | Setup commands, credential boundaries, config schemas/conflicts, model-limit/compatible-context checks before inference and text-only tool refusal specified. | Real keychain/adapter/parser behavior, sink redaction and guided first turn. |
| 004 | All four families/twelve presets remain M1; explicit metadata/discovery refresh, endpoint/account distinctions and early SIWC feasibility output required. | Exact endpoint/model fixtures, usable model paths, selected metadata notices and actual SIWC feasibility. |
| 005 | Basic output/spill, finite capture/job limits, no-rewind M1 results and minimum cancellation/deadline/lifetime/persistence precede real effects. | Actual path/race/enforcement/evidence/partial-patch cases and honest overhead measurements. |
| 006 | Durable queued/interjected text, stable message identity, at-most-once activation, pending recovery, exact operational limits and process ownership specified. | Real cancellation/interjection/queue/limit/race tests, without auto-running recovered work. |
| 007 | Nested instruction scope, compatible context, reserves/compaction failure, original history and marked redacted-read coverage specified. | Actual instruction/context/compaction transforms and bounded spill behavior across adapters. |
| 008 | Early terminal-control sanitization, honest progress/doctor, full M1 model paths and independent dual-client coding acceptance specified. | Real PTY, all-preset setup/tool qualification, independent task results and performance. |
| 009 | Final four-mode matrix plus hard-deny/authority precedence fixed; checkpoint-dependent Auto mutations blocked until 011 and retested there. | Real all-mode dispatch, reflection, Unattended and mode-switch races. |
| 010 | Versioned restricted project config, exact bytes/hash/canonical identity, TOCTOU/symlink checks, revocation and headless trust refusal specified. | Actual trust-change/config-race/revocation behavior and no credential/rule elevation. |
| 011 | Known-credential-containing files excluded before staging, exact-byte snapshots, explicit cleanup references, restore invalidation and sticky taint specified. | Actual Git/file/restore/cleanup failures and real checkpoint-backed 009 integration. |
| 012 | Filesystem/network/descriptor/environment/lifetime probes and real descendants/background/local-server cases specified. | Supported hosts and both target architectures prove the requested enforcement; no fallback. |
| 013 | Taint survives compaction/resume/model switch and all rewind scopes; actual effect oracles required for hostile content. | Real authorization/containment adversarial corpus, not a model refusal narrative. |
| 014 | Both MCP revisions/transports plus confirmed static/OAuth profiles, exact registration metadata, consent lifecycle and tool-policy separation specified. | SDK conformance, metadata publication, OAuth/version/transport fixtures and real protected-server behavior. |
| 015 | M1 image/capability basics cannot be deferred; explicit formats/size/count/pixel limits and immutable submitted attachment identity specified. | Actual provider continuation/attachment/race limits and no unknown-operation replay. |
| 016 | Early SIWC report is a dependency; fixed login timeout, protected generations, optional account availability, mandatory successful inference and no fallback billing specified. | Mocha registration/eligible account/tool-capable completed inference, refresh and revocation. |
| 017 | UI no longer depends on SIWC eligibility; source/history search, stable anchors, paging, truthful clipboard status and control-sequence sanitization specified. | Actual PTY, Unicode/source copy, long-history bounded memory and terminal restoration. |
| 018 | Persistent mode at every size, nonblocking theme detection, Volt-only MVP, honest degraded capabilities and no unsupported prototype evidence specified. | Real layouts/themes/NO_COLOR/ASCII/reduced-motion/keyboard behavior and full-process measurements. |
| 019 | Release depends on all required P0 paths; exact signed manifests/provenance/key trust, native arm64 cases and fixed independent coding/recovery corpus specified. | Registry/signing/hosting authority, actual native/static installs and attestation, all P0 acceptance and maintainer daily use. |

## Shared artifacts and repeatable checks

The [slice manifest](../slices/manifest.json) covers all 33 PRD IDs and 19 specs. Its graph separates UI delivery from external account feasibility while keeping release integration gates. [Boundary schemas](../contracts/boundary-payloads.md) define protocol, stored records, config, tool arguments and auth references. Their validators resolve locally without fetching arbitrary schema URLs. [Permission vectors](../contracts/fixtures/permission-decisions.json) retain the approved mode behavior.

The [fixed coding corpus](../fixtures/coding-acceptance.json) names TASK-BUG-001, TASK-FEATURE-001 and TASK-RECOVERY-001. The first two have immutable initial/grader hashes and known failing/passing candidates. The recovery scenario still needs the actual engine/checkpoint implementation. The corpus is deliberately small and cannot establish broad productivity or comparative coding quality.

Rerunnable checks are:

- `python3 scripts/check_docs.py --self-test`
- `python3 scripts/check_slices.py --self-test`
- `python3 scripts/check_permission_contract.py --self-test`
- `uv run --no-project --with jsonschema python scripts/check_boundary_schemas.py --self-test`
- `uv run --no-project --with jsonschema python scripts/check_model_schema.py`
- `python3 scripts/check_acceptance_corpus.py`
- `git diff --check`

Self-tests deliberately inject missing specs, cyclic dependencies, absent requirement coverage, forbidden Plan mutations, unattended approval waits, missing scope, malformed interfaces and corrupted records. Passing them establishes the written artifacts' consistency and that the fixture checks detect these failures. No future cargo verifier, app test, provider call or performance guard is labeled active.

## Remaining work is explicit

No product question is hidden in a slice's implementation task. Detailed private module design, task decomposition and test harness construction remain engineering work. Dependency APIs/features, numerical budgets, account eligibility, filesystem/kernel capabilities, public metadata deployment, package ownership, signing keys and native execution still need real proof. Any failed prerequisite blocks its dependent claim and requires repair or explicit scope review. It cannot be turned into automatic approval, a silent scope cut or a claimed successful build.


## Package-name observation

A read-only request to the [official crates.io API](https://crates.io/api/v1/crates/mocha-code) returned HTTP 404 with a structured crate-does-not-exist response on November 14, 2026. The planned package was therefore unregistered at observation time. This does not reserve it or prove publishing permission. Keep the selected name and recheck immediately before registration/publication; a later conflict remains an explicit release gate.
