# Jcode interactive permission behavior

Observed November 14, 2026 at owner-repository commit `374ed3ecacdc2a08ecd1cdef6a57a036060e424d`, dated November 14, 2026. This is a bounded source inspection, not an execution test or certification of all tools. No Jcode code is copied into Mocha. No Mocha policy decision is approved by this note. [Pinned commit](https://github.com/1jehuang/jcode/commit/374ed3ecacdc2a08ecd1cdef6a57a036060e424d).

## Interactive shell behavior

The local Bash tool applies a deterministic destructive-command assessment before foreground or background dispatch. Its outcomes are materially different from the ambient design document:

| Assessed risk | Actual gate behavior |
| --- | --- |
| Safe | Execute immediately |
| Low, bounded destructive effect | Execute immediately |
| Confirm, uncertain destructive target | Refuse this attempt and ask the generating model to reconsider the user's request |
| Catastrophic protected target | Refuse permanently; model justification cannot unlock it |

The intermediate path is model reflection, not a user approval dialog or separate safety-model review. A subsequent call with a substantive `justification` can pass. The implemented check requires at least 25 characters and rejects empty/affirmative responses; it does not establish that the user actually authorized the operation. The reflection prompt tells the model to ask the user if unsure. [Bash integration](https://github.com/1jehuang/jcode/blob/374ed3ecacdc2a08ecd1cdef6a57a036060e424d/crates/jcode-app-core/src/tool/bash_destructive_gate.rs#L13), [gate implementation](https://github.com/1jehuang/jcode/blob/374ed3ecacdc2a08ecd1cdef6a57a036060e424d/crates/jcode-command-risk/src/gate.rs#L42).

Risk levels consider destructive scope and protected targets rather than only matching a command name. The source identifies root, home, credential locations, and device targets among catastrophic cases. It explicitly describes this filter as defense in depth rather than a sandbox and acknowledges static-analysis evasions. A source comment describing the older ungated behavior explains the motivation; the current Bash integration must take precedence over that historical comment. [Risk classification and limitations](https://github.com/1jehuang/jcode/blob/374ed3ecacdc2a08ecd1cdef6a57a036060e424d/crates/jcode-command-risk/src/lib.rs#L20).

## Dispatch controls and execution boundary

Agent validation and registry dispatch enforce session tool allowlists/disabled tools. The registry also supports an optional user-configured pre-tool hook that can block or transform a call. In the inspected default path there is no universal human approval step for each ordinary edit or shell command. These are tool-policy checks, not a four-mode matrix equivalent to Mocha's proposed rip/careful/plan/yolo. [Agent validation](https://github.com/1jehuang/jcode/blob/374ed3ecacdc2a08ecd1cdef6a57a036060e424d/crates/jcode-app-core/src/agent/turn_execution.rs#L1178), [registry policy and hook](https://github.com/1jehuang/jcode/blob/374ed3ecacdc2a08ecd1cdef6a57a036060e424d/crates/jcode-app-core/src/tool/mod.rs#L1053).

The inspected local Unix path constructs `bash -c`, sets its working directory/environment, and spawns the process. This path does not show mandatory workspace-only OS enforcement or network-off containment. An optional remote execution environment may impose different boundaries, so this finding does not describe every Jcode deployment. A command risk parser must not be presented as proof of containment. [Shell construction](https://github.com/1jehuang/jcode/blob/374ed3ecacdc2a08ecd1cdef6a57a036060e424d/crates/jcode-app-core/src/tool/bash.rs#L687), [local spawning](https://github.com/1jehuang/jcode/blob/374ed3ecacdc2a08ecd1cdef6a57a036060e424d/crates/jcode-app-core/src/tool/bash.rs#L932).

## Ambient safety is a separate system

SAFETY_SYSTEM.md remains marked Design, updated February 8, 2026, and describes an ambient consumer with automatic local work and human approval for external/shared effects. Its statement that explicit user approval can authorize any action cannot describe the current interactive catastrophic-command gate. Actual source restricts `request_permission` to registered ambient sessions. It is therefore incorrect to treat the ambient two-tier document as Jcode's universal interactive permission policy. [Ambient design](https://github.com/1jehuang/jcode/blob/374ed3ecacdc2a08ecd1cdef6a57a036060e424d/docs/SAFETY_SYSTEM.md), [ambient-only enforcement](https://github.com/1jehuang/jcode/blob/374ed3ecacdc2a08ecd1cdef6a57a036060e424d/crates/jcode-app-core/src/tool/ambient.rs#L93).

## Implications for Mocha

The supported design inference is to consider Jcode's low-interruption interaction: ordinary local work proceeds, destructive uncertainty causes a deliberate reconsideration step, and catastrophic targets remain blocked. This does not prove arbitrary scripts safe or require copying Jcode's execution boundary.

Mocha currently requires scoped authority, network-off subprocesses unless granted, fail-closed containment, protected credentials, and approval for unknown MCP effects. Adopting Jcode's exact model-justification unlock for an otherwise unauthorized operation would change Mocha's accepted rule that model rationale cannot grant authority. That product tradeoff needs an explicit decision. A compatible adaptation could use reflection to narrow or abandon a proposed action while still requiring an existing user grant or fresh user approval whenever independent Mocha policy requires it. Preference for Jcode alone does not establish which variant the maintainer intends.
