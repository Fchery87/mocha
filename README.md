<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/mocha-logo-dark.svg">
    <img alt="Mocha" src="assets/mocha-logo-light.svg" width="420">
  </picture>
</p>

# Mocha

**A lightweight, provider-agnostic agent harness for the terminal, built in Rust, first and foremost for coding.**

> **Status: design phase.** No code yet. This repository holds the product and engineering decisions that Mocha will be built from.

Mocha aims to be:

- **Light:** a single static binary. A background daemon owns all sessions, so each extra session costs ~3 MB and idle costs 0% CPU. Targets: ≤ 20 ms to input, ≤ 30 MB for the daemon plus one session.
- **Smart at coding:** structure-aware search, a repo map, LSP, auto-verification after edits, a `/goal` completion loop, self-review, checkpoints with `/rewind`, subagents, and Lead mode.
- **Open:** any provider or model via config (Anthropic, OpenAI, Google, OpenRouter, local models, and more), plus Claude and ChatGPT plan sign-in. MCP, hooks, and skills for extension. Reads `AGENTS.md` and `CLAUDE.md`.
- **Fast without being reckless:** `rip` mode runs freely and asks only for genuinely dangerous actions. Catastrophic actions are always blocked, and the Linux sandbox is on by default.
- **Calm:** a clean, fullscreen terminal UI that takes as little of your attention as possible, with an inline mode when you want native scrollback.

## Documents

| Document | What it is |
|---|---|
| [DESIGN.md](DESIGN.md) | Terminal UI and UX: the Full layout, the pour, the rail and dock, the Focus toggle, components, keymap, and rendering rules |
| [docs/FEATURES.md](docs/FEATURES.md) | The complete feature and capability catalog, with priorities |
| [docs/research/2026-11-10-mocha-engineering-blueprint.md](docs/research/2026-11-10-mocha-engineering-blueprint.md) | Architecture, crates, subsystems, performance budgets, and the build sequence |

UI explorations live on the [`prototype/tui-variants`](../../tree/prototype/tui-variants) branch (throwaway code).

## License

[MIT](LICENSE) © 2026 Fchery87
