# SLICE-017: full transcript navigation, search and source copy

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M2. Requirements: FR-019, FR-018, NFR-001, NFR-008, NFR-009. Prerequisites: [008](../SLICE-008/spec.md), [009](../SLICE-009/spec.md), [011](../SLICE-011/spec.md).

## User-visible result

Users can inspect long streamed histories, search text, expand tool evidence and copy source text without losing their reading position or being told an unavailable clipboard operation succeeded.

## Interfaces and behavior

Follow the [current UI reference](../../../DESIGN.md) within PRD scope. Fullscreen owns virtual scrollback; inline retains the same input, evidence, approval and cancellation semantics without the fullscreen rail. Pin a stable source-block/offset anchor when scrolled back; newly arriving output and resize/reflow cannot jump the view to the bottom. End explicitly returns to live output.

Transcript search is literal Unicode text, case-insensitive by default with a case-sensitive toggle; no regular-expression query language. Search redacted original source text, including collapsed and older history, rather than only the compacted model view. Search does not automatically load hidden spill payloads or hidden credential material. Show match count/current position, support next/previous keyboard traversal and cancel back to the prior anchor. Next/previous wraps to the first/last match with a visible wrap notice. No match preserves the prior anchor and reports zero. Cancelling search restores the pre-search anchor; new matches do not steal focus. Search must not load the full log into memory to evade the RSS budget.

Source selection excludes gutters, wrapping artifacts and hidden collapse markers. OSC 52 is best effort. Without positive acknowledgement say copy requested; unavailable support offers a source-text viewer for terminal-native selection. Clipboard failure never yields a copied-success toast. Every group/diff/selection/search control has a keyboard path; mouse is optional. Hostile control/OSC sequences in transcript content are rendered safely rather than executed as terminal controls.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 017-A01 | Scroll while streaming/resize | Same readable source anchor retained until explicit live-edge navigation. |
| 017-A02 | Long log/search | Correct match navigation and bounded-memory behavior over the declared resume fixture. |
| 017-A03 | Unicode/wrapped selection | Copied source matches original content, excludes rendered gutters and preserves grapheme boundaries. |
| 017-A04 | OSC 52 absent/blocked/unacknowledged | Truthful status and usable manual-selection fallback. |
| 017-A05 | Keyboard-only and inline | All in-scope decisions/navigation remain reachable without mouse/rail. |
| 017-A06 | Untrusted escape sequences | Transcript/tool bytes cannot inject terminal OSC commands or forge system UI state. |
| 017-A07 | Failure/exit | Terminal restored, progress/title cleared and outstanding effects remain honestly recorded. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-017`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

008 plain TUI, 009 mode/dock, 011 checkpoint controls and existing protocol/store/source blocks are required. UI work does not wait on the external ChatGPT account gate. Real PTY/pipe tests complement snapshots; mocked widget state alone does not prove terminal restoration or clipboard behavior. Recheck keypress/stream CPU/RSS budgets with the actual full renderer.

## Scope and decision status

No Focus/Lead/agent views, whole-workspace/cross-session search, regex search, clipboard binary image import or mandatory advanced image rendering.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
