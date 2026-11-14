# Coding-agent permission comparison

Observed November 14, 2026. These are current first-party documentation findings, not runtime tests or archived proof of the behavior of every released version. This note informs the pending Mocha permission decision. It approves no Mocha policy changes.

## OpenCode

The current official documentation describes V2. Rules use an ordered `permissions` array with action, resource, and allow/ask/deny effect. Later matching rules win. The shipped base policy allows actions broadly, with approval for sensitive environment-file reads and an exception for example environment files. Build therefore allows ordinary edits and shell execution by default. External-directory access is also allowed unless configured otherwise. An unmatched action falls back to ask, but the broad shipped allow rule normally matches. V1 field names and old defaults must not be mixed with V2. [Permissions and defaults](https://opencode.ai/docs/permissions)

Shell scanning checks compound commands and inferred directories. Unanalyzable dynamic syntax fails scanning. The owner explicitly warns that shell execution still has the host user's filesystem, process, and network authority, and directory inference is best effort. Approval choices include once, durable project-scoped patterns, and reject. Saved approvals cannot override a configured deny. This is a permission-policy mechanism, not evidence of OS sandbox containment. [Shell boundary and approvals](https://opencode.ai/docs/permissions)

Plan denies normal file edits, with an exception for OpenCode's own plan files. Shell commands remain controlled by permission configuration; a Plan label alone does not establish an OS-enforced read-only process. [Built-in agents](https://opencode.ai/docs/agents)

## Gemini CLI

The documented approval modes are default, autoEdit, plan, and yolo. Default generally asks for write operations. AutoEdit permits some editing without approval. Plan is intended for read-only research/design. Yolo automatically approves tools. The policy engine independently supports allow, deny, and ask_user rules, prioritized by rule and policy tier. Administrative policies have higher authority than default/user policies. Persistent approvals are scoped to the current and more permissive modes so an approval in a permissive mode does not silently authorize Plan behavior. [Policy engine](https://geminicli.com/docs/reference/policy-engine/)

Settings name the command-line mode `auto_edit`. The normal default setting is `default`; yolo must be selected through the CLI rather than saved as the default approval-mode setting. [Settings](https://geminicli.com/docs/cli/settings/)

Sandbox configuration is separate. The docs describe full-process and individual-tool isolation, selectable backends, and per-command requests to expand filesystem/network access. Network restrictions depend on the selected profile; the documented default macOS Seatbelt profile allows network access while limiting writes. Therefore neither selecting an approval mode nor enabling an unspecified sandbox profile establishes network-off containment. [Sandboxing](https://geminicli.com/docs/cli/sandbox/)

## Claude Code

Current docs distinguish Manual/default, acceptEdits, plan, auto, dontAsk, and bypassPermissions. Manual asks before most edits, shell commands, and network actions. AcceptEdits automates file edits and common filesystem operations. Plan is for read-only analysis, with eligible commands reviewed through its classifier where available. Auto mode uses a separate classifier to review relevant actions, and its availability/default depends on client surface, version, and provider. Bypass skips most permission prompts, but explicit deny/ask rules and documented special guards remain relevant. It is inaccurate to describe it as having no safeguards. [Permission modes](https://code.claude.com/docs/en/permission-modes)

The shell sandbox is off by default and is separate from permission modes. Its documented coverage is the Bash tool, not every built-in or external integration. Consequently an approval-mode name alone does not establish OS containment for all tools. [Sandboxed Bash](https://code.claude.com/docs/en/sandboxing)

## Codex

The documented default permits autonomous workspace editing and routine commands within a bounded sandbox, with approval for operations outside the configured boundary. Sandbox configuration and approval policy are separate: selecting an approval policy that never asks does not itself remove the sandbox. Full access combines the broader danger-full-access sandbox setting with the never approval policy. Parent-agent local CLI inspection also found distinct read-only, workspace-write, and danger-full-access choices in Codex CLI 0.169.0. [Sandbox and approval boundaries](https://learn.chatgpt.com/docs/sandboxing)

Optional automatic approval review uses a separate reviewer and is distinct from ordinary model reflection or OS enforcement. [Automatic review](https://learn.chatgpt.com/docs/sandboxing/auto-review)

## Jcode evidence limitation

The owner's Safety System document is marked Design, updated February 8, 2026, and says ambient mode is its only current consumer. It describes two categories: automatic local/reversible work and actions requiring approval, especially externally visible communication or shared/system changes. It has no always-denied category when the user explicitly approves. Because of that stated scope/status, this document cannot establish interactive-session enforcement or a current universal permission matrix. No interactive Jcode behavior was tested in this review. [Owner design document](https://github.com/1jehuang/jcode/blob/master/docs/SAFETY_SYSTEM.md)

## Implications for Mocha

The following are design inferences, not claims that the products implement the same controls:

- There is no single industry default. OpenCode's documented default is broad execution, while Gemini offers several explicit approval modes.
- Both edit automation with command approvals and broader autonomous execution within a sandbox have precedent. Codex supports the latter interaction pattern. A scoped workspace-command grant could reduce Mocha prompts without treating a command name as proof of harmless effects.
- A mode called yolo commonly implies broad automatic approval. Mocha's proposal still asks for unknown effects. Keep that difference explicit or choose a less ambiguous name.
- A shell command named `npm test` is not inherently read-only. Repository scripts can mutate files or communicate externally. Classification, scoped authorization, and OS enforcement must remain distinct.
- Mocha's already-confirmed network-off default, fail-closed containment, credential isolation, and absolute denies are independent product decisions. Competitor convenience defaults do not authorize removing them.

The pending choice is how much local execution Mocha should authorize by default within those established boundaries. The comparison supports explaining the tradeoff and choosing explicitly, rather than claiming one mode matrix is an industry standard.
