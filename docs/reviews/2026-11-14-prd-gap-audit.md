# PRD gap audit

Reviewed November 14, 2026 after maintainer confirmation of the build handoff. Method: read the PRD against the runtime, policy, provider, storage, architecture, and first-slice specifications. This is a semantic document audit, not runtime testing or a new external-source review. Confirmed choices remain the baseline. The previous claim that no known product choices remained was too broad.

## Findings

Follow-up status, November 14, 2026: all five findings are resolved at specification level. The maintainer rejected a cumulative token cap, approved Jcode-inspired automatic behavior and the 30-second stalled-delivery timeout, and delegated final mode naming/behavior. Contracts now define auto/approve/plan/unattended, independent cancellation, shared-state coordination and minimum first-command guards. All corresponding runtime execution checks remain pending. The table retains the original findings as audit history.

| ID | Finding and concrete consequence | Required closure | Latest resolution point |
| --- | --- | --- | --- |
| GAP-01 (specified; execution pending) | FR-011 and the policy contract name rip, careful, plan, yolo and five tiers, but define only some decisions. Two implementations could disagree on whether rip automatically runs a workspace command, whether careful asks for a covered edit, and what yolo changes. | An action-by-mode decision table, tier classification rules, exact hard-deny categories, checkpoint prerequisites, and tests for unknown actions, taint and explicit grants. Product-facing differences need maintainer confirmation. | Before SLICE-009 policy implementation. M1 retains its already-confirmed ask/scoped-grant behavior. |
| GAP-02 (resolved) | FR-002 requires token budgets. The runtime supplies step/tool/time defaults and model context/output limits, but no cumulative per-turn token accounting or default. Many individually valid requests can consume a large total. Context capacity is not a cumulative budget. | Define input/output/reasoning accounting, whether repeated input and compaction count, default and override behavior, usage-unavailable estimates, and the stop outcome. Confirm the product-facing limit rather than inventing a spending policy. | Before SLICE-006 budget implementation; establish the minimal applicable guard before real tools. |
| GAP-03 (specified; execution pending) | The runtime requires bounded backpressure and cancellation within 50 ms, but does not state how cancellation reaches an engine whose event channel is full. A stalled client could prevent the control request or provider shutdown from progressing. | Specify independently serviced cancellation/control and delivery-failure handling, including persistence/final-outcome behavior when the consumer never drains. Exercise a full channel and a stalled consumer while cancelling. | SLICE-001 concurrency design, before implementing its channel loop. |
| GAP-04 (specified; execution pending) | The store contract gives one writer per session. Models/defaults, last-good snapshots, project indexes, trust records and login registration/refresh state can still be shared across independent processes/sessions. Atomic file replacement alone does not prevent one writer from losing another writer's update. | Assign ownership and locking/version checks for each shared object. Define conflict/retry behavior, crash-safe publication and refresh serialization across processes. Test two simultaneous setup/default changes and refresh attempts. | Before each shared store lands, starting SLICE-003. Rebuildable indexes may use a different policy from credentials/trust. |
| GAP-05 (specified; execution pending) | The build plan puts real tools in SLICE-005 and full cancellation/budgets in SLICE-006. It does not explicitly require a working minimal cancellation, child timeout/escalation and bounded-call guard before the first real command. Developers could interpret the order as allowing unbounded execution temporarily. | Split minimum prerequisites from later UI/full-loop controls and make command acceptance depend on tested cancellation, termination and applicable budgets. Do not change the confirmed two-second grace or containment requirements. | Before SLICE-005 tools are implemented or exercised. |

GAP-01's product behavior is now specified in the final mode matrix. GAP-02's product choice is now settled without a cumulative token cap. GAP-03 through GAP-05 require engineering contracts and sequencing detail. These findings do not automatically revoke approved requirements or authorize changing them.

## Existing gates, not newly discovered gaps

Exact provider/model endpoint fixtures, the bundled metadata snapshot, SIWC registration/account eligibility, the selected dependency graph, actual static linkage, benchmark repeatability, and OS containment/durability evidence were already explicitly pending. They block associated support/release claims. They are not evidence that a written requirement is missing.

At the initial audit, versioned payload schemas and SLICE-002 through SLICE-019 specifications were absent. The [final slice review](2026-11-14-final-slice-review.md) subsequently supplied all 19 local specs and concrete boundary schemas. Their implementation, verifier construction and external feasibility gates remain pending; local documentation cannot establish runtime release readiness.

## Verification limits

`python3 scripts/check_docs.py --self-test` checks local references and all 33 requirement mappings. `scripts/check_model_schema.py` validates the configuration schema and fixture. Neither check proves behavioral completeness, the permission matrix, aggregate budgets, or concurrent-store correctness. Passing them cannot justify a zero-gap claim.


## Engineering closures recorded during the interview

GAP-04 is specified in [shared-state coordination](../contracts/storage-and-context.md#shared-state-across-processes), including ownership, conflicts, protected credential generations, refresh/logout serialization, and failure behavior.

GAP-05 is specified in the [delivery dependencies](../04-architecture.md#delivery-dependencies) and [tool contract](../contracts/tools-and-policy.md#file-observations-and-patches). SLICE-005 now requires tested minimal cancellation, limits, termination/lifetime control, bounded output, and persistence before real commands. SLICE-006 adds richer controls rather than introducing these safeguards late. These are specification closures, not passed runtime tests.


GAP-03 is specified in [cancellation and stalled delivery](../contracts/runtime.md#cancellation-and-stalled-delivery). The confirmed 30-second timeout is separate from command runtime and from the 50 ms cancellation acknowledgement. Full-channel cancellation and persistence/delivery failure cases remain implementation gates.

GAP-01 is closed by the [permission mode contract](../contracts/tools-and-policy.md#permission-modes) and [decision matrix](../contracts/tools-and-policy.md#mode-decision-matrix). The maintainer delegated final names and differences. Representative policy acceptance vectors are supplied; runtime enforcement remains unverified.
