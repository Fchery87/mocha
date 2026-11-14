# Tools and policy contract

Specification dated November 14, 2026. Enforcement remains unimplemented. The [PRD](../02-prd.md) defines required scope.

## Mutation admission

Every call passes schema validation, path resolution, capability checks, authorization, required checkpoint creation, and durable dispatch intent before execution. Partial streamed arguments cannot dispatch. File tools enforce their own boundaries. Child processes additionally require OS containment.

M1 provides the minimum policy before any real tool dispatch. Reads stay within authorized workspace paths. Every command and mutation requires interactive approval or a scoped user grant. `--allow-writes` grants only built-in workspace file mutations, excludes sensitive paths, and never grants shell execution or network access. `--allow-command <exact-command>` grants that exact command and cwd for the run, with descendants confined by the same sandbox. Network remains off. These user flags do not authorize repository configuration to grant permissions.

M2 adds `auto`, `approve`, `plan`, and `unattended`, trust UI, and persistent rules. Explicit deny wins. Absolute blocks cover writes to Mocha's own credentials, trust/configuration state and private store, credential extraction, workspace escape, and attempts to disable enforcement. `plan` disallows agent mutations. Unknown MCP effects require approval. Local-command uncertainty follows the approved auto reflection contract below; actions outside an existing grant still require approval. Model reflection supplies an explanation, never authority. A checkpoint does not authorize remote effects or arbitrary destructive commands.

Grants bind action, normalized arguments, cwd, effective paths, capability, and server or destination identity when relevant. Changes outside that scope require reevaluation. Once, session, persistent, and deny are separate user choices. Persistent grants can originate only in user-owned configuration.

## Permission modes

The maintainer approved a Jcode-inspired interactive flow and delegated final mode naming/behavior on November 14, 2026. The canonical modes are `auto` by default, `approve`, `plan`, and `unattended`. Names describe approval behavior rather than imply a safety guarantee or compatibility with another product's mode. No legacy aliases are required because no released Mocha configuration exists. This is an independently specified Mocha policy, not a claim that Jcode supplies Mocha's containment guarantees. The [pinned source review](../research/2026-11-14-jcode-permission-behavior.md) explains the comparison.

Ordinary workspace reads, covered edits, and local commands proceed automatically within an explicit user-controlled workspace-execution grant. The grant identifies the canonical workspace, allowed local execution/write capabilities and any declared disposable output/scratch paths. It does not include network access, credential exposure, unknown remote/MCP effects, or uncovered sensitive-file mutations. A repository file cannot create or enlarge this grant. M1 retains its minimum ask/scoped-grant policy; full auto behavior is an M2 mode.

In auto mode, assess each complete action using deterministic paths, command structure, capabilities and current grants. Recognized safe/local bounded operations proceed. Covered mutations still require their read/checkpoint prerequisites where applicable. Uncertain destructive local actions cause a `reflection_required` response without execution. The model can abandon, narrow, or resubmit the action with a substantive explanation of intent and scope. Reevaluate the exact resubmitted action against all independent authorization, containment, credential, checkpoint and deny checks. Explanation alone never establishes authority or proves unknown effects harmless.

Auto permits at most one reflection retry for an unchanged normalized action within a turn. If uncertainty still prevents establishing the required execution scope or recovery coverage, ask the user or return the headless approval-required outcome. Model rewording or a new call ID does not reset the retry or bypass an unresolved-operation block. A reflection attempt counts toward provider-step/tool-call/time limits. No cumulative token cap applies.

Actions needing new scope follow the mode matrix: request user approval where interactive approval is permitted, otherwise stop with approval_required. Unknown MCP effects always follow the separate approval rule. Absolute denies block independently of reflection. These include agent-tool credential extraction; writes to Mocha's own credential, authorization/configuration and private-state stores; containment bypass; unauthorized workspace escape; and recognized destructive operations targeting filesystem root, user home, credential stores, devices, the workspace root or its `.git` directory. Normal scoped Git operations are distinct from direct destructive `.git` removal/tampering. Trusted setup/login/cleanup operations retain their explicitly authorized host pathways; they are not permissions granted to model tools.

Protected-target detection is defense in depth. It cannot prove all arbitrary scripts safe. The sandbox and the granted execution scope remain required even when the parser finds no dangerous construct. Unsupported path/risk analysis requires user approval or fails closed according to the required capability. Unattended/headless cannot wait for approval. No analysis failure silently grants broader access.

### Mode decision matrix

The matrix assumes the action meets its independent scope, containment, credential, observation and recovery requirements. A workspace-execution grant supplies scope, not automatic permission in every mode. An exact-action user rule/approval can satisfy an ordinary approval requirement. Hard denies, Plan mutation blocks, unavailable containment and unresolved effects take precedence.

| Action | auto | approve | plan | unattended |
| --- | --- | --- | --- | --- |
| Authorized read or established read-only command | Allow | Allow | Allow | Allow |
| Covered built-in mutation | Allow | Ask unless exact-action approval exists | Block | Allow |
| Authorized local command that may mutate | Allow | Ask unless exact-action approval exists | Block | Allow |
| Uncertain destructive local action, with scope and coverage established | Reflect once, then reevaluate | Ask for exact-action approval | Block | Reevaluate without reflection; allow only if independent requirements pass |
| Missing scope, uncovered sensitive mutation, tool network capability, or unknown MCP effects | Ask unless an applicable explicit grant exists | Ask unless an applicable explicit grant exists | Only an authorized established read-only action can proceed | Stop with approval_required unless an applicable explicit grant exists |
| Absolute deny, unsupported required containment, or forbidden Plan mutation | Block | Block | Block | Block |

`auto` uses the reflection flow above. `approve` requires action-level confirmation for edits and potentially mutating commands, even if a broader workspace grant exists. Proven read-only commands must use constrained definitions and an enforced read-only execution profile; a repository test script is not read-only merely because it is named test.

`plan` blocks agent mutations, side-effecting commands, and unknown-effect tools. An allow rule cannot turn a blocked mutation into a Plan action. Mocha can still maintain its own authorized transcript/configuration through host pathways. Provider inference uses its separate host network boundary.

`unattended` requires explicit selection for the run/session and is excluded from the ordinary keyboard mode cycle and saved default. It executes authorized local work without the extra reflection round trip. It never pauses for new approval. If an operation would need new approval, end the turn as Failed with `approval_required`, exit 3 in headless mode, and retain completed work. Missing required user input similarly stops with `input_required`, exit 2. TUI use shows the reason and returns to idle. This prevents an unattended run hanging or silently gaining authority.

### Tiers and precedence

The five tiers are descriptive classifications, not permission grants. Tier 0 covers authorized reads/established read-only operations. Tier 1 covers known local mutations whose required checkpoint covers their effects. Tier 2 covers destructive local uncertainty eligible for reflection only after scope/coverage can be established. Tier 3 requires additional user authority or explicit acknowledgement of missing recovery coverage. Tier 4 is an absolute block. Unknown MCP effects are at least Tier 3. Arbitrary scripts and unknown write sets cannot be promoted to Tier 1 from their names or model assurances.

Apply hard denies and required-capability failures first, then Plan's mutation block, then scope/coverage and explicit ask constraints, then the mode's ordinary approval/reflection behavior. A missing checkpoint needed for a recoverable classification cannot be waived by a mode. A newly approved uncovered-file action may execute only with its absence of coverage explicitly recorded; it is never described as checkpoint-protected.

### Selection and changes

The planned CLI interface is `--mode auto|approve|plan|unattended`. Interactive `/mode` provides the same choices and shows the active mode persistently. Shift+Tab cycles auto → approve → plan. Unattended is an explicit choice with a scope summary; selecting it does not create a grant. Persist a changed new-session default only through an explicit user settings action, and never persist unattended as that default.

A mode change applies before the next dispatch and reevaluates queued actions/approvals. Switching into Plan closes mutation dispatch immediately and requests cancellation of running mutating or unknown-effect work. Acknowledge the completed switch only after that work terminates or is reconciled; record partial/unknown effects honestly. No mode change can retroactively undo an effect, convert old model rationale into authority, or reset budgets/taint/unresolved operations. Resume restores history and reevaluates current grants; it does not automatically resume execution.

[Permission decision fixtures](fixtures/permission-decisions.json) specify representative expected outcomes for the future policy tests. They are acceptance vectors, not evidence of a running policy engine.

## File observations and patches

Read observations identify resolved path, file identity, content hash, and observed spans. Full overwrite, deletion, and `replace_all` require a full read. Targeted edits require the replaced and context spans to have been observed. Target read/stat yielding ENOENT establishes absence. An omitted glob result does not.

Revalidate immediately before publication. Unexpected content produces `stale_observation` and asks for a reread. Reject symlink traversal and hard-linked mutation targets in the MVP. Root-relative descriptor traversal prevents path-component replacement escapes. These checks do not promise universal compare-and-swap against unrelated external writers.

Validate all patch targets and stage all replacements before publishing any. Serialize overlapping Mocha mutations. Publish by atomic per-file replacement, preserve existing permission bits, and sync the file and containing directory before durable success. New regular files use mode 0600 unless an explicit supported mode is supplied. MVP edits support UTF-8 regular text, preserve existing line endings, and reject binary content or unsupported mode changes with no mutation.

A second-file failure reports changed, failed, and pending paths plus hashes. Never report whole-patch success or blindly roll back an external edit. Invalidate affected read observations after mutations. Unknown shell/MCP write sets invalidate the entire workspace ledger and serialize with other mutations. Failed deletion and rename have explicit per-path results.

`grep` and `glob` respect ignore rules; `read` of an explicit path remains subject to access policy. Default displayed tool output is capped at 32 KiB or 500 lines, whichever comes first. Store the redacted remainder as referenced spill evidence. `bash` defaults to a 120-second timeout, bounded by the turn deadline. Background jobs have IDs, bounded output, explicit status and kill operations, and cannot outlive engine shutdown unnoticed. Before the first real command, verify cancellation, dispatch closure, deadlines, step/tool limits, timeout/escalation, output/storage failure handling, and durable intent. The lifecycle profile must prevent unsupported descendant escape or prove continued control after it. A process-group signal alone is not proof that all descendants remain controlled. Unsupported lifecycle containment fails closed.

## Execution coverage

| Path | Boundary |
| --- | --- |
| Built-in files | Resolved workspace paths, credential/store denies, read ledger, per-file atomic publication |
| Shell and descendants | Landlock and seccomp, workspace-limited writes, sanitized environment, process-group lifetime |
| Local MCP | Same process containment; trust before startup; tool effects separately authorized |
| Remote MCP | Host HTTP with server-scoped credentials and action authorization; no claim of remote OS containment |
| Provider HTTP | Configured provider endpoint, selected account, host credential resolver; does not grant tools network access |
| Login | Explicit browser flow and temporary loopback callback; no inherited child credentials |

Minimum Linux profile denies child networking, including UDP, new Internet sockets, and access to external Unix services. Close inherited non-stdio descriptors, including sockets, before execution. Stdio pipes remain available. Sanitize environment and deny access to Mocha state and known credential paths. Restrict writes to the workspace and declared private scratch paths. Required kernel/filesystem rights must be probed and tested; unsupported enforcement fails closed with a diagnostic.

An explicit network grant permits outbound access for the scoped command or server and its descendants. The preview states that arbitrary destinations may be reachable. Landlock TCP-port controls do not enforce hostnames. Destination-only filtering is outside MVP scope. Network permission does not grant credentials. There is no unsandboxed fallback.

## Trust and instructions

M1 reads instructions as untrusted guidance and executes no repository config or MCP startup. M2 trust binds canonical workspace identity and hashes of `.mocha/config.toml` and `.mcp.json`. Changed hashes require renewed approval before use. Trust permits only supported configuration, not arbitrary policy elevation. Repository config cannot change credential bindings or provider endpoints.

Instruction precedence is explicit user instruction, global guidance, then applicable repository guidance with nearest-file scope resolving local conflicts. At each directory AGENTS.md takes precedence over CLAUDE.md. Limit each file to 64 KiB and combined active guidance to 256 KiB. Report overflow. Reject instruction symlinks that escape the workspace. Reload changed applicable guidance before the next affected operation. Batch operations retain each path's scope. Instructions cannot grant permissions.

Tool/file/MCP content taints the session. Preserve taint through compaction and resume. Model-proposed outbound actions in a tainted session require approval unless an exact authorized rule applies. Configured provider inference remains a separate host operation. Test the real enforcement path rather than trusting a model's stated refusal.
