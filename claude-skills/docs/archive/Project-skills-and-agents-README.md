# My Claude Skills & Agents — Project / Build Tooling

These are the skills and agents I have available in Claude Code that are useful when actively building or maintaining a personal project (e.g. Hack4Hope, UAV).

## Skills

### `dataviz`
Load before writing any chart, graph, plot, dashboard, or data visualization — in an HTML/React artifact, inline SVG, or a plotting library (matplotlib, plotly, d3, Recharts, …). Provides a design-system-agnostic method: form heuristics, a validated color palette, mark specs, and interaction rules, so visualizations look consistent in light and dark mode.

### `artifact-design`
Design guidance and fundamentals for building Artifacts (the shareable web-page output format), used to calibrate how much design effort a given page needs.

### `artifact-capabilities`
Describes runtime capabilities a published Artifact can be granted beyond static HTML — live/connected data, shared state across viewers, self-updating pages. Load before declaring any such capability or writing `window.claude.*` runtime code.

### `run`
Launches and drives a project's app to visually confirm a change works — looks for a project-specific "run" skill first, otherwise falls back to built-in patterns per project type (CLI, server, TUI, Electron, browser app, library).

### `init`
Initializes a new `CLAUDE.md` file with documentation for a codebase — used when starting to work in a new project folder that doesn't have one yet.

### `simplify`
Reviews changed code for reuse, simplification, efficiency, and unnecessary complexity, then applies the fixes directly. Quality-focused only — does not hunt for bugs.

### `review`
Reviews a GitHub pull request (for the current local diff, `security-review` or `/code-review` are used instead).

### `security-review`
Runs a full security review of the pending changes on the current branch.

### `remote-pi-min`
Remotes into the Raspberry Pi named "min" (`min@10.235.169.151`) via SSH/SCP using the pre-installed key at `~/.ssh/id_ed25519` — no password prompt needed. Used for UAV camera/TFLite work on that Pi.

### `upload-to-github`
Preps a project folder for GitHub and uploads it: static code checks, README generation, `.gitignore` + `LICENSE` (checking upstream licenses when the code is derived from another project), then pushes to a new or existing repo via `gh`. Always confirms before the actual push.

### `andrej-karpathy-skills:karpathy-guidelines`
Behavioral guidelines to reduce common LLM coding mistakes, derived from Andrej Karpathy's observations. **Mandatory: use this skill any time a program/code is being written.** Surfaces assumptions, keeps changes minimal and surgical, and defines verifiable success criteria before/after coding.

### `emilkowalski/skills` (installed via `npx skills@latest add`, root of `C:\Knight`)
UI/animation "taste" skills from Emil Kowalski (Vercel/Linear, creator of Sonner/Vaul) — meant to fix the small design mistakes agents tend to make (e.g. wrong easing direction, solid border instead of soft shadow). Installed to `.agents\skills\` at the repo root and symlinked into Claude Code.

- **`animate`** — builds an animation from scratch: picks the tool, properties, curve, duration, and how it enters/exits.
- **`review-animations`** — strictly reviews existing animations against Kowalski's rules.
- **`improve-animations`** — audits all animation code in a codebase, outputs a prioritized fix plan (read-only, doesn't apply fixes).
- **`find-animation-opportunities`** — finds UI spots that would genuinely benefit from motion, and flags what shouldn't be animated.
- **`animation-vocabulary`** — reverse-lookup glossary for describing a motion effect precisely (e.g. "the bouncy popover thing" → Pop in).
- **`apple-design`** — Apple's interface/motion design principles (WWDC talks), adapted for the web.
- **`pick-ui-library`** — picks a trusted UI/component library instead of hand-rolling one.
- **`prototype`** — builds multiple variants of a UI piece and lets you switch between them.
- **`emil-design-eng`** — the umbrella skill; general animation + design advice.

## Agents

### `Explore`
Fast, read-only search agent for locating code — finding files by pattern, grepping for symbols/keywords, answering "where is X defined." Not for review or open-ended analysis.

### `Plan`
Software-architect agent for designing implementation plans — step-by-step plans, critical files, architectural trade-offs — before writing code.

### `general-purpose`
Catch-all agent for researching complex questions, searching code, and executing multi-step tasks when the right match isn't obvious on the first few tries.

## pcb-autoroute (skill) — added 2026-09-15
Location: `C:\Knight\.claude\skills\pcb-autoroute\SKILL.md` (scripts in `scripts/`, Freerouting + JRE in `tools/`).
Purpose: generate, autoroute and DRC-clean a KiCad 8 PCB entirely from scripts (placement generator → Specctra DSN with via fanout → Freerouting → pcbnew fill/clean/link → `kicad-cli` DRC → Gerbers). Written after the CanSat carrier board (Project/SPACE/Cansat/hardware2, 4-layer, DRC 0/0); the SKILL.md carries the full failure catalogue (units, mirror conventions, GND-island dead ends on 2 layers, SWIG pitfalls) and the placement/stack-up rules that avoid them.
Invoke: `/pcb-autoroute`, or ask to "route the board" / "redo the CanSat PCB".

## pcb-design (skill) — added 2026-09-16
Location: `C:\Knight\.claude\skills\pcb-design\SKILL.md`.
Purpose: combines two complementary KiCad tools rather than replacing either — `kicad-mcp` (MCP server `kicad`, user-scoped, installed at `Project/tools/kicad-mcp`) for live, interactive board control in a running KiCad 9 session (inspect nets/footprints, move/rotate parts, add traces, refill zones, with instant GUI feedback and undo), and the existing `pcb-autoroute` pipeline (unmodified) for headless bulk autorouting and DRC-cleanup. kicad-mcp requires KiCad 9 with its IPC API server enabled and runs under a pinned Python 3.12 `uv` environment (Python 3.14 has no prebuilt `pynng` wheel yet). pcb-autoroute's KiCad-8-specific workarounds haven't been re-verified against KiCad 9.
Invoke: ask to design, route, fix, or inspect a KiCad board — the skill picks live vs. headless tools based on the task.
