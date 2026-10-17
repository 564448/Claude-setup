# Knight Workflow Guide

## Paths
- **Setup root**: the folder this repo is cloned to, and where Claude is run from (e.g. `/home/knight/claude`). Holds `CLAUDE.md`, `.claude/`, `.agents/` and `Project/claude-skills/`.
- **Work root**: the sibling folder `Knight` (e.g. `/home/knight/Knight`) holding the three work folders `ClaudeTaughtMe/`, `CS/` and `Project/`. `bootstrap.sh` adds it to `permissions.additionalDirectories`.

The rules below say "setup root" and "work root"; Auto mode covers both.

## Behavior by permission mode

- **Manual mode** (default, requires approval per action): follow all rules in this file as written — confirm before creating/writing `.md` files, ask before filing ambiguous work, etc.
- **Auto mode** (auto-accept edits): full access to read/write any file and run any terminal command *within the setup root and work root only*, without asking for confirmation first. Filing-location rules still apply, but no need to pause and confirm before writing `.md` files.
- **Bypass-permissions mode**: full access to this pc, read/write/edit any file and run any terminal command *anywhere on this PC* and every other things that you want, without asking for confirmation first.

## How to approach a request
Before acting, decide which kind of request it is:

1. **Clear steps, or a simple task.** Read the steps and predict the result they will actually produce. Then judge whether doing them makes sense, and whether a simpler or better way would reach the same result or a better one. If there is one, tell the user before going ahead.
2. **Only the desired outcome is given.** Before choosing a method, work out whether the outcome is achievable and what limits it (technical, time, hardware, permissions, data). Tell the user about any blocker or trade-off. If the outcome still leaves several real design decisions open (e.g. a new project, skill or board, or work spanning more than one session), load the `grilling` skill and raise these findings in its first round instead of separately.

For either kind, if the task is very complex, you may search GitHub for similar projects or ideas before designing your own solution.

The work root is a personal workspace with three top-level folders, categorized by purpose. Store new work in the folder matching its purpose.

- **ClaudeTaughtMe/** — Things the user wants to learn that are *not* related to their academic studies (general knowledge, side curiosities, explanations).
- **CS/** — Academic coursework. Organized by year level, then by subject (e.g. `CS/CS3/<subject>`).
- **Project/** — Personal projects (e.g. `Hack4Hope`, `UAV`).

## Filing new work
When creating new files or folders, place them under the category that matches their purpose.

Before creating or writing to any `.md` file, confirm with the user first (what will be written and where) — do not write silently, even for routine documentation updates like the skills/agents filing rule below.

If an existing file or folder looks miscategorized, ambiguous, or doesn't fit any of the three categories, flag it to the user and ask how to proceed rather than moving or recategorizing it yourself.

## Claude skills, agents & commands
All skills, agents and commands are indexed in one place: `Project/claude-skills/README.md`. The full rules are in `Project/claude-skills/CLAUDE.md`. Read that file before adding, moving or documenting a skill.
- **Self-written skills** live in `Project/claude-skills/skills/<bucket>/<name>/`. Buckets are `general` (user scope), `cs`, `project`, `in-progress`, `deprecated`. After any change, run `Project/claude-skills/link-skills.sh`, which symlinks them into `~/.claude/skills` or `<setup root>/.claude/skills`. Edit skills in the repo, not through the `.claude/skills` symlinks.
- **Third-party skills** from `npx skills` stay in `.agents/skills` + `skills-lock.json`, and plugins stay where they are. Never move them. They only get a row in the index.
- **Agents / commands** stay in `<setup root>/.claude/agents` and `.claude/commands`. They only get a row in the index.

If a skill doesn't clearly fit one bucket, ask rather than guessing.

## Temporary working files
Claude creates temporary scripts, data, and intermediates in `<setup root>/.scratchpad` to respect the permission boundary and avoid unnecessary permission prompts. This directory can be safely deleted between sessions.

## End-of-task summary
After finishing a piece of work, give the user a brief summary covering:
- What was done
- Any problems encountered
- How each problem was resolved
- Before writing the summary, run the `verification-before-completion` gate and end with its **[Verified]** block.

## Memory organization
Memories in this project's memory folder (`~/.claude/projects/<setup root path with / replaced by ->/memory/`, e.g. `-home-knight-claude`) are grouped by topic:
- A topic with several memories gets its own folder (e.g. `UAV/`) with a `README.md` that lists each file in one line. `MEMORY.md` has only one line per folder, pointing to its README.
- When working on a topic, read its README first, then open only the files that apply.
- A new memory on a topic goes in that topic's folder, and its README is updated in the same step (also when a file is edited or deleted).
- A memory that applies across topics stays at the top level with its own line in `MEMORY.md`.
- Store guidelines only. Mission details, values in code and machine-specific connection data (IP, COM) are not stored.
