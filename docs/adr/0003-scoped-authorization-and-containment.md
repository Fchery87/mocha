---
status: accepted
date: 2026-11-14
---

# Keep authorization and containment distinct

Mocha requires scoped grants for subprocess networking and fails closed when requested containment cannot be enforced. Project trust cannot grant itself permissions, unknown MCP effects require approval, and absolute blocks apply in every mode including unattended. These boundaries take precedence over the convenience of unrestricted automation and apply consistently to interactive and headless operation.

Provider inference and authentication have separately specified host-side access. The coverage matrix must identify authorization, OS containment, network access, and credential exposure for each execution path. The [PRD](../02-prd.md#fr-012-linux-sandbox) remains the source for required behavior; implementation proof is still pending.

Minimum containment precedes M1 real commands. A network grant permits outbound access for the named action scope and can reach arbitrary destinations. Destination-only egress filtering is outside the MVP. The preview must state this boundary.
