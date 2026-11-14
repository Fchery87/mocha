# SLICE-018: welcome, rail, themes and accessibility qualification

Status: specified from the confirmed PRD and contracts; implementation and execution evidence pending. Owner: maintainer. Milestone: M2. Requirements: FR-019, FR-018, FR-021, NFR-001, NFR-008. Prerequisites: [017](../SLICE-017/spec.md).

## User-visible result

The full UI is usable at small and large terminal sizes, with truthful connection/trust/progress state, current-session rail navigation, dark/light themes and keyboard operation without color or motion dependencies.

## Interfaces and behavior

Use Volt dark/light as the only required palette. Honor CLI theme over MOCHA_THEME over user settings/detection; failed detection defaults to dark and an explicit light override remains available. Input readiness never waits for OSC 11 or other terminal probes; optional probing runs asynchronously with a 100 ms timeout, and an explicit theme never changes in response. Honor NO_COLOR without removing status words/glyph meaning. Reduced motion disables shimmer/moving progress while leaving activity visible. ASCII substitutes preserve decisions/status.

Welcome shows actual selected provider/model, canonical folder and up to three recent workspace sessions. Show trust and connection state separately; reading instructions never implies project config is trusted. First-run setup uses existing provider operations. The wide rail contains current-session tasks, changed files and checkpoints only; no Agents feature is implied. At narrow widths these remain reachable through transcript groups, /diff and /rewind.

Target 80×24 for complete required operation. Below that size, collapse decorative chrome and keep a minimum input/status area; show a resize message when even that cannot fit. Do not silently discard a pending approval. Preserve logical focus/selection on resize. Keep the active mode visible at every size, moving it to the status/footer when composer chrome collapses. Explicit aliases/settings outside the MVP are not accepted then ignored; unsupported options fail or are visibly unavailable.

## Acceptance and failure cases

| Case | Trigger | Required observable outcome |
| --- | --- | --- |
| 018-A01 | 80×24 and smaller/larger sizes | Required choices/input usable at target size; undersized fallback preserves pending state. |
| 018-A02 | Dark/light/NO_COLOR/ASCII | Status remains identifiable and readable without color or unsupported glyphs. |
| 018-A03 | Reduced motion and idle | No hidden required animation cue; idle redraws cease when nothing changes. |
| 018-A04 | Welcome and recent sessions | Actual connection/trust/default states, no invented account access or resumed inference. |
| 018-A05 | Rail keyboard/resize | Current-session tasks/diffs/checkpoints reachable at every supported layout width. |
| 018-A06 | Terminal capability failure | Inline/text fallbacks and truthful doctor reports; no false support/success indicators. |
| 018-A07 | Integrated performance | Real UI meets calibrated budgets with the in-process engine and selected features counted. |

## Verification and evidence

The planned acceptance entry point is `cargo xtask verify slice-018`. It must exercise the cases above through the highest applicable client/protocol boundary and retain independently observed effects. It is not implemented yet. Supporting checks are `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and the documentation/contract checks in [the verification plan](../../verification.md). Targeted tests run during development; required full checks run before acceptance.

Retain sanitized command output, fixture hashes, build revision, selected features, environment/tool versions, case results, and failures in this slice's future evidence directory. The [common completion contract](../README.md#completion-contract) defines acceptance and handoff. A provider or agent assertion is not proof of a passed case.

## Dependencies and stop conditions

017 navigation/accessibility semantics are required. Snapshot coverage includes dark/light Volt and declared degraded capabilities, not future palette/Focus features. Declare actual terminal/reference metadata for benchmark evidence before accepting it.

## Scope and decision status

No Focus, subagents, extra palettes, arbitrary key remapping, screen-reader-specific mode, visual prototype branch dependency or guaranteed OSC/image support.

No new product choice is delegated to an implementer by this spec. Requirements and selected engineering behavior are defined here and in the [PRD](../../02-prd.md) and normative contracts. Unproved integration assumptions above are execution gates. A failed gate stops the dependent claim for repair or an explicit scope revision; it cannot silently remove a confirmed requirement.
