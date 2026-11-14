# Mocha market and build-readiness research

Research cutoff: **November 14, 2026**, inclusive. Status: research and proposed changes, not an accepted replacement specification.

## Finding

Mocha has a credible product direction: a compact, provider-flexible coding agent with a calm terminal interface, explicit execution boundaries, useful evidence, and recoverable work. The research does not establish that another large feature catalog is an unmet market need. Native executables, Rust implementations, provider choice, MCP, and unattended operation already appear in comparable products. The proposed differentiator should be the combination of verified coding outcomes, predictable automation, bounded resource use, and precise recovery behavior. This is a positioning hypothesis to test, not an established competitive advantage. [Codex](https://github.com/openai/codex), [Goose](https://github.com/block/goose), [Aider verification](https://aider.chat/docs/usage/lint-test.html).

The immediate obstacle is specification consistency. The current docs disagree on scope, safety, headless outcomes, durability, and accepted revision history. They also leave build-tool prerequisites and compatibility unverified. Research should inform those corrections before implementation begins.

No research exercise can prove the permanent absence of gaps. A useful completion standard is narrower: every known requirement has an owner, an observable acceptance condition, a delivery slice, and evidence appropriate to the claim; unresolved assumptions are visible and block the work that depends on them.

## 1. Method and confidence

The work covered four research areas: competitor products; safety and recovery; interoperability and provider behavior; and developer demand, evaluation, dependencies, and releases. Exa was used for discovery and page retrieval. Sources were restricted to protocol maintainers, project repositories, vendor documentation, original studies, benchmark maintainers, kernel documentation, and package registry metadata.

Search accounting: 23 Exa searches requested **137 result slots** across the workstreams: 33 competitor, 25 safety, 35 interoperability, and 44 evaluation/demand/toolchain/supply-chain. These are requested result slots, not 137 distinct validated sources. Repeated URLs and secondary commentary were excluded from the evidence synthesis. Direct primary-source reads and 22 exact-version registry checks supplied additional evidence. The companion [source inventory](2026-11-14-mocha-research-sources.json) records fetched URLs; the [dependency evidence](2026-11-14-mocha-dependency-evidence.json) records registry results.

Evidence is used in three different ways:

- **Dated evidence:** published releases, announcements, studies, and dated protocol revisions no later than the cutoff. These can support date-specific claims.
- **Observed documentation:** current official pages or repository READMEs without a verified historical snapshot. These describe the material retrieved, not guaranteed availability in every release by the cutoff.
- **Recommendation:** an inference for Mocha. Recommendations in this report do not silently change the PRD or settle the pending design interview.

Vendor sources are strong evidence of documented interfaces and limitations, but do not independently establish product quality, market share, or productivity. The developer survey is a self-selected sample; it is not a market-size estimate. No competitor was installed or benchmarked, no paid model calls ran, and no user interviews were conducted. Exact vendor prices, market share, willingness to pay, and comparative resource advantages were not established.

## 2. Developer needs and positioning

### Verification and reliability have evidence behind them

Stack Overflow released its 2026 survey on October 6. The trust question had 14,304 respondents: 48.0% selected trust when output is easily verified; 6.6% selected trust including important work decisions. The broader survey had 30,903 valid responses and was promoted through Stack Overflow channels. Those denominators and recruitment limits matter: this is evidence about participating developers, not all developers. [Trust question and data](https://survey.stackoverflow.co/2026/ai/data/ai-trust), [methodology](https://survey.stackoverflow.co/2026/methodology), [dated release](https://stackoverflow.co/company/press/archive/stack-overflow-annual-developer-survey-ai-trust-conditional/).

**Implication:** make it easy to inspect what changed, which checks ran, what they proved, and what remains uncertain. Prioritize a dependable edit-check-repair workflow and reviewable results over expanding the number of modes or integrations. This is an inference from the survey and existing product workflows, not proof that respondents would adopt Mocha.

### Productivity claims need task-level evidence

METR's February 24, 2026 update says its follow-up developer productivity experiment became difficult to interpret because developers and tasks were increasingly selected out of the no-AI condition; concurrent agents also complicated time measurement. The authors explicitly caution against treating the resulting estimates as a reliable current productivity effect. Neither the older slowdown finding nor the follow-up should become a universal claim about coding agents. [METR update](https://metr.org/blog/2026-02-24-uplift-update/).

**Implication:** dogfood Mocha on declared real tasks and record accepted outcomes, repair time, human intervention, and verification effort. A fast first paint is useful, but it does not establish faster successful development.

### Proposed audience and value hypothesis

Retain the current maintainer-first audience provisionally. A plausible secondary audience is terminal-oriented developers who want provider choice, unattended workflows, transparent behavior, and low local overhead. That secondary audience is a research hypothesis, not measured demand.

Test the hypothesis with representative tasks: repair a failing test in an unfamiliar project, add a feature across several files, recover after interruption, resume a long session, and run unattended with restricted permissions. Ask potential users what would make them switch from their existing agent, then observe the same workflows. Do not use repository stars, model benchmark ranks, or feature counts as substitutes for switching evidence.

## 3. Competitive landscape

This is a capability comparison, not a ranking. Unless a date is stated, the evidence is mutable owner documentation observed during research.

| Product | Relevant documented behavior | What Mocha should learn |
| --- | --- | --- |
| Claude Code | Interactive and headless workflows, permission modes, authentication options, and code/conversation checkpoints with explicit exclusions. [Automation](https://code.claude.com/docs/en/headless), [permissions](https://code.claude.com/docs/en/permission-modes), [checkpoints](https://code.claude.com/docs/en/checkpointing) | Specify the same core outcomes across TUI and headless. Explain recovery exclusions clearly. |
| Codex CLI | Native Rust implementation, terminal UI, unattended execution, MCP, and separately configured execution controls. Repository identifies Apache-2.0 licensing. [Repository](https://github.com/openai/codex), [Rust implementation README](https://github.com/openai/codex/blob/eaf81d3f/codex-rs/README.md) | Rust/native/headless/MCP is an existing combination. Resource advantages must be demonstrated on a declared workload. |
| Gemini CLI | Google distinguishes consumer access from enterprise/API access; its dated transition documents supersede older consumer-quota pages. [May announcement](https://developers.googleblog.com/en/an-important-update-transitioning-gemini-cli-to-antigravity-cli/), [October deprecation record](https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals) | Separate an API format, model endpoint, authentication mechanism, and subscription entitlement. |
| Antigravity CLI | Google's May 19 announcement describes a Go terminal client, asynchronous multi-agent work, and a shared backend with its desktop product. It explicitly does not promise immediate feature parity with Gemini CLI. [Announcement](https://developers.googleblog.com/en/an-important-update-transitioning-gemini-cli-to-antigravity-cli/) | Vendor products and access models change. Maintain dated integration evidence and avoid copying their entire scope. |
| OpenCode | Provider selection and authentication, build/plan agents, and subagent workflows. Repository identifies MIT licensing. [Repository](https://github.com/anomalyco/opencode), [providers](https://opencode.ai/docs/cli/providers/) | Provider choice and plan/build modes are expected comparison points, not unique positioning. |
| Aider | Repository mapping and configurable lint/test feedback during editing. Repository identifies Apache-2.0 licensing. [Repository](https://github.com/Aider-AI/aider), [map](https://aider.chat/docs/repomap.html), [verification](https://aider.chat/docs/usage/lint-test.html) | Good coding assistance needs relevant context and a repair loop. These matter more than transcript polish alone. |
| Goose | Rust local agent with CLI/desktop/API surfaces, provider integrations, and MCP. Repository identifies Apache-2.0 licensing and describes external-agent integration. [Repository](https://github.com/block/goose) | Separate native model adapters from delegating to another agent through a protocol. Rust plus provider flexibility is already represented. |
| Pi | Shared interactive/print/JSON/RPC/session machinery, compaction preserving original history, and extensibility. Its docs distinguish project trust from OS isolation. [Architecture and boundaries](https://pi.dev/docs/latest/how-pi-works) | A small core can serve several interfaces. Trust, policy, and containment still need independent contracts. |

Software licenses in this table describe source repositories. They do not establish access rights to a vendor's hosted service. No legal entitlement conclusion is made here.

### Date-sensitive Google correction

Google's May 19, 2026 announcement set June 18 as the end of Gemini CLI consumer/free and Google AI Pro/Ultra access, while distinguishing enterprise/API access. Its October 9 deprecation page confirms that the consumer change occurred and points users to Antigravity. Do not repeat older free-tier claims from the February Gemini overview as the current consumer story. This does not mean that Gemini model APIs disappeared, or that every enterprise access path follows the consumer schedule. [Announcement](https://developers.googleblog.com/en/an-important-update-transitioning-gemini-cli-to-antigravity-cli/), [deprecation](https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals).

## 4. Protocol and provider findings

### Name the supported MCP revisions

The official MCP versioning page identifies **2026-07-28** as current. Its changelog removes the initialization handshake and protocol-level sessions, introduces per-request version/capability metadata and `server/discover`, revises notifications and multi-round-trip requests, and removes SSE response resumability. Older handshake-based revisions need a separate compatibility path. [Versioning](https://modelcontextprotocol.io/specification/versioning), [dated changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [lifecycle](https://modelcontextprotocol.io/specification/2026-07-28/basic/lifecycle).

**Recommendation:** replace generic “MCP support” with a support profile: revisions, transports, capabilities, authentication, discovery, pagination, schema limits, cache scope, tool-list changes, and unsupported-feature behavior. Test the chosen Rust SDK against both promised modern and legacy fixtures. A package version alone does not prove protocol conformance.

The tools specification includes credential-sensitive discovery, cache freshness, structured results, and untrusted annotations. Preserve server identity in tool names and policy decisions; avoid sharing authenticated discovery across credentials. A tool schema disappearing or changing must not silently redirect a previously approved operation. [Tools specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

A protocol requirement to reissue a request after a broken stream is not evidence that repeating a remote mutation is safe. Define an uncertain outcome and retry policy above the transport.

### ACP is a separate editor-agent interface

The official ACP repository states stable wire protocol **v1**; its July 20, 2026 v2 announcement labels v2 Draft. SDK/schema package versions do not determine wire compatibility. [Repository](https://github.com/agentclientprotocol/agent-client-protocol/), [draft announcement](https://agentclientprotocol.com/announcements/acp-v2-draft), [migration](https://agentclientprotocol.com/protocol/v2/migration).

**Recommendation:** keep the planned internal engine protocol and a future ACP adapter distinct. Define IDs, prompt acceptance, progress, cancellation, replay, and completion now. Do not claim that JSON-RPC-shaped internal messages automatically implement ACP, and do not add draft v2 to MVP solely because it is newer.

### Provider neutrality needs an explicit capability matrix

OpenAI's live function-calling documentation says GPT-6 Astra and GPT-6.1 Sol require Responses for tool calling. This makes the existing Chat-first M1/Responses-M2 sequence conditional on the actual target models. The page is mutable, so pin the supported model/API combination before implementation. [Function calling](https://developers.openai.com/api/docs/guides/function-calling).

OpenAI reasoning items can contain opaque/encrypted continuity state. Anthropic thinking blocks carry signatures that must be preserved. Google's current guide distinguishes signature-bearing `generateContent` parts from Interactions thought steps. Those are different API contracts, not interchangeable visible text. [OpenAI reasoning](https://developers.openai.com/api/docs/guides/reasoning), [Anthropic thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), [Google thought signatures](https://aistudio.google.com/docs/thought-signatures).

**Recommendation:** define an ordered common message model plus adapter-owned opaque state. The support matrix must name provider, API family/version, target models, tool/schema behavior, images, reasoning state, usage, cache accounting, cancellation, and authentication. Specify unsupported combinations and provider/model switching. “Lossless round-trip within an adapter” is a different promise from arbitrary lossless cross-provider conversion.

Revisit Responses sequencing before committing M1 implementation. If current OpenAI coding models are part of M1, test the required API early. This is a proposed change, not an automatic milestone expansion.

### Streaming needs semantic correctness under pressure

Responses exposes typed events for items, deltas, arguments, completion, failure, and errors. Rendering text is only one consumer of that stream. [Streaming guide](https://developers.openai.com/api/docs/guides/streaming-responses).

**Recommendation:** fixtures should split UTF-8, JSON, and SSE at arbitrary boundaries; interleave calls; end mid-argument; disconnect after an effect; and cancel during dispatch. Partial arguments cannot dispatch a tool. Coalescing display deltas must not drop tool events, approval events, durable evidence, or the final outcome. Specify bounded queues and slow-client behavior.

### Instruction and context rules must follow actual work

AGENTS.md guidance uses the nearest applicable file for the file being edited; explicit conversation instructions take precedence. Loading only root-to-starting-cwd guidance misses nested subtrees touched later. [AGENTS.md](https://agents.md/).

**Recommendation:** specify instruction discovery per touched path, nested overrides, updates during a session, multi-path conflicts, symlink/workspace limits, and import limits if imports remain promised. Instruction text cannot expand OS permissions.

Anthropic's September 29, 2025 context-engineering article emphasizes useful context, clear tools, just-in-time retrieval, and compaction fidelity. Its caching docs describe provider-specific serialization and prefix behavior. [Context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents), [tool caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching).

**Recommendation:** separate durable history from each provider's active context. Reserve space for output/reasoning, tools, and unfinished exchanges. Preserve user decisions, pending calls, file state, goals, and evidence references through compaction. Treat a universal logical prompt order as an internal convention; actual cache behavior belongs to each adapter.

### Authentication mechanisms do not settle third-party access

OpenAI documents ChatGPT sign-in and API-key authentication for Codex. That documentation demonstrates the supported client flow; it does not independently establish an arbitrary third-party application's subscription entitlement. [Codex authentication](https://developers.openai.com/codex/auth/).

**Recommendation:** keep BYOK usable without subscription integration. Before committing native subscription sign-in as a release requirement, verify intended client support, endpoints/scopes, credential ownership, refresh/revocation, keychain availability, browser cancellation, and headless behavior. Record the source and review date. Do not infer permission or prohibition from open-source OAuth mechanics alone.

**Decision-interview follow-up, November 14:** further official documentation explicitly describes ChatGPT plan usage for open-source applications through client registration. That closes the earlier gap about whether a documented third-party path exists. The route uses public Responses with its own account-specific model and request limitations. Mocha's actual registration, eligibility, and inference remain untested. These mutable pages do not establish their original publication date. [Open-source quickstart](https://developers.openai.com/siwc/quickstart), [inference contract](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference), [limitations](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).

## 5. Safety and recovery findings

### Separate four enforcement questions

For every operation, document: who authorizes it; what OS boundary constrains it; which destinations it can reach; and which credentials it receives. OpenAI's deployment account separates these controls. Claude's sandbox documentation explicitly lists execution paths outside its shell sandbox. Neither example makes a single “sandbox enabled” flag sufficient evidence of complete coverage. [OpenAI deployment](https://openai.com/index/running-codex-safely/), [Claude sandbox scope](https://code.claude.com/docs/en/sandboxing).

The Mocha matrix should cover built-in file tools, shell descendants/background jobs, local MCP, remote MCP, provider HTTP, login callbacks, and future hooks/extensions. A shell parser explains syntax; it cannot establish what arbitrary invoked code will do. Model reflection is not an OS enforcement mechanism.

### State the actual Linux boundary

Pinned Linux v6.12 documentation describes Landlock filesystem access, TCP bind/connect port rules from ABI 4, runtime capability detection, and limits involving threads and existing descriptors. A TCP-port rule is not a hostname allowlist. [Kernel documentation](https://www.kernel.org/doc/html/v6.12/userspace-api/landlock.html).

**Recommendation:** define required kernel capabilities rather than a vague Linux support promise. Specify setup before exec, inherited descriptors/sockets, UDP, Unix services such as Docker or SSH agents, environment construction, and explicit failure when the selected profile is unavailable. A network-disabled child profile must be distinguished from the host's necessary provider HTTP access. A domain policy needs its own mechanism and tests; it cannot be inferred from allowing TCP 443.

Approving a destination does not inspect every payload sent there. Bind approval scope to the effective operation, destination, arguments, and lifetime. Separately decide redirects, proxy behavior, localhost access, and capability changes. These are proposed contracts, not claims that the current design already provides them.

### Trust and credential handling belong before dispatch

Gemini's trusted-folder documentation describes restrictions on executable project resources and noninteractive trust behavior; it also says the feature is opt-in. MCP guidance discusses confused-deputy and token-passthrough risks. [Trusted folders](https://geminicli.com/docs/cli/trusted-folders/), [MCP security practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices).

**Recommendation:** distinguish reading repository text, loading configuration, trusting server identity, and granting effects. For M1, project instructions/config must not gain permissions just because full trust machinery comes later. Bind MCP credentials to the intended resource, and construct/scrub subprocess environments independently of log redaction. Unknown MCP capabilities require explicit conservative policy; an advisory read-only hint cannot grant authority.

Resolve the documented conflict over declined trust and `yolo` taint handling through the interview. Preserve the hard-deny promise only if the user confirms it, then make its precedence explicit in every mode.

### Persisting a log is different from exactly-once execution

Temporal describes an external action completing before its worker can durably record completion; retry can duplicate that action. Idempotency depends on the operation and receiver, not merely an event log. [Activity semantics](https://docs.temporal.io/activity-definition), [idempotency discussion](https://temporal.io/blog/idempotency-and-durable-execution).

**Recommendation:** record durable intent before dispatch where recovery evidence is required. An intent without a durable result becomes `outcome unknown` after a crash. Do not automatically repeat arbitrary commands or remote writes. Reconstructing a session for display must never execute recorded tools. Local reconciliation and receiver-supported idempotency keys can be specified where they actually apply.

Cancellation also needs an observable contract: UI acknowledgement, stopping model generation, stopping dispatch, and terminating an entire process group are different events. Define the SIGINT grace period, escalation, partial results, background jobs, and when a new turn may start.

### Atomic visibility and durable persistence are separate

Linux `fsync(2)` explains that flushing a file does not necessarily persist its directory entry; directory synchronization is separate. It also documents storage failures. [Manual](https://man7.org/linux/man-pages/man2/fsync.2.html).

**Recommendation:** specify temporary-file placement, rename, metadata preservation, file/directory synchronization, acknowledgement ordering, and supported filesystem assumptions. State the streamed-text loss window independently of acknowledged user inputs and completed tool results. A SIGKILL test does not prove survival of every power-loss/storage-failure scenario.

### Rewind needs exact scope and a secret policy

Claude's checkpoint documentation names recovery limitations and positions checkpoints separately from version control. [Checkpoint coverage](https://code.claude.com/docs/en/checkpointing).

**Recommendation:** enumerate tracked/untracked/ignored/binary files, modes, links, creation/deletion/rename, external edits, snapshot failure, interrupted restore, retention, and external side effects. In particular, exact plaintext snapshots of secret-bearing user files conflict with an absolute promise never to write secrets. Encryption, explicit exclusions/degraded restore, and a narrowly defined storage exception are different product choices. Redacting a backup cannot preserve exact original contents. Settle the choice before implementing checkpoint storage.

## 6. Toolchain, dependencies, and release engineering

### Concrete corrections to the existing dependency assumptions

Rust **1.100.0 was released on November 12, 2026**. The architecture's 1.96.1 pin is therefore not the latest stable compiler at the research cutoff. This does not automatically make it an invalid product compiler; compatibility and upgrade policy still need a decision. [Official release](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/).

The exact-version registry checks found:

- `toml` publishes **`1.2.1+spec-1.1.0`**, dated November 6. The bare `/toml/1.2.1` endpoint returned 404, but the build-metadata-qualified endpoint succeeded. The failed lookup does not establish that Cargo's `1.2.1` requirement is invalid; no Cargo resolution was run. [Exact published version](https://crates.io/api/v1/crates/toml/1.2.1%2Bspec-1.1.0).
- `hyperfine 2.0.0` declares Rust **1.97.0**, newer than the pinned 1.96.1. Separate development-tool prerequisites from the application's runtime MSRV; compiling that tool and using a prebuilt tool are different setup paths. This is a prerequisite discrepancy, not proof that the application cannot build. [Registry metadata](https://crates.io/api/v1/crates/hyperfine/2.0.0).
- All 22 checked entries have corresponding published versions by the cutoff, none yanked, with registry license strings matching the table. This does not prove transitive resolution, feature compatibility, advisory status, or musl builds. [Recorded responses](2026-11-14-mocha-dependency-evidence.json).
- `minisign 0.10.0` in the Rust registry is a crate. Its existence does not verify the separate signing CLI's version or installation process. [Crate metadata](https://crates.io/api/v1/crates/minisign/0.10.0).

For the exact `reqwest 0.13.5` feature page, `default-tls` enables `rustls`. This answers one explicit architecture uncertainty. It does not prove that Mocha's eventual complete dependency graph excludes OpenSSL or that its binaries link statically. Select features deliberately and inspect/build both promised targets. [Exact-version features](https://docs.rs/crate/reqwest/0.13.5/features).

**Recommendation:** use one justified release-toolchain pin, an independently tested application MSRV, and separately recorded tool requirements. Treat dependency metadata as input to a compatibility spike, not evidence that a nonexistent workspace has built. Keep exact versions, selected features, license/advisory evidence, and review dates together.

### Release evidence should go beyond a checksum

The Rust supply-chain guide recommends committed lockfiles with `--locked`, isolation for builds that execute dependencies, and considering reproducibility and dependency inventories. GitHub artifact attestations link an artifact to its build provenance and can carry SBOM associations; verification is required to gain that assurance, and an attestation does not establish that software is vulnerability-free. [Rust build guidance](https://rust-secure-code.github.io/rust-supply-chain-security/build.html), [GitHub attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations).

**Recommendation:** retain maintainer-controlled publication and the chosen signature policy; add source/build provenance and a dependency inventory where justified. Document the user verification path, key/identity trust, target architecture, static-link checks, toolchain/lockfile, and failure behavior. Pin release actions by immutable revisions and keep privileged release work separate from untrusted PR execution. Do not claim reproducible builds until an independent rebuild comparison passes.

## 7. Evaluation and performance

### Replay verifies mechanics, not autonomous coding quality

OpenAI's July 8, 2026 evaluation audit identifies underspecified prompts, overly strict tests, low coverage, and misleading instructions as sources of invalid coding-benchmark outcomes. Scale's SWE-Bench Pro V2 publication describes isolated grading, sanitized inputs, and network controls. Its retrieved publication metadata and visible date differ, so no precise release-day claim or leaderboard ranking is used here. [OpenAI audit](https://openai.com/index/separating-signal-from-noise-coding-evaluations/), [Scale methodology](https://labs.scale.com/blog/swe-bench-pro-v2).

Terminal-Bench's owner describes container-based agent evaluation and task-quality work through Harbor. This is useful infrastructure to investigate, not evidence that Mocha needs to run a large public suite in every PR. [Terminal-Bench/Harbor announcement](https://www.tbench.ai/news/announcement-2-0).

**Recommendation:** keep three separate verification layers:

| Layer | Purpose | Evidence |
| --- | --- | --- |
| Deterministic mechanics | Protocol, tool safety, policy, persistence, parsing, cancellation, context transforms | Fixtures, failure injection, golden event traces, actual policy enforcement tests |
| End-to-end coding | Can a specified model plus Mocha solve the intended tasks? | Versioned tasks, pinned environment/model/config, independent grading, repair/intervention records, repeated trials |
| Human workflow | Does Mocha help the maintainer complete useful work? | Dogfooding log, accepted changes, review burden, recovery incidents, time with a defined measurement method |

Preserve the no-paid-network-calls rule in CI. If live model evaluation is wanted, make it a separately authorized and budgeted job. Mock replay cannot prove model reasoning quality or universal prompt-injection resistance; it can prove that an attempted unauthorized action is blocked by the actual enforcement path.

Do not compare agent scores without model/version, reasoning settings, tools, context limits, network policy, task revision, retries, and budget. Grade the submitted patch in a fresh environment so modifying caches or tests in the working sandbox does not count as success.

### Make the performance promise reproducible

Hyperfine documents warmups, cache preparation, repeated runs, outlier handling, and exports. Its timing of command completion does not by itself establish when an interactive TUI became ready for input. [Hyperfine](https://github.com/sharkdp/hyperfine).

**Recommendation:** keep the current performance values as proposed budgets until the measurement protocol exists. Specify:

- Reference hardware, OS/kernel, terminal or PTY harness, toolchain, build profile, and workload revision.
- Cold and warm startup separately, with an observable input-ready boundary; interactive readiness is different from printing `--version`.
- Process accounting: the MVP includes the engine in the client; future daemon/child/session memory must not disappear from comparisons.
- Transcript length, tool/schema count, stream rate, redraw conditions, idle duration, and input-latency sampling.
- Repeated measurements, p99 sample adequacy, acceptable noise, raw artifact storage, comparison rules, and reviewed budget changes.
- Static binary size/linkage as separate deterministic checks from noisy latency/CPU measurements.

No source in this study validates Mocha's specific 20 ms, 12 MB, or 3% thresholds. They are product targets to test, not industry standards or measured achievements.

## 8. Recommended documentation shape

Keep the existing PRD and architecture filenames to avoid unnecessary churn. Add a short index and only enough supporting contracts to make implementation unambiguous. The paths below are proposed; they are not created by this research pass.

| Document | Responsibility |
| --- | --- |
| `docs/README.md` | Authority order, current status, delivery boundary, reading path, unresolved decisions, links to evidence. |
| `docs/02-prd.md` | Audience, jobs, release scope, non-goals, observable requirements, failure outcomes, completion gates. |
| `docs/04-architecture.md` | Ownership, dependency boundaries, chosen mechanisms, rationale, and links to contracts; truthful implementation status. |
| `docs/FEATURES.md` | Product roadmap clearly separated from current release obligations; stable links to requirements instead of a second contradictory priority system. |
| `docs/contracts/runtime.md` | Event protocol, IDs/order, terminal outcomes, channels/backpressure, scheduling, cancellation, headless interfaces and exit codes. |
| `docs/contracts/tools-and-policy.md` | Mutation/read ledger rules, concurrency, approval precedence, trust, capability and containment matrix, environment/network grants. |
| `docs/contracts/providers-and-mcp.md` | Provider/model/API matrix, opaque state, fixtures, auth support evidence, MCP revisions/capabilities, unsupported cases. |
| `docs/contracts/storage-and-context.md` | Durable acknowledgement, unknown outcomes/retry, migration, compaction, instructions, checkpoint scope/secrets/retention/restore. |
| `docs/verification.md` | Requirement-to-slice-to-check mapping, benchmark specification, test boundaries, release evidence, status conventions. |
| `docs/slices/SLICE-001/` | First ready-to-build vertical slice, behavioral criteria, dependencies, verifier and evidence. Later slices get sufficient scope/dependencies now and detailed specs before their implementation. |
| Root `GLOSSARY.md`, `docs/adr/` | Resolved domain language and the few consequential trade-offs that need rationale. Follow the configured single-context layout. |
| `docs/research/` | Dated evidence and historical background; recommendations here do not override accepted requirements. |

Review `DESIGN.md` and README alongside `docs/`: they currently influence the implementation reading path. Mark post-MVP UI behavior, settle the state-aware keymap, bound inline parity, and provide keyboard paths for every supported action. Fix missing assets/license links without inventing historical prototype evidence.

Do not restore an absent discovery file by fabricating the old DEC/FCT conversation. Recover authentic records if available; otherwise replace dangling authority references with self-contained decisions confirmed in the current session. Similarly, reset an `ACTIVE` check to proposed unless its execution evidence exists in this repository.

## 9. Gap-to-verification checklist

These are proposed acceptance obligations, not reports of passing tests.

| Area | Required decision or contract | Minimum observable evidence | Needed by |
| --- | --- | --- | --- |
| Baseline | Accepted revision, scope, authority, authentic decision provenance | Index links resolve; contradictory release obligations removed; unavailable evidence labeled | Before SLICE-001 |
| Build inputs | Existing dependency versions/features, toolchain vs MSRV vs tool versions | Locked build on both promised targets; tool/version checks; license/advisory checks | First dependent slice |
| Skeleton | Startup boundary, terminal restoration, inline fallback, cancellation keys | Real binary under PTY; resize/failure/exit paths; defined ready event | SLICE-001 |
| Protocol/headless | IDs/order, one final outcome, stdout/stderr, numeric exits, missing input/approval | Golden traces, non-TTY approval denial, slow client, cancellation races | First headless slice |
| Mutations | New/absent files, partial reads, stale hashes, multi-file failure, modes/links | Create, targeted edit, full overwrite, stale race, patch target failure fixtures | Before core tools |
| Dispatch | Intent/result durability, concurrency, unknown outcomes, retry limits | Kill before dispatch and after effect-before-result; resume never duplicates command | Before side-effecting tools |
| Trust/policy | Mode matrix, deny precedence, taint behavior, approval binding, M1 boundary | Untrusted checkout cannot load executable config or grant permissions; shared TUI/headless decisions | Before instruction/config execution |
| Containment | Tool coverage, minimum capabilities, filesystem/env/FD/socket/network rules | Outside-root write, unintended descriptor/socket, absent-kernel-capability tests | Before sandbox claims |
| Providers | Named models/APIs/features, reasoning state, incomplete streams, usage | Exact adapter fixtures; opt-in live smoke evidence for promised combinations | Before adapter support claim |
| Authentication | BYOK, supported subscription evidence, missing keychain, revocation, cancellation | Fresh install to first real turn; failed refresh and noninteractive outcomes | Before auth release gate |
| MCP | Current/legacy revisions, SDK proof, discovery/auth/cache, unknown tools | Both promised transport/version fixtures; changed schema, hostile hint, expired auth, disconnect | Before MCP slice |
| Context | Token reserves, call/result integrity, nested instructions, compaction failure | Long traces retain facts and pending calls; deeper file instructions apply; no silent data loss | Before long-session claim |
| Storage/rewind | Durable boundary, migration, retention, secret files, restore conflicts | Torn record, full disk/I/O error, backup migration, ignored secret file, interrupted restore | Before durability/rewind claims |
| Coding quality | Declared tasks and independent outcome grading | Edit-test-repair workflows; accepted changes and explicit failed/blocked outcomes | M1 exit onward |
| Performance | Reproducible workloads and noise/decision rules | Raw results plus environment/workload metadata; no empty-work benchmark | Before enforcing budgets |
| Release | Artifact identity, inventory, signatures/provenance, publication authority | Clean-machine install/verification, target smoke tests, locked build and evidence links | Before public binary release |

## 10. Decisions to revisit after the research

The earlier interview questions remain unanswered. This report does not treat silence as acceptance. Resume in dependency order:

1. Confirm the intended completion boundary and document authority. Research does not require expanding the MVP to match every competitor.
2. Name the M1 target providers/models and test the required API families, especially Responses. Confirm separately whether subscription sign-in must block the MVP when third-party support remains unverified.
3. Resolve execution defaults: sandbox network, unavailable containment, declined project trust, taint and hard-deny precedence, and headless approval behavior.
4. Resolve mutation, cancellation, durable acknowledgement, uncertain effects, checkpoint coverage/secrets, and retention.
5. Accept the verification protocol, readiness checklist, and first executable slice. Choose the toolchain/dependency baseline using compatibility evidence.

Capture resolved language in the root glossary as it crystallizes. Record ADRs only for real consequential trade-offs, not every implementation detail. Then revise the normative docs together, preserving the research as evidence and marking old blueprint choices superseded where appropriate.

The research pass creates this report and its evidence companions only. It does not change product scope, accept a safety policy, publish GitHub issues, or claim implementation readiness.


## 11. Handoff follow-up

Observed November 14, 2026. Google's [migration guide](https://aistudio.google.com/docs/migrate-to-interactions) recommends Interactions for new development while retaining generateContent support. Its [announcement](https://blog.google/innovation-and-ai/technology/developers-tools/interactions-api-general-availability/) identifies Interactions as GA. The current Mocha contract therefore selects native Interactions with `store:false` and full local history. This is a selected request profile within the confirmed Gemini family, not evidence of a tested adapter. These mutable reads are recorded in the source inventory without changing original search accounting.

The [documentation index](../README.md) now records confirmed choices and the current build handoff. Recommendations and decision lists earlier in this research are historical inputs, not remaining product questions or an alternative authority. Runtime snapshot licensing/provenance, adapter fixtures, actual provider/account access, and performance/containment/durability evidence remain build gates.
