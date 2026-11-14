# Mocha documentation

Current baseline: November 14, 2026. The repository is in specification work. Product choices from the interview are recorded. The maintainer confirmed the complete handoff on November 14, 2026. SLICE-001 is ready for implementation. All 19 slices now have local specifications. No runtime, benchmark, account-access, or active-CI claim follows from these documents.

## Authority and reading order

1. [PRD revision 5](02-prd.md) defines scope, requirements, accepted decisions, and release gates.
2. [Architecture revision 7](04-architecture.md) defines ownership and delivery dependencies.
3. [Runtime](contracts/runtime.md), [tools and policy](contracts/tools-and-policy.md), [providers and MCP](contracts/providers-and-mcp.md), and [storage and context](contracts/storage-and-context.md) define shared engineering behavior.
4. [Verification](verification.md) maps every requirement to evidence and fixes benchmark rules.
5. [The slice index](slices/README.md) links all 19 local specifications and their dependency graph. [SLICE-001](slices/SLICE-001/spec.md) begins the build.
6. [UI design](../DESIGN.md) supplies current visual interactions within the PRD scope. [Feature roadmap](FEATURES.md) separates MVP from later ideas.

The [glossary](../GLOSSARY.md) defines terms. [ADRs](adr/0001-bounded-local-recovery-storage.md) record costly tradeoffs. Research explains evidence and uncertainty; it cannot expand scope or override current contracts. Conflicts require updating the owning specification and affected references before implementation.

## Settled handoff

M0 builds a measured mock skeleton. M1 delivers both clients, real tools after minimum containment, durable sessions, all four API families and twelve API-key providers plus Custom. Users choose their model explicitly. M2 delivers the full safety/UI experience, rewind, tools-only MCP, required native ChatGPT sign-in, and verified Linux releases.

Retention is explicit, recovery coverage is bounded, history/checkpoints are private plaintext, known harness credentials stay protected, and uncertain effects never blindly replay. Headless missing approval/input stops distinctly. Numeric performance targets include safety and persistence costs.

The interview choices and delegated mode finalization are recorded. All five findings in the [semantic gap audit](reviews/2026-11-14-prd-gap-audit.md) now have specification closures. Canonical modes are auto, approve, plan and explicitly selected unattended. There is no cumulative token cap. Independent cancellation, the 30-second blocked-delivery timeout, shared-state coordination, and first-command prerequisites are specified. All affected runtime checks remain pending. No claim of universal completeness or a hiccup-free build follows from closing these findings.

The [final per-slice review](reviews/2026-11-14-final-slice-review.md) records engineering closures and the confirmed remote MCP OAuth choice. Remaining work includes ticketing and execution evidence: dependency/static-build resolution, performance calibration, actual containment/durability tests, adapter fixtures and usable model paths, early SIWC feasibility, and independently graded coding workflows. A failure blocks its dependent claim and requires repair or an explicit scope revision.

## Research provenance

[Market/build-readiness report](research/2026-11-14-mocha-market-and-build-readiness.md), [source inventory](research/2026-11-14-mocha-research-sources.json), and [dependency metadata](research/2026-11-14-mocha-dependency-evidence.json) distinguish dated publications, mutable documentation, registry checks, and untested assumptions. The [November 10 blueprint](research/2026-11-10-mocha-engineering-blueprint.md) is historical.

Run `python3 scripts/check_docs.py --self-test` for structural documentation checks and `python3 scripts/check_permission_contract.py --self-test` for mode acceptance-example consistency. Semantic review and implementation verification remain separate.
