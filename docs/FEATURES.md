# Mocha feature roadmap

Reconciled November 14, 2026. This roadmap summarizes [the PRD](02-prd.md). It does not add acceptance requirements. Features are planned, not implemented. The earlier catalog mixed MVP promises with future ideas and overstated competitor comparisons; those comparisons are withdrawn.

## MVP

| Milestone | Capabilities |
| --- | --- |
| M0 | Mock terminal conversation, versioned protocol, measured startup/rendering, initial CI |
| M1 | Real coding loop, headless text/JSON, twelve built-in API-key providers plus Custom, four API families, provider/model pickers, explicit defaults, reviewed metadata and discovery |
| M1 | Read/edit/write/patch/search/shell tools, read ledger, source evidence, minimum containment and scoped approvals before commands, instructions, compaction/spill, durable resume, plain TUI |
| M2 | Full permission modes and trust UI, bounded checkpoints/rewind, taint controls, tools-only MCP, required native ChatGPT sign-in, full TUI, Linux release/install pipeline |

Provider names and adapter profiles live in [the provider contract](contracts/providers-and-mcp.md). A custom endpoint still needs a supported API family and verified capabilities. A catalog entry does not establish account access. Subscription access is distinct from API-key support. No implicit paid-model or cross-provider fallback occurs.

Subprocess networking is off until an explicit scoped grant. Required containment fails closed. Unknown MCP effects ask, and headless unavailable approval stops. Hard denies apply even in unattended. A user mode cannot disable credential blocks. There is no unsandboxed retry.

Recovery is coverage-limited private plaintext. Ignored/configured sensitive paths are excluded from checkpoints, with explicit approval for uncovered edits. No automatic separate `.env` backup exists. Keep recovery/evidence until explicit previewed deletion. External services are not rewound. See [storage](contracts/storage-and-context.md).

Performance budgets are targets subject to [calibration and honest cost accounting](verification.md). Rust and native distribution do not prove lower overhead or better coding outcomes than competitors.

## Later work

These ideas need separate scope decisions, specifications, and verification before implementation. No version/date commitment is made.

- Daemon, multiple attached clients, cross-session search, editor integration through ACP, SDK, macOS, and Windows.
- Subagents, named custom agents, worktree orchestration, Lead mode, multi-model review, and model routing.
- Repo maps, LSP diagnostics, structure-aware search, automatic verification workflows, long-running goals, and richer memory.
- Packaged skills, custom commands, hooks, WASM extensions, MCP resources/prompts/sampling, and browser/service integrations.
- Focus mode, model-generated receipts, richer image rendering, extra palettes, and broader terminal personalization.
- Multiple saved accounts per built-in auth method, credential pools/rotation, fallback chains, local-model-specific workflows, staged tool-result pruning, and spending caps.

Claude subscription sign-in and a Z.ai Coding Plan preset are excluded from the MVP. Native ChatGPT sign-in remains required, with actual Mocha eligibility and inference as release gates. No telemetry, analytics, or automatic crash reporting is planned. Clean-room and dependency-license constraints apply throughout.
