# Mocha Code — Architecture and Build Plan (MVP)

| | |
|---|---|
| Status | ACCEPTED (revision 4, see Revision history) |
| Revision | 4 (2026-11-12) |
| Built on | `docs/02-prd.md` revision 3 (ACCEPTED: "accept CHG-002 and CHG-003") |
| Long-form reference | `docs/research/2026-11-10-mocha-engineering-blueprint.md` (the blueprint). This document only records what the MVP builds, where it differs from the blueprint, and the guardrails that enforce it. |

---

## 1. Shape

One static binary, `mocha`. Inside it, clients talk to an engine only through a versioned protocol (FR-022). In the MVP the transport is an in-process channel; the daemon (M4) swaps the transport, not the code.

```
 mocha (TUI) ──┐                                   ┌── mocha-llm ── providers (HTTPS)
               ├─ mocha-proto ─(in-process chan)─ mocha-engine ─┼── mocha-tools ── workspace, child processes
 mocha run  ───┘   requests ↓  ↑ events           │            ├── mocha-policy ── rules, tiers, sandbox
                                                   │            ├── mocha-mcp ── MCP servers (stdio / HTTP)
                                                   └────────────┴── mocha-store ── ~/.mocha/sessions, checkpoints
```

**Trust boundaries**
1. *User ↔ Mocha:* keystrokes and config the user owns are trusted. Repo config is trusted only after the trust prompt (FR-013).
2. *Mocha ↔ model:* model output is untrusted. Every tool call it makes passes the policy engine; the model cannot grant itself anything (FR-011).
3. *Mocha ↔ world:* file contents, command output, web content and MCP results are untrusted data and taint the session (FR-015).
4. *Mocha ↔ OS:* commands and MCP stdio servers run in the Linux sandbox when enabled, failing closed (FR-012).

## 2. Crates for the MVP

Start with these; split only when a crate's compile time or interface demands it. Blueprint §4.3 crates `mocha-server`, `mocha-ext` and `mocha-embed` are not created until their milestones.

| Crate | Owns | Depends on |
|---|---|---|
| `mocha-core` | Message IR (text, thinking with signature, tool_use, tool_result, image), IDs, errors, config types, `models.json` and `config.toml` parsing, the redactor (`Redactor`, SLICE-003). No async, no IO. | serde, serde_json, toml |
| `mocha-proto` | Protocol requests/events, version handshake, JSON Schema generation | core |
| `mocha-store` | Session JSONL logs, migration, spill files, checkpoint shadow repo | core |
| `mocha-llm` | Four wire formats, streaming parser, `compat` handling, retries, key resolution, ChatGPT sign-in, mock provider | core |
| `mocha-policy` | Modes, tiers, rules, bash analysis, trust store, taint rules, Linux sandbox | core |
| `mocha-tools` | Tool contract trait and built-in tools, read ledger, evidence | core, policy |
| `mocha-mcp` | MCP client (stdio, Streamable HTTP), tools only | core, policy |
| `mocha-engine` | Agent loop state machine, context layout, compaction, budgets, queues | core, proto, store, llm, policy, tools, mcp |
| `mocha-tui` | Renderer and widgets per DESIGN.md v2 | core, proto (**never** engine) |
| `mocha` (bin, crate name `mocha-code`) | CLI parsing, composition, `run`, `doctor`, `login` | all |
| `xtask` | Bench rig, dependency-direction check, release prep | dev only |

Dependency rule: lower rows never import upward; `mocha-tui` and `mocha run` reach the engine only through `mocha-proto` (enforced by G-02).

## 3. Subsystem decisions for the MVP

Blueprint §5 is the long-form design. Below is what the MVP implements and every deliberate difference.

### 3.1 Protocol (FR-022)
JSON-RPC 2.0 shaped messages with `v` (protocol version) and request IDs, as Rust types in `mocha-proto`. Handshake first; mismatch is an error naming both versions. Text deltas are coalesced to ≤ 60 Hz per client. `mocha run --json` prints these events verbatim, so the headless output *is* the protocol and the replay suite records it.

### 3.2 Agent loop (FR-002)
State machine per blueprint §5.3. One `CancellationToken` tree per session (session → turn → tool → child process group). Interject (ctrl+enter) cancels the current step at the next safe point and submits; follow-up (tab) queues. Loop detection: same tool + same arguments 3 times, or edit/revert of the same hunk twice → nudge, then stop with reason `Loop`. Budgets: turns, tokens, wall-clock, tool calls; no dollar cap (DEC-020).

### 3.3 Providers (FR-006, FR-007, FR-008, FR-024)
- One `WireFormat` trait, four implementations: `anthropic-messages`, `openai-completions`, `openai-responses`, `gemini`. Lossless IR round-trip; Anthropic thinking signatures preserved.
- Hand-written incremental SSE parser over `bytes::Bytes` (fuzzed, NFR-005).
- `compat` flags are a typed struct with an `extra` map for unknown keys (warn once). Known keys from FCT-009: `supportsStrictMode`, `forceAdaptiveThinking`, `supportsTemperature`, `supportsStore`, `supportsDeveloperRole`, `requiresReasoningContentOnAssistantMessages`, `thinkingFormat`, `maxTokensField`.
- Model catalog: a build-time snapshot of public model metadata fills missing limits (FR-006), built and used from SLICE-004; no background refresh in the MVP (M3). SLICE-003 loads and validates `models.json` without it.
- Retries: jittered backoff honoring `retry-after`; no credential pools or fallback chains (M3).
- **Mock provider:** an in-process provider that streams recorded fixtures at a configurable tokens/second, plus a local HTTP fixture server that speaks each wire format, so format code is tested over real HTTP without a network.
- **Sign in with ChatGPT:** PKCE with a loopback listener bound to `127.0.0.1` only for the duration of sign-in; tokens in the keychain; models served over the Responses format. Endpoint details are taken from OpenAI's official open-source client at build time of that slice and recorded with source and date (clean-room: read the protocol docs, write our own code).
- Z.ai Coding Plan notice: a small list of known Coding Plan base URLs (FCT-007) checked on first use.

### 3.4 Context (FR-009, FR-017)
Layout in cache order: core system prompt → tool schemas (stable byte order) → instruction files (global `~/.mocha/AGENTS.md`, then repo root down to cwd; `CLAUDE.md` where no `AGENTS.md`) → environment block → conversation. Token accounting trusts provider usage, with a byte-based estimate for planning. Compaction threshold default 80 % of the model's window (or the session ceiling); summary produced by the same model with a fixed handoff template (goal, decisions, files touched, open todos, working-tree state). Compaction is an event in the log; the TUI keeps showing original turns. Output spill: results over the tool's output budget are written to `~/.mocha/sessions/<project>/<session>/spill/<n>.txt` and the model gets head + tail + path.

### 3.5 Tools (FR-004, FR-005)
MVP set: `read`, `write`, `edit`, `apply_patch`, `grep`, `glob`, `ls`, `bash` (+ background run/output/kill), `todo`, `ask_user`. Not in the MVP: `outline`, `lsp`, `web_fetch`/`web_search`, `delegate`, `memory_note`, `tool_search` for built-ins (MCP tools are still deferred, FR-016). Read ledger: per session, path → (content hash, mtime, ranges read). Writes require a ledger entry whose hash matches the file on disk. `bash` runs through a PTY-less pipe by default with a process group; interactive PTY is M3.

**Until permissions land (SLICE-009), M1 runs with a fixed safe default:** reads run freely; every write, edit and command asks in the TUI and is denied in `mocha run` unless `--allow-writes` is passed. This keeps M1 dogfooding safe without building the full policy engine first.

### 3.6 Policy, trust, sandbox (FR-011…FR-015)
- Tier classification and rules per FEATURES.md §7 and blueprint §5.6. Bash analysis with `tree-sitter-bash`; unparseable input is tier 3 ("ask").
- Trust store: `~/.mocha/trust.toml`, keyed by repo root path + hash of the trust-relevant files; a change re-prompts.
- Taint: a session flag set when untrusted content enters context. While set, the exfiltration classifier raises network-capable commands, URL-bearing tool calls and remote MCP calls to "ask", unless a user rule names the exact action.
- Sandbox: Landlock for filesystem (workspace + declared writable roots + temp), Landlock network rules plus a seccomp filter that blocks creating non-Unix sockets when network is off. Applied in the child before `exec`. If the kernel lacks the needed Landlock ABI, the sandbox is "unavailable" and commands fail closed when it was requested. `bubblewrap` is not used in the MVP.

### 3.7 Store (FR-010, FR-014, NFR-002)
- Sessions: `~/.mocha/sessions/<project-hash>/<session-id>.jsonl` (DEC-031; the blueprint's `~/.local/share/mocha` path is superseded). First line is a header with `schema` version. Appends are line-buffered; `fsync` after each tool result and at turn end. A torn last line is detected and dropped on load.
- Session list: read headers and a small `index.json` per project, rebuilt if missing. **No SQLite in the MVP** (ADR-004); full-text search across sessions is M3.
- Checkpoints: shadow repository via the `git` CLI with its own `GIT_DIR` under the session folder and `GIT_WORK_TREE` = workspace; never touches the user's refs, index or stash. If `git` is missing, checkpoints are unavailable, tier-1 actions are treated as tier 3, and `mocha doctor` says so.

### 3.8 TUI (FR-001, FR-018, FR-019)
`ratatui` + `crossterm`, single-threaded render loop on a `current_thread` runtime. Fullscreen by default with inline fallback. The transcript is rendered from a model of **source blocks** (message text, tool rows, diffs) laid out into screen lines with a back-map, so selection copies source text (FCT-005). Scroll pins to an absolute line. Search runs over source text. Clipboard via OSC 52 only. Themes: Volt dark/light tokens from DESIGN.md, including `del_bg`. SLICE-001's welcome screen is minimal (mark, model, folder); recent sessions and the full welcome land in M2 (DEC-037).

### 3.9 Config and secrets (FR-020, NFR-009)
`~/.mocha/` (`MOCHA_HOME` overrides): `config.toml`, `models.json`, `mcp.json`, `trust.toml`, `sessions/`, `skills/`, `agents/`. Precedence: CLI > env `MOCHA_*` > trusted project `.mocha/config.toml` > user > defaults. Managed `/etc` policy and profiles are post-MVP. Keys: `keyEnv = "NAME"` in a provider entry or a keychain item `mocha/<provider>`; on Linux the keychain is the Secret Service. If no Secret Service is running, env vars still work and `mocha doctor` says the keychain is unavailable; there is no plain-text file fallback (stricter than blueprint §4.4). A redaction layer sits on every output sink (log, session log, transcript, `--json`, panic hook).

### 3.10 Release (FR-023)
`x86_64-unknown-linux-musl` and `aarch64-unknown-linux-musl`, release profile per blueprint §4.4, rustls TLS (no OpenSSL) so binaries are static. CI builds, checksums and attaches artifacts to a draft release; the maintainer signs with minisign locally and publishes. Signing keys never live in CI.

## 4. Dependencies

Versions checked on crates.io with `cargo info` on 2026-11-10. Pin minor versions in `Cargo.toml`; `Cargo.lock` is committed. Each new dependency beyond this table needs a one-line justification in the PR (job, alternatives, license).

| Crate / tool | Version | License | Job | Source |
|---|---|---|---|---|
| ratatui | 0.30.2 | MIT | TUI widgets/layout | https://github.com/ratatui/ratatui |
| crossterm | 0.29.0 | MIT | Terminal IO, mouse | https://github.com/crossterm-rs/crossterm |
| tokio / tokio-util | 1.54.1 / 0.7.20 | MIT | Async runtime, cancellation tokens | https://github.com/tokio-rs/tokio |
| serde / serde_json | 1.0.229 / 1.0.154 | MIT OR Apache-2.0 | Serialization | https://github.com/serde-rs |
| toml | 1.2.1 | MIT OR Apache-2.0 | `config.toml` | https://github.com/toml-rs/toml |
| reqwest | 0.13.5 | MIT OR Apache-2.0 | HTTPS to providers (rustls) | https://github.com/seanmonstar/reqwest |
| rmcp | 3.9.0 | Apache-2.0 | MCP client (`client`, `transport-child-process`, `transport-streamable-http-client-reqwest`) | https://github.com/modelcontextprotocol/rust-sdk |
| keyring | 4.2.0 | MIT OR Apache-2.0 | Secret Service keychain | https://github.com/open-source-cooperative/keyring-rs |
| landlock | 0.4.7 | MIT OR Apache-2.0 | Filesystem/network sandbox | https://github.com/landlock-lsm/rust-landlock |
| seccompiler | 0.5.0 | Apache-2.0 OR BSD-3-Clause | Syscall filter | https://github.com/rust-vmm/seccompiler |
| tree-sitter / tree-sitter-bash | 0.27.2 / 0.25.1 | MIT | Bash command analysis | https://github.com/tree-sitter |
| ignore / grep-searcher | 0.4.34 / 0.1.17 | Unlicense OR MIT | In-process search, `.gitignore` | https://github.com/BurntSushi/ripgrep |
| similar | 3.2.1 | Apache-2.0 | Diffs for previews and tool rows | https://github.com/mitsuhiko/similar |
| thiserror | 2.0.21 | MIT OR Apache-2.0 | Error types | https://github.com/dtolnay/thiserror |
| tracing | 0.1.44 | MIT | Local diagnostics only (no export) | https://github.com/tokio-rs/tracing |
| cargo-deny (tool) | 0.20.2 | MIT OR Apache-2.0 | License/advisory/ban checks | https://github.com/EmbarkStudios/cargo-deny |
| hyperfine (tool) | 2.0.0 | MIT OR Apache-2.0 | Startup benchmark | https://github.com/sharkdp/hyperfine |
| minisign (tool) | 0.10.0 crate; maintainer uses the CLI | MIT | Release signatures | https://github.com/jedisct1/minisign |

Toolchain: Rust 1.96.1 pinned in `rust-toolchain.toml`; MSRV 1.90 (highest `rust-version` above: tree-sitter). Not chosen for the MVP: `rusqlite` (ADR-004), `portable-pty` (M3), `nucleo`, `syntect`, `mimalloc` (add only if the RSS budget needs it), `clap` (decide in SLICE-001 against binary size and startup; a small hand parser is the fallback). Not yet verified: whether reqwest 0.13's default TLS backend is rustls — SLICE-001 checks and sets features explicitly.

## 5. Guardrails

Each rule is enforced by a tool, not by prose. Status is PROPOSED until the CI job exists and has failed once on purpose.

| ID | Rule | Enforcing tool / command | Status | Failure behavior | Owner |
|---|---|---|---|---|---|
| G-01 | Performance budgets (NFR-001) | `cargo xtask bench --check budgets.json` (hyperfine + RSS/CPU sampler + PTY harness, mock provider) | PROPOSED | CI fails; change blocked until fixed or `budgets.json` raised in its own commit | Maintainer |
| G-02 | Crate dependency direction; TUI/bin never import engine internals | `cargo xtask deps` (reads `cargo metadata`) | PROPOSED | CI fails | Maintainer |
| G-03 | License allowlist, advisories, banned crates (OpenSSL) | `cargo deny check` with `deny.toml` | PROPOSED | CI fails | Maintainer |
| G-04 | Lints clean; `unsafe` forbidden except `mocha-policy::sandbox` | `cargo clippy --all-targets -- -D warnings`; `#![forbid(unsafe_code)]` per crate | PROPOSED | CI fails | Maintainer |
| G-05 | Formatting | `cargo fmt --check` | PROPOSED | CI fails | Maintainer |
| G-06 | No paid or networked provider calls in tests | CI sets no provider keys and `MOCHA_PROVIDER_LOCK=mock`; non-mock providers refuse to start under the lock. `MOCHA_PROVIDER_LOCK=loopback` (from SLICE-003) also lets a provider start when its `baseUrl` host is an IP literal in `127.0.0.0/8` or `::1`; host names never count as loopback, so no DNS lookup happens. CI keeps `mock` globally; only fixture tests set `loopback`, per command, and a test shows that `loopback` refuses a host name and an `https` address | PROPOSED | Test fails | Maintainer |
| G-07 | Secrets never reach an output sink (NFR-009) | `cargo test -p mocha-code --test secret_leak` (the binary's package is `mocha-code`; from SLICE-003, active once shown failing in CI) | PROPOSED | CI fails | Maintainer |
| G-08 | Hidden-instruction trick suite (NFR-006) | `cargo test --test tricks` | PROPOSED (from SLICE-013) | CI fails | Maintainer |
| G-09 | Replay regression suite (NFR-005) | `cargo test --test replay` | PROPOSED (from SLICE-008) | CI fails | Maintainer |
| G-10 | Never lose work (NFR-002) | `cargo test --test durability` (SIGKILL mid-turn, torn line, disk full via a size-limited tmpfs) | ACTIVE (from SLICE-002); shown failing locally, CI failure on purpose pending | CI fails | Maintainer |
| G-11 | Fuzz untrusted parsers | `cargo fuzz` targets for SSE, patch, bash analysis, config; short run per PR, long run nightly | PROPOSED | CI fails on a crash | Maintainer |
| G-12 | Protected files not loosened by agents | `AGENTS.md` lists `budgets.json`, `deny.toml`, `.github/workflows/*`, `clippy.toml`, test suites; CI rejects a change to them without a `Guardrail-Change:` commit trailer | PROPOSED | CI fails | Maintainer |
| G-13 | Clean-room rule | Contribution statement in PR template; no automated check exists | NOT_AVAILABLE (tooling) | Review rejects | Maintainer |
| G-14 | Toolchain pinned | `rust-toolchain.toml` 1.96.1; CI uses it | PROPOSED | Build uses the pinned toolchain | Maintainer |

## 6. Testing strategy

| Layer | What | Where |
|---|---|---|
| Unit | Each tool, parser, classifier, migration | Per crate |
| Format fixtures | Recorded request/response streams for each wire format and preset, served by the local fixture server | `mocha-llm/tests/fixtures/` |
| Protocol | Handshake, event ordering, coalescing | `mocha-proto` |
| Replay | Recorded `--json` sessions replayed on the mock provider (G-09) | `tests/replay/` |
| Durability | Kill/resume, torn writes, disk full (G-10) | `tests/durability/` |
| Tricks | Adversarial fixtures (G-08) | `tests/tricks/` |
| PTY end-to-end | The real binary driven in tmux at fixed sizes; screen captured and compared with snapshots | `tests/pty/` |
| Bench | Budgets (G-01) | `xtask` |

Real-model use is the maintainer's daily use; no paid calls in CI (DEC-020).

## 7. Build plan: slices for M0–M2

Each slice is a thin vertical path the user can observe, specified in `docs/slices/<ID>/` with its own Verification table accepted before code. Only SLICE-001 is written now; each later slice is written when the previous one merges (`shared/slice-loop.md`). Order follows DEC-037: the loop before the face.

| Slice | Milestone | Delivers | Requirements |
|---|---|---|---|
| SLICE-001 | M0 | Walking skeleton: workspace, protocol handshake, mock provider, minimal welcome, prompt, streamed reply, bench rig and CI gates | FR-001, FR-022, NFR-001 |
| SLICE-002 | M1 | `mocha run` (text and `--json`) and durable session logs with resume | FR-003, FR-010, NFR-002 |
| SLICE-003 | M1 | `models.json` loading and validation, last good copy, `mocha models`, key resolution, redaction, Anthropic Messages format | FR-006 (part), FR-007 (part), FR-020 (part), NFR-009 |
| SLICE-004 | M1 | Model catalog snapshot (fills missing limits; asks for what is still missing); OpenAI Chat format; DeepSeek, Z.ai, TheClawBay presets; Coding Plan notice | FR-006 (rest), FR-007 (part), FR-024 |
| SLICE-005 | M1 | Core tools, read ledger, evidence, fixed safe-default approvals | FR-004, FR-005 |
| SLICE-006 | M1 | Loop controls: interrupt, interject, follow-up, loop detection, budgets | FR-002 |
| SLICE-007 | M1 | Instruction files, cache-ordered layout, compaction, output spill | FR-009, FR-017 |
| SLICE-008 | M1 | Plain TUI (top bar, pour, transcript, tool rows, composer, diff tints), replay suite, basic doctor | FR-018, FR-021 (basic), NFR-005 |
| — | **M1 exit** | Mocha fixes a bug in its own repo, headless and in the plain TUI | |
| SLICE-009 | M2 | Permission modes, tiers, rules, bash analysis, dock approvals | FR-011 |
| SLICE-010 | M2 | Project trust and layered config | FR-013, FR-020 |
| SLICE-011 | M2 | Checkpoints and rewind | FR-014 |
| SLICE-012 | M2 | Linux sandbox | FR-012 |
| SLICE-013 | M2 | Taint, exfiltration checks, trick suite | FR-015, NFR-006 |
| SLICE-014 | M2 | MCP client | FR-016 |
| SLICE-015 | M2 | OpenAI Responses and Gemini formats | FR-007 (rest) |
| SLICE-016 | M2 | Sign in with ChatGPT | FR-008 |
| SLICE-017 | M2 | Full TUI: scroll, selection copy, search | FR-019 (part) |
| SLICE-018 | M2 | Rail, full welcome, themes, accessibility pass | FR-019 (rest), NFR-008 |
| SLICE-019 | M2 | Release pipeline, complete doctor | FR-023, FR-021 |
| — | **M2 exit (MVP)** | All P0 pass; Mocha is the only harness | |

NFR-003, NFR-004 and NFR-007 apply to every slice and are checked by G-03 and the migration tests in SLICE-002/003.

## 8. Architecture decisions

| ID | Decision | Alternatives | Why | Revisit |
|---|---|---|---|---|
| ADR-001 | In-process protocol transport in the MVP; daemon at M4 | Daemon from day one (blueprint default) | Same code path, far less to build before the loop works; FR-022 keeps the seam honest | M4 |
| ADR-002 | Nine runtime crates + xtask | One crate; full blueprint layout | Enforceable boundaries (G-02) without empty crates | When a crate's build time hurts |
| ADR-003 | `models.json` keeps the user's existing layout (FCT-009) | New TOML provider schema | Zero-migration for the user; providers stay data | If the layout blocks a needed feature |
| ADR-004 | No SQLite in the MVP; JSONL + small JSON index | rusqlite WAL + FTS5 | Less binary size and C code; cross-session search is M3 | M3 |
| ADR-005 | Checkpoints via the `git` CLI with a separate `GIT_DIR` | `gix` library; own snapshot format | Small, proven; missing git degrades safely | If git CLI startup cost shows in G-01 |
| ADR-006 | No plain-text secret fallback | 0600 file (blueprint) | NFR-009; env vars cover headless machines | Never without a new decision |
| ADR-007 | Sandbox = Landlock + seccomp, fail closed; no bubblewrap | bubblewrap when present | One mechanism to test and state precisely | macOS work |
| ADR-008 | Fixed safe-default approvals in M1 before the policy engine | Build the policy engine first | Keeps "loop first" without unsafe dogfooding | Replaced by SLICE-009 |
| ADR-009 | Transcript model of source blocks with a screen back-map | Copy rendered cells (prototype) | FCT-005: copy must be source text | — |
| ADR-010 | Clean-room: read published protocol docs and the user's own files; write our own code | — | DEC-001 | — |

## 9. Reference updates

When this document is accepted, the blueprint gets a short "Superseded for the MVP by `docs/04-architecture.md`" note at §4.1 (daemon default), §4.3 (crates), §4.4 (SQLite, secrets fallback), §5.7 (session path) and §9 (build sequence), and `DESIGN.md` gets `del_bg` in its token table if missing. These are edits to point at this document, not rewrites.

## Revision history

- **Revision 4 (2026-11-12, accepted "I accept and approve your recommendation"):**
  - G-06 gains the `MOCHA_PROVIDER_LOCK=loopback` value, with the conditions above (IP literals only, CI keeps `mock`, fixture tests set `loopback` per command, a refusal test).
  - G-07 command corrected to `-p mocha-code`; active from SLICE-003 once it has failed in CI on purpose.
  - Model catalog snapshot and the "ask for missing limits" step move from SLICE-003 to SLICE-004 (§3.3 and §7).
  - `mocha-core` owns `config.toml` parsing and the `Redactor`.
  - Header brought up to date with PRD revision 3.
- **Revision 3 (accepted "accept the architecture change for G-10"):** G-10 is ACTIVE from SLICE-002.
