# SLICE-019: verified Linux release and daily-driver acceptance

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M2. Requirements: FR-023, FR-021, NFR-001, NFR-003, NFR-004, NFR-005, NFR-007, NFR-009. Prerequisites: [008](../SLICE-008/spec.md), [012](../SLICE-012/spec.md), [013](../SLICE-013/spec.md), [014](../SLICE-014/spec.md), [015](../SLICE-015/spec.md), [016](../SLICE-016/spec.md), [018](../SLICE-018/spec.md).

## User-visible result

The maintainer can inspect draft static Linux release artifacts, verify their integrity/provenance, install the mocha command on clean x86_64 and arm64 hosts, and assess the completed MVP against all P0 gates.

## Interfaces and behavior

Build x86_64-unknown-linux-musl and aarch64-unknown-linux-musl from the declared source revision, Rust toolchain, lockfile and selected features. Inspect ELF program headers/dependencies and run on clean target environments; cross-compiling alone does not prove execution or static linkage. Run native functional and containment cases on each supported target, including arm64. Generate SHA-256 checksums, minisign signatures, dependency/license notices and verifiable provenance for each exact artifact. Keep build and signing/publication privileges separate. Sign a release manifest containing version, source commit, artifact filenames/byte sizes/SHA-256 values and provenance references. Publish the public key/fingerprint through the release documentation and repository; consumers must use a separately trusted key source rather than trust an arbitrary key shipped alongside an archive. Verify wrong-key and manifest/artifact tampering failures. Provenance binds artifact subject hashes, source commit, workflow/build identity and declared inputs; a JSON file claiming provenance is not by itself verifiable attestation.

Prepare draft releases only. Signing key use and final publication remain maintainer-controlled. The release evidence bundle includes key fingerprint/public-key distribution instructions, source/build identifiers, checksum/provenance verification steps and clean-install logs. Do not claim reproducible builds without an independent byte comparison. Verify registry/package ownership/name availability before relying on cargo install mocha-code --locked. A conflict blocks that installation claim and requires explicit package naming resolution, never silent substitution.

Doctor separates embedded build metadata from independently verified signature evidence. A copied binary without a verified adjacent signature is unverified, not automatically authentic. Complete doctor reports terminal/config/model/credential availability, required tools, runtime coverage and PATH shadowing without keys. No automatic updater or background update network request is introduced.

Before publication, independently grade TASK-BUG-001 and TASK-FEATURE-001 from the checked [acceptance corpus](../../fixtures/coding-acceptance.json) in both clients, and run TASK-RECOVERY-001 against actual crash/rewind controls. The independent grader copies only submitted source into a fresh grading environment, checks immutable grader/input hashes and reviews the resulting diff; agent-written tests cannot replace the golden oracle. Before real use prove the corpus initial candidates fail and reference candidates pass. Independently grade the fixed tasks, review their patches outside agent-write scope, and complete the maintainer daily-driver checklist. The checklist covers setup, provider/model switch, edits/tests, cancellation, restart/recovery, denied actions, rewind, MCP and native ChatGPT. Any P0 failure remains a release blocker; optional P1 omissions are explicitly listed.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 019-A01 | Both target binaries | Clean-machine execution and ELF evidence support actual architecture/static-linkage claims. |
| 019-A02 | Integrity and provenance | Valid artifacts verify; altered archive/checksum/signature/provenance fails verification. |
| 019-A03 | Clean source install | Locked published package installs mocha under confirmed registry ownership; no hidden system dependency omitted. |
| 019-A04 | Signing/publication boundary | Untrusted PR code never receives signing keys; no artifact published without explicit authority. |
| 019-A05 | License/feature/advisory graph | Resolved selected graph and bundled metadata notices pass checks, not merely registry metadata. |
| 019-A06 | Doctor copied/unverified binary | Build info and signature status remain distinct and unsupported checks never pass by default. |
| 019-A07 | MVP daily-driver gate | All P0 mapped evidence exists, real task results independently graded, limitations/P1 omissions visible. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-019`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

All prior acceptance gates and real SIWC/MCP/provider support claims must have evidence. Package registration/signing access, target hosts and actual release authority are external execution prerequisites, not satisfied by these docs. Failure stops publication. The maintainer may revise a blocked external assumption explicitly; an implementer cannot silently rename packages or remove required platforms/features.

## Scope and decision status

No automatic updates, Windows/macOS artifacts, telemetry, unverifiable authenticity claim, paid CI evaluation, automatic release publication or assumption of bit-for-bit reproducibility.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
