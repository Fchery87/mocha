# Mocha

A planned Rust coding agent with a terminal UI and a headless interface.

The repository is in the design phase. The current build specification covers a measured mock skeleton, a real coding loop with twelve API-key providers plus Custom, durable sessions, Linux containment, checkpoints, MCP tools, and native ChatGPT sign-in. These are planned capabilities. No application code or release binary exists yet.

Start with [the documentation index](docs/README.md), [the PRD](docs/02-prd.md), and [the architecture and build sequence](docs/04-architecture.md). The [first build slice](docs/slices/SLICE-001/spec.md) defines the initial implementation and its verifier.

Prompts and code go to selected providers. Authorized tools can reach granted services. History and covered checkpoints use private, unencrypted local storage; provider/login credentials use environment references or the OS keychain. Recovery and safety claims are bounded by the contracts and require implementation evidence.

Run `python3 scripts/check_docs.py --self-test` to check documentation structure. This does not test application behavior.

[MIT](LICENSE) © 2026 Fchery87.
