---
status: accepted
date: 2026-11-14
---

# Separate replay from execution

A crash can leave an operation completed without a saved result, so replaying history is not permission to repeat its effects. Mocha reports such operations as outcome unknown and never automatically reruns arbitrary shell commands or remote mutations merely because completion is unrecorded. This favors explicit reconciliation over potentially duplicating an external effect.

History replay reconstructs observations without live tool execution. Required approval or information unavailable to a headless run produces a distinct nonzero result, as specified in the [PRD](../02-prd.md#fr-003-headless-mode-mocha-run).
