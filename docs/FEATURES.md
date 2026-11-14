# Mocha — Features & Capabilities

**Status:** Product catalog, 2026-11-10. Companion to `docs/research/2026-11-10-mocha-engineering-blueprint.md`.
**Tags:** **P0** = first daily-drivable release · **P1** = matches the strongest harnesses · **P2** = beyond them / later.

> **Mocha is a lightweight, provider-agnostic agent harness, built first and foremost for coding, that can also research, automate, and operate anything reachable from a terminal.**

---

## How a harness makes an agent "smart"

The model supplies the raw intelligence. The harness decides how much of it turns into correct work. Mocha raises the ceiling in six ways:

1. **Sees the right context.** It understands the repo structurally, not by reading whole files.
2. **Plans before acting.** Explicit plans and acceptance criteria.
3. **Checks its own work.** Tests, type checks, and diagnostics run automatically, and "done" requires evidence.
4. **Uses more than one mind.** Second opinions, reviewer agents, escalation to a stronger model.
5. **Learns.** Corrections become reviewed memory and rules.
6. **Never loses work.** Checkpoints, durable sessions, a daemon that survives closed windows.

Sections 1 and 2 cover what makes it smart. Section 3 covers what it can do.

---

## 1. Intelligence layer

### 1.1 Codebase understanding
- **[P0] Project profile auto-detection:** language(s), framework, package manager, build, test, lint, and format commands, detected once, cached, and shown in `/status`
- **[P0] Package manager follows the project:** detected from the lockfile (`bun.lock` → bun, `pnpm-lock.yaml` → pnpm, `package-lock.json` → npm, `yarn.lock` → yarn), so Mocha never mixes managers in an existing repo
- **[P0] Preferred JS toolchain for new work = Bun** (decided 2026-11-10): scaffolding, one-off scripts, and repos with no lockfile use `bun install` / `bun run` / `bunx` / `bun test`. Configurable: `[tools] js_package_manager = "bun"`.
- **[P0] Structure-aware search:** every grep hit comes with its enclosing function or class, and results already seen are trimmed
- **[P1] Repo map:** a tree-sitter symbol index of the repo, ranked by how connected each file is, injected as a compact overview so the agent knows where things live
- **[P1] File and directory outlines:** symbols, signatures, docstrings without reading full files
- **[P1] LSP semantic navigation:** go-to-definition, references, workspace symbols, hover types, call hierarchy
- **[P1] Dependency awareness:** reads manifests and lockfiles, knows which library versions are in use (to avoid outdated API suggestions), and can fetch matching docs
- **[P1] Git history awareness:** `blame`, `log -S`, and recent changes, to learn *why* code is the way it is
- **[P1] Test discovery:** finds the tests that cover a file or function and runs just those
- **[P2] Cross-repo context:** attach sibling repos (e.g. frontend + backend) as read-only references

### 1.2 Planning & reasoning
- **[P0] Plan mode:** read-only exploration, then a structured plan you approve, edit, or reject
- **[P0] Todo/plan tracking:** phases → items, updated in place and visible live
- **[P0] Clarifying questions:** structured multiple-choice prompts instead of guessing
- **[P1] Acceptance criteria:** each task gets explicit "done means…" checks, tied to evidence
- **[P1] Reasoning-effort control:** per-turn and per-role thinking budgets, auto-raised for hard steps
- **[P1] Task decomposition:** large requests are split into steps, which can be farmed out to subagents

### 1.3 Self-verification (the biggest quality lever)
- **[P0] Edit diagnostics:** when an edit doesn't match, the agent is told the closest match and the whitespace difference instead of a bare failure
- **[P0] Read-before-write ledger:** no edits to files the agent hasn't seen, or that changed since it read them
- **[P1] Auto-verify after edits:** LSP diagnostics attached to every edit result, with configured lint, typecheck, and test commands run at turn end
- **[P1] `/goal` completion loop:** keep working until a condition holds (e.g. `cargo test` passes). A command judges first, a small model only if needed. Capped turns.
- **[P1] Evidence records:** exit codes, test results, and patch hashes captured by the tools themselves. "Done" claims are backed by records.
- **[P1] Self-review pass:** before finishing, a reviewer subagent reads the full diff against the request and flags bugs, missed requirements, and leftover debug code
- **[P1] Loop and degeneration detection:** repeated identical calls or edit/revert oscillation trigger a nudge, then a stop with an explanation
- **[P2] Hill-climbing mode:** for measurable goals (benchmark time, bundle size, coverage) the agent iterates against the number, not its own opinion

### 1.4 Multiple models working together
- **[P1] Model roles:** main, fast (titles, summaries), compact, judge, vision, each assignable to any provider
- **[P1] Second opinion (`/consult`):** ask a different model or provider to critique a plan or diff
- **[P1] Escalation:** after repeated failures on a step, retry with a stronger model or higher effort automatically (configurable)
- **[P2] Best-of-N:** run N attempts in parallel worktrees and keep the one that passes the checks

### 1.5 Learning & memory
- **[P0] Instruction files:** `AGENTS.md` (primary) and `CLAUDE.md` (compatible), loaded hierarchically (global → repo → subfolder), with `@imports`
- **[P1] Path-scoped rules:** `.mocha/rules/*.md` that load only when matching files are touched
- **[P1] Reviewed memory inbox:** the agent proposes notes from your corrections. You accept or reject them in `/memory`. Accepted notes load in future sessions and are shared across worktrees. Secrets are blocked.
- **[P1] Skills:** reusable packaged know-how (`SKILL.md`). Only the name and description are always loaded, the body on demand.
- **[P2] `/memory audit`:** finds stale paths, contradictions, and dead commands in instructions and notes
- ~~[P2] Semantic memory via embeddings~~ **Removed (2026-11-10 review):** the field moved to file-based memory that a model consolidates (Codex memory v2, Claude auto memory). See §17.
- **[P1] Memory consolidation:** a fast model periodically merges, dedupes, and expires notes. Changes still go through the review inbox.
- **[P1] Import memories** from Claude Code / Codex / Apex

### 1.6 Context management
- **[P0] Cache-friendly prompt layout:** a stable prefix, so provider prompt caches hit (cheaper, faster)
- **[P0] Large-output spill:** huge command outputs are saved to a file and summarized, and the agent reads slices as needed
- **[P1] Smart pressure ladder:** drop stale tool results → trim → summarize with a structured handoff → emergency compaction
- **[P1] On-demand tool loading:** large tool sets (MCP) load schemas only when needed
- **[P1] Cache-cold warning:** tells you when a request will miss the cache and cost more
- **[P1] Context meter:** live tokens used versus budget, with a per-session cap

---

## 2. Coding capabilities

| Capability | What Mocha does | Tag |
|---|---|---|
| **Feature implementation** | Plan → implement across files → run tests → self-review → summary with evidence | P0 |
| **Bug fixing** | Reproduce first (failing test or command), find the root cause, fix, prove with the now-passing check | P0 |
| **Explain / onboard** | Architecture tours, "how does X work", call-flow walkthroughs, generated diagrams (Mermaid) | P0 |
| **Write tests / TDD** | Generate tests matching project conventions. Red → green → refactor mode. | P0 |
| **Refactoring** | Multi-file edits, LSP-powered rename, extract function/module, with tests run after | P1 |
| **Code review** | Review local diff, branch, or a GitHub PR (via `gh`). Findings ranked by severity with file:line. | P1 |
| **Git workflows** | Commits with good messages, branches, rebase / merge-conflict resolution, PR creation and description | P1 |
| **Debugging** | Log analysis, stack-trace triage, `git bisect` automation, targeted instrumentation | P1 |
| **Frontend / UI work** | Run the dev server, open it in a browser, screenshot, read console errors, click through flows, compare to a design image | P1 |
| **Dependency upgrades & migrations** | Read changelogs, update versions, fix breakages, rerun the suite | P1 |
| **Performance work** | Run profilers and benchmarks, find hotspots, optimize, prove with before/after numbers | P1 |
| **Security review** | Scan the diff or repo for common vulnerability classes, secrets, unsafe patterns, and dependency advisories | P1 |
| **Documentation** | READMEs, API docs, code comments, changelogs generated from the diff | P0 |
| **Project scaffolding** | New projects from a description or template, with build, test, and CI working | P1 |
| **DevOps / CI** | Dockerfiles, CI workflows, read failing CI logs and fix the cause | P1 |
| **Databases** | Schema design, migrations, query writing and debugging (via shell or MCP) | P1 |
| **Data / notebooks** | Read and edit `.ipynb`, run analysis scripts, summarize data | P2 |
| **Issue → PR pipeline** | Take an issue, work in an isolated worktree, verify, open a PR for your review | P2 |
| **Parallel big jobs** | Split a large change across subagents in separate worktrees, then integrate and test the combined result | P2 |
| **Polyglot** | Any language with a tree-sitter grammar or language server. Rust, TS/JS, Python, Go, Java, C/C++, C#, Ruby, PHP, Swift, Kotlin, and more. | P0–P1 |

---

## 3. Beyond coding (the "do everything" layer)

| Capability | How | Tag |
|---|---|---|
| **Web research with citations** | `web_search` + `web_fetch`, multi-step research, sourced answers | P1 |
| **Live library docs lookup** | Fetch current docs for the exact dependency version in use | P1 |
| **Shell & system automation** | Sysadmin tasks, scripts, file organization, log digging, all under permissions | P0 |
| **Browser automation** | Fill forms, scrape pages, test flows (built-in local browser module or MCP) | P1 |
| **Documents & files** | Read PDFs and images, write Markdown/HTML. Office formats via scripts or MCP. | P1 |
| **Image understanding** | Screenshots, diagrams, mockups, error dialogs pasted from the clipboard | P1 |
| **Writing** | Specs, design docs, release notes, technical blog drafts | P0 |
| **Connect any service** | Anything with an MCP server: GitHub, Linear, Jira, Slack, databases, cloud consoles | P1 |
| **Scheduled / recurring tasks** | "Every morning, check CI and summarize failures", run by the daemon | P2 |
| **Long-running background jobs** | Start a task, close the terminal, check back later (`mocha ps`, `attach`) | P1 |
| **Remote machines** | Drive a Mocha daemon on a server over SSH from your laptop | P2 |

---

## 4. Built-in tools

| Tool | Purpose | Tag |
|---|---|---|
| `read` | Files, line ranges, images, PDFs, notebooks | P0 |
| `write` | Create or overwrite files (atomic) | P0 |
| `edit` / `multi_edit` | Exact-match replacement, many edits in one call | P0 |
| `apply_patch` | Multi-file patch format (for models trained on it) | P1 |
| `grep` | Built-in ripgrep engine, structure-aware results | P0 |
| `glob` / `ls` | Find files, gitignore-aware | P0 |
| `outline` | Symbols of a file or directory | P1 |
| `repo_map` | Ranked symbol overview of the repo | P1 |
| `bash` | Commands with PTY, timeouts, background mode, output spill | P0 |
| `bash_output` / `bash_kill` | Manage background processes (dev servers, watchers) | P0 |
| `lsp` | Diagnostics, definition, references, symbols, rename | P1 |
| `web_fetch` / `web_search` | Read pages, search the web | P1 |
| `browser` | Open localhost or allowed sites, screenshot, console, click, type | P1 |
| `todo` | Structured plan tracking | P0 |
| `ask_user` | Structured questions | P0 |
| `delegate` | Spawn subagents | P1 |
| `memory_note` | Propose a memory note | P1 |
| `tool_search` | Load deferred tool schemas | P1 |
| `notebook_edit` | Edit Jupyter cells | P2 |
| *MCP tools* | Anything from connected MCP servers | P1 |

---

## 5. Multi-agent & orchestration
- **[P1] Subagents** with their own context window and instructions, so the main conversation stays clean
- **[P1] Built-in agent types:** explorer (read-only search), planner, implementer, reviewer, debugger, verifier, researcher
- **[P1] Custom agents** via markdown files (`.mocha/agents/*.md`): name, description, tools, model, permissions
- **[P1] Permission ceilings:** a subagent can never do more than its parent is allowed to
- **[P1] Worktree isolation:** subagents can work in their own git worktree, so there are no collisions
- **[P1] Background agents:** keep working while you do other things, with a notification when done
- **[P1] Typed, validated results:** subagents return structured output checked against a schema, and failures are explicit
- **[P3] Declarative workflows** (demoted: Jcode removed its swarm task graph in v0.99 to simplify. Revisit only if subagents + the command center prove insufficient.)
- **[P2] Coordination:** agents are notified when another agent edits a file they've read. Agents can message each other.
- **[P2] Integration step:** merge parallel results in order, detect conflicts, run combined tests

---

## 6. Sessions, history & recovery
- **[P0] Durable sessions:** every turn is saved immediately. Resume with `-c` (last) or `--resume <name>`.
- **[P0] Named sessions** that are easy to recall
- **[P1] Checkpoints & `/rewind`:** undo code changes, conversation, or both, to any earlier turn (a hidden git store that never touches your branches)
- **[P1] Branching:** fork a conversation at any point and explore alternatives (`/tree`)
- **[P1] Full-text search across all past sessions** (`mocha search`)
- **[P1] Export:** Markdown, HTML, JSON
- **[P1] `--worktree <name>`:** start a session in its own git worktree, copying needed gitignored files (`.env`) via `.worktreeinclude`
- **[P1] Survives closed windows:** the daemon keeps sessions alive, and you reattach anytime
- **[P2] Import from Apex-Code, Claude Code, and Codex session formats**
- **[P2] Session hibernation:** idle sessions shrink to near-zero memory and wake instantly

---

## 7. Safety: "rips by default, asks only when it truly matters"

**Decided 2026-11-10:** Mocha's default is to run freely, the way Jcode does. You're only interrupted for genuinely dangerous actions, and everything else is made **recoverable** instead of approved.

### 7.1 Default mode: `rip`
Every action is classified by **blast radius** (what could it destroy or leak, and can it be undone?), not by command name. Classification is deterministic and local, with no model call, so it costs ~0 ms on the safe path.

| Tier | Examples | What happens | You're asked? |
|---|---|---|---|
| **0 Safe** | reads, grep, builds, tests, `git status/diff/log`, installing deps into the project | Runs immediately | No |
| **1 Recoverable** | edits/deletes inside the workspace, `git commit`, `git checkout` of tracked files, temp files | Runs immediately. **A checkpoint is taken first**, so `/rewind` undoes it. | No |
| **2 Unclear** | a delete whose target can't be determined statically, `sh -c "$(…)"`, `eval`, scripts that write outside the workspace | **Reflection:** Mocha refuses once and makes the model state which part of your request this serves. A blind retry fails. An optional AI reviewer can be enabled on top. | No (unless reflection fails twice → escalates to tier 3) |
| **3 Dangerous** | writes or deletes **outside** the workspace, `sudo`, `git push --force` / rewriting a shared branch, `git reset --hard` with uncommitted work, dropping or truncating databases, publishing (`npm/cargo publish`), deploys, `kubectl/terraform` apply/destroy, sending secrets or files to the network, `curl … \| sh` | Pauses with a clear preview and asks you | **Yes** |
| **4 Catastrophic** | recursive delete of `~`, `/`, system dirs, or credential stores (`~/.ssh`, `~/.gnupg`, `~/.aws`, `~/.kube`, `~/.docker`, Mocha's own tokens). Reading credential files to send them anywhere. | **Blocked absolutely.** No justification or approval unlocks it. Run it yourself outside Mocha if you truly mean it. | Never runs |

### 7.2 Why this beats Jcode's model
Jcode's checks were added **after** a user lost their home directory (jcode issue #604, "jcode just deleted everything in my ~"). Before that, bash ran with no gate at all. Its current design (`jcode-command-risk`) is good, and Mocha adopts its core ideas: blast-radius classification, recall-biased parsing, model reflection instead of a human prompt, and an absolute path-based deny. Mocha goes further in four ways:
1. **Automatic checkpoints make tier 1 truly free.** Mistakes inside the project are one `/rewind` away.
2. **It covers more than deletion:** secret exfiltration, force-pushes, publishing, deploys, `sudo`, and DB drops. Jcode's classifier focuses on destructive filesystem operations.
3. **Tier 3 asks you instead of silently refusing.** You stay in control of legitimately risky actions without having to leave Mocha.
4. **The same rules apply to every tool:** `bash`, `write`/`edit`, MCP tools (by declared capability), hooks, and subagents. Not just bash.

### 7.3 Other modes (one key to switch)
- `rip` (default): the tiers above
- `careful`: also asks on tier 2 and on edits (for unfamiliar or important repos)
- `plan`: read-only
- `yolo`: asks for nothing. Tier 4 is **still** blocked.
- Per-project default: e.g. `careful` for a production repo, `rip` everywhere else

### 7.4 Always on, in every mode
- **[P0] Tier-4 catastrophic block**, path-based after normalization, independent of command parsing
- **[P0] Workspace checkpoints** before mutations, with `/rewind`
- **[P0] Protected credentials:** the agent can't read `~/.ssh`, cloud keys, or Mocha's token store unless managed policy allows it
- **[P0] Project trust prompt:** a new repo's config, hooks, and MCP servers don't load until you trust it (once per repo)
- **[P1] Real shell parsing:** `a && b | c $(d)` is split and each part classified. Ambiguity escalates a tier and is never waved through.
- **[P1] Secret redaction and credential masking** in output, transcripts, and logs
- **[P1] Prompt-injection hygiene:** web, MCP, and tool output is marked as untrusted. A tier-3 action proposed right after reading untrusted content gets extra scrutiny.
- **[P1] Activity log:** every tier-1+ action is recorded (what, why, checkpoint id), shown in `/audit`

### 7.5 Customizing
- **[P0] Rules** to move things between tiers: `allow bash(npm publish --dry-run)`, `ask bash(git push*)`, `deny edit(migrations/**)`
- **[P0] When it does ask:** a preview (diff or parsed command) with allow once / this session / always (writes a rule)
- **[P1] Headless (`mocha run`):** tier 3 is denied instead of prompting and the turn continues. Opt in to allow it.
- **[P1] AI reviewer, automatic when the session is tainted** (§7.6 decision 3), with explanations and safer alternatives. It can be forced on or off.
- **[P0] OS sandbox, on by default on Linux:** Landlock + seccomp / bubblewrap for shell, hooks, and MCP. Workspace-write, network on, optional network allowlist (P1). Fails closed. See §7.6 decision 1.
- **[P2] macOS Seatbelt, Windows containment, enterprise managed policy**

### 7.6 Review notes and open decisions (2026-11-10)

**Fixes adopted regardless of the open decisions:**
- **Child-process environment scrubbing:** provider keys and Mocha tokens are never passed into `bash`, hooks, or MCP processes (so `env` or `printenv` can't leak them). Configurable allowlist.
- **MCP tool hints are untrusted:** a server's `readOnlyHint` / `destructiveHint` is advisory. An unknown MCP tool starts at tier 2, and a server becomes trusted once, per server.
- **"Safe" assumes a trusted repo:** builds, tests, and installs execute repo code. In an untrusted repo they are tier 2 at minimum.
- **Package installs with lifecycle scripts** (`npm/pnpm install`, `pip install` of sdists) run arbitrary code. They're tier 1 only inside the sandbox, otherwise tier 2. **Exception: `bun install`.** Bun doesn't run dependency lifecycle scripts unless the package is in `trustedDependencies`, so it's tier 1. Editing `trustedDependencies` is tier 2.
- **Taint escalation (prompt-injection defense):** once untrusted content (web pages, MCP output, files from an untrusted repo) enters the context, any network-send or outside-workspace action moves up one tier, and reflection alone can't clear it. This targets the "private data + untrusted content + a way out" combination.
- **`/rewind` limits are stated in the UI:** it restores workspace files and the conversation, not databases, remote git, installed packages, or files outside the workspace.
- **Background subagents never block:** their tier-3 requests queue in the agent command center with a notification.
- **Classifier test corpus in CI:** a red-team set of dangerous commands (recall must be 100% for tier 4, tracked for tier 3) plus a false-positive rate measured on replayed real sessions.
- **Safety event log** for every block, ask, and reflection (OpenTelemetry-compatible, local by default).

**Decisions (settled 2026-11-10):**

| # | Question | Decision |
|---|---|---|
| 1 | OS sandbox in `rip` mode | **On by default on Linux** (bubblewrap/Landlock + seccomp). Shell, hooks, and MCP stdio processes can write only inside the workspace and temp dirs. Network on. If the sandbox blocks a legitimate command (Docker, global installs), Mocha asks once: "run outside sandbox?" (allow once / for this session / always for this command). Fails closed if the helper is missing; `mocha doctor` explains how to install it. |
| 2 | Non-force `git push` | **Tier 1 to the current non-default branch. Tier 3 (ask) to `main`/the default branch or any protected branch.** Force-push is always tier 3. |
| 3 | AI safety reviewer | **Automatic only when the session is tainted** by untrusted content (web, MCP output, untrusted repo files). It reviews tier-2 and network-send actions in that state. Otherwise off, at zero cost. Can be forced on or off in config. |
| 4 | Instruction files in untrusted repos | **Not loaded until the repo is trusted** (`AGENTS.md`, `CLAUDE.md`, `.mocha/`, hooks, MCP config). Global `~/.mocha/AGENTS.md` always loads. |
| 5 | Checkpoint scope | **Tracked + untracked, non-ignored files.** Ignored build output (`node_modules`, `target`) is excluded. Ignored sensitive files (`.env*`) are backed up individually before any edit. |

## 8. Providers & models (fully provider-agnostic)
- **[P0] Built-in wire formats:** Anthropic Messages, OpenAI Chat Completions, OpenAI Responses, Google Gemini. **[P1]** AWS Bedrock.
- **[P0] Add any provider or model through config:** base URL + wire format + auth + model list. No code changes, and anything OpenAI-compatible works.
- **[P0] API-key sign-in**, stored in the OS keychain
- **[P1] Subscription sign-in:** Claude plans (Anthropic) and ChatGPT/Codex plans (OpenAI)
- **[P1] Plan quota display:** remaining 5-hour and weekly limits, warnings, automatic fallback to an API key or another provider
- **[P1] Multiple accounts**, switchable mid-session when rate-limited
- **[P1] First-class presets:** Anthropic, OpenAI, Google, xAI, DeepSeek, Mistral, Groq, Cerebras, Together, Fireworks, OpenRouter, GitHub Copilot, Azure, Vertex, Bedrock
- **[P1] Local models:** Ollama, llama.cpp, LM Studio, vLLM, as ordinary providers
- **[P1] Model catalog** with context sizes, prices, and capabilities, auto-refreshed
- **[P1] Switch model mid-session** without losing context
- **[P1] Retries, rate-limit handling, fallback chains**
- **[P1] Thinking/reasoning settings**, image input, prompt caching per provider
- **[P2] Measured routing:** pick models by cost and success data from your own usage

---

## 9. Extensibility
- **[P0] Custom slash commands:** markdown prompt templates with arguments (`.mocha/commands/*.md`)
- **[P1] Hooks:** run your own scripts on events (session start, before/after tool, turn end, stop, permission request, pre-compact) to block, modify, log, or notify
- **[P1] MCP:** connect local (stdio) and remote (HTTP + OAuth) MCP servers. Connected lazily, schemas cached, shared across sessions.
- **[P1] Skills**, user and project scope, compatible with the common `SKILL.md` format, and reads `.claude/skills` for migration
- **[P1] Custom agents** (also reads `.claude/agents`)
- **[P2] Plugin bundles:** install a package of commands, skills, agents, hooks, and MCP configs from a git URL, with checksums and trust prompts
- **[P2] MCP server mode:** other tools can use Mocha as a tool
- ~~In-process WASM plugins~~ **Removed.** Hooks + MCP + skills cover extension. Code Mode (§17) is the only embedded runtime Mocha may ever carry.

---

## 10. Ways to use Mocha
- **[P0] Interactive terminal UI:** the Full layout (fullscreen, edge-to-edge, rail at ≥ 140 columns, docked approvals) with a Focus toggle and an inline fallback. Spec: `/DESIGN.md`.
- **[P0] `mocha run "<task>"`:** one-shot, scriptable, with text, JSON, and streaming-JSON output and reliable exit codes
- **[P0] Pipe in / pipe out:** `cat error.log | mocha run "explain"`
- **[P1] Multiple clients on one daemon:** many windows, one lightweight background server
- **[P1] Editor integration via ACP:** Zed, JetBrains, Neovim, and other ACP clients
- **[P1] SDK** (Rust first) over the same protocol
- **[P2] TypeScript / Python SDKs, GitHub Action, remote attach over SSH**

---

## 11. Lightweight by design (the promise, with numbers)

| Target | Budget |
|---|---|
| Launch to ready (daemon running) | ≤ 20 ms |
| Background server + 1 idle session | ≤ 30 MB RAM |
| Each additional session | ≤ 3 MB RAM |
| 10 idle sessions | ≈ 0% CPU, ≤ 60 MB total |
| Keystroke to screen | ≤ 8 ms |
| Streaming output CPU | ≤ 3% of one core |
| GPU | No GPU use by Mocha itself. Minimal redraws keep GPU terminals idle. |
| Binary | Single static file, ≤ 25 MB, no runtime to install |

CI enforces these budgets, and `/debug memory` and `/debug render` show live numbers.

---

## 12. Everyday usability
- **[P0]** `@file` mentions with fuzzy completion, plus `@folder` and `@url`
- **[P0]** Paste images from the clipboard. Drag-and-drop file paths.
- **[P0]** `Esc` interrupts instantly. Type while the agent works (steer) or queue follow-ups.
- **[P0]** Works properly in **tmux, screen, and over SSH**
- **[P0]** Correct handling of emoji/CJK width, CRLF files, binary files
- **[P1]** Desktop notification when a long task finishes or needs approval
- **[P1]** Notices when *you* edit a file mid-session and re-reads before touching it
- **[P1]** Fast on huge monorepos (gitignore-aware, no full indexing at startup)
- **[P1]** Git helpers: commit message drafts, PR descriptions, branch and dirty state always visible
- **[P1]** `/init` creates a starter `AGENTS.md` (never overwrites)
- **[P1]** Clear offline / provider-down behavior: queue, retry, or switch provider
- **[P1]** `!command` runs a shell command yourself and puts its output in the conversation
- **[P1]** Prompt history search, multi-line editor, open the prompt in `$EDITOR`
- **[P1]** Cost and token usage per turn and per session, always visible
- **[P2]** Voice input via an external tool hook (not built-in)

---

## 13. Commands

**CLI:**
`mocha` · `mocha run` · `mocha -c` / `--resume <name>` · `mocha --worktree <name>` · `mocha ps` · `mocha attach <name>` · `mocha kill <name>` · `mocha search` · `mocha login` / `logout` · `mocha models` · `mocha mcp add|list|remove` · `mocha doctor` · `mocha config` · `mocha update` · `mocha daemon start|stop|restart|status` · `mocha import apex|claude|codex` · `mocha forget <session>`

**In-session slash commands:**
`/help` `/model` `/login` `/account` `/mode` `/plan` `/goal` `/consult` `/review` `/init` `/memory` `/rules` `/skills` `/agents` `/mcp` `/hooks` `/tools` `/permissions` `/tree` `/rewind` `/fork` `/rename` `/export` `/compact` `/context` `/usage` `/cost` `/status` `/diff` `/tasks` `/ps` `/config` `/doctor` `/debug` `/clear` `/quit`

---

## 14. Configuration at a glance
- Root folder `~/.mocha/` (`MOCHA_HOME` overrides): `config.toml` (settings), `models.json` (your providers and models, BYOK), `mcp.json` (your MCP servers). Projects may add a trust-gated `.mocha/config.toml` and `.mcp.json`, never providers. Plus managed policy `/etc/mocha/managed.toml`
- Precedence: managed > CLI flags > env (`MOCHA_*`) > project > user > defaults
- **Profiles** (`mocha -p fast`, `-p review`, `-p ci`)
- A published JSON Schema gives editor autocomplete and validation
- Hot reload for most settings
- Full section list in blueprint §5.14

---

## 15. Privacy, security & distribution
- **[P0]** No telemetry by default, and nothing leaves your machine except calls to the providers you configure
- **[P0]** Credentials in the OS keychain
- **[P1]** Session retention policy, `mocha forget`, redaction before writing to disk
- **[P1]** Signed releases with checksums, verified self-update, SBOM, audited dependencies
- **[P1]** Install via `curl | sh`, Homebrew, `cargo install`, AUR. Linux x86_64/arm64 first, then macOS, then Windows.
- **[P1]** Versioned config, session, and protocol formats with automatic migration
- **License:** MIT

---

## 16. Deliberately *not* in Mocha
- Built-in voice, email, or chat-app clients (connect via MCP if wanted)
- A mandatory cloud account or hosted backend
- An embedded scripting VM pretending to be a sandbox
- Self-modifying "self-dev" mode in normal builds (developer flag only)
- Auto-loading memory you haven't reviewed
- Features that aren't measured to help coding outcomes or lightness

---

## 17. State-of-the-art review (2026-11-10)

Checked against releases from the last ~4 weeks: Claude Code 2.1.299–2.1.322, Codex CLI 0.164–0.167, OpenCode 2.2.6, Jcode 0.99.x, Gemini CLI 0.66–0.67, the MCP spec 2026-07-28, and Factory/Copilot/Cursor news.

### Added

| Feature | Seen in | Tag |
|---|---|---|
| **Agent command center:** `mocha agents` lists every session and subagent across projects with unread-result markers. Reopen a finished subagent and message it. | Codex 0.167 (`codex agents`), Claude Code 2.1.319 (`/tasks` earlier subagents) | P1 |
| **Optional AI reviewer** for unclear actions: see §7.5 | Claude Code auto mode + `/auto-mode-setup`, Codex "Guardian" review of exec calls | P1 |
| **Code Mode / programmatic tool calling:** the model writes one short script that calls many tools (especially MCP) and returns only the result. 90%+ token savings on tool-heavy tasks. **Safety design:** the script runs in an isolated subprocess, and every tool call it makes goes back through Mocha's normal permission gate. The runtime is never trusted as a sandbox. Use provider-native programmatic tool calling where offered. | Codex Code Mode, OpenCode Code Mode VM, Anthropic programmatic tool calling, Cloudflare Code Mode | P2 |
| **Idle compaction & cache warming:** summarize a big idle session just before its prompt cache expires, so resuming is cheap. Optional TTL-based keep-warm per provider. | Claude Code 2.1.299, OpenCode 2.2.6 session warming | P1 |
| **Resume cost warning:** "resuming this session will use ~X% of your 5-hour limit. Resume, or start fresh with a summary?" | Claude Code 2.1.304 | P1 |
| **Automatic account failover:** when one subscription hits its limit, retry the turn on the next account in the pool | Jcode 0.99 | P1 |
| **Fork subagents:** a subagent that inherits the full current context (for side investigations) next to fresh-context subagents | Claude Code 2.1.302 (default on) | P1 |
| **Per-subagent and per-task effort:** cheap side tasks run at low effort. Effort can change mid-conversation. | Claude Code 2.1.316/2.1.318, Codex 0.165 | P1 |
| **Smaller-model switch safety:** switching to a model with a smaller context first summarizes with the current model | Claude Code 2.1.301 | P1 |
| **Background MCP tasks:** long MCP tool calls move to the background and report when done | Claude Code 2.1.319, MCP tasks extension | P1 |
| **MCP built to the 2026-07-28 spec from day one:** stateless requests, `server/discover`, multi-round-trip input requests, tasks extension, result caching via `ttlMs`, deterministic tool order (good for prompt cache), Client ID Metadata Documents for OAuth. **Not** implementing deprecated Roots, Sampling, Logging, or HTTP+SSE. | MCP spec 2026-07-28 | P1 |
| **Reconnect only changed MCP servers** on config edits | Jcode 0.99 | P1 |
| **Per-request network approvals:** a command reaching a non-allowlisted host prompts once per host, queued, never stacked | Codex 0.167 | P1 |
| **Compressed request bodies** to providers (faster uploads of long contexts) | Jcode 0.99 | P1 |
| **`mocha run` polish:** waits for its own background jobs and subagents before exiting. `--worktree`. `--archived` keeps CI runs out of your session list. | OpenCode 2.2.6 | P0–P1 |
| **Inline command args:** `/model opus effort=high`, `/permissions auto` | Codex 0.164 | P0 |
| **Prompt presets:** numbered quick slots for saved prompts | Codex 0.164 `/presets` | P2 |
| **Review depth levels** for `/review`: quick / standard / deep | Claude Code 2.1.304 | P1 |
| **Transcript navigation:** keyboard selection, search, jump to message (details in the TUI doc) | Codex 0.166, OpenCode 2.2.6 | P1 |
| **`mocha doctor --network`** for focused connectivity checks | Codex 0.166 | P1 |
| **OpenTelemetry GenAI conventions** on spans (opt-in export only), including safety events | Claude Code 2.1.300/2.1.307 | P2 |
| **Remote control from phone/browser:** securely pair a device to your local daemon to watch and approve. The daemon architecture makes this natural. | Claude Code remote-control, Cursor remote control (Oct 7), Copilot | P2 |

### Removed or demoted

| Item | Change | Why |
|---|---|---|
| Embedding-based semantic memory | **Removed** | The industry standard is now model-consolidated file memory. Embeddings cost ~140 MB RAM (Jcode's own numbers), which conflicts with lightness. |
| WASM plugin runtime | **Removed** | Hooks + MCP + skills are what everyone actually uses. One fewer heavy dependency. |
| Durable DAG workflows | **P2 → P3** | Jcode dropped its swarm task graph in v0.99. Subagents + the command center cover the need. |
| MCP Roots / Sampling / Logging, HTTP+SSE transport, Dynamic Client Registration as the default | **Never implement** | Deprecated in MCP 2026-07-28 |
| Built-in browser as a big module | **Kept small** | Localhost check + screenshot + console + click/type. Anything bigger goes through MCP. |

### Already at or ahead of the field (keep)
Daemon + thin clients (Codex now ships a daemon too), session hibernation, cache-miss display, worktree sessions, read-before-write ledger, plan-quota display, reviewed memory, `/goal`, evidence records, deterministic prompt prefix, shared MCP pool.

### Not adopting
Voice / realtime speech (Codex realtime V3), GUI/mobile plugin themes (OpenCode), cloud-only features (gateways, org analytics, hosted routines). These are outside a lightweight local coding harness, though remote control (above) keeps the door open.

---

## 18. Lessons from DeepSeek Super-Agent (2026-11-10)

**What it is:** `deepseek-ai/dsh-superagent-prototype` (MIT, TypeScript, published 2026-10-31, ~21.9k stars). A research prototype, not a product, built as a bundle for DeepSeek Harness. One long-lived **router session** talks to people (GitHub, optionally Feishu chat) and hands each request to an **isolated worker session** with its own directory/worktree. Workers run in parallel and report back through structured states. Its core principle: *"Take as little human attention as possible, and give as much value as possible."*

**Its evidence (self-reported, small):** slow-end completion time fell from 29.5 to 15.7 min versus one session with subagents. Router time per decision fell from 6.4 s to 1.6 s as load rose, thanks to batching. Coding was **simulated** in the test, so this measures scheduling, not code quality. The economics rely on cheap DeepSeek pricing.

**The key finding:** asking one agent to "use subagents when appropriate" produced **zero** delegation across 5 runs, and a stronger prompt worked 4 of 5 times. **Delegation must be structural** (separate sessions, tools removed from the router), not requested in the prompt.

### Adopted into Mocha

| Lesson | Mocha feature | Tag |
|---|---|---|
| Human attention is the scarce resource | **Design principle #9: minimize attention.** The agent confirms once, stays quiet while working, and speaks only for a result, a decision, or a failure. One structured question at a time. The command center lists "needs you" first, and a healthy state takes no space. (Drives the TUI doc.) | P0 |
| Structural delegation beats prompting | **Lead mode** (`mocha --lead` or `/lead`): your session becomes a router with **no edit/bash tools**. It splits requests into tasks and dispatches each to a worker in its own worktree. Cheap or fast model for the lead, strong model for workers. Built on the daemon, worktrees, and command center. | P1 |
| Workers must stay responsive | **Auto-background long commands:** in workers, a shell command running longer than N seconds (default 5 s in lead mode) becomes a background job, so the worker can read new messages at its next step | P1 |
| People must never be starved by new work | **Reserved human slot:** the scheduler always keeps one extra slot so your message to an existing task runs even when all worker slots are busy | P1 |
| States should come from what work waits on | **Task stages:** `needs-answer`, `needs-review`, `blocked`, `failed`, `working`, `queued`, `idle`. Worker reports: `progress`, `waiting`, `ready`, `blocked`, `failed`, `dropped`. Questions travel in a structured field, never inferred from free text. | P1 |
| Background work needs limits | After a worker's turn, background jobs get a time limit (default 30 min). A handoff to you frees the slot immediately, and a dev server left running for review keeps running. | P1 |
| Context is a cache | **ID-linked recall:** sessions, tasks, checkpoints, and spilled outputs all have IDs. The model first sees an ID + summary and pulls details on demand ("chain of recall"). Extends the spill-to-file design. | P1 |
| Messages can't grant permissions | Already Mocha policy (§7.6 taint escalation). Reaffirmed: content from events, PR comments, or chat is input to a decision, never a permission change. | P0 |
| Credentials never reach the model | Already Mocha policy (environment scrubbing, §7.6). | P0 |
| Proactive work starts in observe mode | **`mocha watch`** (event-triggered work from GitHub issues, PR comments, and CI failures on a repo): only explicit requests from allowed users are accepted, plus written rules. Accept mode `off` → **`observe`** (default: logs "would have done X") → `auto`. Never merges under its own account. | P2 |
| An agent can do its own setup | **Agent-guided onboarding:** first run can hand setup (providers, MCP, hooks) to the agent, which asks one short question at a time and shows the full plan once | P2 |

### Not adopted
- **Its full domain model** (Source, Trigger, Thread, Eval, Mandate, Subscription, Ticket, Assignment, …). That's the right complexity for a team-wide bot, and too much for a personal coding harness. Mocha keeps task → worker → report.
- **Team chat integrations (Feishu etc.) as core.** Use MCP/webhooks if wanted.
- **Running workers without the sandbox** (DSH workers run commands without approval as your OS user). Mocha's workers keep `rip` tiers + the Linux sandbox.
- **Cheap-model-dependent defaults.** Lead mode lets you pick models per role, and nothing assumes DeepSeek pricing.
