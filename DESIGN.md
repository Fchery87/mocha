# Mocha — DESIGN.md

**Status:** v2, 2026-11-10. The source of truth for Mocha's terminal UI and UX.

**Decided:**
- The **Full** layout is the default. It's fullscreen and edge-to-edge, with the **Volt** palette and the **Cup** mark.
- **Focus** is a toggle.
- **Inline** mode is the fallback for people who want the terminal's native scrollback.

**Prototype:** branch `prototype/tui-variants`, variant A "Full" (`prototypes/tui-variants/src/full.rs`).

**Related:**
- `docs/FEATURES.md`: what Mocha does
- `docs/research/2026-11-10-mocha-engineering-blueprint.md`: how it's built

---

## 1. Principles

1. **Take as little attention as possible.** Mocha confirms once, stays quiet while it works, and speaks for a result, a decision, or a failure. Every line on screen must earn its place.
2. **Bands, not boxes.** Structure comes from whitespace, indentation, and **tinted bands**. There are no borders in the main view.
   - A band means *you*: your sent messages and the composer share one band, so what you type looks exactly like what it becomes.
   - A band with an accent edge means *Mocha needs you*.
3. **One canvas, one accent.** Mocha paints its own neutral background, so it looks the same in every terminal. Color is rationed:
   - neutrals for everything
   - the accent (**Volt** lime) for brand, focus, and "needs you"
   - teal and red only for success and failure
4. **Use the whole screen, with purpose.** The top bar, bands, and diffs span the full width. Details sit next to what they describe, and only time and cost pin to the right edge. Wide screens gain a **rail** (plan, agents, changes, checkpoints) instead of empty space.
5. **Nothing that needs you can scroll away.** Approvals and questions dock above the composer until answered.
6. **One signature: the pour.** A line under the top bar fills as a turn progresses, the spinner is a cup filling up, and the terminal's own progress bar mirrors both. Everything else is calm. Nothing moves when idle.
7. **Quiet by default, detail on demand.** Everything collapses to one line and expands with a key. Nothing is hidden that can't be reached in one keystroke.
8. **Light means light.** The UI never costs more than the budgets in §12. Idle is 0% CPU and zero redraws.

---

## 2. Screen anatomy (Full)

```
 ◒ mocha  ~/code/api · main                                  48k of 200k ██░░░░░░ 24%   ← top bar
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━──────────────────────────────────────   ← the pour
┌─ band ─────────────────────────────────────────────────────────────┐ │  Plan       2 of 4
│  › where do we generate the session key?                   2:39 pm │ │  ✓ reproduce the flake
└────────────────────────────────────────────────────────────────────┘ │  ✓ clock behind a trait
   In src/auth/session.rs:88, new_session_key() hashes the user id…    │  ▅ add LoginLimiter
   ✓ 8s · read 2 files                                 ↓1.2k · $0.01   │  ○ review the full diff
┌─ band ─────────────────────────────────────────────────────────────┐ │
│  › fix the flaky login test and add rate limiting          2:41 pm │ │  Agents          3
└────────────────────────────────────────────────────────────────────┘ │  ● docs-sweep  needs you
   ◦ thought for 3.2s                                                  │  ◐ web-app          2m
   I'll reproduce the flake first, then add the limiter.               │  ✓ ci-fix         done
                                                                       │
   ◦ Explored                                                          │  Changed      2 files
       read     src/auth/session.rs  212 lines                         │  auth/limiter.rs +38 −0
       search   "login" in tests/  14 hits in 3 files                  │  auth/clock.rs   +12 −3
   ◦ Edited    src/auth/limiter.rs  +38 −0  ⟲ 7                        │
 ░░░░░░░ 12  + pub struct LoginLimiter {  ░░░░░░░░ (tinted row) ░░░░░ ┃  Checkpoints      8
   ▅ Running   cargo test auth::  18/24 passed                         ┃  ⟲ before clock.rs ctrl+z

   Root cause                                                                 ← rail (≥ 140 cols)
   The flake came from a shared SystemTime clock …▍
▌                                                                                    ← dock: needs you
▌ git push origin main   docs-sweep wants to run this       pushes to the default branch
▌ › 1 allow once     2 allow for this session     3 no                      1–3 or enter
▌
 ▅ brewing  15s                                         ↓9.4k · $0.04 · 17s  esc stop   ← status
  ── band ──────────────────────────────────────────────────────────────────────────
   › ask mocha anything · / commands · @ files                     opus-5.5 high · rip  ← composer
  ──────────────────────────────────────────────────────────────────────────────────
 esc stop    ctrl+enter interject    shift+tab mode    alt+j agents    ? shortcuts      ← footer
```

The `┌─ band ─┐` outlines above only mark where a band is. Bands have no borders on screen: they're a background tint.

**Regions, top to bottom:**

| Region | Height | Contents |
|---|---|---|
| Top bar | 1 | Brand, folder and branch on the left. Context used and the meter on the right. |
| Pour | 1 | The turn's progress (§4.2). A plain hairline when idle. |
| Transcript | fills | The conversation. It grows from the top and follows the newest line once it overflows. The **rail** sits on the right at ≥ 140 columns. |
| Dock | 0–6 | Whatever needs you. It's absent when nothing does. |
| Status | 1 | What's happening and its cost, while working |
| Composer | 3+ | Your input on the "you" band, with model and mode on the right. It grows with multi-line input. |
| Footer | 1 | Key hints for *this moment* |

**Fullscreen, with an inline fallback.** Full runs in the alternate screen. Mocha owns scrolling, search, selection, and copy (§12).
- **On exit,** Mocha prints a short receipt into the terminal's normal scrollback: `◒ mocha · fox · 2 turns · +50 −3 · resume: mocha -r fox`. Your shell history still shows what happened.
- **Inline layout:** `--inline` or `ui.layout = "inline"` renders the same components into the terminal's native scrollback. That means no rail, no top bar, and a dock that sits in the live area.

---

## 3. Visual language

### 3.1 Color tokens (Volt, the default palette)

| Token | Dark | Light | 256 / 16 | Use |
|---|---|---|---|---|
| `bg` | `#141416` | `#FAFAF8` | 233 / default | The canvas Mocha paints |
| `text` | `#E4E4E7` | `#1C1C1F` | 254 / default | Primary text |
| `muted` | `#86868F` | `#7A7A82` | 245 / bright black | Metadata, verbs, hints, timestamps |
| `line` | `#34343A` | `#D4D4D2` | 237 / bright black | Hairlines, the idle pour, the scrollbar track, empty meter cells |
| `band` | `#232327` | `#EEEEEC` | 235 / reverse | **You:** sent messages, the composer, the dock |
| `accent` | `#C5F23A` | `#4D7C0F` | 191 / bright yellow | Brand `◒`, `›`, the pour, the spinner, focus and "needs you" edges, the active mode |
| `accent2` | `#7DD3FC` | `#0369A1` | 117 / cyan | **Only** the crema in the cup mark |
| `ok` | `#5EEAD4` | `#0F766E` | 80 / cyan | Success, `+` lines, passed tests, `✓`. It's teal so it never reads as the brand. |
| `bad` | `#FF6B81` | `#BE123C` | 204 / red | Failure, `−` lines, `✗` |
| `add_bg` | `#15261B` | `#E3F4E6` | 22 / — | The tint behind added diff lines |
| `del_bg` | `#2A1719` | `#FBE7EA` | 52 / — | The tint behind removed diff lines |

**Rules:**
- **Headings and inline code are bold `text`, never a color.**
- **The meaning is never carried by color alone.** Every colored thing also has a glyph or a word (`+38`, `✓`, `needs you`, `▌`).
- **Contrast:** body text vs. `bg` and vs. `band` is checked to APCA ≥ 75. `muted` is APCA ≥ 45 (metadata only). The accent on `bg` is ≥ 60 in both themes.
- **Light/dark:** detected with the OSC 11 background query, overridable with `ui.theme = "auto" | "dark" | "light"`.
- **`ui.background = "terminal"`** skips painting `bg` and uses the terminal's own background. Bands and tints stay.
- **Fallbacks:**
  - Color depth is detected (`COLORTERM`, terminfo), falling back to 256 colors, then 16.
  - In 16 colors, bands become reverse video and diff tints are dropped.
  - `NO_COLOR` keeps glyphs, bold, and the band shape (reverse), and nothing else.
- **Alternate palettes** are swappable with `ui.palette`. Only the accent, `accent2`, `ok`, and `bad` change; the neutrals stay.
  - `iris` (violet): it reads close to the popular Catppuccin "Mocha" theme, so it isn't the default.
  - `glacier` (ice blue)
  - `gold` (bright gold)

### 3.2 The mark: Cup

Mocha's mark is a **pixel-art cup with steam**, drawn in half-blocks (`▀▄`), so each terminal row carries two pixel rows. It's 15 × 10 pixels, which is 15 × 5 cells:
- **Crema:** a single top row in `accent2`, the only place it appears
- **Body and handle:** in `accent`
- **Steam:** two wisps in a muted tone that drift for **3 seconds** at startup, then settle (§9)

Next to it, the name is set in plain bold text (`mocha`). There's no custom lettering.

| Form | Where |
|---|---|
| **Cup + name** | Welcome screen (centered, at heights ≥ 20) · README and social preview (SVG, dark and light, from the same grid via `assets/gen_logo.py`) |
| **`◒ mocha`** | Top bar · exit receipt · `mocha --version` · agent views. `◒` is a cup from above, half poured. |
| **`◒`** | Terminal title prefix, notifications |

**Fallbacks:**
- 16-color: yellow body plus cyan crema.
- `NO_COLOR`: the cup mark and glyphs stay; only color is removed (see above).
- `ui.ascii`: `mocha` in bold, with `(o)` as the mark.

### 3.3 Glyphs

| Glyph | Meaning |
|---|---|
| `◒` (accent) | Brand |
| `›` (accent) | You: on sent messages, the composer, and the selected choice |
| `▌` (accent edge) | Needs you (dock), or the composer while typing |
| `━` / `─` | The pour: progress filled / remaining (`─` alone = idle hairline) |
| `▁▂▃▄▅▆▇█` (accent) | The cup spinner: something is running *right now* |
| `◦` (muted) | A finished action group |
| `✓` (ok) / `✗` (bad) | Finished: success / failure |
| `⟲ 7` (muted) | Checkpoint 7 was taken before this change (`ctrl+z` / `/rewind 7`) |
| `⋯` (muted) | Collapsed content (`ctrl+o` expands) |
| `▍` (accent, trailing) | Streaming cursor |
| `●` `◐` `○` | Agents and plan steps: needs you / working / pending |
| `│` `┃` | Rail divider and scrollbar: track / thumb |

Glyphs come from widely supported Unicode only. ASCII fallbacks under `ui.ascii = true`:

| Glyph | Fallback |
|---|---|
| `◒` | `(o)` |
| `›` | `>` |
| `▌` | `\|` |
| `━` | `=` |
| spinner | `-\|/` |
| `◦` | `o` |
| `✓` / `✗` | `+` / `x` |
| `⟲` | `@` |
| `⋯` | `...` |

### 3.4 Spacing and alignment

- **Outer margin:** 1 column on each side. Bands span margin to margin. Agent content has a 2-column gutter inside that.
- **Tool rows:**
  - The glyph sits at column 2, and the verb is padded to 9 columns.
  - Targets start at column 13, and sub-rows align their targets to the same column.
  - **Stats follow the target after two spaces**, not in a far column.
- **The right edge is reserved** for time (timestamps, durations) and cost (`↓9.4k · $0.04`). Nothing else pins right.
- **Vertical rhythm:**
  - One blank line between blocks.
  - Bands carry one tinted padding row above and below their text.
  - A tool block gets a blank line before and after.
- **Measure:** prose wraps at **min(transcript width − 6, 132)**. Code, diffs, and command output use the full width, and diff tints always span it.
- **Rail:** 36 columns, separated by the `│` divider, which doubles as the transcript's scrollbar.

### 3.5 Typography
Bold is for headings, your words in the transcript, verbs in tool rows, and keys in hints. `muted` is for everything secondary. Italic isn't used, because too many terminals and fonts render it badly.

---

## 4. Components

### 4.1 Top bar
- **Left:** `◒ mocha  ~/code/api · main`
- **Right:** `48k of 200k ██░░░░░░ 24%`. The meter cells turn `accent` as the context fills, and above 85% the percentage is bold `bad`.
- When it matters, plan quota appears before the meter: `5h 82%`.
- It's always one row and never animates.

### 4.2 The pour (signature)
A full-width line directly under the top bar:
- **Idle:** a `line`-colored hairline that separates the bar from the transcript.
- **Working:** it fills left to right in `accent` (`━`) to the turn's progress, and a short bright drop runs along the poured part.
  - Progress = completed plan steps plus the current step's share.
  - With no plan, it fills asymptotically by elapsed time and never reaches the end until the turn completes.
- **Done:** it fills completely, holds for 400 ms, then fades back to the hairline.
- **Failed:** the filled part turns `bad` for 400 ms.
- **The terminal's own progress bar** mirrors it via OSC 9;4 (Ghostty, Windows Terminal, WezTerm, Konsole, and others; unsupported terminals ignore it). The state is cleared on exit.

### 4.3 Your message
- A full-width `band`, with one padding row above and below.
- `›` in accent, then your text, with the time pinned right in `muted`.
- Wrapped lines indent under the text.
- Attachments are listed `muted` on the band's last text row: `@src/auth/session.rs · screenshot.png`.

### 4.4 Agent text
- Rendered Markdown:
  - headings in bold `text`
  - lists
  - inline code in bold
  - fenced code blocks syntax-highlighted on a `band`-tinted block with a `muted` language label
  - aligned tables
  - links as OSC 8 hyperlinks
- Streams in place with a trailing `▍`. It's rendered incrementally: only the last block re-renders.
- Thinking shows as one `muted` line, `◦ thought for 3.2s`, which expands with `ctrl+o`.

### 4.5 Action groups
Consecutive tool calls of the same kind merge into one group. A running group shows the **cup spinner** instead of `◦`.

| Group | Verbs inside | Collapsed default |
|---|---|---|
| `◦ Explored` | read, search, list, outline, lsp | Rows shown. More than 5 rows collapse to `⋯ 9 more`. |
| `◦ Edited <file>  +a −d  ⟲ n` | edit, write, patch | First 3 changed lines, then `⋯ n more lines · ctrl+o` |
| `◦ Ran <command>  ✓ exit 0` | bash | Last 2 lines of output |
| `▅ Running <command>  18/24 passed` | bash (live) | A live tail of 1–3 lines, with progress if parseable |
| `◦ Fetched` | web_fetch, web_search | Titles + domains |
| `◦ Delegated <agent>` | delegate | One line + its final report |
| `◦ Called <server>.<tool>` | MCP | One line + a summary |

`ctrl+o` expands the most recent group. A mouse click expands any group.

### 4.6 Diffs
- Added lines sit on a **full-width `add_bg` row**, in `ok`. Removed lines sit on `del_bg`, in `bad`.
- Line numbers are `muted`, and context lines are plain.
- Word-level changes inside a line are bold.
- At ≥ 160 columns, `ui.diff = "split"` shows them side by side.

### 4.7 Turn receipt
When a turn finishes, one line closes it:
- **Left:** `✓` in `ok` plus `muted` facts: `8s · 3 files +56 −4 · tests ✓`.
- **Right:** cost, pinned: `↓1.2k · $0.01`.
- If no check ran: `✓ done · not verified`, which is honest by design.
- A failed turn uses `✗` in `bad`.

### 4.8 Dock (needs you)
Appears **only** when a person must act: a tier-3 permission, a question from the agent, a background agent that's blocked, a plan to approve, or a quota decision. It sits between the transcript and the status line, and it can't scroll away.

```
▌
▌ git push origin main   docs-sweep wants to run this       pushes to the default branch
▌ › 1 allow once     2 allow for this session     3 no                      1–3 or enter
▌
```
- On a `band` with an `accent` `▌` edge.
  - **Row 1:** what's being asked in bold, who's asking in `muted`, and *why it's tier 3* pinned right.
  - **Row 2:** the choices.
- **Keys:** `1–9`, or `←/→` + `enter`. `d` shows the diff or the parsed command, and `e` asks the agent why.
- **One request at a time.** Others queue, shown as `◆ 1 more waiting` on the status line, and the rail shows a `needs you` count.
- **A question from the agent** uses the dock, with numbered options and an "other" option that focuses the composer.
- **Plan approval** shows the plan's first lines with `enter approve · e edit · esc keep planning`.
- Tiers 0–2 never produce a dock (see FEATURES §7).
- **Below 72 columns,** the choices stack vertically and the "why" moves to its own row.

### 4.9 Status line (while working)
- **Left:** `▅ brewing  15s`. A shimmer sweeps across the verb, and the verb changes with the phase:
  - *brewing*: thinking
  - *pouring*: streaming an answer
  - *steeping*: waiting on a long command
  - *grinding*: compacting context
- **Right:** `↓9.4k · $0.04 · 17s  esc stop`. When relevant: `↑ 2 queued`, `◆ 1 more waiting`, `⚠ cache cold`.
- **When idle,** the row stays empty, so the layout doesn't jump.

### 4.10 Composer
- It sits on the **same band as your sent messages**: a padding row, then `›` plus your input, then a padding row.
- An accent `▌` edge appears while you type.
- **Right side:** `opus-5.5 high · rip`. The mode is in `accent` and bold when it isn't `rip` (e.g. **careful**, **plan**).
- The placeholder is `ask mocha anything · / commands · @ files`.
- Multi-line input grows to 8 rows, then scrolls.

**Behavior:**
- `enter` sends · `shift+enter` / `ctrl+j` newline · `ctrl+g` opens `$EDITOR`
- `@` file and folder mention with fuzzy completion · `/` commands · `!` runs a shell command yourself
- **While Mocha works:**
  - `enter` steers: the message is delivered after the current tool batch.
  - `ctrl+enter` interjects now: the current step is interrupted.
  - `tab` queues the message as a follow-up instead.
- Pasted images show as `[image 1]` chips. Large pastes collapse to `[pasted 240 lines]`.
- `↑` / `ctrl+r`: history and history search.

### 4.11 Footer
Key hints for **this moment**. The bold key comes first, then the `muted` action, with four spaces between hints. The set changes with state:

| State | Hints |
|---|---|
| Idle | `enter send` · `shift+tab mode` · `ctrl+r resume` · `? shortcuts` |
| Working | `esc stop` · `ctrl+enter interject` · `shift+tab mode` · `alt+j agents` · `ctrl+z undo` · `? shortcuts` |
| Dock open | `1–3 choose` · `d diff` · `e explain` · `esc dismiss` |
| Overlay | That overlay's own keys |

Hints drop from the right as the width shrinks (§8).

### 4.12 Rail (≥ 140 columns)
A 36-column side panel that turns width into information. Sections appear only when they have content:
- **Plan:** `2 of 4`, with steps marked `✓` / spinner / `○`
- **Agents:** `●` needs you (accent) / `◐` working / `✓` done, each with a right-pinned state or age
- **Changed:** files with `+a −d`
- **Checkpoints:** the latest one, with `ctrl+z`

Clicking an item opens it: a step, an agent, a file diff, or a checkpoint. `alt+r` toggles the rail at any width. Below 140 columns, its contents are reachable through `alt+j` (agents), `/diff`, and `/rewind`.

### 4.13 Errors and warnings
- **A tool failure** is an action row with `✗` plus its short reason. The agent usually recovers, so it doesn't interrupt.
- **A provider or harness error** is a `✗` line in `bad`, plus a `muted` next step: `✗ rate limited by anthropic · retrying on account 2 in 8s`.
- **Warnings** use `muted` `⚠` lines. Never modal.

---

## 5. Focus mode (toggle)

**What:** the same screen with everything except *now* turned down. Toggle with **`alt+f`** or `/focus`, and choose it as the default with `ui.focus = true`.

| Element | Full | Focus |
|---|---|---|
| Past turns | Full | Your band plus a one-line `muted` summary of the answer |
| Finished action groups | Shown, collapsed per §4.5 | **One line per turn:** `✓ read 2 files · edited 3 files +56 −4 · 3 checkpoints   ctrl+o details` |
| Current answer | Normal | Normal (the brightest thing on screen) |
| Running action | Group with a live tail | One `now` line: `▅ cargo test auth::  18/24  12s` |
| Rail | Shown at ≥ 140 | Hidden. The transcript centers at the prose measure. |
| Pour, dock, status | Shown | Shown |

Focus changes only rendering. The full detail is always one `ctrl+o` away, and `ctrl+t` shows everything.

---

## 6. Screens beyond the conversation

Overlays replace the transcript region. The top bar, pour, dock, and composer stay in place, and `esc` closes the overlay.

### 6.1 Welcome
The empty session, shown on launch and after `/clear`. Centered in the transcript region:
```
                    ▄ ▀  ▄▀
                  ▀▀▀▀▀▀▀▀▀▀▀▀
                  ████████████▀▄
                   ▀████████▀
                   mocha  v0.1.0
          opus-5.5 high · rip · ~/code/api · main

            ✓ AGENTS.md loaded · repo trusted

  Recent                                        ctrl+r resume
  fox      fix the flaky login test                    2h ago
  heron    move sessions to sqlite                  yesterday
  otter    docs sweep                              3 days ago

        / commands    @ files    shift+tab mode    ? keys
```
- The cup's steam rises for 3 seconds.
- The trust line reads `⚠ untrusted repo · AGENTS.md and hooks not loaded · /trust` when that's the case.
- Recent sessions are this folder's, at most 3, and `↑` selects them.
- Below 20 rows the cup is dropped. Below 50 columns the session titles are dropped.

### 6.2 Agent command center (`alt+j`, `/agents`, `mocha agents`)
A list grouped by what needs you:
```
  Agents                                   needs you 1 · working 2 · ready 1

  needs you
  › ● docs-sweep      wants git push origin main                     2m
  working
    ◐ auth-refactor   cargo test auth:: 18/24 · 48k · opus           6m
    ◐ web-app         editing src/app.tsx · 21k · opus               3m
  ready
    ✓ ci-fix          +14 −6 · evidence ✓ · review                  12m

  enter open · r reply · d diff · x stop · / filter · esc back
```
- The selected row sits on a `band` with an accent `▌`.
- Selecting a row opens that session.
- Unread results stay bold until opened.

### 6.3 Lead mode (`/lead`)
- Your messages go to the lead.
- Workers render in the rail (or pinned above the status line below 140 columns) as a task list:
  ```
  ◐ auth-refactor   cargo test 18/24        ● docs-sweep   needs you
  ◐ web-app         editing 3 files         ○ changelog    queued · after merge
  ```
- The top bar shows `◒ mocha · lead` in accent, so you always know who you're talking to.
- `@task` addresses a worker directly.

### 6.4 Pickers (model, session resume, files, commands)
- A fuzzy list rising from the composer: a query line and up to 10 results.
- The selection is a `band` row with an accent `▌`.
- On wide screens, a `muted` preview column.
- `/model` shows provider · context · price · speed.

### 6.5 Transcript search and viewer (`ctrl+t`, `/` while scrolled)
- Search the whole session.
- `[` `]` jump between turns.
- Every group is expandable.
- `y` copies a block (OSC 52).
- `r` rewinds to the checkpoint of the selected change.

### 6.6 Diff review (`/diff`, `d` from the dock)
- All session changes, grouped by file, with full-width tinted rows.
- Each hunk has its own `⟲` checkpoint, and `u` undoes a hunk.

### 6.7 First run
1. The welcome screen, with the cup and one sentence.
2. "Sign in": Claude plan · ChatGPT plan · API key · local model · configure later.
3. Theme check: dark or light is auto-detected, and a sample diff on the band confirms the colors are readable.
4. The trust question for the current folder.
5. Into the composer. No tour, and `?` is always there.

---

## 7. Keymap (defaults; all rebindable in `~/.mocha/keys.toml`)

| Key | Action |
|---|---|
| `enter` / `shift+enter` | send (steer while working) / newline |
| `ctrl+enter` | interject now (interrupt the current step and send) |
| `esc` | stop the current turn · close an overlay · dismiss the dock (= "no") |
| `tab` | queue as a follow-up instead of steering |
| `shift+tab` | cycle mode: rip → careful → plan |
| `ctrl+o` | expand/collapse the latest group |
| `ctrl+t` | transcript viewer and search |
| `ctrl+z` | undo to the latest checkpoint (`/rewind` for older ones) |
| `alt+f` | Focus mode |
| `alt+j` | agent command center |
| `alt+r` | toggle the rail |
| `ctrl+g` | edit the input in `$EDITOR` |
| `ctrl+r` | resume a session (idle) · history search (while typing) |
| `pgup` / `pgdn`, wheel | scroll the transcript. `end` jumps back to the live edge. |
| `ctrl+l` | redraw |
| `ctrl+c` | stop. Twice on an empty composer exits. |
| `?` | shortcuts sheet |
| `1`–`9` | answer the dock |

**Mouse** (on by default; `ui.mouse = false` turns it off):
- the wheel scrolls
- clicking expands groups and opens rail items
- dragging selects text, and Mocha copies it via OSC 52
- `shift`+drag falls through to the terminal's native selection

**Conflicts:** macOS terminals that send `alt` as a character get `esc f` / `esc j` / `esc r` equivalents. `mocha doctor` reports keys the terminal can't deliver, including `ctrl+enter`. The fallback for that is `alt+enter`.

---

## 8. Responsive behavior

Mocha must be fully usable from a 30 × 12 split pane to a 240-column ultrawide. Verified in the prototype at 164×46, 150×46, 120×40, 100×44, 70×40, 56×40, 48×30, and 44×34, in dark and light.

| Width | Top bar | Transcript | Tool rows & diffs | Dock | Status & composer | Footer |
|---|---|---|---|---|---|---|
| **≥ 140** | Full: path, branch, `48k of 200k`, meter | Transcript + **rail** | Stats inline · 3 diff lines | One row of choices | Cost and time right · model and mode right | All hints |
| **100–139** | Full | Transcript only (rail via `alt+r`) | Same | One row | Same | All hints |
| **64–99** | Drops `48k of 200k` below 90 | Same | Same | Choices stack below 72 | Same | `esc` · `shift+tab` · `?` |
| **< 64** | Path only, `24%` without the meter below 46 | Same | Stats and `⟲` dropped · diffs hidden (`ctrl+o`) | Short label, stacked | Status: seconds + `esc` · composer: no model/mode | Two hints |

| Height | Behavior |
|---|---|
| ≥ 20 | Welcome shows the cup |
| < 20 | Welcome is text only |
| < 16 | The status line merges into the composer's right side, and band padding rows drop |
| < 12 | The top bar and pour merge into one row (the pour is drawn under the brand) |

**Rules that make this hold:**
- **No truncated words.** Long paths truncate in the middle (`src/…/limiter.rs`), never at the end.
- **Right-pinned items drop first.** When the left and right sides of a row would collide, the right side is dropped, never overlapped.
- **Live resize** re-lays out the whole screen in one frame. The scroll position is kept relative to the turn you're reading.
- **Overlays** have their own breakpoints. Below 60 columns, preview columns disappear and lists go full-width.
- **Tests:** every component has snapshot tests at widths 30 / 48 / 64 / 100 / 140 / 180 and heights 12 / 24 / 46 (§14).

---

## 9. Motion

All motion shares one ~14 fps clock that runs **only while something is happening**, and stops the instant it isn't.

| Motion | When |
|---|---|
| **The pour** fills and its drop runs | While a turn is working |
| **The cup spinner** fills | On the running row, the current plan step, and the status line |
| **The shimmer** sweeps the status verb | While working |
| **The steam** rises over the cup | On the welcome screen, for 3 s |
| **Streaming text** | As it arrives, coalesced to ≤ 30 repaints/s |

- **The caret** blinks at 530 ms (the terminal default).
- **Nothing else moves.** There are no transitions or slide-ins, and the pour's done/failed flash is the only "effect".
- **`ui.motion = "reduced"`** (or `REDUCE_MOTION`):
  - the pour fills in steps with no drop
  - the spinner becomes a static `▅`
  - the verb is static, with a once-per-second elapsed counter
  - the steam doesn't animate

---

## 10. Voice and copy

- Short, plain, and specific. `edited 3 files`, not "I have successfully made changes to several files".
- Status verbs carry the brand (brewing, pouring, steeping, grinding). Everything else is literal.
- Numbers over adjectives: `18/24 passed`, `48k of 200k`, `2m 14s`.
- Never claim what isn't verified: `done · not verified` over `done!`.
- Errors say what happened and what's next, in one line.
- The dock always says *why* it's asking (`pushes to the default branch`).
- No emoji in the UI chrome.

---

## 11. Accessibility

- **Color is never the only signal.** Every color has a glyph or word alongside it (§3.1). Bands survive `NO_COLOR` as reverse video.
- **`NO_COLOR` and `ui.ascii`** are supported.
- **Reduced motion** (§9).
- **`ui.screen_reader = true`** switches to the inline layout with no shimmer and no in-place rewrites. Output is append-only plain lines, status changes are announced as text lines, and the dock is announced with its choices.
- **Contrast targets** are in §3.1, and they're checked in tests for every palette, in both themes.
- **Everything is reachable by keyboard.** The mouse is optional.

---

## 12. Rendering and performance rules

| Rule | Budget |
|---|---|
| Keystroke to paint | ≤ 8 ms p99 |
| Streaming repaint rate | ≤ 30/s, coalesced |
| Animation clock | ~14 fps, only while working. 0 when idle. |
| Idle | 0 repaints, 0% CPU (no timers when nothing animates) |
| Bytes per streaming frame | Only changed cells. Typically < 400 bytes. |
| Thin client memory | ≤ 12 MB, including the transcript buffer |

- **Alternate screen** with **synchronized output** (DEC mode 2026) around every frame, so GPU terminals never tear.
- **Transcript buffer:** Mocha owns scrollback.
  - Rendered lines are cached per block and invalidated only on resize or expand.
  - Only the visible window is laid out, so very long sessions scroll in O(visible).
  - The full history lives in the session log (JSONL), not in memory.
- **Selection and copy:** Mocha's own selection, written to the clipboard with OSC 52. `shift`+drag uses the terminal's selection.
- **Painting the canvas:** every cell gets `bg` explicitly, so terminals with transparency or custom backgrounds still look consistent (unless `ui.background = "terminal"`).
- **OSC 9;4** progress mirrors the pour (§4.2). The terminal title is `◒ mocha · <session> · <state>`.
- **Width-correct text:** Unicode width via a grapheme-aware measure. CJK and emoji are tested in snapshots.
- **tmux/screen/SSH:**
  - OSC passthrough (hyperlinks, OSC 52, OSC 9;4, images) is detected, with a graceful fallback.
  - No truecolor is assumed inside tmux unless `Tc`/`RGB` is set.
- **Images:** Kitty / iTerm2 / Sixel when available, otherwise `[image: 1280×720 · ctrl+t to view]`.

---

## 13. Theming and settings

```toml
[ui]
layout = "full"         # full | inline
theme = "auto"          # auto | dark | light
palette = "volt"        # volt | iris | glacier | gold
accent = ""             # optional hex override of the palette's accent
background = "mocha"    # mocha (paint the canvas) | terminal
rail = "auto"           # auto (≥ 140 cols) | always | never
focus = false           # start in Focus mode
motion = "full"         # full | reduced
mouse = true
ascii = false           # ASCII glyph fallbacks
diff = "unified"        # unified | split
wrap = 132              # prose measure
screen_reader = false
```
Themes may override only the color tokens in §3.1, never layout, glyphs, or the pour. That keeps Mocha recognizably Mocha.

---

## 14. Testing the UI

- **Snapshot tests** (`insta`) for every component at widths 30 / 48 / 64 / 100 / 140 / 180 and heights 12 / 24 / 46. Each runs in dark and light for every palette, plus `NO_COLOR`, ASCII, and `ui.background = "terminal"`. The welcome screen and the cup mark have their own snapshots.
- **vt100 end-to-end tests:** drive the real binary in a PTY and assert screen contents. Cases:
  - streaming
  - the dock flow
  - Focus toggle
  - rail toggle
  - resize mid-stream
  - mouse scroll and selection
  - the exit receipt
- **Perf tests:** a mock provider streaming at 200 tokens/s, with bytes per frame, repaint counts, and idle CPU asserted against §12.
- **Visual review:** throwaway explorations live on `prototype/*` branches, never on `main`. A winner is folded into real components and rewritten properly.

---

## 15. How we got here

| Round | What was tried | Verdict |
|---|---|---|
| 1 | Boxed layouts: Scrollback, Cockpit, Lead Board | Too boxy, too much like Pi |
| 2 | Borderless inline: Pour, Ledger, Focus | Pour chosen, with Focus as a toggle. Later found too narrow, with weak separation between you and the agent. |
| 3 | Palettes, ways to separate your messages, marks | The band won for separation. The pixel lettering and the caramel palette were dropped. |
| 4 | Full: fullscreen, edge-to-edge | Right direction, but too close to its influence |
| 5 | Full + signature: the pour, rail, dock, composer-on-band, welcome, tighter tool rows | **Accepted** |

**Influence:** the fullscreen structure of round 4 was influenced by the *look* of xAI's Grok Build TUI, from its public screenshot and demo. No code was read or reused. Round 5 replaced its distinctive elements (the boxed composer with the model in its border, `◆` thought markers, the `│`-separated hints) with Mocha's own.

---

## 16. Open UI questions (to settle during M1)

1. **Pour progress with no plan:** is elapsed-time asymptotic fill honest enough, or should it pulse in place instead? *Leaning: asymptotic, capped at 80% until done.*
2. **Mouse selection:** is our own selection (OSC 52) plus `shift`+drag fallback good enough, or should mouse capture be off by default over SSH?
3. **Rail in Focus mode:** hidden (current spec), or kept with only "needs you" items?
4. **Inline parity:** which components must look identical in `ui.layout = "inline"`, and which may simplify (no rail, dock in the live area)?
5. **Focus summaries of past turns:** written by the fast model, or generated from the event log? *Leaning: event log first, with a model summary only for the answer line.*
6. **The shortcuts sheet layout** (`?`).
