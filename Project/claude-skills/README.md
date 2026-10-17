# claude-skills

The single index of every Claude Code skill, agent and command I use. Self-written skills live in this repo. Everything else is only listed here.

## Layout

```
skills/
├── general/      → ~/.claude/skills          (user scope, every folder)
├── cs/           → <setup root>/.claude/skills  (project scope)
├── project/      → <setup root>/.claude/skills  (project scope)
├── in-progress/  not linked: drafts
└── deprecated/   not linked: retired
```

Claude Code only loads `<skills-dir>/<name>/SKILL.md`, one level deep. After adding, moving or removing a skill, run:

```bash
./link-skills.sh          # add --dry-run to preview
```

It creates symlinks, refuses duplicate names, and prunes links to skills that moved to `in-progress/` or `deprecated/`.

## Index

**Source** column: *own* = in this repo · *npx* = `npx skills` (in `<setup root>/.agents/skills`, tracked by `<setup root>/skills-lock.json`, **do not move**) · *plugin* = installed Claude Code plugin · *built-in* = ships with Claude Code.

### Own skills

| Skill | Bucket | What it does |
|---|---|---|
| [remote-pi-min](skills/general/remote-pi-min/SKILL.md) | general | SSH/SCP into the Raspberry Pi "min" with a key, used for UAV work |
| [coding-guidelines](skills/general/coding-guidelines/SKILL.md) | general | Guidelines against common LLM coding mistakes. **Use whenever writing code.** Forked from karpathy-guidelines |
| [upload-to-github](skills/general/upload-to-github/SKILL.md) | general | Check code, add README + .gitignore + LICENSE, then push via `gh` |
| [root-cause-debugging](skills/general/root-cause-debugging/SKILL.md) | general | Debug loop: recite marker, reproduce, map fail path/knobs, falsify hypotheses, run ledger, one fix, stop after 3 fails |
| [verification-before-completion](skills/general/verification-before-completion/SKILL.md) | general | Run a fresh check before any "done/fixed" claim; end with a [Verified] evidence block. Forked from obra/superpowers |
| [grilling](skills/general/grilling/SKILL.md) | general | Interview the user in numbered rounds over a plan's design tree, with a recommended answer per question; no action until shared understanding. Forked from mattpocock/skills |
| [grill-me](skills/general/grill-me/SKILL.md) | general | `/grill-me` entry point (user-invoked only) that loads `grilling`. Forked from mattpocock/skills |
| [skill-intake](skills/general/skill-intake/SKILL.md) | general | `/skill-intake <link or name> [method]` (user-invoked only): read an outside skill/plugin/MCP server, compare with this setup, recommend tiers, then install or fork only the chosen way |
| [report-format-check](skills/cs/report-format-check/SKILL.md) | cs | Check an NKRAFA report `.docx` against the format spec |

Longer notes are in each bucket's README: [general](skills/general/README.md) · [cs](skills/cs/README.md) · [project](skills/project/README.md). The ``linux`` branch leaves out remote_vm_kali, pcb-autoroute and pcb-design (Windows-only); they live on ``main``.

### Own agents & commands

None on the `linux` branch. The `nkrafa-*` agents and `/Review_NKRAFA_report` need Word COM, so they live on `main` only.

### Third-party skills

| Skill | Source | What it does |
|---|---|---|
| `animate` | npx · emilkowalski/skills | Build an animation from scratch (tool, properties, curve, duration, enter/exit) |
| `review-animations` | npx · emilkowalski/skills | Strict review of existing animations against Kowalski's rules |
| `improve-animations` | npx · emilkowalski/skills | Read-only codebase motion audit and prioritized fix plan |
| `find-animation-opportunities` | npx · emilkowalski/skills | Find UI spots that should animate, and reject the ones that shouldn't |
| `animation-vocabulary` | npx · emilkowalski/skills | Reverse glossary: vague motion description → exact term |
| `apple-design` | npx · emilkowalski/skills | Apple interface/motion principles adapted for the web |
| `emil-design-eng` | npx · emilkowalski/skills | Umbrella skill for UI polish and animation advice |
| `pick-ui-library` | npx · emilkowalski/skills | Choose a trusted UI library instead of hand-rolling one |
| `prototype` | npx · emilkowalski/skills | Build several variants of a UI piece with a switcher |
| `figma:*` | plugin | Figma design ↔ code, FigJam diagrams, Slides |

### Built-in skills & agents worth remembering

| Name | Kind | Use for |
|---|---|---|
| `dataviz` | skill | Load before any chart, plot or dashboard |
| `artifact-design` / `artifact-capabilities` | skill | Designing Artifact pages and their runtime features |
| `run` | skill | Launch the app to see a change working |
| `init` | skill | Create a `CLAUDE.md` for a new project folder |
| `simplify` | skill | Quality cleanup of changed code (not bug hunting) |
| `code-review` / `security-review` | skill | Bug review / security review of a diff or PR |
| `update-config` | skill | `settings.json`: hooks, permissions, env vars |
| `keybindings-help` | skill | Edit `~/.claude/keybindings.json` |
| `loop` / `schedule` | skill | Run something on an interval / as a cron cloud agent |
| `claude-api` | skill | Claude API / SDK reference |
| `Explore` | agent | Read-only broad code search |
| `Plan` | agent | Implementation plans before coding |
| `general-purpose` / `claude` | agent | Catch-all multi-step tasks |
| `claude-code-guide` | agent | Questions about Claude Code, the Agent SDK, and the API |
| `statusline-setup` | agent | Configure the status line |
