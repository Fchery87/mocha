# SLICE-008: plain terminal daily workflow and M1 qualification

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M1. Requirements: FR-005, FR-006, FR-007, FR-018, FR-021, NFR-001, NFR-003, NFR-005, NFR-008, NFR-009. Prerequisites: [007](../SLICE-007/spec.md).

## User-visible result

The maintainer completes an independently verified edit-test-repair task in headless and plain TUI. The UI shows real provider/model state, evidence, honest progress and actionable setup/doctor results.

## Interfaces and behavior

Implement the M1 subset of [UI design](../../../DESIGN.md): top bar, transcript/tool rows, activity, composer, diff tints and basic approvals. Unknown progress uses activity rather than elapsed-time percentages. Color and status meaning survive NO_COLOR/ASCII; dark/light display at 80×24 and resize preserve usable input/history. Keyboard paths reach all in-scope choices. Sanitize untrusted control/OSC/CSI sequences before rendering from the first streamed text/tool output, including sequences split across chunks. Only renderer-generated terminal controls may affect clipboard, title, hyperlinks or screen state.

The minimal setup controls from 003/004 remain the shared provider/model/default operations. A fresh non-mock install with no provider enters guided setup, never a plausible mock response. `mocha doctor` reports actual configuration, credential availability without values, external tools, capability failures, binary path shadowing and unavailable checks honestly.

For each preset, record a supported coding-model path and full stream/tool/error qualification against its declared family. Live-account observations remain distinct from deterministic fixture support. The representative task repository/version and independent grader are frozen before the acceptance run. Record model/profile, task budget, final patch, actual verification output and human interventions. Failing checks require repair or an explicit scope revision.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 008-A01 | Headless and TUI edit-test-repair | Both complete the same fixed task and independently graded project checks; evidence identifies actual commands/results. |
| 008-A02 | All twelve providers | Usable guided setup and declared coding-tool profile, with dated fixtures and honest account availability. |
| 008-A03 | Unknown progress and evidence receipt | No invented completion percentage, billing guarantee or tests-passed claim without recorded evidence. |
| 008-A04 | Resize/NO_COLOR/ASCII/80×24 | Readable state, accessible input and correct terminal restoration on all terminal outcomes. |
| 008-A05 | Doctor failure | Missing capabilities/tools/credentials shown without secret values or false passed checks. |
| 008-A06 | Regression replay | Reconstructs mechanics without live effects; untrusted stream/patch/config cases are exercised. |
| 008-A07 | Performance qualification | Applicable real-subsystem budgets include engine, persistence, checkpoints where present and policy costs. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-008`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

001–007 behavior and evidence are required for M1 completion. Real paid calls are deliberate maintainer actions, never CI. A lack of a key may leave live entitlement unverified but cannot be hidden as a passed model test. Every claimed provider path still needs its contractual fixture and setup proof.

## Scope and decision status

No full transcript search/copy/rail, rich project trust UI, full modes, rewind, MCP or required native ChatGPT login completion. These remain later slices. Passing a mock task does not establish real coding quality.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
