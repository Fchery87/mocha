# Mocha — Engineering Blueprint

**Date:** 2026-11-10
**Status:** Proposal for discussion (engineering only; TUI/UX is a later document)
**Inputs:** Apex-Code review (`~/Documents/Coding Projects/apex-code`, `e2d2a99ff`), Jcode (`github.com/1jehuang/jcode`, README + `docs/` as of 2026-11-10), Apex's own landscape research (Claude Code, Codex CLI, Gemini CLI, OpenCode, Copilot CLI, Goose, Crush).

---

## 0. TL;DR

1. **Mocha should be a clean-room Rust harness: one static binary, a daemon that owns sessions, and thin clients attached over a versioned protocol.** That shape is what lets Jcode report ~3 MB per extra session and ~19 ms to first input. Build it into the protocol from day one, even while the first transport is in-process.
2. **Carry over Apex's *ideas*, not its code.** Apex's 39 ADRs (tool contracts, read ledger, protected targets, capability ceilings, session trees, eviction, workflows-as-data) are the most valuable thing you own. Its TypeScript, its Pi lineage (`pi-ai`, `pi-tui`, `jiti` extensions), and its Node runtime are what you leave behind.
3. **"Great on GPUs" = light on the machine (decided 2026-11-10).** Mocha must barely register in CPU, RAM, and GPU usage at idle, and many sessions must run side by side without bogging the machine down. That's achieved by the daemon model (§4.1), near-zero idle cost (no timers, no redraws when nothing changes), and a renderer that sends minimal bytes so GPU terminals stay idle (§5.12). Local-model features (§5.2) remain an optional P2 extra, not the headline.
4. **Set performance budgets before you write features, and gate CI on them.** Jcode's self-published numbers are the bar to beat.
5. **Extensions go through WASM components (wasmtime) plus MCP plus declarative hooks, with no embedded JS VM.** Apex already learned that `node:vm` is not a sandbox (modernization review P0, ADR 0039).

---

## 1. What Apex-Code teaches us

### 1.1 Measured state

| Package | Files | LOC (TS) | Role |
|---|---:|---:|---|
| coding-agent | 431 | 105,226 | Tools, sessions, permissions, TUI modes, CLI (fork of `pi-coding-agent`) |
| agent | 118 | 33,894 | Agent loop (fork of `pi-agent-core`) |
| ai | 225 | 25,141 | Providers (Pi's `pi-ai`, 35 providers over 9 dialects) |
| tui | 42 | 18,270 | Terminal primitives (Pi's `pi-tui`) |
| chord, durable, server, client, protocol, telemetry | 74 | ~14,600 | Apex additions |

Hot spots: `interactive-mode.ts` (7,751 lines), `agent-session.ts` (5,704), `delegation/runtime.ts` (1,905). Upstream merges have breached the 159-conflict-hunk ceiling (ADR 0003). **The fork itself is now the main tax.** That's the strongest argument for a ground-up rebuild.

### 1.2 Concepts to port as designs (re-implement, don't translate)

| Apex concept | Why it survives into Mocha |
|---|---|
| **Tool contract** (ADR 0010): capabilities `fs.read / fs.write / exec / net / delegate / ui / state`, permission grammar, context behavior, evidence | One declared source of truth that permissions, plan mode, verification, and delegation ceilings all read. In Rust it becomes a trait plus a static descriptor. |
| **Read ledger** | Edits are refused against files the model hasn't read, has read only partially, or that changed since. Cheap and very effective against hallucinated edits. |
| **Workspace / protected target / sensitive path** | A clean three-tier filesystem trust model. |
| **Session tree** (JSONL, `id`/`parentId`) | Branch in place, no file explosion. Keep it, and add a SQLite index. |
| **Steering vs follow-up queues** | The right interrupt model. |
| **Eviction before compaction** | Dropping replayable tool results is cheaper than summarizing. |
| **Deferred tool schemas / skill catalog deferral** (ADR 0011, 0021) | Keeps a large tool surface affordable. |
| **Capability ceilings for delegation** (ADR 0008) | A child can never exceed its parent. |
| **Workflows are data** (ADR 0039) | A bounded JSON DAG, never executable script. |
| **Evidence captured at the source** | Exit codes, patch hashes, and argv recorded by the tool that did the work, not inferred from the model's claims. |
| **Reviewed memory inbox, path-scoped rules, completion check (`/goal`), session worktrees** | All recent wins. Rebuild them natively. |
| **Environment block last in the system prompt** | Cache-friendly prompt layout. |
| **Replay corpus** | The deterministic regression instrument. Build it first in Mocha. |
| **Clean-room discipline** (ADR 0002) | Same rule for Mocha: no copying Pi, Jcode, Codex, or leaked sources. Read behavior, write your own. |

### 1.3 Things to leave behind

- The whole Pi stack: the provider layer, TUI primitives, `jiti` TypeScript extensions, and the upstream-merge machinery (`.upstream-tag`, backports, shrinkwrap/install-lock checks).
- Any scripting VM as a "sandbox".
- Mutating-tool name lists that duplicate the contract (`MUTATING_TOOLS`).
- Process-global approval caches.
- Free-text worker results. Use typed result envelopes validated against JSON Schema.
- God files. Enforce module boundaries with crate boundaries plus a size lint (e.g. fail CI over 1,500 lines per file).

---

## 2. What Jcode (and others) teach us

### 2.1 Jcode, the performance benchmark to beat

Self-published by Jcode, measuring resource use rather than task success:

| Metric | Jcode | Pi | Claude Code | Codex CLI | OpenCode |
|---|---:|---:|---:|---:|---:|
| RAM, first session (headless) | 71.3 MB | 84.0 MB | 272.9 MB | 398.6 MB | 637.1 MB |
| RAM, each additional session | ~3.3 MB | ~79.6 MB | ~169.3 MB | ~194.1 MB | ~5.9 MB |
| Time to first input | 19.1 ms | 596.4 ms | 3,512.8 ms | 905.8 ms | 1,047.9 ms |

A third-party write-up reports 27.8 MB for one session with embeddings off and ~167 MB with semantic memory on. **So the embedding model is most of the footprint. Make it optional.**

**Architecture lessons worth adopting:**
- **Server owns sessions; clients are views.** `session = server runtime`, `surface = client attachment`. Versioned JSON requests with request IDs and correlated events. This is why extra sessions cost ~3 MB.
- **Prompt-cache discipline:** append-only context, MCP tool schemas cached on disk so reconnects don't rewrite the prefix, async MCP connect (no startup block), and a **KV-cache monitor** that compares request signatures and warns before a cold-cache request.
- **Structure-aware grep (`agentgrep`):** matches come back with their enclosing function/symbol, trimmed by what the agent has already seen.
- **Swarm coordination:** the server tracks per-agent reads and writes and notifies agent B when agent A edits a file B has read. Agents can message one agent, broadcast, or spawn sub-swarms.
- **Memory budgets as documented hard caps** (e.g. highlight cache ≤ 256 entries, Mermaid disk cache ≤ 50 MiB, 3-day expiry), with debug commands that print live counters. Copy this practice exactly.
- **Context ceiling per session** (`max_context_tokens`), independent of the model window.
- **Self-dev mode:** the agent edits, rebuilds, and hot-reloads the harness. Fun, but security-sensitive. Treat it as a dev-only feature flag.

**Jcode lessons to avoid:**
- **~100 workspace crates**, including per-provider `*-runtime` crates and many `*-types` crates, while its own Modular Architecture RFC admits the root crate is still a monolith. Crate sprawl hurts compile times and cognition. Start with ~12 crates and split only when a seam proves itself.
- Scope creep (email, voice, iOS, cloud, Gmail backends). Mocha should stay a coding harness.
- Default-on automatic memory without review.

### 2.2 Other harnesses (one row each, what to take)

| Harness | Take |
|---|---|
| **Codex CLI (Rust)** | OS sandboxing done right: Landlock + seccomp / bubblewrap on Linux, Seatbelt on macOS, fail-closed. An exec-policy language for command approval. An app-server protocol that lets IDEs embed the same core. `apply_patch` as a first-class edit format. |
| **Claude Code** | Hooks as the governance layer, skills (progressive disclosure), subagents with worktree isolation, plan mode, `/goal` completion loop, path-scoped rules, auto memory, checkpoints / `/rewind`, background tasks, deferred tool search. |
| **Gemini CLI** | Sandbox profiles (Seatbelt / bwrap / gVisor / LXC), the memory inbox with review, atomic writes, non-interactive plan execution. |
| **OpenCode** | Client/server split, LSP diagnostics fed back after edits, multi-session, very broad provider support via models.dev. |
| **Goose** | MCP-first design ("extensions are MCP servers"), recipes. |
| **Copilot CLI** | Hand off a prompt to a cloud agent (`&` prefix), "open this session in my editor". |
| **ACP (Zed)** | Settled the editor-integration protocol. Mocha should speak it natively. |

---

## 3. Mocha's design principles

1. **Lightweight is a feature with numbers.** Every PR runs the perf suite, and regressions block merge.
2. **One core, many surfaces.** TUI, headless `run`, ACP, SDK, and MCP-server mode are all clients of the same protocol.
3. **Contract-driven tools.** Tools declare capabilities, and every other subsystem reads that declaration. Nothing re-derives it.
4. **Cache-first context.** Prompt layout is designed for prefix-cache hits, both cloud and local KV.
5. **Honest boundaries.** Permission policy and OS containment are separate and both named. Never claim coverage you don't have (the lesson from Apex ADR 0005 to 0032).
6. **Local models are first-class, not an "OpenAI-compatible" afterthought.**
7. **Evidence over assertion.** "Done" means a check passed, and the check is recorded.
8. **Small surface, deep modules.** Few crates, narrow interfaces.
9. **Minimize human attention** (from DeepSeek Super-Agent): speak only for a result, a decision, or a failure. Delegation is enforced structurally (lead mode), never just requested in prompts.

---

## 4. Architecture

### 4.1 Process model

```
                ┌───────────── mocha (single static binary) ─────────────┐
 mocha (TUI) ───┤                                                        │
 mocha run   ───┤  transport: in-process | unix socket | named pipe | ws │
 ACP (Zed…)  ───┤                    │                                   │
 SDK / MCP   ───┤                    ▼                                   │
                │   mocha-server (daemon, auto-spawned, idle-exits)      │
                │    ├─ SessionHost × N  (agent loop, context, tools)    │
                │    ├─ ProviderPool     (HTTP/2 conn reuse, rate limits)│
                │    ├─ McpHub           (shared stdio/HTTP servers)     │
                │    ├─ Scheduler        (subagents, workflows, bg jobs) │
                │    ├─ FileWatch/Coord  (who read/edited what)          │
                │    └─ Store            (JSONL logs + SQLite index)     │
                └────────────────────────────────────────────────────────┘
```

- **Default:** `mocha` connects to a running daemon or spawns one (`mocha serve --detach`). The daemon exits after N minutes with no sessions.
- **`--no-daemon` / CI:** the same server runs in-process over a channel transport. The code path is identical, only the transport differs.
- **Crash isolation:** a client crash never kills a session. A daemon crash is recovered from the append-only log.
- **Session hibernation:** idle sessions drop caches and keep only the log offset (Jcode has this too).

### 4.2 Protocol (`mocha-proto`)

- JSON-RPC 2.0 framing with `v` and a negotiated capability set. Requests (`session.create`, `turn.submit`, `turn.steer`, `turn.interrupt`, `permission.respond`, …) and a server event stream (`turn.delta`, `tool.started`, `tool.output`, `permission.request`, `usage`, `cache.miss`, …).
- Types defined once in Rust. Generate the JSON Schema with `schemars`, and from that the TypeScript and Python SDK types.
- Optional binary framing later (MessagePack/CBOR) if profiling shows JSON cost. It won't matter at first.
- Backpressure: clients subscribe with a coalescing policy (e.g. merge text deltas into ≤ 60 Hz updates).

### 4.3 Crate layout (start here, split later)

```
crates/
  mocha-proto      wire types + schema generation           (serde, schemars)
  mocha-core       message IR, ids, errors, config types    (no async, no IO)
  mocha-llm        provider dialects, streaming, catalog, auth
  mocha-engine     agent loop, context engine, compaction, budgets
  mocha-tools      built-in tools + tool contract trait
  mocha-policy     permissions, rules, command analysis, OS sandbox
  mocha-store      session logs, SQLite index, checkpoints
  mocha-mcp        MCP client (and server mode)              (rmcp)
  mocha-ext        WASM component host, hooks, skills loader (wasmtime, feature-gated)
  mocha-server     daemon, scheduler, coordination, transports
  mocha-tui        renderer + widgets                        (ratatui, crossterm)
  mocha            bin: CLI parsing + composition            (clap)
  # feature-gated, off by default:
  mocha-embed      local embeddings for semantic memory       (ort or candle)
```

Dependency rule: `core ← llm/tools/policy/store ← engine ← server ← tui/bin`. Lower layers never import upward. Enforce it with `cargo-deny` bans or a small xtask check.

### 4.4 Runtime choices

| Concern | Choice | Note |
|---|---|---|
| Async | `tokio` (multi-thread in daemon, `current_thread` in thin client) | |
| HTTP | `reqwest` + `rustls`, HTTP/2, one pool per provider | Connection reuse cuts first-token latency. |
| SSE / stream parse | Hand-written incremental parser over `bytes::Bytes` | Avoid per-chunk allocations. Parse tool-call JSON incrementally. |
| JSON | `serde_json` (`simd-json` only if profiling says so) | |
| Allocator | `mimalloc` | Lower RSS and fragmentation in a long-lived daemon. |
| Search | `ignore` + `grep-searcher` / `grep-regex` (ripgrep's libraries) in-process | No `rg` subprocess. Respects `.gitignore`. |
| Parsing | `tree-sitter` (lazy-loaded grammars) | Outline, symbol grep, bash command analysis. |
| Diff | `similar` | |
| PTY | `portable-pty` | Interactive commands, background shells. |
| Fuzzy | `nucleo` | File and command pickers. |
| Markdown / highlight | `pulldown-cmark`, plus `tree-sitter-highlight` or `syntect` | Cache with hard caps. |
| Storage | JSONL + `rusqlite` (WAL, FTS5) | |
| Secrets | `keyring` (OS keychain), file fallback with 0600 permissions | |
| Telemetry | `tracing`, optional `opentelemetry-otlp` | Off by default. No phone-home. |
| Release profile | `lto = "fat"`, `codegen-units = 1`, `strip = true`, `opt-level = 3`, `panic = "abort"` for bin | Measure `opt-level="s"` too. |

---

## 5. Subsystems in depth

### 5.1 Provider layer (`mocha-llm`)

- **Four wire dialects cover almost everything:** Anthropic Messages, OpenAI Chat Completions, OpenAI Responses, Gemini `generateContent`, plus Bedrock Converse as a fifth. Every other provider is **configuration** (base URL, auth style, header quirks, capability flags), not code. That's the key simplification over Pi's 35 providers.
- **Canonical message IR:** content blocks `text | thinking{signature} | redacted_thinking | tool_use | tool_result | image | document`, with lossless round-tripping per dialect. Thinking signatures must be preserved, or multi-turn reasoning breaks on Anthropic.
- **Model catalog:** embed a snapshot of models.dev data at build time and refresh in the background. Store context window, output limit, pricing, cache pricing, modalities, tool support, and reasoning knobs.
- **Model roles:** `main`, `fast` (titles, summaries, classification), `compact`, `judge` (completion checks), `embed`, `vision`. Each role can point at a different provider, e.g. a cloud main model with a local fast model.
- **Prompt caching:** an explicit cache-breakpoint planner for Anthropic and Bedrock, plus automatic-prefix assumptions for OpenAI and Gemini. Report `cache_read` and `cache_write` tokens per turn.
- **Resilience:** retries with jittered backoff that respect `retry-after` and rate-limit headers, a fallback chain per role, a credential pool with rotation on 429s, and mid-stream reconnect where the dialect allows.
- **Auth:** API keys, env vars, OAuth device and PKCE flows. **Subscription OAuth (Claude/ChatGPT plans) is a legal and ToS minefield. Make it a deliberate decision, not a default.**
- **Structured output:** native JSON-schema modes where they exist, and local validation (`jsonschema` crate) always.

### 5.2 Local-model support (optional, P2, not the headline)

*Your answer on 2026-11-10 made lightness the goal, not local inference. Keep this section as a later option.*

| Feature | What it does |
|---|---|
| **Backend detection** | Probe `localhost` for llama.cpp server, Ollama, LM Studio, vLLM, SGLang, MLX-LM, and TGI. Read their model, context, and slot info. |
| **Prefix stability contract** | System prompt, tool list, and instructions are byte-stable across turns. Tool order is deterministic. No timestamps in the prefix. That's what makes llama.cpp `cache_prompt` and vLLM/SGLang automatic prefix caching hit. |
| **KV slot management** | Pin a session to a llama.cpp slot (`id_slot`), save and restore slot KV to disk on hibernate and resume. Resuming a 60k-token session becomes instant instead of a full re-prefill. |
| **Prefill/decode telemetry** | Show prompt-processing tok/s, generation tok/s, cache-hit tokens, and time-to-first-token per turn. GPU users care about these numbers. |
| **VRAM-aware sizing** | Read NVML (NVIDIA), ROCm SMI, or Metal stats. Recommend context size and quantization, and warn before you request a context the KV cache can't fit. |
| **Grammar-constrained tool calls** | Generate a GBNF grammar or JSON-schema guided decoding from the active tool set, so small local models never emit malformed tool calls. That's the biggest quality lever for 7B–32B models. |
| **Lean prompt profile** | A compact system prompt and a reduced tool set for small-context models, selected automatically by model size and context window. |
| **Concurrency-aware scheduling** | vLLM and SGLang batch well, so subagents run in parallel. Single-slot llama.cpp serializes, so the scheduler queues instead of thrashing. |
| **Speculative decoding / draft model config** | Pass-through settings where the backend supports them. |
| **Don't steal VRAM** | Mocha itself never touches the GPU. Optional embeddings run on CPU by default. |
| **Local judge / fast role** | Let a tiny local model handle titles, summaries, and completion checks, so the cloud bill drops. |

**GPU terminals:** see §5.12. The harness's job there is emitting as few bytes as possible.

### 5.3 Agent loop (`mocha-engine`)

- An explicit state machine: `Idle → Streaming → ToolsPending → Executing → (Streaming | Done | AwaitingPermission | Interrupted | BudgetExhausted)`. Every state transition is an event in the log.
- **Streaming tool execution:** start read-only, idempotent tools as soon as their arguments finish parsing, before the model's turn ends.
- **Parallel execution:** batch by contract. Read-only calls run concurrently, writes to the same path are serialized, and `exec` follows its declared concurrency class.
- **Cancellation:** a `CancellationToken` tree (session → turn → tool → child process group). `Esc` interrupts within 50 ms, and child processes get SIGINT, then SIGKILL.
- **Queues:** *steer* (inject after the current tool batch) and *follow-up* (run when the agent would otherwise stop).
- **Budgets:** max turns, tokens, cost in dollars, wall-clock time, and tool calls, per session and per child. Every one ends in a typed terminal reason.
- **Completion conditions:** `/goal "<condition>"`. After each stop, run the pinned verification command first. Fall back to the `judge` model only if the condition can't be a command. Cap retries.
- **Stop/continue hooks** (see §5.9).
- **Loop and degeneration detection:** identical tool call N times, or edit/revert oscillation, triggers a nudge and then a stop.

### 5.4 Context engine

- **Layout, in cache order:** `[core system prompt] [tool schemas, deterministic order] [skills index] [AGENTS.md/CLAUDE.md] [env block] ‖ conversation…`.
- **Token accounting:** take provider-reported usage as truth, with local estimation (`tiktoken-rs` or a heuristic per family) for planning.
- **Pressure ladder:** (1) evict old replayable tool results, leaving a marker, (2) truncate large outputs and spill them to a file the agent can `read`, (3) compact with a structured handoff summary (goal, decisions, files touched, open todos, working-tree state), (4) reactive compaction on `prompt_too_long`.
- **Deferred tool schemas:** a tool search returns schemas on demand. MCP tools are deferred by default.
- **Skills:** progressive disclosure (name and description always present, body loaded on demand). Compatible with the Agent Skills `SKILL.md` format.
- **Path-scoped rules:** load when a matching path is read or edited.
- **Cache monitor:** hash the prefix of every request, detect unintended prefix changes, warn before a cold-cache request, and show the hit rate.
- **Per-session context ceiling** (Jcode idea): e.g. cap at 200k even on 1M-window models, for cost and quality.
- **Untrusted content marking:** tool outputs, web pages, and MCP results are wrapped and labeled as data, a basic prompt-injection mitigation.

### 5.5 Built-in tools (`mocha-tools`)

| Tool | Notes |
|---|---|
| `read` | Line ranges, images, PDFs (text extraction), notebooks. Writes to the read ledger (hash + coverage). |
| `write` | Atomic rename. Requires a ledger entry if the file exists. |
| `edit` | Exact string replace with a uniqueness check and `replace_all`. Diagnostic hints on a miss (closest match, whitespace diff). |
| `multi_edit` / `apply_patch` | Multi-hunk, multi-file. Codex-style patch format is well trained into models. Offer both by model family. |
| `grep` | In-process ripgrep libraries. **Structure-aware mode:** each match carries its enclosing symbol via tree-sitter (an `agentgrep` equivalent). Already-seen trimming. |
| `glob` / `ls` | Respect `.gitignore`, mtime sort. |
| `outline` | Tree-sitter symbol outline of a file or directory, so the agent doesn't have to read whole files. |
| `bash` | Persistent shell session or per-call PTY. Timeouts, background mode (`bash_bg`, `bash_output`, `bash_kill`), output caps with spill-to-file, process-group kill, OS sandbox when enabled. |
| `lsp` | Diagnostics after edits (auto-attached to the edit result), definition, references, symbols, rename. Spawns language servers lazily, or reuses the editor's. |
| `web_fetch` / `web_search` | Pluggable search backends. HTML → markdown. Domain policy. |
| `todo` / `plan` | Structured plan with phase → item hierarchy, updated by id (Jcode's plan-diffing saves tokens). |
| `ask_user` | Structured multiple-choice questions. Disabled in headless mode. |
| `delegate` | Subagents (see §5.8). |
| `memory_note` | Proposes a note to the reviewed inbox. |
| `browser` | **Via MCP or an optional CDP module.** Don't hard-bundle Chromium logic in core. |
| `tool_search` | Loads deferred schemas. |

**Tool contract (Rust sketch):**

```rust
pub struct ToolSpec {
    pub name: &'static str,
    pub caps: CapSet,                 // FsRead | FsWrite | Exec | Net | Delegate | Ui | State
    pub concurrency: Concurrency,     // Parallel | PerPath | Exclusive
    pub replayable: bool,             // eligible for eviction
    pub output_budget: Tokens,
    pub schema: &'static RawValue,    // stable bytes → cache-friendly
}

#[async_trait]
pub trait Tool: Send + Sync {
    fn spec(&self) -> &ToolSpec;
    fn permission_subject(&self, args: &Args) -> Subject;   // what the rule matcher sees
    async fn run(&self, ctx: ToolCtx, args: Args) -> ToolResult; // ToolResult carries Evidence
}
```

### 5.6 Permissions and sandbox (`mocha-policy`)

**Policy (what may run):**
- **Default mode `rip` (decided 2026-11-10):** tiered blast-radius classification (safe → recoverable+checkpoint → reflection → ask → absolute block). Full design in `docs/FEATURES.md` §7. Other modes: `careful`, `plan`, `yolo`.
- Rules: `{source, allow|deny|ask, tool, pattern}` from managed > CLI > project (trust-gated) > user. Deny always beats allow.
- **Bash analysis with a real parser** (tree-sitter-bash), not regex. Split pipelines, `&&`, subshells, and `$(…)`, then match each simple command against rules. Flag redirections to protected paths and `curl | sh` patterns.
- Protected targets (credentials, `~/.ssh`, cloud configs, Mocha's own auth store) can only be granted by managed policy. Sensitive paths (`.env*`) can only be granted by a rule that names the file.
- Permission prompts show a **preview** (diff for edits, parsed argv for bash) and offer "allow once / this session / always (writes rule)".

**Containment (what it can touch if it runs):**
- **Linux:** Landlock (filesystem) + seccomp (`seccompiler`) for syscalls, or bubblewrap if present. Network off, or via a local allowlisting proxy.
- **macOS:** Seatbelt profiles generated per policy.
- **Windows:** restricted token / AppContainer later, documented as unsupported until then.
- Applies to `bash`, MCP stdio servers, hooks, and WASM extensions (WASI capabilities are inherently scoped).
- **Fails closed** when sandboxing is requested but the platform helper isn't available.
- The docs state the boundary precisely, and so does `mocha doctor`.

### 5.7 Sessions, checkpoints, persistence (`mocha-store`)

- **Event log:** append-only JSONL per session (`~/.local/share/mocha/sessions/<project-hash>/<id>.jsonl`). Entries form a tree. Fsync at turn boundaries.
- **Index:** SQLite (WAL) with session metadata, titles, costs, and FTS5 full-text search across all sessions (`mocha search "…"`).
- **Operations:** resume (`-c`, `--resume <name>`), fork, branch navigation (`/tree`), rename, export (Markdown, HTML, JSON), share (opt-in), import from Claude Code / Codex / Apex session formats.
- **Checkpoints:** a shadow git repo (separate `GIT_DIR`, never touching the user's refs) snapshots the working tree before each mutating batch. `/rewind` restores code, conversation, or both. Restore asks first if the workspace has diverged.
- **Worktrees:** `mocha --worktree <name>` and `delegate{isolation: worktree}`, with a `.worktreeinclude` file for copying gitignored files.
- **Concurrent sessions in one checkout:** the daemon knows about them and warns, or offers a worktree.

### 5.8 Multi-agent

- **Subagents:** `delegate{agent, prompt, isolation?, model?, budget?, output_schema?}`, foreground or background. Capability ceilings are enforced against contracts. Configurable depth and concurrency caps.
- **Typed result envelope:** `{status: ok|failed|cancelled|blocked|budget, output (schema-validated), artifacts[], evidence[], usage}`.
- **Agent definitions:** markdown with frontmatter (`name, description, tools, model, permission_mode, isolation`), compatible in spirit with `.claude/agents`.
- **Workflows:** a declarative DAG (TOML/JSON) of steps with dependencies, fan-out, and join. Durable step records (dispatch → running → done) with idempotency keys and restart reconciliation. This fixes the exact P1 findings in Apex's review.
- **Coordination (from Jcode):** the daemon tracks per-agent read and write sets, and editing a file another agent has read emits a `file.changed_under_you` event to that agent. Direct and broadcast messaging comes later.
- **Integration step:** when parallel worktree children finish, merge their patches in order, detect conflicts, then run combined verification.

### 5.9 Extensibility

| Mechanism | Purpose | Notes |
|---|---|---|
| **MCP client** (`rmcp`) | External tools, resources, prompts | stdio + streamable HTTP + OAuth. Lazy and async connect. **Schemas cached on disk.** Servers shared across sessions in the daemon. |
| **Hooks** | Governance and automation | Events: `SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PermissionRequest, Stop, SubagentStop, PreCompact, Notification`. A command receives JSON on stdin and returns allow/deny/modify. Consider Claude Code-compatible event names so existing hook scripts work. |
| **Skills** | Packaged instructions and scripts | `SKILL.md` standard. User, project, and plugin scopes. |
| **Slash commands** | Prompt templates | Markdown with args. |
| **Custom agents** | Subagent personas | See §5.8. |
| **WASM extensions** (`wasmtime` component model, WIT interface) | In-process tools, providers, renderers | Capability-scoped by construction (WASI). Language-agnostic (Rust, Go, JS via componentize-js, Python). Near-zero cost when unused. **This is the clean, non-Pi answer to "TypeScript extensions".** |
| **Plugins** | Bundles of the above | A manifest plus a versioned registry (git URLs first, marketplace later). Checksums, and trust prompts on install. |

### 5.10 Integration surfaces

- `mocha run "<prompt>"`: headless, with `--output-format text|json|stream-json`, stable exit codes, and `--permission-mode` required in CI.
- **ACP server** (`agent-client-protocol` crate) for Zed, JetBrains, Neovim, and others.
- **SDK:** Rust crate plus generated TypeScript and Python clients over the daemon protocol.
- **MCP server mode:** expose Mocha as a tool for other agents.
- **GitHub Action / CI recipe** for PR review and issue-to-PR.
- **Remote attach:** `mocha connect ssh://host`, so a TUI on a laptop drives a daemon on a GPU box. **This pairs naturally with the local-GPU story.**

### 5.11 Memory

1. **Instructions:** `AGENTS.md` (and `CLAUDE.md` for compatibility), hierarchical (global → repo → subdirectory), with `@import`.
2. **Path rules:** `.mocha/rules/*.md` with `paths:` globs.
3. **Reviewed notes:** the agent proposes notes, the user accepts them in `/memory`, and loading is capped (e.g. 25 KB), scoped per repo and shared across worktrees. Secret scanning on write.
4. **Semantic memory (feature-gated, off by default):** local embeddings (CPU), an embedding graph over turns, a verifier pass before injection, and background reconciliation. This is Jcode's design, opt-in because it costs RAM.
5. `/memory audit`: stale paths, contradictions, nonexistent commands.

### 5.12 Rendering engine constraints (engineering only, UX later)

- `ratatui` + `crossterm`, **fullscreen (alternate screen) by default** per DESIGN.md v2: Mocha owns the transcript buffer, scrolling, search, and OSC 52 copy, and prints an exit receipt to normal scrollback. `--inline` renders into native scrollback instead.
- **Synchronized output** (DEC private mode 2026), so GPU terminals present whole frames and never tear.
- **Damage-tracked diff rendering:** only changed cells are emitted. The frame-rate cap (e.g. 60 fps active, 0 fps idle) is driven by events, not a timer.
- **Streaming markdown:** incremental parse that re-renders only the tail block. Code highlighting is cached with hard caps.
- Kitty graphics, iTerm2, and Sixel image protocols, detected at runtime.
- **Metrics:** bytes written per frame, frames per second, render time p99, and keystroke-to-paint latency. All exposed via `/debug render`.
- **Testing:** headless backend + `insta` snapshots, and a `vt100` emulator for end-to-end screen assertions.

### 5.13 Observability, cost, diagnostics

- `tracing` spans correlated across session → turn → model call → tool → child agent. Optional OTLP export.
- Per-turn and per-session cost, tokens, cache hit rate, TTFT, and tok/s. `/usage`, `/cost`, and a status line.
- `mocha doctor`: providers, credentials, sandbox availability, MCP health, local GPU backends, terminal capabilities.
- `/debug memory` and `/debug render` counters (Jcode practice), with **documented hard caps** in `docs/budgets.md`.
- No telemetry by default. Opt-in only, and documented field by field.

### 5.14 Configuration

- **Format:** TOML. A published JSON Schema (from `schemars`) gives editors completion.
- **Precedence:** managed (`/etc/mocha/managed.toml`, enterprise) > CLI flags > env (`MOCHA_*`) > project `.mocha/config.toml` (**only after project trust**) > user `~/.mocha/config.toml` (root folder; `MOCHA_HOME` overrides) > defaults.
- **Profiles:** `mocha -p local-gpu`, `-p ci`, `-p review`.
- **Hot reload** of non-structural settings while running.
- **Sections:**

```toml
[model]        main / fast / compact / judge / embed roles, reasoning effort, max output
[providers.*]  dialect, base_url, auth, headers, quirks, rate limits, fallback
[local]        backend autodetect, slot pinning, kv_persist, grammar_tools, vram_guard
[context]      max_context_tokens, eviction, compaction threshold, deferred_tools
[permissions]  mode, allow/deny/ask rules, protected paths, sensitive paths
[sandbox]      enabled, network = off|allowlist, writable_roots, fail_closed
[tools]        enable/disable, timeouts, output caps, bash shell, lsp servers
[mcp.servers.*] command/url, env, oauth, lazy, trust
[hooks]        event → command matchers
[agents]       depth, concurrency, default isolation
[memory]       inbox, size caps, semantic (off)
[session]      storage dir, retention, autosave, checkpoint policy
[ui]           layout full|inline, theme, palette, rail, mouse, keymap, motion  (see DESIGN.md §13)
[telemetry]    otlp endpoint (off), metrics
[daemon]       autostart, idle_exit, socket path, remote listen (off)
```

### 5.15 Security and supply chain

- Secrets in the OS keyring, with redaction in logs, transcripts, and exports (pattern + entropy scanner).
- `cargo-deny` (licenses, bans, advisories), `cargo-audit`, and `cargo-vet` or a pinned dependency policy. Minimal dependency tree as a stated goal.
- Signed releases (minisign or Sigstore), SHA-256 manifests, SBOM, reproducible builds where feasible.
- Self-update verifies the signature before swapping the binary.
- Project trust prompt before loading any project config, hooks, MCP servers, or extensions.

### 5.16 Distribution

- `cargo-dist`: static musl on Linux (x86_64, aarch64), universal or dual macOS, Windows x64 and ARM64.
- **Mocha has no JS runtime dependency.** It's built with `cargo`. Optional P2: publish a tiny npm-registry shim that downloads the native binary, so `bun add -g mocha` / `bunx mocha` work. The generated TypeScript SDK is built and tested with Bun.
- `curl | sh` and PowerShell installers with checksum verification, Homebrew, `cargo install`, AUR, Nix flake.
- Target binary size **≤ 25 MB stripped** (tree-sitter grammars lazy-loaded or downloadable to keep this).

---

## 6. Performance budgets (gate CI on these)

| Metric | Target | Jcode reference |
|---|---:|---:|
| Cold start to input ready (warm daemon) | ≤ 20 ms | 19.1 ms |
| Cold start incl. daemon spawn | ≤ 60 ms | — |
| Thin client RSS | ≤ 12 MB | — |
| Daemon + 1 idle session (no embeddings) | ≤ 30 MB | 27.8 MB |
| Each additional idle session | ≤ 3 MB | ~3.3 MB |
| Keystroke → paint p99 | ≤ 8 ms | — |
| Streaming render CPU (1 session, fast model) | ≤ 3% of one core | — |
| Harness overhead per tool call (excluding the tool) | ≤ 1 ms | — |
| Session resume of a 10k-entry log | ≤ 100 ms | — |
| Binary size (stripped) | ≤ 25 MB | — |

**Bench rig:** `hyperfine` for startup, a custom RSS/CPU sampler, a **mock provider** that streams recorded responses at configurable tok/s (so render cost is measured without a network), and a PTY harness that measures input latency. Results are committed as JSON and compared per PR.

---

## 7. Quality and evaluation

- **Deterministic tests:** mock provider plus recorded fixtures. Every tool has unit tests and contract tests.
- **Replay corpus:** scrubbed real sessions replayed offline, emitting metrics (tokens, cache hits, tool errors). Port Apex's Phase 0 idea.
- **Outcome evals:** a small internal suite of real repo tasks graded by tests, plus Terminal-Bench 2.0. Run per model family, multiple trials, and track cost per solved task.
- **Local-model evals:** the same suite on 8B / 14B / 32B local models with and without grammar-constrained tools, to prove the GPU wedge with numbers.
- **Fuzzing:** SSE parser, patch applier, bash analyzer, config loader (`cargo-fuzz`).
- **Sandbox escape tests:** adversarial scripts in CI on Linux and macOS.

---

## 8. Complete feature checklist

Legend: **P0** = MVP (daily-drivable), **P1** = parity with strong harnesses, **P2** = differentiators and later.

### Core loop & context
- [P0] Streaming agent loop, parallel tool calls, interrupt (Esc), steer and follow-up queues
- [P0] Turn, token, cost, and time budgets with typed stop reasons
- [P0] Cache-ordered prompt layout, provider usage accounting
- [P0] Tool output truncation with spill-to-file
- [P1] Eviction → compaction ladder, reactive compaction, handoff summaries
- [P1] Deferred tool schemas plus tool search
- [P1] Streaming tool execution (start reads before the turn ends)
- [P1] `/goal` completion loop (command first, judge model second)
- [P1] Loop and degeneration detection
- [P1] Cache-cold monitor and warnings
- [P2] Per-session context ceiling, auto lean-profile for small models

### Providers & models
- [P0] Anthropic, OpenAI Chat, OpenAI Responses, Gemini dialects. OpenAI-compatible config entries.
- [P0] API-key auth, keyring storage, `/model` switching mid-session
- [P1] Bedrock, Vertex, Azure, OpenRouter, Copilot. models.dev catalog. Model roles.
- [P1] Retries, rate-limit awareness, fallback chains, credential pools
- [P1] Thinking/reasoning controls, thinking signature preservation, image input
- [P1] Subscription sign-in for Anthropic and OpenAI (decided). Isolated module, labeled in the UI.
- [P1] Add-any-provider via config: base URL + wire format + auth + model list, no code changes
- [P2] Measured routing (cost/quality), once evals exist

### Local models (optional extras)
- [P1] Ollama / llama.cpp / LM Studio / vLLM as ordinary config-entry providers
- [P1] Prefix-stability contract plus a cache-hit display
- [P1] Grammar / JSON-schema constrained tool calls
- [P1] Prefill/decode tok/s and TTFT telemetry
- [P2] llama.cpp slot pinning plus KV save/restore on hibernate
- [P2] VRAM-aware context and quant recommendations (NVML / ROCm / Metal)
- [P2] Backend-aware subagent concurrency
- [P2] Remote daemon on a GPU box (`mocha connect ssh://…`)

### Tools
- [P0] read, write, edit, multi_edit / apply_patch, grep, glob, ls, bash (timeouts, bg jobs), todo, ask_user
- [P0] Read ledger, atomic writes
- [P1] web_fetch, web_search, LSP diagnostics after edit, outline (tree-sitter), structure-aware grep
- [P1] Image and PDF read
- [P2] LSP rename and code actions, notebook editing, CDP browser module

### Safety
- [P0] Permission modes (plan / ask / accept-edits / bypass), allow/deny/ask rules, previews
- [P0] Protected targets and sensitive paths, project trust prompt
- [P1] Parser-based bash analysis
- [P1] Linux Landlock+seccomp / bwrap and macOS Seatbelt sandbox, network allowlist proxy, fail closed
- [P1] Secret redaction in transcripts and logs
- [P2] Windows containment, `auto` mode with a safety classifier, managed enterprise policy

### Sessions & state
- [P0] JSONL tree log, resume / continue, named sessions
- [P1] SQLite index plus FTS search, fork / branch / tree navigation, export (MD/HTML/JSON)
- [P1] Shadow-git checkpoints plus `/rewind` (code, chat, or both)
- [P1] `--worktree` sessions with `.worktreeinclude`
- [P2] Import Claude Code / Codex / Apex sessions, share links, session hibernation

### Multi-agent
- [P1] `delegate` with capability ceilings, worktree isolation, background mode, typed results with schema validation
- [P1] Custom agent definitions (markdown frontmatter)
- [P2] Declarative durable workflows (DAG) with restart reconciliation
- [P2] File-touch coordination events, agent messaging, patch integration step

### Extensibility
- [P0] AGENTS.md / CLAUDE.md loading, slash-command templates
- [P1] MCP client (stdio, HTTP, OAuth, schema cache, lazy connect), hooks, skills, path rules
- [P2] WASM component extensions, plugin bundles and registry, MCP server mode

### Memory
- [P1] Reviewed notes inbox with caps and secret scanning
- [P2] `/memory audit`, opt-in semantic memory

### Surfaces
- [P0] Interactive TUI, `mocha run` headless with JSON streaming and exit codes
- [P1] Daemon plus multi-client attach, ACP server, Rust SDK
- [P2] TS/Python SDKs, GitHub Action, remote attach, desktop/IDE clients

### Ops
- [P0] Perf bench rig plus CI gates, mock provider, `mocha doctor`
- [P1] Cost/usage reporting, tracing, OTLP opt-in, signed releases, self-update
- [P1] Replay corpus, outcome eval suite
- [P2] Local-model eval matrix, fuzzing in CI

---

## 9. Build sequence

| Milestone | Deliverable | Exit criterion |
|---|---|---|
| **M0 — Skeleton & instruments** | Workspace, `mocha-proto`, `mocha-core`, mock provider, bench rig, CI with budgets | Empty TUI hits ≤ 20 ms / ≤ 12 MB, and budgets are enforced in CI |
| **M1 — First real loop** | Anthropic + OpenAI-compatible dialects, core tools, read ledger, JSONL sessions, minimal Full-layout TUI (top bar, transcript, composer), `mocha run` | Mocha can fix a bug in its own repo end to end |
| **M2 — Safe daily driver** | Permission modes and rules, parser-based bash analysis, project trust, checkpoints / `/rewind`, keyring auth | Usable as your main harness. Apex retired for personal use. |
| **M3 — Context & providers** | Eviction / compaction, deferred tools, cache monitor, all dialects, model roles, catalog | 100-turn sessions without manual intervention. Cache hit rate shown. |
| **M4 — Daemon & many sessions** | Background server, multi-client attach, session hibernation, shared MCP pool, subscription sign-in | 10 concurrent sessions: ≤ 60 MB total, ~0% CPU when idle |
| **M5 — Multi-agent** | Subagents, worktrees, background jobs | Parallel children with ceilings, no per-child process bloat |
| **M6 — Ecosystem** | MCP, hooks, skills, ACP, sandbox, SDK | Zed via ACP works. Sandbox escape suite passes. |
| **M7 — Differentiators** | WASM extensions, durable workflows, KV slot persistence, remote GPU attach, semantic memory | Feature-flagged and measured |

Then the **TUI/UX document**: layout, composer, transcript, panels, theming, keymaps, and the Mocha brand.

---

## 10. Decisions

### Settled (2026-11-10)

| # | Decision |
|---|---|
| 1 | **"Great on GPUs" = lightweight.** Minimal idle CPU, RAM, and GPU use, and many concurrent sessions without slowing the machine. Local-model features move to optional P2. |
| 2 | **Background server (daemon) on by default**, Jcode-style: the first `mocha` launch starts it, later launches attach over a Unix socket (`$XDG_RUNTIME_DIR/mocha.sock`), clients reconnect after a server reload, the MCP pool is shared across sessions, and there's a `--no-daemon` escape hatch for CI. *(Recommended; confirm.)* |
| 3 | **Extensions, phased:** P1 = external-command hooks (TOML-configured, as Jcode does), MCP servers, skills, slash commands, and agent definitions. No in-process plugin runtime at first. WASM components stay a P2 option, added only if a real need appears. *(Recommended; confirm.)* |
| 4 | **Subscription sign-in for Anthropic (Claude plans) and OpenAI (ChatGPT/Codex plans) is included**, alongside API keys. The provider layer stays fully open: any provider or model can be added through config (base URL + wire format + auth), plus local servers. The terms-of-service risk of subscription sign-in is accepted knowingly: label it in the UI and isolate it in its own module so it can be disabled. |
| 5 | **Linux first**, then macOS, then Windows. The first sandbox is Landlock + seccomp/bwrap, and Linux-specific budgets are measured on your machine. |
| 6 | **Instruction files:** read `AGENTS.md` (primary) and `CLAUDE.md` (fallback/compat), hierarchically. Mocha's root folder is `~/.mocha/` (config.toml, models.json, mcp.json); projects may add a trust-gated `.mocha/config.toml` and `.mcp.json`. Optionally also read `.claude/skills` and `.claude/agents` for migration (P1). |

| 8 | **Permissions:** `rip` mode with a Linux sandbox on by default, branch-aware `git push`, a taint-triggered AI reviewer, trust-gated instruction files, and checkpoints of tracked + untracked files. See `docs/FEATURES.md` §7.6. |
| 7 | **License: MIT** (`LICENSE`, © 2026 Fchery87). No "derived from Pi" notice, because nothing is derived. |

---

## 11. What Mocha does differently from Apex-Code

Evidence from the Apex repo (`e2d2a99ff`): 68 specs, 39 ADRs, 21 research notes (~27k lines of docs) for one maintainer. A 441 MB `node_modules`. A daemon was specified in Phase 6, then removed on 2026-10-16 "because nothing constructed it". An OS sandbox was built, then removed (ADR 0032), then partly re-added as optional bash confinement. The modernization review found its workflow feature declared contained while it wasn't.

| # | Apex did | Mocha does instead | Why |
|---|---|---|---|
| 1 | Forked Pi, then fought the fork (merge-hunk ceiling breached) | Owns every line. No upstream to track. | The fork became the main maintenance cost. |
| 2 | Designed big subsystems in specs before a thin version worked end to end (daemon, sandbox, workflows) | **Vertical slices:** each milestone ships something you use daily, and nothing lands that isn't wired into the running product | Avoids building, removing, and rebuilding. |
| 3 | Bolted client/server packages on later | Protocol and daemon are the skeleton from M0 (in-process transport first) | The architecture choice that makes Mocha light can't be retrofitted cheaply. |
| 4 | Heavy governance: a spec per change, ADR per decision, release-governance checklist, ~10 check scripts in `npm run check` | **Light process:** short ADRs only for decisions that are hard to reverse, one `ROADMAP.md`, an `AGENTS.md` for agents working on Mocha. CI under 5 minutes. | Paperwork was outpacing product for a solo maintainer. |
| 5 | Docs claimed things code didn't do (README agent count, workflow containment) | **Generated truth:** `mocha doctor --inventory` prints tools, providers, sandbox coverage, and limits from the code. README tables are generated from it. | Docs can't drift from a single source. |
| 6 | Tests measured correctness. Outcome evals and perf numbers came late. | **Bench + eval from day one:** perf budgets gate CI, and a small real-task eval suite runs before any feature is called better | Lightness is the product promise, so it needs a scoreboard. |
| 7 | 35 providers inherited as code | 4–5 wire formats in code. Everything else is config. | Less code, easier to add providers. |
| 8 | God files (7.7k / 5.7k lines) | Crate boundaries plus a file-size lint (≈1,500 lines) | Keeps things navigable for you and for agents. |
| 9 | Safety boundary decided, undone, redone | Decide once: **permissions = policy, sandbox = optional containment**. Document coverage exactly. | No more reversals. |
| 10 | npm + standalone archives + shrinkwrap/install-lock machinery | One static binary per platform, one installer, signed | Simpler releases, nothing to install first. |
| 11 | Hard-coded tool lists alongside the contract | The tool contract is the only source. Rust's type system enforces it. | Removes a whole bug class. |
| 12 | System prompt and tool descriptions treated as code text | **Prompts are versioned assets** with eval runs on change, plus per-model-family variants (edit format, tool wording) | Prompt and tool wording affect task success as much as features do. |

**Keep from Apex unchanged in spirit:** clean-room rule, read ledger, protected targets, capability ceilings, session tree, evidence capture, reviewed memory, `/goal`, worktree sessions.

---

## 12. Gaps found on second review (added to scope)

### Daemon-specific (new risks the daemon model creates)
- **Socket security:** socket file `0600` in `$XDG_RUNTIME_DIR`, and verify the peer UID (`SO_PEERCRED`). Never listen on TCP by default.
- **Version skew:** after an update, an old daemon may meet a new client. Use a protocol version handshake, and run the client in-process or prompt a graceful daemon restart (`mocha daemon restart`) on mismatch.
- **Fault isolation:** a panic in one session must not kill the others. Run each session in its own task with `catch_unwind` and a supervisor restart. Set per-session memory caps.
- **Zero idle cost:** no polling timers in the daemon or client. Event-driven only. Verify ~0% CPU with 10 idle sessions in the perf suite.
- **Session lifecycle visibility:** `mocha ps` (list sessions, state, RAM, cost), `mocha attach <name>`, `mocha kill <name>`.

### Subscription sign-in
- **Plan usage limits:** show remaining 5-hour and weekly quota for Claude and ChatGPT plans, warn before hitting them, and offer automatic fallback to an API key or another provider.
- **Multiple accounts:** switch accounts mid-session when one is rate-limited (Jcode has `/account`).
- **Token refresh** handled in the daemon only, so all sessions share one refreshed token.

### Everyday usability (easy to forget, painful to miss)
- Image paste from the clipboard, drag-and-drop file paths, `@file` mentions with fuzzy completion
- Desktop notification when a long turn finishes or needs permission (`notify-send` / OSC 9/777)
- Works correctly inside **tmux, screen, and over SSH** (no truecolor or graphics assumptions, a tmux passthrough setting)
- Correct Unicode width (CJK, emoji), CRLF files, binary-file detection
- External edits: notice when you change a file in your editor mid-session (file watcher → read ledger invalidation)
- Large monorepos: gitignore-aware walking, file-count caps, no full-repo indexing at startup
- Git helpers: draft commit messages, a PR description command, and show branch / dirty state in the status line
- `/init`: generate a starter `AGENTS.md` for a repo (never overwrite an existing one)
- Offline / provider-down behavior: clear errors, queue the prompt, retry

### Data & compatibility
- **Versioned formats:** session log, config, and protocol each carry a schema version, with automatic migration and tests for old files.
- **Import from Apex:** sessions, `permissions.json`, `mcp.json`, and skills from `~/.apex-code`, so you don't lose history.
- **Retention & privacy:** auto-delete sessions after N days (configurable), `mocha forget <session>`, secret redaction before anything is written to disk.
- **Log rotation** for daemon logs.

### Developer experience of building Mocha itself
- Fast Rust builds: the `mold` linker, `sccache`, a dev profile with `opt-level=1` for dependencies, and `cargo nextest`.
- `AGENTS.md` in the Mocha repo, so coding agents (including Mocha itself) work well on it.
- Dogfood from M1: use Mocha to build Mocha as soon as it can edit files.
