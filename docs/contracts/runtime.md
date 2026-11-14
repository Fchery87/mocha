# Runtime contract

Specification dated November 14, 2026. Implementation and execution evidence are pending. This contract supplies the shared behavior required by [the PRD](../02-prd.md).

## Protocol v1

The composition root creates the engine and gives clients a protocol handle. Clients cannot import engine internals. Requests carry `protocol_version`, `request_id`, and a tagged `method` with typed parameters. Session requests also carry `session_id`. Version negotiation precedes other requests. Reject duplicate request IDs within a connection.

M0 methods are `initialize`, `create_session`, `submit_prompt`, and `cancel_turn`. M1 adds `resume_session`, `list_sessions`, `respond_approval`, `respond_question`, `queue_followup`, and `interject`. M2 adds `rewind`. Unsupported methods produce `unsupported_method`. A request gets exactly one accepted or rejected response. Submission acceptance identifies its turn; asynchronous outcomes are separate events.

Events carry protocol version, session and turn identities where applicable, a monotonically increasing session sequence, event type, and payload. The event types include `prompt_accepted`, `text_delta`, `tool_requested`, `approval_required`, `tool_started`, `tool_result`, `evidence`, `persistence_error`, and `turn_finished`. M0 uses only its applicable subset. Semantic events keep their order. A tool result identifies its matching call. A final event follows all earlier semantic events for its turn. No event can dispatch an operation during replay.

Use bounded channels of 256 events and a 1 MiB pending text buffer. Coalesce adjacent display text only. Apply backpressure to the producer when full. Client disconnect cancels further dispatch and persists observed outcomes through the engine's independent store path. It cannot discard approval, evidence, or final events to make room for text. Event persistence sequence and delivery sequence remain distinguishable on reconnect.

### Cancellation and stalled delivery

Each turn has an independently serviced cancellation signal and dispatch gate. Event delivery, provider streaming, child-output forwarding, and storage waits must not hold the control path. A full display channel pauses production but cannot prevent cancellation, shutdown, or deadline expiry. Blocking stdout/terminal writes run outside the engine's control task.

The 50 ms cancellation acknowledgement means the engine has observed cancellation and closed the dispatch gate. It is distinct from durable cancellation/final-state acknowledgement, which follows the required persistence. Stop provider IO and terminate controlled children independently of draining display events. A store wait can delay durable confirmation but cannot reopen dispatch or delay signalling children.

If delivery remains continuously blocked for 30 seconds, cancel the active turn with `Interrupted` and reason `client_unresponsive`. Measure from the first blocked delivery; reset only when the consumer accepts pending events. A quiet provider or long-running command with no blocked delivery does not start this timer. Client disconnect triggers cancellation immediately.

M1 onward persists observed semantic events and the final outcome through the store path even if the client cannot receive them. Keep undelivered and durably recorded states distinct. Deliver retained events in sequence if the client recovers within the running connection; reopening a session reconstructs durable history without automatically executing work. A failed store follows the existing storage-failure/unknown-effect rules, never a false durable-success claim.

M0 has no persistent store. Reserve terminal-state capacity in its bounded buffer so cancellation can complete without a draining consumer. A disconnected M0 client receives no promise of persistent recovery. In all milestones, never report a final event as delivered merely because it was generated or persisted.

Headless `client_unresponsive` exits 1 when termination completes. Writing a final JSON event remains best effort if stdout is blocked or broken. User SIGINT retains exit 130. Storage failure or unresolved effects take precedence with exit 6 when detected before ordinary termination. Persist final reason and termination evidence when the store is available.

Required cases include cancellation with a full event channel, a blocked stdout writer, stalled provider/child output, slow persistence, consumer recovery before the timeout, continuous blockage past the timeout, disconnect, and final-event ordering. Use an injected monotonic clock for deterministic deadline cases and a real PTY/pipe for integration checks. Runtime enforcement evidence remains pending.

Errors include `protocol_mismatch`, `empty_prompt`, `not_initialized`, `unknown_session`, `turn_in_progress`, `duplicate_request`, `unsupported_method`, `provider_failed`, `approval_required`, `input_required`, `storage_failed`, `client_unresponsive`, and `outcome_unknown`. Diagnostics include actionable context with secrets removed. Unknown enum variants are unsupported-version failures, never guessed actions.

## Turn control

The transition model is Idle → Preparing → Streaming → AwaitingApproval or ExecutingTools → Streaming → terminal. A terminal outcome is exactly one of `Done`, `Failed`, `Interrupted`, or `BudgetExhausted`. Failures include a typed reason. Provider completion alone cannot mark an unfinished tool task Done.

Esc first closes the focused overlay. Otherwise it denies a pending approval or dismisses a question without authorizing an action. Otherwise it cancels an active turn. Ctrl+C cancels active work and arms a two-second quit hint. A second Ctrl+C inside that window exits, regardless of composer content. Other keys do not cancel the hint. Explicit interactive quit exits 0 after terminal restoration.

Cancellation acknowledges within 50 ms on the reference workload and prevents new dispatch. Signal each child process group with SIGINT, wait two seconds, then SIGKILL survivors. Record termination or unknown effects. Do not start an overlapping mutation while the old process can still mutate. Late stream events cannot revive a cancelled turn.

Ctrl+Enter interjects by cancellation and then submits at the safe boundary. Alt+Enter is the terminal fallback. Tab queues a submitted follow-up for the next idle boundary. Enter during active work queues rather than silently changing already-dispatched work. Queue capacity is 16 messages; overflow leaves composer text intact with an error.

Initial configurable per-turn limits are 50 provider steps, 200 tool calls, and 30 minutes of wall time, including retries and compaction. There is no cumulative token-usage cap, following the maintainer's November 14, 2026 decision. Track provider-reported input/output usage, including cached/reasoning details where supplied, without double counting. Label missing or estimated usage. Usage totals are informational and do not stop work or require a budget extension. The selected model's context and output limits still constrain individual requests. No dollar cap is implied. A third identical tool call with unchanged inputs/state or a second edit/revert cycle produces one nudge. The next repetition stops with `loop_detected`.

## Headless outcomes

`mocha run` text mode sends the final answer to stdout and progress to stderr. `--json` emits one protocol event per line, with no escape sequences. A rejected request emits a typed rejection; an accepted turn emits one `turn_finished` before normal process exit. Abrupt termination cannot promise delivery of that final event.

| Exit | Meaning |
| --- | --- |
| 0 | Done |
| 1 | Task or tool failure |
| 2 | Invalid configuration, usage, or required input unavailable |
| 3 | Required approval or trust unavailable |
| 4 | BudgetExhausted |
| 5 | Provider or authentication failure |
| 6 | Storage failure or unresolved effect preventing continuation |
| 130 | Interrupted by SIGINT |

A headless process never waits for an absent interactive approval channel. Its authorization policy is the same as the TUI's.

Permission modes follow the [policy matrix](tools-and-policy.md#mode-decision-matrix). Unattended mode never waits for approval or required user input, including in the TUI. It returns the same typed approval/input-required outcomes and headless codes documented here.
