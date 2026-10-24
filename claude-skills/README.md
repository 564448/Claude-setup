# claude-skills

The single index of every Claude Code skill, agent and command I use. Self-written skills live in this repo. Everything else is only listed here.

## Layout

```
skills/
├── general/      → ~/.claude/skills          (user scope, every folder)
├── cs/           → C:\Knight\Claude\.claude\skills  (project scope)
├── project/      → C:\Knight\Claude\.claude\skills  (project scope)
├── in-progress/  not linked: drafts
└── deprecated/   not linked: retired
```

Claude Code only loads `<skills-dir>/<name>/SKILL.md`, one level deep. After adding, moving or removing a skill, run:

```powershell
.\link-skills.ps1          # add -DryRun to preview
```

It creates directory junctions (no admin rights needed), refuses duplicate names, and prunes links to skills that moved to `in-progress/` or `deprecated/`.

## Index

**Source** column: *own* = in this repo · *npx* = `npx skills` (in `C:\Knight\Claude\.agents\skills`, tracked by `C:\Knight\Claude\skills-lock.json`, **do not move**) · *plugin* = installed Claude Code plugin · *built-in* = ships with Claude Code.

### Own skills

| Skill | Bucket | What it does |
|---|---|---|
| [remote-pi-min](skills/general/remote-pi-min/SKILL.md) | general | SSH/SCP into the Raspberry Pi "min" with a key, used for UAV work |
| [remote_vm_kali](skills/general/remote_vm_kali/SKILL.md) | general | SSH/SCP into the Kali VM (key first, password fallback), used for Cyber |
| [coding-guidelines](skills/general/coding-guidelines/SKILL.md) | general | Guidelines against common LLM coding mistakes. **Use whenever writing code.** Forked from karpathy-guidelines |
| [upload-to-github](skills/general/upload-to-github/SKILL.md) | general | Check code, add README + .gitignore + LICENSE, then push via `gh` |
| [root-cause-debugging](skills/general/root-cause-debugging/SKILL.md) | general | Debug loop: recite marker, reproduce, map fail path/knobs, falsify hypotheses, run ledger, one fix, stop after 3 fails |
| [verification-before-completion](skills/general/verification-before-completion/SKILL.md) | general | Run a fresh check before any "done/fixed" claim; end with a [Verified] evidence block. Forked from obra/superpowers |
| [grilling](skills/general/grilling/SKILL.md) | general | Interview the user in numbered rounds over a plan's design tree, with a recommended answer per question; no action until shared understanding. Forked from mattpocock/skills |
| [grill-me](skills/general/grill-me/SKILL.md) | general | `/grill-me` entry point (user-invoked only) that loads `grilling`. Forked from mattpocock/skills |
| [skill-intake](skills/general/skill-intake/SKILL.md) | general | `/skill-intake <link or name> [method]` (user-invoked only): read an outside skill/plugin/MCP server, compare with this setup, recommend tiers, then install or fork only the chosen way |
| [distill-memory](skills/general/distill-memory/SKILL.md) | general | `/distill-memory [topic]` (user-invoked only): distill the session's instructions into topic-folder memories, confirming each step |
| [frontend-design](skills/general/frontend-design/SKILL.md) | general | Single entry point for front-end design: picks the lead among taste / impeccable / emil and applies 8 decisions where they conflict. Reads their files by path |
| [report-format-check](skills/cs/report-format-check/SKILL.md) | cs | Check an NKRAFA report `.docx` against the format spec |
| [pcb-autoroute](skills/project/pcb-autoroute/SKILL.md) | project | Headless KiCad 8 placement → Freerouting → DRC → Gerbers |
| [pcb-design](skills/project/pcb-design/SKILL.md) | project | Live KiCad 9 editing via kicad-mcp, plus pcb-autoroute for bulk routing |

Longer notes are in each bucket's README: [general](skills/general/README.md) · [cs](skills/cs/README.md) · [project](skills/project/README.md).

### Own agents & commands (in `C:\Knight\Claude\.claude\`)

| Name | Kind | What it does |
|---|---|---|
| `nkrafa-report-formatter` | agent | Formats a report `.docx` into NKRAFA format (structure, fonts, page numbers, Thai justification) |
| `nkrafa-detail-checker` | agent | Read-only hunt for tiny spec deviations in a formatted NKRAFA report |
| `/Review_NKRAFA_report` | command | Loops formatter ↔ checker until the report is fully conformant ([how they fit](skills/cs/README.md#how-the-nkrafa-tooling-fits-together)) |

Agents and commands are single `.md` files. Junctions only work for folders, so these stay in `.claude/` and are listed here only.

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
| `design-taste-frontend` | npx · Leonxlnx/taste-skill | Anti-slop web page / app-screen art direction: dealt palettes and directions, real-browser inspector, screenshot fix loop (MIT, v2.1.4) |
| `impeccable` | `npx impeccable install` · pbakaus/impeccable | Front-end design: `/impeccable <command>` with 24 commands (shape, critique, audit, polish, typeset, layout, colorize, animate, live…) + detector engine. Installed project-scope, **no hooks** (Apache-2.0, v4.7.0). Hooks: `/impeccable hooks on` |
| `impeccable-*` (4 agents) | `npx impeccable install` · pbakaus/impeccable | asset-producer, documenter, finish-reviewer, manual-edit-applier; used by impeccable commands, in `.claude\agents` |
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
