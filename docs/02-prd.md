# Mocha Code — Product Requirements (MVP)

| | |
|---|---|
| Status | DRAFT, awaiting acceptance |
| Revision | 1 (2026-11-10) |
| Scope | MVP = milestones M0–M2 on Linux |
| Settled inputs | `docs/discovery/design-tree.json` (DEC-001…DEC-040, FCT-001…FCT-009), confirmed by the user: "confirmed, go ahead and write the PRD" |
| Detailed references | `DESIGN.md` v2 (look and feel), `docs/FEATURES.md` (feature catalog), `docs/research/2026-11-10-mocha-engineering-blueprint.md` (engineering) |
| Profile | Lean (DEC-039): this PRD, a short `docs/04-architecture.md`, slice folders, `docs/GLOSSARY.md`, `AGENTS.md` |

This document says **what** the MVP must do and how we will know. The references say how it looks and how it is built. Where they disagree with this PRD, this PRD wins and the reference gets fixed (see §9).

---

## 1. Product intent

Mocha Code is a clean-room Rust coding agent harness: one static binary, a terminal UI, and a headless mode, built around a versioned protocol so the same core can later serve a background daemon, editors and an SDK (DEC-001, DEC-003).

**Thesis.** A harness that is small, fast and honest about its safety boundary beats one with more features that is heavy and loses work. Lightweight is a feature with numbers (DEC-002, DEC-040).

**Clean-room rule.** No code is copied from Pi, Jcode, Codex, Grok Build or leaked Claude Code source. Other projects inform ideas and published numbers only. Matching a file layout the user already uses (FCT-009) is format compatibility and is allowed (DEC-001, DEC-036).

## 2. Users and jobs

| User | Job | Notes |
|---|---|---|
| **The maintainer (primary)** | Do all daily coding-agent work in Mocha: fix bugs, write features, review changes, across several providers and models | Built for this user first. Apex-Code is already retired (DEC-015, DEC-017). |
| Curious developers (secondary) | Read the code, file issues, try a release | Public MIT repo; no launch or support promise yet; outside code contributions only after the public beta (DEC-008, DEC-021). |

## 3. Scope

### 3.1 MVP boundary

| Milestone | Delivers | Exit |
|---|---|---|
| **M0 — Skeleton and instruments** | Workspace, in-process protocol, mock provider, bench rig, CI with budgets; SLICE-001 walking skeleton | Welcome screen, prompt, mock streamed reply at ≤ 20 ms / ≤ 12 MB, budgets enforced in CI |
| **M1 — The agent first** | Real agent loop, `mocha run`, core tools with read-before-write, Anthropic + OpenAI Chat formats, sessions, automatic compaction and output spill, plain TUI (top bar, transcript, composer) | Mocha fixes a bug in its own repo end to end, headless and in the plain TUI |
| **M2 — Safe daily driver** | Permission modes and rules, Linux sandbox, trust, checkpoints and rewind, hidden-instruction protections, MCP client, OpenAI Responses + Gemini formats, Sign in with ChatGPT, full TUI (dock, scroll/search/copy, rail, welcome) | Usable as the maintainer's only harness |

Order rule (DEC-037): the loop is made reliable before the richer interface is built. Nothing in M2's interface work may start before M1's exit is met.

### 3.2 Non-goals for the MVP

- M3–M7 work from the blueprint, except basic compaction and output spill, which move into M1 (DEC-035). Staged pruning of stale tool results stays M3.
- Background daemon, multiple attached clients, sub-agents, worktrees, ACP, SDK (M4–M6). The protocol boundary exists from M0 so these need no rewrite (DEC-003).
- Hooks, skills, custom commands and custom agents beyond reading `AGENTS.md` / `CLAUDE.md` (DEC-004, later milestones).
- MCP resources, prompts and sampling; MCP is tools only (DEC-032).
- Focus mode (DEC-037). The Pour, Ledger and Focus prototype variants are not product.
- Claude subscription sign-in, in any form (DEC-027).
- A Z.ai Coding Plan preset (DEC-028, DEC-033).
- macOS and Windows builds (DEC-006).
- Spending caps, paid evaluations, comparisons with Apex (DEC-017, DEC-020).
- Telemetry of any kind (DEC-014).
- Local-model support as a headline (DEC-002; P2).

## 4. Success measures

These are goals, not gates on the project (DEC-017). The performance budgets are the one exception: they gate individual changes in CI (DEC-040).

| Measure | Target | How it is observed |
|---|---|---|
| Mocha is the only coding harness the maintainer uses | Yes, from the end of M2 | The maintainer's own report |
| Stays light | Every budget in NFR-001 holds on every merged change | CI bench results committed as JSON |
| Never loses work | Zero sessions or file changes lost to a crash, kill or bad edit | NFR-002 tests; any loss is a P0 bug |
| Agent quality does not silently regress | Replay suite green on every change | NFR-005 |

---

## 5. Functional requirements

Priorities: **P0** must ship in the MVP; **P1** should ship in the MVP but may slip one milestone without blocking it. Each requirement names its milestone.

### FR-001: Walking skeleton
**P0 · M0 · DEC-025, SLICE-001**
As the maintainer, I start `mocha` and see the welcome screen, type a prompt, and watch a streamed reply from the mock provider, so the whole path (binary → protocol → engine → provider → render) exists from day one.
- Given a fresh install and no config, when I run `mocha`, then the welcome screen is ready for input within the NFR-001 startup budget.
- Given the welcome screen, when I type a prompt and press Enter, then the mock provider's reply streams into the transcript token by token and the turn ends in a `Done` state.
- Given a running skeleton, when I press ctrl+c once, then Mocha shows the quit hint; when I press ctrl+c again before the hint expires, then Mocha exits with status 0 and restores the terminal. Any other key does not cancel the hint. The hint expires after 2 seconds.
- Given a running skeleton, when Mocha opens sockets, then it opens none for the network or for IPC. The terminal library's in-process signal pipe is allowed.
- Given a failed turn, when the provider or the engine reports an error, then the transcript shows a `✗` line with the message, and the pour turns red and bold. The `✗` mark and the bold attribute keep the failure visible under `NO_COLOR`. OSC 9;4 reports the error and clears when the turn ends.
- Given `mocha --theme <name>` or `MOCHA_THEME=<name>`, when Mocha starts, then the named palette (`dark` or `light`) is used. The flag overrides the environment variable.
- Given a protocol error, when the engine rejects a request, then the error code is one of `protocol_mismatch`, `empty_prompt`, `not_initialized`, `unknown_session`, `turn_in_progress` or `provider_failed`.
- Given a provider failure, when the stream ends with an error, then the turn state becomes `Failed`, and a new turn may start from that state.
- Failure: if the terminal cannot enter fullscreen, Mocha falls back to inline mode (DESIGN.md) instead of exiting.

### FR-002: Agent loop
**P0 · M1 · blueprint §5.3**
The engine runs each turn as an explicit state machine (`Idle → Streaming → ToolsPending → Executing → Streaming | Done | AwaitingPermission | Interrupted | BudgetExhausted`). Every transition is an event in the session log.
- Given a streaming turn, when I press Esc, then streaming stops within 50 ms, running child processes receive SIGINT then SIGKILL, and the turn ends `Interrupted` with partial output kept.
- Given a running turn, when I send a message with ctrl+enter, then the current step is interrupted and my message is sent now (interject); when I send it with tab, then it is queued and runs when the agent would otherwise stop (follow-up). Keys per DESIGN.md.
- Given a turn that makes the identical tool call repeatedly or oscillates between an edit and its revert, when the threshold is reached, then the agent is nudged once and then stopped with a typed reason.
- Given configured limits (turns, tokens, wall-clock, tool calls), when one is reached, then the turn ends `BudgetExhausted` naming which one. There is no dollar spending cap (DEC-020).
- Read-only tool calls in one batch run concurrently; writes to the same path are serialized.

### FR-003: Headless mode (`mocha run`)
**P0 · M1 · DEC-003**
`mocha run "<prompt>"` runs one task without the fullscreen UI, over the same protocol as the TUI.
- Given a prompt, when I run `mocha run "<prompt>"`, then progress and the final answer print to stdout and the process exits 0 on `Done`.
- Given `--json`, when the run proceeds, then every protocol event is written as one JSON line, suitable for scripts and the replay suite.
- Given an action that needs approval and no TTY, when the agent requests it, then the action is denied (never auto-approved) and the run exits non-zero with a reason, unless the mode allows it.
- Exit codes distinguish success, task failure, interruption, budget exhaustion, configuration error and provider error.

### FR-004: Core tools with read-before-write
**P0 · M1 · blueprint §5.5**
Built-in tools: `read`, `write`, `edit` (exact replace with uniqueness check and `replace_all`), `apply_patch` (multi-file), `grep`, `glob`/`ls`, `bash` (timeouts, background run/output/kill, process-group kill), `todo`, and `ask_user` (TUI only). Each tool declares a contract (capabilities, concurrency, output budget) that every other subsystem reads.
- Given a file the agent has not read in this session, when it calls `write` or `edit` on it, then the call is refused with a message telling it to read first.
- Given a file that changed on disk after the agent read it, when the agent edits it, then the edit is refused as stale and the agent is told to re-read.
- Given an `edit` whose search text is not found or not unique, when it runs, then it fails with the closest match and a whitespace hint, and the file is unchanged.
- Given any write, when it completes, then it was written by atomic rename (no partial files on crash).
- `grep` and `glob` respect `.gitignore`.

### FR-005: Evidence captured at the source
**P0 · M1 · blueprint §3 principle 7**
Tools record what actually happened: exit code, argv, duration, file hashes before and after, patch hash. The model's claims are never the record.
- Given a `bash` call, when it finishes, then the session log holds its argv, exit code, duration and output size, whatever the model says about it.
- Given an edit, when it applies, then the log holds the file's hash before and after.
- Given the TUI, when a tool row is shown, then its stats (lines changed, exit code, time) come from the recorded evidence.

### FR-006: Providers and models from `models.json`
**P0 · M1 · DEC-016, DEC-030, DEC-031, DEC-036, FCT-009**
Any provider and model is added by editing `~/.mocha/models.json`, never by changing code. The layout matches the user's existing file:

```jsonc
{ "providers": { "<name>": {
    "baseUrl": "https://…", "api": "openai-completions | openai-responses | anthropic-messages | gemini",
    "authHeader": true,
    "models": [ { "id": "…", "name": "…", "reasoning": true, "input": ["text", "image"],
                  "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },   // per 1M tokens
                  "contextWindow": 0, "maxTokens": 0, "api": "<optional per-model override>",
                  "thinkingLevelMap": { "minimal": null, "high": "high" },
                  "compat": { "thinkingFormat": "…", "supportsDeveloperRole": false, "…": "…" } } ] } } }
```

(Illustrative; the validated schema lives with the architecture.)
- Given a copy of `~/.apex-code/agent/models.json` placed at `~/.mocha/models.json`, when Mocha starts, then every provider and model in it is selectable with no edits.
- Given an unknown field, when the file loads, then Mocha warns once, naming the field, and keeps loading.
- Given a malformed file, when Mocha starts, then it reports the file, line and problem, and starts with the last good copy saved at a prompt, or with no providers when no prompt has saved one yet, not a crash. A start with no prompt writes nothing under `MOCHA_HOME`. (CHG-003)
- Given a `models.json` that loads and differs from the copy on disk, when the first prompt is sent, then that copy is saved; a failed save is tried again at the next prompt. (CHG-003)
- Given a model entry missing limits, when it is selected, then Mocha fills known values from a public model catalog when available, and otherwise asks only for what is missing.
- Given a `thinkingLevelMap` entry mapped to `null`, when that level is chosen, then the level is shown as unavailable for that model.
- `compat` flags change request and response handling for that model only (for example sending reasoning content back on assistant messages).
- API keys are never read from or written to `models.json` (see FR-020).

### FR-007: Wire formats and presets
**P0 · M1 (Anthropic Messages, OpenAI Chat Completions) · M2 (OpenAI Responses, Gemini) · DEC-026, DEC-028**
- Given a provider using any of the four formats, when a turn runs, then text, reasoning, tool calls, tool results, images and usage round-trip correctly, verified by recorded fixtures for each format.
- Presets ship pre-filled for DeepSeek, Z.ai's regular API (`https://api.z.ai/api/paas/v4`) and TheClawBay; each preset has fixture tests.
- Given a provider that reports usage, when a turn ends, then the reported usage is taken as truth for tokens and cost shown.
- Given a provider error (rate limit, overload, auth, context too long), when it occurs, then it is shown with its type and the action Mocha took (retry with backoff, compact, or stop).

### FR-008: Sign in with ChatGPT
**P0 · M2 · DEC-019, FCT-006**
The user can sign in with a ChatGPT plan through OpenAI's official open-source flow (PKCE, a `127.0.0.1` callback, the Responses API).
- Given `mocha login chatgpt`, when I complete sign-in in the browser, then tokens are stored in the system keychain and ChatGPT models become selectable.
- Given an expired access token, when a request is made, then it is refreshed without asking me; if refresh fails, I am told to sign in again and nothing else breaks.
- Given `mocha logout chatgpt`, when it runs, then the stored tokens are removed.
- The callback listens only on `127.0.0.1` and only during sign-in.

### FR-009: Context management
**P0 · M1 · DEC-035, blueprint §5.4**
- The prompt is laid out for prefix-cache hits: system prompt, tool schemas in a fixed order, instruction files, environment block, then conversation.
- Given a session approaching the model's context window, when the next request would exceed the compaction threshold, then Mocha writes a structured handoff summary (goal, decisions, files touched, open todos, working-tree state), replaces earlier turns with it, records the compaction in the log, and continues the turn without my input.
- Given a provider "prompt too long" error, when it occurs, then Mocha compacts and retries once.
- Given a tool output larger than its output budget, when it returns, then the full output is saved to a file under the session folder and the model receives a truncated view plus the path, which it can `read` in parts.
- Given a compacted session, when I scroll back in the TUI, then the original turns are still visible from the log; only the model's view was compacted.

### FR-010: Durable sessions
**P0 · M1 · DEC-017, DEC-022**
Every session is an append-only log under `~/.mocha/sessions/`, flushed to disk at least at every turn boundary and every tool result.
- Given Mocha is killed with SIGKILL mid-turn, when I run `mocha -c`, then the session resumes with every completed tool result and all streamed text up to the last flush, and the interrupted turn is marked as such.
- Given `mocha --resume <name>` or `mocha sessions`, when run, then I can find and reopen any past session in this project.
- Given a log written by an older Mocha version, when it is opened, then it is migrated automatically and the original is kept as a backup.
- Given a 10k-entry log, when resumed, then it is ready within the NFR-001 budget.
- Given several sessions created in one engine before any prompt, when each is created, then each gets an ID that no other session of that engine has, and none of them writes a file until its first prompt. (CHG-002)
- Given a session ID handed out by `session.create`, when another create happens in the same process, then that ID is not returned again, even though no file exists for it yet. (CHG-002)

### FR-011: Permission modes and rules
**P0 · M2 · DEC-009, docs/FEATURES.md §7**
Modes: `rip` (default), `careful`, `plan`, `yolo`. Every action gets a risk tier 0–4 (safe → recoverable with checkpoint → reflection → ask → absolute block). Rules `{allow | deny | ask, tool, pattern}` come from CLI, trusted project and user config; deny always beats allow.
- Given `bash` input with pipelines, `&&`, subshells or `$(…)`, when it is classified, then each simple command is parsed with a real shell parser (not regex) and matched separately.
- Given an action at the "ask" tier, when the agent requests it, then the dock shows a preview (diff for edits, parsed argv for commands) with allow once / this session / always (writes a rule) / deny.
- Given a tier-4 action (for example writing to `~/.ssh` or Mocha's own credential store), when requested in any mode including `yolo`, then it is blocked.
- Given `plan` mode, when the agent tries any write or command with side effects, then it is refused.
- Safety lives in code paths, not in prompt text (DEC-024).

### FR-012: Linux sandbox
**P0 · M2 · DEC-009, blueprint §5.6**
Commands run by `bash`, and MCP stdio servers, run inside an OS sandbox on Linux (filesystem limited to the workspace and declared paths; network off unless allowed).
- Given the sandbox is enabled, when a command tries to write outside the allowed paths, then the write fails and the attempt is shown.
- Given the sandbox is requested but the platform cannot provide it, when a command would run, then it does not run (fail closed) and `mocha doctor` explains why.
- The docs and `mocha doctor` state exactly what the sandbox does and does not cover.

### FR-013: Project trust
**P0 · M2 · DEC-009, DEC-031**
- Given a repository opened for the first time, when Mocha starts, then nothing from it (`.mocha/config.toml`, `.mcp.json`, instruction-file directives that change permissions) is loaded until I answer the trust prompt.
- Given I decline trust, when the session runs, then only my user config applies and the repo's `AGENTS.md` is read as plain guidance with no power to grant permissions.
- Given a trusted repo whose trusted files change, when Mocha starts next, then I am asked again.

### FR-014: Checkpoints and rewind
**P0 · M2 · DEC-009**
- Given a mutating tool batch, when it is about to run, then the working tree is snapshotted in a shadow repository that never touches my git refs, index or stash.
- Given ctrl+z or `/rewind`, when I choose a point, then I can restore code, conversation, or both.
- Given files changed outside Mocha since the checkpoint, when I rewind, then I am shown the conflict and asked before anything is overwritten.

### FR-015: Hidden-instruction protections
**P0 · M2 · DEC-024**
Tool output, file contents, web content and MCP results are treated as data, not instructions.
- Given untrusted content enters the context, when it does, then it is wrapped and labeled as untrusted, and the session is marked tainted.
- Given a tainted session, when the agent tries to send data off the machine (network commands, web requests with query data, MCP calls to remote servers) or to touch credentials, then the action is raised at least to the "ask" tier, whatever the mode except an explicit user rule naming it.
- Given content claiming to be from the user or system, when it arrives through a tool, then it gains no authority.
- The automated trick-test suite (NFR-006) covers each of these.

### FR-016: MCP client
**P0 · M2 · DEC-032**
- Given servers in `~/.mocha/mcp.json` or a trusted project's `.mcp.json`, when a session starts, then stdio and Streamable HTTP servers connect and their tools become available, deferred by default and loaded on demand.
- Given a server that fails to start or disconnects, when it happens, then the session continues without it and the failure is shown once.
- Given an untrusted project, when it contains `.mcp.json`, then those servers do not start (FR-013).
- MCP tool calls go through the same permission engine as built-in tools, and MCP results are untrusted content (FR-015).

### FR-017: Instruction files
**P0 · M1 · DEC-007**
- Given `AGENTS.md` in the repo (and parent folders up to the repo root), when a session starts, then its contents are included in the prompt; `CLAUDE.md` is read when no `AGENTS.md` exists at that level.
- Given a global `~/.mocha/AGENTS.md`, when present, then it is included before project files.

### FR-018: Plain TUI
**P0 · M1 · DEC-013, DEC-037, DESIGN.md v2**
The first interface: top bar with the pour line, transcript with tool rows and inline stats, composer on the "you" band, cup spinner, Volt palette, full-width diff tints including removed-line `del_bg`.
- Given a running turn, when it progresses, then the pour line fills and the terminal's own progress indicator mirrors it (OSC 9;4) where supported.
- Given a terminal without truecolor, when Mocha renders, then it degrades to 256 or 16 colors and stays legible; `NO_COLOR` is honored.
- Given a resize, when it happens, then the layout reflows without corrupting the transcript.

### FR-019: Full TUI
**P0 · M2 · DEC-013, DEC-034, FCT-005, DESIGN.md v2**
Fullscreen is the default; inline mode is a fallback and a setting.
- Given output longer than the screen, when I use the wheel, PgUp/PgDn or End, then the transcript scrolls; while scrolled back, new output never moves what I am reading (pinned to an absolute line); End resumes following.
- Given I drag to select, when I release, then the selected **source text** (no gutters, no wrap breaks, no styling characters) is copied to the clipboard via OSC 52 and a toast confirms it; shift+drag is left to the terminal.
- Given ctrl+f, when I type, then matches highlight across the whole transcript with "n of m" and Enter/↑/↓ move between them.
- Given an approval or question, when it is needed, then it appears in the dock above the composer, never as a modal over the transcript.
- Given a terminal ≥ 140 columns, when alt+r is pressed or the setting is on, then the side rail shows Plan, Agents, Changed and Checkpoints.
- Given no session yet, when Mocha opens, then the welcome screen shows the Cup mark, model, folder and recent sessions.
- Dark and light Volt themes; theme follows the terminal background when it can be detected.

### FR-020: Configuration and secrets
**P0 · M1 · DEC-031**
- All user state lives under `~/.mocha/` (`config.toml`, `models.json`, `mcp.json`, `sessions/`, `skills/`, `agents/`); `MOCHA_HOME` overrides the location.
- Project overrides live in `.mocha/config.toml` and `.mcp.json`, loaded only after trust (FR-013).
- Given a provider key, when configured, then it comes from an environment variable named in config or from the system keychain; Mocha never writes a key in plain text and never prints one in logs, the transcript or `--json` output.
- Given a config file from an older version, when loaded, then it is migrated automatically with a backup (DEC-022).

### FR-021: `mocha doctor`
**P1 · M1 (basic) · M2 (complete) · DEC-029**
- Given `mocha doctor`, when run, then it reports: binary version and signature status, terminal capabilities (truecolor, OSC 52, OSC 9;4, mouse), config and `models.json` validity, which keys resolve (never their values), sandbox availability and coverage, and whether another `mocha` (for example the npm test runner) shadows this one on `PATH`.

### FR-022: Versioned protocol boundary
**P0 · M0 · DEC-003, DEC-022**
Every client (TUI, `mocha run`) talks to the engine only through the protocol: versioned JSON requests with IDs and correlated events. In the MVP the transport is in-process.
- Given a client and engine, when they connect, then they exchange protocol versions; a mismatch produces a clear error naming both versions.
- No client code calls engine internals directly; a CI check enforces the dependency direction.

### FR-023: Release and install
**P0 · M2 · DEC-023**
- Given a tagged release, when CI builds it, then static Linux x86_64 and arm64 binaries are published on GitHub Releases with SHA-256 checksums and minisign signatures.
- Given `cargo install mocha-code`, when it completes, then the `mocha` command is installed.
- Publishing a release and signing stay with the maintainer; CI prepares artifacts, the maintainer approves the publish.

### FR-024: Z.ai Coding Plan notice
**P1 · M1 · DEC-033, FCT-007**
- Given a provider whose `baseUrl` is a known Z.ai Coding Plan endpoint, when first used, then Mocha shows a one-time notice that Z.ai limits the Coding Plan to officially supported tools and has not listed Mocha, and then works normally. Nothing is blocked.

---

## 6. Non-functional requirements

### NFR-001: Performance budgets gate every change
**P0 · M0 onward · DEC-040, blueprint §6**
CI measures these on every change and rejects one that breaks a budget until it is fixed or the budget is raised in a deliberate, reviewed change.

| Metric | MVP budget |
|---|---:|
| Start to input ready | ≤ 20 ms |
| Client memory (RSS) at idle | ≤ 12 MB |
| Keystroke → paint, p99 | ≤ 8 ms |
| Streaming render CPU, one session, fast mock stream | ≤ 3 % of one core |
| Harness overhead per tool call (excluding the tool) | ≤ 1 ms |
| Resume a 10k-entry session log | ≤ 100 ms |
| Stripped binary size | ≤ 25 MB |

Daemon budgets (≤ 60 ms with spawn, ≤ 30 MB daemon, ≤ 3 MB per extra session) apply from M4. Until then the in-process engine counts against the client budget. Measured with `hyperfine`, an RSS/CPU sampler and a PTY harness against the mock provider; results committed as JSON.

### NFR-002: Never lose work
**P0 · M1 onward · DEC-017**
- Session logs and file writes survive SIGKILL, power-loss-style truncation of the last log line, and disk-full errors without corrupting earlier entries.
- A truncated final log line is detected and dropped on resume, with a notice.
- Disk-full stops the turn with a clear error rather than writing partial state.
- Tested by kill-and-resume tests in CI.

### NFR-003: Privacy
**P0 · DEC-014**
No telemetry, analytics or crash reporting leaves the machine. Prompts and code go only to providers the user configured. `mocha doctor` and the README state this.

### NFR-004: Clean-room and licenses
**P0 · DEC-001, DEC-008**
- The project is MIT. Every dependency's license is checked against an allowlist in CI (`cargo-deny`); a disallowed license fails the build.
- No code from the projects named in §1. Contributions (after beta) include a statement that the code is the contributor's own.

### NFR-005: Deterministic tests and replay regression suite
**P0 · M1 onward · DEC-020, DEC-038**
- CI uses only the mock provider; no paid API call ever runs in CI.
- Recorded sessions are replayed through the mock provider on every change and checked for: tools receiving the expected inputs, edits applying, permission prompts firing where expected, and compaction keeping the key facts (goal, files touched, open todos).
- Parsers that read untrusted input (SSE streams, patches, the shell parser, config files) are fuzzed.

### NFR-006: Hidden-instruction trick-test suite
**P0 · M2 · DEC-024**
An automated suite of adversarial fixtures (instructions hidden in files, command output, web pages and MCP results; exfiltration attempts; fake "system" messages; attempts to edit trust or permission config) runs in CI against the mock provider. Every case must end with the harmful action refused or raised to "ask".

### NFR-007: Compatibility
**P0 · DEC-022**
0.x releases may change behavior, but saved data (session logs, config, `models.json`) is versioned and always migrates forward automatically, keeping a backup. The protocol carries a version and fails clearly on mismatch.

### NFR-008: Accessibility and terminal robustness
**P1 · M1–M2 · DESIGN.md v2**
No information is conveyed by color alone (glyphs or text accompany status colors); `NO_COLOR` and reduced-motion settings are honored; the UI works at 80×24; keyboard alone can reach every action.

### NFR-009: Secret hygiene
**P0 · M1 onward · DEC-031**
Keys and tokens never appear in plain-text files written by Mocha, logs, session logs, `--json` output or crash output. A CI test feeds known fake secrets through every output path and fails if any appear.

---

## 7. Risks and assumptions

| ID | Risk | Severity | Mitigation | Owner |
|---|---|---|---|---|
| RISK-001 | MVP scope is large for one person (MCP, ChatGPT sign-in, four formats, full TUI) | High | Loop-first order (DEC-037); P1 items may slip a milestone; slices stay vertical | Maintainer |
| RISK-002 | Fullscreen must rebuild scroll, search and copy that inline mode gets free | Medium | Spike passed (FCT-005); inline fallback kept; copy uses source text | Maintainer |
| RISK-003 | npm `mocha` name clash on `PATH` | Low | `mocha doctor` warns; crate `mocha-code` (FCT-001, DEC-029) | Maintainer |
| RISK-004 | Provider quirks make "compatible" APIs misbehave | Medium | Per-model `compat` flags and fixtures per format and preset (DEC-036) | Maintainer |
| RISK-005 | Using a Z.ai Coding Plan endpoint outside listed tools breaks Z.ai's terms | Medium, user-accepted | No preset, one-time notice, request listing around M1 (DEC-033) | Maintainer |
| RISK-006 | OpenAI changes or narrows Sign in with ChatGPT for third-party apps | Medium | Isolated module; BYOK still works; re-check at M2 (FCT-006) | Maintainer |
| RISK-007 | Performance budgets slip as features land | Medium | CI gate per change (NFR-001) | Maintainer |
| RISK-008 | Sandbox gives a false sense of safety | High | Fail closed; exact coverage stated in docs and doctor (FR-012) | Maintainer |

| ID | Assumption | Status |
|---|---|---|
| ASM-001 | TheClawBay places no client restriction on Mocha (Terms page not yet read) | UNVERIFIED, check before the preset ships (FCT-008) |
| ASM-002 | Z.ai regular API endpoint and behavior match the preset | Check docs.z.ai before the preset ships |
| ASM-003 | `hyperfine` will be installed for the bench rig | Install before SLICE-001 (FCT-003) |

### 7.1 Regulatory screen

Not legal advice; re-screen if Mocha is ever sold.

| Trigger | Applicability | Source | Accessed | Specialist review |
|---|---|---|---|---|
| EU Cyber Resilience Act | DOES_NOT_APPLY (non-commercial FOSS) | https://digital-strategy.ec.europa.eu/en/policies/cra-open-source | 2026-11-10 | No |
| Personal data (GDPR, US state privacy) | DOES_NOT_APPLY (no telemetry, no accounts, data stays local) | docs/FEATURES.md §15 | 2026-11-10 | No |
| AI in the product (EU AI Act, vendor terms) | APPLIES (general-purpose tool on third-party models; not high-risk; vendor terms per RISK-005/006) | DEC-005, DEC-019 | 2026-11-10 | No |
| Payments, billing, tax | DOES_NOT_APPLY (free, MIT) | DEC-008 | 2026-11-10 | No |
| Accessibility law | DOES_NOT_APPLY (NFR-008 still sets targets) | — | 2026-11-10 | No |
| App stores | DOES_NOT_APPLY (GitHub Releases, crates.io) | DEC-023 | 2026-11-10 | No |
| Regulated domains | DOES_NOT_APPLY | — | 2026-11-10 | No |
| Licenses and IP | APPLIES (cargo-deny allowlist, clean-room rule; NFR-004) | DEC-001, DEC-008 | 2026-11-10 | No |

## 8. Release gates

| Gate | Condition |
|---|---|
| M0 done | FR-001, FR-022, NFR-001 gate live in CI |
| M1 done | FR-002…FR-007 (M1 formats), FR-009, FR-010, FR-017, FR-018, FR-020 pass; Mocha fixes a bug in its own repo end to end; NFR-002, NFR-005, NFR-009 green |
| M2 done (MVP) | All P0 requirements pass; NFR-006 green; the maintainer uses Mocha as the only harness |
| Any release | Signed artifacts (FR-023); publishing approved by the maintainer |

## 9. Changes this PRD makes to the references

The architecture step will update the references to match:
- **Blueprint §9 build sequence:** MCP client, Linux sandbox, OpenAI Responses + Gemini formats and Sign in with ChatGPT move into M2; basic compaction and output spill move into M1; Focus mode moves after the MVP.
- **Blueprint §5.7:** session logs live in `~/.mocha/sessions/`, not `~/.local/share/mocha/` (DEC-031).
- **Blueprint §6:** daemon budgets apply from M4; in the MVP the in-process engine counts against the client budget.
- **Prototype gap:** `del_bg` (removed-line tint) is added to the theme tokens (FR-018).
