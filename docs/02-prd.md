# Mocha Code product requirements (MVP)

| Field | Value |
| --- | --- |
| Status | CONFIRMED: maintainer approved the shared build specification on November 14, 2026 |
| Revision | 5, November 14, 2026, incorporating the final 19-slice review and confirmed remote MCP OAuth scope |
| Scope | Milestones M0–M2 on Linux, with the integration gates stated below |
| Evidence cutoff | November 14, 2026. Mutable sources are identified in the research report. |
| Research | [Market and build-readiness findings](research/2026-11-14-mocha-market-and-build-readiness.md), [source inventory](research/2026-11-14-mocha-research-sources.json), [dependency evidence](research/2026-11-14-mocha-dependency-evidence.json) |
| Supporting documents | [Architecture](04-architecture.md), [UI design](../DESIGN.md), [feature roadmap](FEATURES.md), [historical blueprint](research/2026-11-10-mocha-engineering-blueprint.md) |

This PRD defines the MVP's required behavior and acceptance conditions. Architecture selects mechanisms that satisfy it. UI design specifies interactions within its scope. The feature catalog and historical blueprint do not add MVP requirements. Conflicts require a recorded update to the affected supporting document.

The former DEC, FCT, and CHG references depended on discovery records absent from this checkout. This revision states the requirements directly. It does not reconstruct missing approvals or treat the former architecture's unsupported accepted-revision reference as approval evidence. No implementation or active CI guardrail is evidenced in this checkout at this revision.

## 1. Product intent

Mocha Code is a Rust coding agent with a terminal UI and a headless interface, distributed as a static Linux executable. Clients use a versioned engine protocol with an in-process transport for the MVP. A future daemon or editor adapter is separate work.

The product hypothesis is that verified coding outcomes, predictable automation, recoverable work, and measured local overhead can make Mocha useful as the maintainer's daily coding tool. Rust, provider choice, MCP, and native distribution already exist among competitors. They are product characteristics, not demonstrated competitive advantages. See the [competitive research](research/2026-11-14-mocha-market-and-build-readiness.md#3-competitive-landscape).

The implementation follows the existing clean-room constraint: no code is copied from Pi, Jcode, Codex, Grok Build, or leaked Claude Code source. Public specifications and documentation inform independently written implementations. Compatibility with an existing configuration format requires explicit fixtures and a supported schema.

## 2. Users and jobs

| User | Job | Evidence of success |
| --- | --- | --- |
| Maintainer, primary | Fix bugs, implement features, review changes, and resume work across supported providers | Accepted changes with verification evidence, predictable interruptions, and successful recovery |
| Curious developers, secondary | Inspect the source, file issues, install a release, and try supported workflows | Accurate setup instructions, supported configurations, clear failure outcomes, and verifiable artifacts |

The project remains free and intended for MIT distribution. Public availability does not imply a support commitment. Outside code contributions remain deferred until the public beta. Broader demand and willingness to switch tools are unvalidated. The research does not establish market share or a productivity advantage.

## 3. Scope

### 3.1 MVP boundary

| Milestone | Delivers | Exit |
| --- | --- | --- |
| M0: skeleton and instruments | Workspace, in-process protocol, explicit mock provider, minimal welcome, streamed reply, performance harness, and initial CI checks | FR-001 and FR-022 pass. The NFR-001 measurement protocol is accepted and applicable budget checks run in CI. |
| M1: the agent first | Real agent loop, `mocha run`, minimum containment and authorization, core tools, read ledger, evidence, durable sessions, instructions, compaction, output spill, all four wire formats, the 12-provider catalog plus Custom, and plain TUI | The maintainer completes an edit-test-repair task in both interfaces. Every built-in provider has usable API-key setup and a supported coding-model path. Required combinations pass FR-007. |
| M2: safe daily driver | Full permission modes, project trust UI, checkpoints, injection defenses, MCP tools, full TUI, required native ChatGPT sign-in, and release pipeline | All P0 requirements, including FR-008, pass. The maintainer reports daily-driver readiness. |

All four API families are required by the end of M1: Anthropic Messages, OpenAI Chat Completions, OpenAI Responses, and native Gemini. This moves Responses and Gemini earlier than the original sequence so the confirmed provider catalog is complete before richer M2 interface work. API-key support for all 12 providers is an M1 gate; native ChatGPT subscription sign-in remains separate M2 work.

Native Sign in with ChatGPT is a confirmed P0 M2 capability using the official open-source integration. Mocha's registration, eligible-account access, refresh/revocation, and successful inference must be verified early. Failed integration blocks this release gate unless the maintainer explicitly changes scope. One saved account per provider/auth method is supported; replacement and logout are explicit.

Order: establish a reliable loop before richer M2 interface work. Minimum workspace enforcement, credential isolation, absolute denies, and subprocess containment precede M1's first real tools. Full modes, trust UI, and rewind follow in M2.

### 3.2 Non-goals for the MVP

- Background daemon, multiple attached clients, subagents, worktrees, editor integration through ACP, and an SDK.
- Hooks, packaged skills, user-defined commands, and custom agents. Built-in commands and instruction-file support remain in scope.
- MCP resources, prompts, and sampling. The client advertises only its supported tool-oriented capabilities.
- Focus mode and the historical Pour, Ledger, and Focus prototype variants.
- Claude subscription sign-in and a Z.ai Coding Plan preset.
- macOS and Windows builds, managed enterprise policy, and dollar spending caps.
- Paid evaluation suites or paid provider calls in CI. Real-model use by the maintainer is separate from automated CI.
- Telemetry, analytics, or automatic crash reporting.
- Local-model-specific features as a release promise. Endpoints using supported APIs can be configured subject to FR-007.
- Staged pruning of stale tool results, fallback chains, credential pools, and cross-session search. Basic compaction and output spill remain M1.

ACP's stable wire protocol is v1 and v2 is draft in the researched sources. Neither is an MVP dependency. The internal protocol is not automatically ACP-compatible. [ACP status](https://github.com/agentclientprotocol/agent-client-protocol/).

## 4. Success measures

| Measure | Target | Evidence |
| --- | --- | --- |
| Daily use | The maintainer can use Mocha as the only coding agent after M2 | Completed representative tasks and the maintainer's report |
| Local overhead | NFR-001 budgets hold under the accepted workload and environment | Raw measurements with build, machine, workload, and sampling metadata |
| Recovery | Acknowledged durable records survive supported failures, and uncertain effects are reported accurately | NFR-002 failure-injection and resume tests |
| Coding outcomes | Changes satisfy the task and pass independent verification | End-to-end edit-test-repair scenarios and reviewable evidence |
| Mechanical regression control | Protocol, policy, tools, storage, and context transforms retain required behavior | Deterministic fixtures and replay tests |

Mock replay demonstrates mechanics. It does not independently demonstrate coding quality, a productivity gain, or universal prompt-injection resistance. Performance targets and recovery guarantees are bounded by their specified acceptance protocols.

## 5. Functional requirements

P0 requirements must pass for their release milestone. P1 requirements are planned but may slip without blocking MVP completion. Section 7.2 records settled decisions and their implementation contracts. Pending verification blocks its dependent support or release claim.

### FR-001: Walking skeleton

**P0 · M0**

- A fresh M0 skeleton starts with an explicitly identified mock provider and no credentials. Its minimal welcome accepts input within NFR-001's defined startup boundary.
- A submitted prompt traverses the client, protocol, engine, provider, and renderer. A mock response streams and finishes with one `Done` outcome.
- Ctrl+C shows a quit hint. A second Ctrl+C within two seconds exits with status 0 and restores the terminal. Other keys do not cancel the hint. The shared state-aware keymap is defined in the runtime contract.
- The M0 path opens no network or IPC sockets. An in-process signal pipe is allowed.
- Provider/engine failure produces a visible error marker and message, including under `NO_COLOR`, and a `Failed` outcome. A subsequent turn can start.
- `--theme dark|light` overrides `MOCHA_THEME`. Unsupported palette names produce a configuration error.
- Rejected requests use typed errors, initially including `protocol_mismatch`, `empty_prompt`, `not_initialized`, `unknown_session`, `turn_in_progress`, and `provider_failed`.
- Fullscreen setup failure restores terminal state and falls back to inline operation. The failure path is tested under a PTY.

### FR-002: Agent loop

**P0 · M1**

The engine records explicit turn states and transitions, including streaming, pending/executing tools, awaiting permission, and terminal outcomes `Done`, `Failed`, `Interrupted`, and `BudgetExhausted`.

- Esc acknowledges cancellation and stops new tool dispatch within 50 ms on the reference workload. Child termination is a separate bounded operation: signal the process group, wait the documented grace period, then escalate. The grace period is two seconds, then SIGKILL.
- Partial output and observed tool outcomes remain available after interruption. Cancellation does not claim to undo an effect that already occurred.
- Ctrl+Enter interjects at a safe cancellation boundary. Tab queues a follow-up for when the current turn would stop. The keymap specifies focus and terminal fallbacks.
- Repeated identical calls and edit/revert oscillation produce one nudge, then a typed stop at documented thresholds.
- Provider-step, wall-clock, and tool-call limits stop work with the exhausted limit identified. Retries and compaction count toward applicable limits. Mocha imposes no cumulative token-usage cap. Track usage for visibility while enforcing each selected model's context and output constraints.
- Independently safe reads may run concurrently. Overlapping mutations are coordinated, including multi-path patches, shell commands, and MCP calls whose write set is unknown. A tool name alone does not establish read-only behavior.
- No tool dispatch occurs from partial or invalid arguments. A late stream event after cancellation cannot revive the cancelled turn.
- Cancellation uses an independent control path even when event delivery is blocked. After 30 seconds of continuously blocked delivery, interrupt with `client_unresponsive`. Quiet commands/provider waits do not trigger this delivery timer. Preserve observed outcomes independently of delivery; the runtime contract defines acknowledgement and exit semantics.

### FR-003: Headless mode (`mocha run`)

**P0 · M1**

`mocha run "<prompt>"` uses the same engine protocol and authorization semantics as the TUI.

- Text mode writes the final answer to stdout and progress/diagnostics to stderr. JSON mode writes only one protocol event per stdout line. Credentials and styling escape sequences do not enter JSON output.
- Every accepted turn has one final outcome. `Done` means the task completed, not merely that the provider stopped generating.
- An action requiring unavailable interactive approval is denied. The run ends nonzero with an approval-required outcome. A preauthorized action can proceed only within its existing grant.
- Required missing information, including model limits, produces a typed input/configuration failure without hanging or guessing. `ask_user` is not advertised as an interactive tool when no input channel exists.
- Numeric exit codes, signal behavior, and final-event ordering are specified and tested before the headless slice is accepted. The codes distinguish success, task failure, interruption, budget exhaustion, configuration/input failure, provider failure, and required approval.
- Resuming or replaying a transcript does not execute recorded commands. FR-010 governs uncertain operations.

### FR-004: Core tools with read-before-write

**P0 · M1**

Built-ins: `read`, `write`, `edit`, multi-file `apply_patch`, `grep`, `glob`, `ls`, `bash` with timeout/background/output/kill controls, `todo`, and interactive `ask_user`. Each declares capabilities, concurrency, output budget, and evidence behavior.

- Existing-file replacement requires a current read observation. Creating a new file requires an observed-absent target and refuses an unexpected intervening file.
- Whole-file overwrite requires a complete read. Targeted edits require observed replaced/context spans. The tools contract defines path/link and patch behavior.
- `write`, `edit`, and every affected `apply_patch` path share stale-observation checks. A stale file produces a reread instruction rather than an overwrite.
- Exact replacement fails without mutation when text is absent or ambiguous, with the closest match and a whitespace hint. `replace_all` is explicit.
- Built-in file replacements are atomic per file. Durable acknowledgement follows NFR-002. This does not make arbitrary shell commands atomic or a multi-file patch a filesystem transaction.
- A multi-file patch reports the actual changed paths and failure outcome. It cannot report complete success after partial application. Validate and stage all files first, publish atomically per file, and report changed/pending paths on partial failure without blind rollback.
- `grep` and `glob` respect `.gitignore`. Unsupported encodings, binary edits, file modes, and links have documented outcomes.

### FR-005: Evidence captured at the source

**P0 · M1**

- Tools record operation identity, effective command/arguments and cwd where applicable, duration, exit/outcome, output size, and file/patch hashes. Redaction applies before persistence or display.
- A side-effecting operation has durable dispatch intent before execution and a result record afterwards. Storage failure before required intent persistence prevents dispatch.
- Evidence distinguishes success, failure, cancellation, partial effect, and `outcome unknown`. Missing evidence cannot be presented as a passed check.
- TUI stats and the final summary use recorded evidence. A provider's assertion that tests passed is not a test result.
- The M1 acceptance task includes an edit, a real project verification command, failure interpretation/repair where needed, and a final result linked to evidence. Automatic LSP diagnostics and reviewer subagents are not added to MVP scope by this requirement.

### FR-006: Provider catalog, connections, and model configuration

**P0 · M1**

Mocha includes a curated provider catalog so a new user can choose a supported provider, connect an API key, and select a coding model without hand-editing configuration. The existing model configuration remains available for custom providers and overrides. The catalog serves Mocha users generally; it is not limited to the maintainer's legacy provider file.

The confirmed M1 catalog contains OpenAI, Anthropic, Google Gemini, OpenRouter, DeepSeek, Z.ai standard API, xAI, Mistral, Groq, Together AI, Fireworks AI, and Cerebras, plus a Custom provider option. TheClawBay and private compatible endpoints use custom configuration or import. This is a curated product scope, not a market-share ranking.

Providers using an implemented API family are configured in `~/.mocha/models.json`. Adding an unsupported wire protocol requires an adapter, not just a base URL. The provider contract names adapter profiles and their required compatibility gates.

- The provider picker identifies connection state and supported authentication methods. It explains unavailable integrations before accepting a key or presenting them as usable.
- Provider setup accepts securely entered API keys or supported environment references, following FR-020. Normal setup does not require manual endpoint or configuration-file edits for a built-in provider.
- After connection, the model picker combines supported catalog metadata, provider discovery where available, and user configuration. Catalog presence, credential availability, account access, and coding-tool compatibility remain distinct states. Unknown account availability is not presented as verified access.
- Ship a reviewed metadata snapshot sourced initially from models.dev, with source/date/hash/schema provenance and its retained license notice. User overrides remain authoritative. [Metadata source](https://github.com/anomalyco/models.dev), [license](https://github.com/anomalyco/models.dev/blob/dev/LICENSE).
- Refresh metadata/discovery on explicit connection or user request, with no default background polling. Keep the last good data on failure. Cache discovery within the selected provider/endpoint/account/auth profile without credential values in cache identifiers.
- Model discovery is separate from an optional inference test that can consume paid/subscription allowance. No paid inference runs merely to refresh the catalog. Refreshes do not silently replace defaults or session models.
- Users explicitly choose their first coding model and may save its provider/model pair as the default for new sessions. Choosing a session model does not silently rewrite that default.
- If a selected model becomes unavailable, Mocha explains the failure and offers alternatives. Switching to another provider or paid model requires user authorization, including an explicitly configured scoped grant if introduced. No implicit paid-model or cross-provider fallback is configured by default.
- A custom-provider path accepts a named endpoint using a supported API family, a credential source, and model configuration. Legacy configuration import remains supported through its fixture. Unsupported formats fail clearly.
- The supported schema retains the existing provider/model layout, including API selection, limits, costs, thinking-level mapping, and scoped compatibility flags. The provider contract links the normative schema and sanitized compatibility fixture.
- A copied legacy file is tested against that fixture. Unsupported APIs or model capabilities remain visible with an actionable explanation rather than being silently selected.
- Unknown extension fields warn once and remain loadable. Unknown API selectors and invalid security-relevant fields are not silently accepted as a supported format.
- Malformed configuration reports path, line, and problem. Mocha uses its last successfully saved valid snapshot, or starts with no providers if none exists.
- Startup and unused session creation write nothing under `MOCHA_HOME`. Valid model configuration is cached at the first prompt when needed. Failed optional cache saves warn and retry at a later prompt without claiming persistence.
- Missing limits use a dated, licensed catalog snapshot when available. Interactive operation asks for remaining required values; headless operation follows FR-003.
- A null thinking-level mapping is unavailable for that model. Compatibility flags affect only the selected model and cannot grant tool permissions.
- Provider keys are not configuration values in this file. FR-020 defines credential sources.

### FR-007: Wire formats and presets

**P0 · M1**

M1 implements Anthropic Messages, OpenAI Chat Completions, OpenAI Responses, and a named native Gemini API surface. The release matrix identifies exact supported models, API families, authentication, images, tools, schema subsets, reasoning state, usage, and cache behavior.

- All four adapters are complete by M1 acceptance. Current OpenAI tool-calling documentation requires Responses for GPT-6 Astra and GPT-6.1 Sol. Do not advertise those combinations through a Chat-only adapter. [Official guide](https://developers.openai.com/api/docs/guides/function-calling).
- An adapter preserves ordered content, call/result identities, and required opaque continuation state, including provider-specific reasoning items or signatures. Fixtures prove round-trip fidelity within the supported API. Arbitrary cross-provider lossless conversion is not promised.
- Provider/model changes identify incompatible state and apply a documented continuation strategy. No foreign reasoning signatures are fabricated.
- Fixtures exercise fragmented UTF-8/JSON/SSE, interleaved calls, incomplete output, refusals, errors, cancellation, and disconnects. Partial arguments never trigger execution.
- Every built-in provider named in FR-006 needs dated endpoint/access evidence and compatibility fixtures before release. Custom/imported providers use the same validation boundaries. An unverified integration cannot count as supported.
- Provider-reported token/cache usage is labeled as reported. Estimated usage and costs are labeled with their pricing source/date. Displayed cost is not a billing guarantee.
- Rate-limit, overload, auth, context-limit, and transport failures have bounded documented retry/stop behavior. A retry cannot silently repeat an operation with an uncertain effect.

### FR-008: Sign in with ChatGPT

**P0 · M2**

OpenAI's Sign in with ChatGPT documentation describes client registration and eligible ChatGPT plan usage for open-source applications. This supplies a documented third-party path. It does not establish that Mocha has completed registration or that every account/model is eligible. The retrieved documentation has no independently verified publication date. [Official quickstart](https://developers.openai.com/siwc/quickstart).

- Verify Mocha's registration, granted scopes, account-specific model access, refresh/revocation, and applicable provider requirements early, with source and review date. Actual account access remains a verification gate, not an unresolved choice about including this feature. Failure does not automatically defer or remove the requirement.
- Use the documented public Responses endpoint and account-specific model catalog. This authentication profile requires `store:false` and `stream:true`, excludes several ordinary BYOK request fields, and treats only `response.completed` as inference success. Preserve it as a distinct adapter profile with its own fixtures. [Inference contract](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference), [preview limitations](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).
- If supported, `mocha login chatgpt` uses the verified browser flow, with a loopback callback bound only to `127.0.0.1` and only during login. Tokens remain in the system keychain.
- Login cancellation and unavailable Secret Service produce an actionable outcome. No plaintext token fallback is introduced. BYOK remains independently usable.
- Expired tokens refresh within bounded behavior. Failed refresh/revocation asks for sign-in without exposing credentials or corrupting the session.
- Logout removes stored credentials. Headless login behavior and browser/callback failures are documented and tested.

### FR-009: Context management

**P0 · M1**

- Logical prompt components have stable ordering. Each adapter defines actual serialization and caching behavior; one universal byte layout is not assumed across vendors.
- Context accounting reserves output/reasoning, tool schemas, and unfinished call/result exchanges. Provider-reported usage and planning estimates remain distinguishable.
- Before the configured threshold is exceeded, compaction creates a structured handoff preserving goals, decisions, current instructions, touched-file state, open work, pending calls, approval scope, and evidence references.
- Compaction updates the model view and records the transition. Original history remains available to the UI. Taint and permission state do not reset through compaction.
- Context-limit errors permit one safe compaction retry within the turn budget. Failed compaction or insufficient remaining capacity produces a typed failure with recoverable history.
- Oversized output spills to the session folder with a bounded view and readable reference. Storage errors follow NFR-002 and output is subject to NFR-009.

### FR-010: Durable sessions

**P0 · M1**

- Sessions use versioned append-only records under `~/.mocha/sessions/`. Supported durability boundaries include accepted prompts, dispatch intent, tool results, and terminal outcomes. The storage contract requires fsync before their durable acknowledgements and batches streamed text at 250 ms or 4 KiB.
- Resume reconstructs durable history and marks an interrupted turn. An operation with intent but no durable result is `outcome unknown`, not automatically failed or safe to rerun.
- Resume never automatically repeats arbitrary shell commands or remote mutations. Reconciliation or retry requires a known safe mechanism or explicit authorization.
- `mocha -c`, `mocha --resume <name>`, and `mocha sessions` find and reopen project sessions. A second writer to the same session is rejected by an exclusive writer lock.
- Every session ID is unique within its engine even before persistence. Unused creation writes nothing, and IDs already handed out are not reused.
- Supported older formats migrate with a retained original. Newer/unsupported formats fail clearly without destructive rewriting. NFR-007 applies.
- A 10k-entry resume meets the NFR-001 workload definition. Retention and cleanup do not silently remove required recovery evidence.

### FR-011: Permission modes and rules

**P0 · M1 minimum enforcement; M2 full modes and rules**

Modes are `auto` by default, `approve`, `plan`, and explicitly selected `unattended`. The maintainer approved the Jcode-inspired automatic local-work flow and delegated final naming/behavior. The [mode matrix](contracts/tools-and-policy.md#mode-decision-matrix) is normative. Auto reflects on uncertain destructive actions, Approve confirms mutations, Plan blocks mutations, and Unattended omits reflection but stops rather than requesting new approval. All retain independent authorization, containment, credential, checkpoint and absolute-deny requirements. Tiers remain safe, recoverable with checkpoint, unclear/reflection, ask, and absolute block. Trusted user decisions grant authority; model rationales and tool descriptions do not.

- Hard denies apply in every mode. Explicit deny beats allow. Instruction content cannot override either. Taint-driven approval rules in FR-015 also apply to `unattended` unless an authorized rule names the allowed action within its scope.
- Permission previews show effective action, paths, arguments, and relevant destinations without secrets. Grants distinguish once, session, persistent rule, and deny. Persistent grants require authorized user-controlled configuration.
- Changed arguments, destination, capability, or server identity trigger reevaluation when outside the existing grant.
- A real shell parser decomposes compound input. Parsing does not prove the effects of arbitrary scripts. Unknown effects and untrusted MCP hints do not become authorized through model reflection alone.
- Unknown MCP effects require approval. In headless mode, missing required approval ends the run with its distinct nonzero outcome.
- `plan` refuses agent mutations and side-effecting commands. A recoverable tier requires the promised checkpoint coverage; unavailable recovery cannot be represented as protected execution.
- M1 requires the minimum containment and authorization contract before real tools. Every command/mutation asks unless a scoped user grant applies. `--allow-writes` covers built-in workspace file mutations only. Commands need their own exact-command grant. Neither bypasses containment, sensitive-path approval, or credential blocks.

### FR-012: Linux sandbox

**P0 · M1 minimum containment; M2 complete coverage**

Commands and local MCP subprocesses use the selected OS containment profile. The PRD baseline remains workspace-limited writes and network off unless explicitly allowed. Provider requests and verified login flows have separately documented host-side network/credential boundaries.

- Required platform capabilities are probed. If a requested profile cannot be enforced, execution fails closed and doctor explains the missing capability. No silent weaker profile or unsandboxed retry occurs.
- Publish a coverage matrix for built-in file tools, shell descendants/background jobs, local MCP, remote MCP, provider HTTP, and login callbacks. Separate authorization, OS containment, network access, and credential exposure.
- The tools contract specifies inherited descriptors, UDP, Unix services, child setup, and environment. Capability probes and real enforcement tests gate supported platforms.
- Destination grants and any hostname policy need their own enforcement/tests. Landlock TCP-port filtering alone is not a hostname allowlist. [Kernel interface](https://www.kernel.org/doc/html/v6.12/userspace-api/landlock.html).
- An allowed destination does not imply inspection of every payload. Documentation states coverage and exclusions precisely.

### FR-013: Project trust

**P0 · M2; authority boundary applies from M1**

- Repository configuration and MCP startup require trust. Declining trust leaves only user configuration active. Repository instruction text may be read as untrusted guidance and cannot grant capabilities.
- Changed trust-relevant configuration prompts again before its new grants or executable resources are used. Repository identity and the relevant file set are specified before trust implementation.
- Headless operation never implicitly trusts a new project. Required trust without an existing grant returns the FR-003 approval outcome.
- M1 instruction loading does not load repository permission config or start repository MCP servers before the later trust machinery exists.

### FR-014: Checkpoints and rewind

**P0 · M2**

- A protected mutation requires a successful checkpoint of its documented recovery scope. Checkpoint failure is visible before dispatch and cannot be labeled recoverable success.
- The proposed shadow repository never changes the user's Git refs, index, or stash. Mechanism choice belongs to the architecture.
- `/rewind` offers code, conversation, or both at a selected point. Ctrl+Z opens a preview of the latest checkpoint; confirmation precedes restore.
- Coverage names tracked/untracked/ignored files, binaries, modes, links, creation/deletion/rename, files outside the workspace, and exclusions. External service effects are not undone by a workspace snapshot.
- Checkpoints of covered workspace files use private, unencrypted local storage. Ignored files and configured sensitive paths are excluded. No separate automatic plaintext `.env` backup is created. A known harness credential must not be copied into checkpoint content, including temporary storage.
- Mutating an excluded file requires approval explaining that the path has no rewind coverage. Exclusion affects recovery coverage, not whether reading that file may place its contents in history or provider context. Absolute credential-path blocks still apply.
- Private plaintext recovery storage can contain unrecognized user secrets. This accepted boundary also applies to session history/spill content, while NFR-009 separately protects known harness credentials. See [the recovery-storage decision](adr/0001-bounded-local-recovery-storage.md). The storage contract fixes coverage and retains recovery material until explicit deletion with a preview.
- External edits trigger conflict review before overwrite. Interrupted restore, disk-full, missing Git, retention, and cleanup have tested outcomes and cannot leave a falsely reported complete restore.

### FR-015: Hidden-instruction protections

**P0 · M2**

- Model output, files, tool results, and MCP content cannot grant authority. Content arriving through a tool never acquires user/system authority by claiming it.
- Untrusted content is labeled, and the session's taint state persists across compaction/resume. Labeling is one control, not proof that the model cannot follow malicious content.
- In a tainted session, model-proposed outbound tool actions and credential access rise at least to ask, in every mode, unless an authorized exact-action rule applies. Tier-4 blocks remain absolute.
- Configured provider requests and required authentication are separate host operations, not blanket grants to model-proposed exports. FR-012's coverage matrix identifies those boundaries.
- NFR-006 exercises the actual authorization/containment path. No universal injection-resistance claim follows from a mock suite alone.

### FR-016: MCP client

**P0 · M2**

- Support tools over configured stdio and Streamable HTTP transports. Project servers require trust. Tool schemas are deferred until needed.
- Remote MCP supports user-scoped static bearer/environment credentials and explicit browser OAuth with discovery, PKCE, resource/issuer binding, protected refresh/logout and supported client registration. OAuth consent never grants tool authority. Headless/Unattended stop when fresh consent is required. The provider/MCP contract specifies exact behavior and public metadata publication gates.
- Publish the supported revision/capability profile and prove it with the selected SDK. The researched current revision is `2026-07-28`, whose request/lifecycle rules differ from handshake-based `2025-11-25` and earlier. Advertised legacy support requires separate fixtures. [Versioning](https://modelcontextprotocol.io/specification/versioning), [dated changes](https://modelcontextprotocol.io/specification/2026-07-28/changelog).
- Discovery handles pagination, schema limits, stable server/tool identity, cache freshness/scope, changed lists, and changed credentials. Unsupported input-required/capability cases return an explicit outcome rather than hanging or falsely advertising support.
- Server/tool hints are advisory. Unknown effects require approval under independent policy. Grants and credentials are scoped to the intended server/resource.
- Disconnect/auth/schema-change failures are visible without losing the session. Transport reconnection does not authorize repeating an uncertain remote effect.

### FR-017: Instruction files

**P0 · M1**

- Global `~/.mocha/AGENTS.md` precedes project guidance. At each level, `AGENTS.md` is primary and `CLAUDE.md` is the fallback.
- Instruction discovery follows the files actually touched, including deeper subtrees beyond the starting cwd. Nearest applicable guidance takes precedence within its scope. Explicit user instructions retain priority. [AGENTS.md guidance](https://agents.md/).
- Changes, conflicting paths in a batch, symlinks, and size limits have deterministic behavior. Import support is not assumed from the broader feature catalog.
- Instruction scope never expands project trust, OS access, or permission grants.

### FR-018: Plain TUI

**P0 · M1**

- Top bar, activity/progress line, transcript/tool evidence, composer, spinner, Volt palette, and added/removed diff tints are present.
- Unknown completion is represented as activity, not a fabricated percentage. Supported terminal progress indicators clear correctly on every terminal outcome.
- Resize preserves readable history. Color degradation and `NO_COLOR` retain status meaning without color alone.
- Keybindings and fallback sequences follow the state-aware contract. Cancellation, approvals, and terminal restoration are tested against the real binary.

### FR-019: Full TUI

**P0 · M2**

- Fullscreen remains default, with inline fallback/setting and documented component differences.
- Wheel, PgUp/PgDn, and End navigate history. New output does not move the content being read while scrolled back. Resize/reflow retains a stable reading anchor.
- Selection copies source text without gutters or wrap artifacts. OSC 52 failure/unavailability has an explicit fallback or failure indication. A toast cannot claim an unsuccessful copy.
- Search covers the transcript, reports match position, and supports keyboard traversal.
- Approvals and questions use the dock. Keyboard-only operation reaches supported transcript groups, diffs, rail items, and every decision option.
- The rail at wide widths shows implemented sections. An Agents label does not introduce subagents into MVP scope.
- Welcome shows model, folder, and recent sessions. Dark/light themes and detection fallbacks remain legible at 80×24.

### FR-020: Configuration, credentials, and first run

**P0 · M1, layered project configuration in M2**

- Mocha-managed file state lives under `~/.mocha/`, overridden by `MOCHA_HOME`. OS-keychain credentials and deliberate workspace edits have distinct locations and policies.
- Project `.mocha/config.toml` and `.mcp.json` require trust. Document configuration precedence and schema versions before layered config implementation.
- Provider credentials come from named environment variables or the OS keychain. They are not persisted as plaintext config. Missing Secret Service permits configured BYOK environment use and an actionable doctor result, not a hidden plaintext fallback.
- Child environments exclude harness provider/login credentials by default. Approved passthrough is explicit. Credential handling for each remote MCP resource is separate.
- Fresh install with no provider opens the provider catalog, guides the user through secure BYOK connection and coding-model selection, and enables a first real turn. Built-in provider setup requires no hand-edited configuration. It never presents a mock reply as a real provider response. Headless missing setup follows FR-003.
- Explicit setup/login commands may persist their intended state. Normal startup remains read-only. Supported configuration migrations retain originals and persist at a documented explicit-write/first-prompt boundary.

### FR-021: `mocha doctor`

**P1 · M1 basic, M2 complete**

Reports version and available signature-verification evidence, terminal capabilities, config/model validity, credential availability without values, sandbox coverage/capability failures, required external tools, and another `mocha` shadowing the command on PATH. Unsupported checks are labeled unavailable, not passed.

### FR-022: Versioned protocol boundary

**P0 · M0 onward**

- TUI and headless clients use versioned requests and correlated events. In-process transport does not permit calls into engine internals from clients. CI checks dependency direction.
- Version mismatch identifies both versions. Request rejection and accepted-turn failure are distinct.
- Stable request/session/turn/event identities, ordering, prompt acceptance, terminal outcomes, bounded channels, and slow-client behavior are specified before the relevant slice.
- Display-delta coalescing preserves all semantic tool, approval, evidence, and final-state events. Replay reconstructs observations without live execution.
- Internal protocol versioning is independent of MCP revisions and future ACP adapter versions.

### FR-023: Release and install

**P0 · M2**

- Release artifacts are static Linux x86_64 and arm64 binaries with SHA-256 checksums and minisign signatures. Builds verify target/linkage claims rather than assuming Rust/TLS choices make them static.
- `cargo install mocha-code --locked` installs the `mocha` command from the published crate. Package-name availability and clean-machine installation are verified before publication.
- Each release records source revision, toolchain, lockfile, selected features, and dependency inventory. The pipeline provides verifiable build provenance and documents how consumers verify artifacts.
- CI prepares draft artifacts. The maintainer retains signature/publication authority. Signing keys are not placed in untrusted PR execution.
- Release tool prerequisites are separate from the application's MSRV. A reproducible-build claim requires an independent comparison, not merely a lockfile.

### FR-024: Provider access notices

**P1 · M1**

No Z.ai Coding Plan preset is shipped. A provider-specific notice needs a dated authoritative source for the intended endpoint/client and is reviewed before release. It cannot claim that Mocha is supported without evidence, or that displaying a notice establishes access permission. Preset access and compatibility verification remain release gates in the provider contract.

## 6. Non-functional requirements

### NFR-001: Reproducible performance budgets

**P0 · M0 onward**

| Metric | MVP target |
| --- | ---: |
| Start to input ready | ≤ 20 ms |
| Idle RSS, client including in-process engine | ≤ 12 MB |
| Keystroke to paint, p99 | ≤ 8 ms |
| Streaming render CPU, one specified mock workload | ≤ 3% of one core |
| Per-tool harness overhead, excluding actual tool work | ≤ 1 ms |
| Resume a specified 10k-entry log | ≤ 100 ms |
| Stripped binary size | ≤ 25 MB |

These remain proposed product budgets, not measured achievements or industry standards. The verification plan fixes workload, accounting, sampling, and noise rules. M0 must calibrate the named candidate reference environment and demonstrate repeatability before budget acceptance.

CI then enforces applicable budgets. Budget changes require an explicit reviewed change, not an automatic baseline reset. Store raw JSON results with environment/workload metadata. TUI readiness is not measured by timing `--version`. Future daemon budgets belong to the later roadmap and cannot hide MVP engine costs.

### NFR-002: Bounded durability and recovery

**P0 · M1 onward**

- Durable acknowledgements occur only after the required persistence steps succeed. The storage contract specifies prompt, intent, result, and terminal boundaries and the transient streamed-text loss window.
- Supported crash recovery preserves earlier durable records, detects/drops a torn final record with a notice, and exposes incomplete operations honestly.
- Built-in file replacement distinguishes atomic visibility from persistence, including file/directory synchronization on supported filesystems. [Linux persistence semantics](https://man7.org/linux/man-pages/man2/fsync.2.html).
- ENOSPC/EIO stops unsafe continuation and cannot report an unpersisted result or restore as durably complete. An effect already executed remains represented as uncertain when its result cannot be saved.
- Failure injection covers kill before dispatch, during execution, after effect/before durable result, torn logs, full disk, failed migration, and interrupted restore when rewind exists.
- SIGKILL testing does not certify every power-loss, hardware-failure, or external-service scenario. Workspace rewind has FR-014's coverage, not universal undo.

### NFR-003: Privacy and destinations

**P0**

No telemetry, analytics, or automatic crash reporting leaves the machine. Prompts/code go to configured providers. Explicit tool actions may communicate with authorized MCP services or other destinations within their grants. Login and updates, if any, have documented destinations and triggers. README and doctor explain local storage, outbound paths, and credential handling without claiming all data stays local.

### NFR-004: Clean-room and dependency licenses

**P0**

MIT is the intended project license. The repository must contain its license and notices before release. Dependency checks cover the resolved graph, selected features, licenses, advisories, banned dependencies, and allowed sources. Registry license metadata alone is not a completed compliance check. The clean-room rule in §1 remains a project constraint.

### NFR-005: Mechanics, coding outcomes, and evaluation

**P0 · M1 onward**

- CI uses mock providers and explicitly isolated loopback fixture servers. It has no real-provider credentials or paid API calls. Fixture allowance cannot reach arbitrary hosts.
- Replay verifies event ordering, tool inputs/results, edits, approvals, context transforms, and recovery in disposable environments. Reconstructing history itself has no live tool effects.
- Fuzz tests cover untrusted streams, patch/shell analysis, and configuration parsers. Their budgets and failure reporting are documented.
- M1 acceptance includes independent grading of a real edit-test-repair workflow in both interfaces. Record task, model/API/config, environment, budgets, resulting patch, verification evidence, and interventions. Keep deterministic mechanics separate from real-model quality observations.
- Public leaderboard scores are not release proof. Any comparative evaluation requires a versioned task/environment, matched settings/budgets, repeated trials, and grading outside the agent-modified environment. No paid evaluation suite is added to CI.

### NFR-006: Injection and authorization regression suite

**P0 · M2**

Adversarial fixtures include hostile files/output/MCP results, fake authority, exfiltration attempts, credential exposure, hostile tool hints, changed grants/schemas, and self-edited trust/config. The real enforcement path must refuse or require authorized approval for harmful actions. Mock fixtures test controls, not universal model resistance. Include containment bypass cases for inherited resources and unavailable capabilities.

### NFR-007: Saved-data compatibility

**P0**

Published supported log/config/model schemas have explicit versions and forward migrations with originals retained. Failed migration leaves the original usable. Newer or unsupported schemas fail with a clear recovery path instead of destructive guessing. Protocol mismatch is separate from saved-data migration. Downgrade support is not implied.

### NFR-008: Accessibility and terminal robustness

**P1 · M1–M2**

Status meaning survives without color. `NO_COLOR`, reduced motion, 80×24 layout, keyboard paths, resize, unavailable OSC features, and terminal restoration have acceptance cases. Missing terminal capabilities do not produce false success indications.

### NFR-009: Credential and secret hygiene

**P0 · M1 onward**

- Mocha does not create plaintext provider/login credential stores or expose harness credentials in logs, transcripts, JSON, diagnostics, or crash output.
- Known credentials are redacted before output/persistence and excluded from child environments by default. Tests include chunked output and every sink. Redaction is not claimed to detect every unknown or transformed secret.
- User history and covered workspace snapshots use private, unencrypted local storage under FR-014's accepted policy. Ignored/configured sensitive paths are excluded from checkpoints. Unrecognized secrets can remain in covered files or history; no secret-free-storage guarantee is made.
- Spill files, session exports if introduced, evidence arguments, backup migrations, and retained recovery records follow the same documented protection/retention policy.

## 7. Risks and decisions

### 7.1 Current risks

| Risk | Mitigation/verification |
| --- | --- |
| A large MVP delays a useful coding loop | Preserve loop-first sequence and an explicit release boundary. P0 changes require a recorded scope decision. |
| Provider compatibility or access changes | Dated model/API/auth matrix, fixtures, and separately verified subscription/preset access. |
| Safety controls cover fewer paths than their names imply | Per-tool coverage matrix, minimum-capability probes, and real enforcement tests. |
| Recovery claims hide uncertain effects or secret storage | Intent/result contract, honest unknown outcomes, bounded checkpoint policy, and failure injection. |
| Fast mechanics are mistaken for useful coding | Independent edit-test-repair acceptance and maintainer workflow evidence. |
| Budgets are noisy or measure empty work | Accepted workloads, reference environment, raw results, and reviewed threshold changes. |
| Dependencies/tools do not fit the chosen build | Locked compatibility spike on both targets, separate MSRV/tool prerequisites, and selected-feature checks. |
| Existing docs are mistaken for implementation evidence | Truthful status/evidence links and reconciliation of supporting documents. |

The [dependency research](research/2026-11-14-mocha-dependency-evidence.json) verifies published metadata for 22 entries, not a compiled workspace. Rust 1.100.0 was released November 12. Hyperfine 2.0.0 declares Rust 1.97.0, above the architecture's 1.96.1 pin if that compiler builds the tool. `toml` publishes `1.2.1+spec-1.1.0`; a bare-version registry 404 did not establish an invalid Cargo requirement. Resolve toolchain, application MSRV, tool installation, and static linking in architecture, not by copying a “latest” number into the PRD. [Rust release](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/).

The previous legal/regulatory applicability screen is withdrawn because this research did not verify it. Provider requirements and licensing remain review items before the associated release claims. This PRD makes no jurisdiction-specific legal determination.

### 7.2 Settled decisions and remaining proof

These interview choices were confirmed by the maintainer. A subsequent [semantic audit](reviews/2026-11-14-prd-gap-audit.md) identified detail gaps in permission-mode behavior, token-budget policy, cancellation under backpressure, shared-store concurrency, and tool prerequisites. The follow-up interview resolved all five findings at specification level. Closures include no cumulative token cap, the final mode matrix, independent cancellation with a 30-second delivery-stall timeout, shared-state coordination, and minimum guards before real commands. The confirmed choices below remain the baseline. Their implementation/failure-path checks remain required before associated behavior is accepted. Engineering defaults in the linked contracts are not claims of executed tests.

| Decision | Confirmed choice | Contract and remaining proof |
| --- | --- | --- |
| D-01 | Twelve built-in providers plus Custom; all four API families in M1 | [Providers](contracts/providers-and-mcp.md). Per-profile fixtures and usable coding-model paths must pass. |
| D-02 | Explicit model choice, optional new-session default, authorized switching, no implicit paid fallback | Provider setup and model-switch tests |
| D-03 | Reviewed models.dev metadata, explicit refresh, last-good preservation and user overrides | Snapshot provenance/license and discovery fixtures |
| D-04 | Native ChatGPT sign-in required in M2; one saved connection per provider/auth method | Early registration, eligible inference, refresh/revocation proof |
| D-05 | Private plaintext history/checkpoints; sensitive/ignored exclusions; explicit approval for uncovered edits | [Storage](contracts/storage-and-context.md). Coverage, secret-boundary and restore tests |
| D-06 | Retain sessions and referenced recovery/evidence until explicit previewed deletion | Storage-pressure and cleanup tests |
| D-07 | Stage/validate multi-file patches first, atomic per-file publication, honest partial results | [Tools](contracts/tools-and-policy.md). Second-file failure and external-change tests |
| D-08 | Network off for subprocesses; fail closed; minimum enforcement before M1 real tools; hard denies in every mode | Real OS containment, inheritance and credential tests |
| D-09 | Noninteractive missing approval/input stops distinctly; unknown effects never blindly replay | [Runtime](contracts/runtime.md) and crash/replay tests |
| D-10 | State-aware Esc/Ctrl+C, two-second child grace, durable boundaries, 250 ms/4 KiB text batching, one writer | PTY, persistence and writer-lock tests |
| D-11 | Retain performance budgets; calibrate repeatability and include persistence/checkpoint/safety costs | [Verification](verification.md). A miss stops for optimization or explicit budget revision. |
| D-12 | auto/approve/plan/unattended mode matrix, scoped reflection, no unattended approval waits | Policy decision fixtures and actual all-mode enforcement tests |
| D-13 | No cumulative token cap; usage remains informational | Usage reporting and model context/output-limit tests |
| D-14 | Independent cancellation; 30-second continuously blocked delivery interrupts | Full-channel, blocked-pipe, persistence and PTY/clock cases |
| D-15 | Cross-process shared-state ownership/revision checks; minimum guards before real commands | Config/auth race tests and SLICE-005 prerequisite failure-path evidence |

All 19 local slice specs now assign acceptance/failure cases, boundary schemas, planned verifier commands, owner, dependencies and evidence requirements. The final review resolved the remote MCP authentication choice with explicit maintainer approval for OAuth plus static keys. Schemas/specifications are not generated execution evidence. Integration failures remain visible gates, not silent scope reductions.

## 8. Release gates

| Gate | Required evidence |
| --- | --- |
| Ready to implement a slice | Its prerequisites above resolved, acceptance and failure cases mapped, interface/schema details supplied, and verifier reviewed. |
| M0 complete | FR-001 and FR-022 pass; accepted NFR-001 checks execute in CI; activation claims link to actual failing/passing evidence. |
| M1 complete | M1 portions of FR-002–FR-007, FR-009, FR-010, FR-017, FR-018, and FR-020 pass. Minimum containment, authorization, and trust boundaries hold. NFR-002, NFR-005, and NFR-009 pass. Real edit-test-repair tasks succeed in TUI and headless with recorded evidence. |
| M2 complete | Every P0 criterion, including required native ChatGPT sign-in, passes. NFR-006 passes; containment/rewind/auth claims have evidence; the maintainer reports daily-driver readiness. Any scope change requires an explicit maintainer decision. |
| Any binary release | FR-023 install, target/linkage, signatures/provenance, dependency/license, and verification evidence exists; publication is authorized by the maintainer. |

A planned test command, a mock narrative, registry metadata, or an `ACTIVE` label is not execution evidence. Unresolved prerequisites and failed checks remain visible and block their dependent claim.

## 9. Build handoff

[The documentation index](README.md) defines authority and status. [Architecture](04-architecture.md) orders the work. Four contracts define runtime, tools/policy, providers/MCP, and storage/context behavior. [Verification](verification.md) maps all requirements to slices and evidence. [The complete slice index](slices/README.md) links all 19 concrete implementation specifications, beginning with SLICE-001.

The feature roadmap and UI design have been reconciled to this scope. The older blueprint is historical. No application behavior, CI guard, benchmark, provider access, or release artifact is claimed as proved by documentation checks. The maintainer confirmed shared understanding on November 14, 2026. SLICE-001 is ready for implementation.

## 10. Revision history

- Revision 5, November 14, 2026: completes the local 19-slice specification review; confirms remote MCP browser OAuth plus static keys; supplies version-1 boundary schemas and acceptance corpus; closes context/capture/queue/redaction/rewind/UI/release detail gaps and corrects UI-versus-SIWC blocking dependencies. Actual implementation and external feasibility gates remain pending.

- Revision 4, November 14, 2026: resolves the five audited specification findings. Final mode naming/behavior was selected under the maintainer's explicit delegation. Renames rip/careful/yolo to auto/approve/unattended, defines the mode matrix and noninteractive refusal, removes the cumulative token cap, specifies independent cancellation/shared-state coordination, and fixes first-command prerequisites. Runtime verification remains pending.

- November 14, 2026 follow-up clarification: the maintainer rejected a cumulative token cap. FR-002 now requires usage visibility and model context/output limits, while retaining the separately agreed step, tool-call, and time safeguards.

- Revision 3, November 14, 2026: incorporates the confirmed interview decisions, closes product-choice prerequisites, adds linked engineering contracts, moves minimum containment before M1 tools, and reconciles the build handoff. The maintainer subsequently confirmed shared understanding of this revision on November 14, 2026.

- Revision 2, November 14, 2026: incorporates the market/build-readiness research, retains FR-001–FR-024 and NFR-001–NFR-009, clarifies product scope and evidence limits, corrects provider/protocol/access claims, bounds safety/recovery/secret guarantees, and adds explicit readiness decisions and follow-up reconciliation.
- Revision 1, November 10, 2026: original checked-in draft. References to later accepted PRD revisions in supporting material were not substantiated by this checkout and are not adopted as approval evidence here.
