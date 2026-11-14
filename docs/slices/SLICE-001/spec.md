# SLICE-001: mock walking skeleton and calibration

Status: specified; implementation and feasibility evidence pending. The maintainer confirmed the handoff on November 14, 2026. No application implementation exists. Owner: maintainer. Milestone: M0. Requirements: FR-001, FR-022, NFR-001, and applicable NFR-003, NFR-004, NFR-008. Dependencies: [PRD](../../02-prd.md), [architecture](../../04-architecture.md), [runtime contract](../../contracts/runtime.md), and [verification plan](../../verification.md).

## User-visible result

A fresh checkout builds `mocha`. Starting `mocha --mock` opens the minimal fullscreen welcome with a visibly labeled mock provider. A typed prompt crosses the protocol, reaches the engine, and receives a deterministic streamed response ending with one Done event. No key, network, IPC socket, or persistent session store is needed. The signal pipe is permitted.

The skeleton does not run real commands, edit files, register accounts, or claim a usable real coding model. M1 first-run setup replaces the mock-only development path rather than disguising mock output as a real provider.

## Implementation sequence

1. Resolve the selected Rust toolchain and dependency graph in a disposable spike. Check API compatibility, selected licenses/features, rustls, both musl targets, and candidate MSRV. Record failures before adopting the lockfile. Do not create unused future crates as empty implementation claims.
2. Add core IDs/errors/IR, protocol-v1 request and event types, and their exported schemas. Use the checked [version-1 boundary schemas](../../contracts/boundary-payloads.md) for version negotiation and the four M0 methods. Exported Rust schemas must match the checked fixtures; schema changes require reviewed caller/fixture updates. Reject malformed, duplicate, and out-of-order requests without a panic.
3. Add the in-process engine and deterministic mock stream with selectable success/failure behavior. Keep request rejection distinct from an accepted turn's failure. Enforce bounded buffers and cancellation.
4. Add the minimal ratatui/crossterm client, dark/light Volt colors, input, streamed text, failure marker, quit hint, and terminal restoration. Implement inline fallback on fullscreen setup failure.
5. Add the PTY verifier and performance instrumentation against the real binary. Record the reference terminal/environment and fixed workload hashes. Run calibration before accepting numeric budgets.
6. Add CI formatting, lint, tests, dependency graph and license/advisory checks. Calibrate benchmark CI on a suitable controlled runner before describing performance checks as active.

## Acceptance and failure cases

| Case | Observable pass condition | Future verifier |
| --- | --- | --- |
| 001-A01: Fresh start | Mock label and input readiness, no credentials/network/store writes | PTY plus isolated-home and socket/file tracing |
| 001-A02: Prompt path | Correlated acceptance, ordered deltas, exactly one Done | Protocol integration and PTY |
| 001-A03: Failure path | Visible non-color error, one Failed, next prompt works | Mock failure fixture and PTY |
| 001-A04: Invalid request | Typed mismatch/empty/not-initialized/unknown-session/turn-in-progress rejection | Protocol fixture suite |
| 001-A05: Cancellation | New dispatch stops; late events cannot revive turn | State-machine race fixture |
| 001-A06: Quit | First Ctrl+C hint, second inside two seconds exits 0, unrelated keys retain hint | Timed PTY input |
| 001-A07: Terminal failure | Restored state and usable inline fallback | Injected setup failure under PTY |
| 001-A08: Terminal capability | NO_COLOR, 80×24, resize, unsupported theme error | PTY and component snapshots |
| 001-A09: Slow client | Bounded buffers, independent cancellation, reserved terminal state, ordered retained events, 30-second continuous delivery-stall interruption | Stalled consumer/blocked pipe with injected clock and real integration case |
| 001-A10: Dependency boundary | TUI has no engine dependency or calls | cargo metadata plus source rule |
| 001-A11: Performance | Valid repeated measurements meet applicable budgets | xtask benchmark with raw JSON |

Implement the planned commands `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`, `cargo deny check`, and `cargo xtask verify slice-001`. These are future interfaces, not commands that currently work. The last command drives the protocol/PTY checks and emits an evidence manifest. `cargo xtask bench` emits samples and environment/workload metadata. A check's activation requires a deliberately failing example followed by a real passing run and CI evidence.

## Evidence and stop conditions

Store sanitized logs, PTY captures, command versions, toolchain/features, workload hashes, raw benchmark JSON, and failing/passing guard examples in this slice's future evidence directory. Mark inapplicable future tool/checkpoint benchmarks pending, not passed.

Stop for an incompatible dependency graph, missing required toolchain/target, inability to instrument actual readiness, unstable measurements, or a valid budget miss. Optimize or request a concrete scope/budget revision with evidence. Do not weaken safety/durability or expand the MVP automatically. M0 completion requires FR-001/FR-022 evidence and calibrated applicable NFR-001 checks, not a successful --version call.


## Review closure

Prerequisites: none within the slice graph. Public payload shapes now exist before code. The [common completion contract](../README.md#completion-contract) applies. Dependency/static-build resolution and benchmark calibration are execution gates, not passed results or product choices. No application implementation exists.
